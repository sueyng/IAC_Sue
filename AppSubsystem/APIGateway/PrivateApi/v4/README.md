# Private API Gateway with Lambda Authorizer Infrastructure (v4)

This CloudFormation template set deploys a private API Gateway infrastructure with Lambda authorizer integration, custom domain support, and Azure AD authentication. The system provides secure API access within a VPC using endpoint integration.

## v4 Changes (Checkmarx/Security Hub Remediation + TISO Compliance)

Four changes in v4:

1. **API Gateway Response Compression** — Addresses finding "API Gateway with invalid compression" on `cf-private-apigw.yaml`.
   - New optional params: `EnableCompression` (yes/no, **default `no`**) + `MinimumCompressionSize` (default `10240` = 10 KB).
   - When `yes`, `MinimumCompressionSize` is applied to the `PrivateApi` — responses ≥ threshold are gzipped when the client sends `Accept-Encoding: gzip`.
   - When `no`, the property is omitted (matches v3 behavior).
   - Project teams should verify their API consumers handle gzip-encoded responses correctly before enabling. Application layer already supports compression — gateway compression is defense-in-depth.

2. **API Gateway Stage Client Certificate** — Addresses Security Hub APIGateway.2 on `cf-private-apigw.yaml`.
   - New optional param: `ApiGatewayClientCertificateId` (default `""`).
   - When provided, the value is attached to the REST API stage via `ClientCertificateId` for backend authentication.
   - When empty, CloudFormation passes an empty `ClientCertificateId` value to clear/unset any certificate previously attached to the stage.
   - Project teams create and rotate the API Gateway client certificate outside CloudFormation, typically from the API Gateway console.

3. **Lambda X-Ray Tracing** — Addresses finding "Lambda functions without X-Ray tracing" on `cf-lambda-authorizer.yaml`.
   - Added `TracingConfig.Mode: Active` on `LambdaAuthorizerFunction`.
   - Added scoped X-Ray IAM policy on `LambdaAuthorizerRole` (`xray:PutTraceSegments`, `xray:PutTelemetryRecords` only).

4. **Lambda VPC Configuration (TISO Compliance)** — Mandatory VpcConfig on `LambdaAuthorizerFunction` for egress control and VPC Flow Log visibility.
   - New **required** params: `VpcId`, `LambdaSubnetIds`, `VpcCidr1`.
   - New **optional** params: `VpcCidr2-5` (for shared-services / multi-CIDR VPC).
   - New resource: `LambdaAuthorizerSecurityGroup` with least-privilege egress:
     - HTTPS (443) → `VpcCidr1-5` (for CloudWatch Logs + X-Ray Interface Endpoints and centralised egress path for Azure AD)

### Pre-deployment requirements (v4)

- Target VPC must have the following Interface Endpoints reachable from `LambdaSubnetIds`:
  - `com.amazonaws.<region>.logs` (for CloudWatch Logs upload)
  - `com.amazonaws.<region>.xray` (for X-Ray trace upload)
- `LambdaSubnetIds` must be **private** subnets with route to Azure AD via the organisation's centralised egress path (shared-services VPC / transit gateway egress). The Lambda SG allows egress only to `VpcCidr1-5` on 443 — public reach is handled by the routing/egress VPC, not the SG.

### Breaking change from v3

- New **required** parameters: `VpcId`, `LambdaSubnetIds`, `VpcCidr1`.

v3 parameter files must be adjusted (add VPC keys) before upgrading to v4. Compression and X-Ray features remain backward-compatible with safe defaults. IaCVersion tag bumped to `AppSubsystem-PrivateApi-v4`.


## Architecture Flow

```
+----------------+     +------------------+     +----------------+     +------------------+
|    Client      |     |   VPC Endpoint   |     |  API Gateway   |     | Lambda          |
|(within VPC)    |---->|   (Execute-API)  |---->|  (Private)     |---->| Authorizer      |
|                |     |                  |     |                |     |                 |
+----------------+     +------------------+     +----------------+     +------------------+
                                                       |
                                                       |
                                                       v
                                              +------------------+
                                              |   Azure AD       |
                                              |   (Authentication)|
                                              |                  |
                                              +------------------+

----------------------------------------------------------------
Flow:
1. Client -> VPC Endpoint  : API request through private endpoint
2. VPC Endpoint -> API GW  : Route request to private API
3. API GW -> Lambda Auth   : Authorize request using Lambda
4. Lambda -> Azure AD      : Validate token with Azure AD
5. API GW -> Backend      : Forward authorized request to backend
```

## Prerequisites

Before deploying this template, ensure you have the following components in place:

### 1. Lambda Authorizer Package
The Lambda authorizer function deployment package must be:
- Built for .NET 8 runtime
- Uploaded to an S3 bucket (specified in LambdaS3bucket parameter)
- Properly configured with the handler specified in parameters

### 2. VPC and Endpoints
Required infrastructure:
- VPC with proper networking setup
- Execute-API VPC Endpoint
- Required security groups and routing

### 3. Azure AD Configuration
Azure AD requirements:
- Registered application with Client ID
- Configured Tenant ID
- Proper permission scopes set up

### 4. SSL Certificate
For custom domain setup:
- Valid SSL certificate in AWS Certificate Manager
- Certificate ARN available for configuration

### 5. Swagger/OpenAPI Definition
API definition requirements:
- Valid Swagger/OpenAPI JSON file
- Uploaded to an S3 bucket
- Path specified correctly in template parameters

## Template Components

### 1. API Gateway CloudWatch Setup (cf-apigw-cloudwatch.yaml)
One-time global setup for API Gateway logging:
- IAM role for CloudWatch logging
- API Gateway account settings
- Environment-based naming conventions

Key Features:
- Account-level CloudWatch configuration
- Reusable across multiple API Gateways
- Environment-specific role naming

### 2. Lambda Authorizer Template (cf-lambda-authorizer.yaml)
Deploys:
- Lambda function for request authorization
- IAM role with necessary permissions
- CloudWatch logging configuration
- Environment variables for Azure AD integration

Key Features:
- VPC deployment support
- Azure AD integration
- Forward proxy configuration
- Environment-based naming

### 3. Private API Gateway Template (cf-private-apigw.yaml)
Deploys:
- Private REST API
- Custom domain configuration
- Base path mappings
- Lambda authorizer integration
- VPC endpoint associations
- Stage configuration with logging and tracing
- Conditional access logging

Key Features:
- Swagger/OpenAPI integration from S3
- Private endpoint access
- Custom domain support
- Stage management
- Optional CloudWatch access logging
- X-Ray tracing enabled

## Deployment Order
1. Deploy CloudWatch setup first (one-time per account)
2. Deploy Lambda Authorizer
3. Deploy Private API Gateway

## Upgrading from v3 to v4

v4 is **NOT a transparent in-place upgrade** from v3. It introduces mandatory VPC configuration for the Lambda authorizer (TISO compliance), which adds new required parameters and changes the Lambda's network egress path. Existing v3 stacks can be upgraded, but require coordinated parameter file changes and a network pre-flight check.

### Breaking changes

**1. New mandatory parameters (no defaults — `update-stack` will fail without them)**

| Parameter | Purpose |
|---|---|
| `VpcId` | VPC where the Lambda SG and ENIs are created |
| `LambdaSubnetIds` | Min 2 private subnets where Lambda ENIs are provisioned |
| `VpcCidr1` | Primary VPC CIDR for SG egress to Interface Endpoints |

**2. Lambda function gets `VpcConfig` (in-place modify, no replacement, but with side effects)**
- ENIs created in the chosen subnets during the update window (~60–90s)
- Cold-start path now uses VPC DNS — slightly longer cold starts (~1–2s)
- Egress path completely changes: v3 used Lambda's managed network with direct internet; v4 uses the subnet's route table

### Pre-flight requirements (silent failures if missed)

The Lambda must be able to reach:
- **CloudWatch Logs / X-Ray** → via Interface VPC Endpoints reachable from `VpcCidr1` (SG egress is wired automatically)
- **Azure AD** (`login.microsoftonline.com` for JWKS) → via the forward proxy at `ForwardProxyAddress` (unchanged from v3)

Without a working egress path, the Lambda runs but every API call returns 401 because the JWKS fetch fails. There is no deploy-time error.

### Safe / in-place changes (no replacement)
- `IaCVersion` tag bumped `v3` → `v4` on every resource
- IAM policy expansion: added `LambdaAuthorizerVPCAccessExecutionPolicy` (ENI lifecycle) and `LambdaAuthorizerXRayWriteAccessPolicy`
- Hardcoded ARN partition `arn:aws:` → `arn:${AWS::Partition}:` (resolves to the same string in commercial AWS — zero diff)
- `TracingConfig: Active` added on Lambda
- `LambdaAuthorizerRole` retention policy changed from blanket `Retain` to `!If [IsProduction, Retain, Delete]` — this is stack metadata, not a resource property, so CF detects no change
- New `LambdaAuthorizerSecurityGroup` with inline egress rules (mandatory `VpcCidr1` + conditional `VpcCidr2-5` via `!If`) — pure new resource

### Recommended upgrade procedure

1. **Verify Interface VPC Endpoints exist** for CloudWatch Logs and X-Ray, and that they are reachable from `VpcCidr1`.
2. **Update the parameter file**: add `VpcId`, `LambdaSubnetIds`, `VpcCidr1`, optional `VpcCidr2`–`VpcCidr5`. Keep the existing `ForwardProxyAddress` value from v3.
3. **Create a changeset** (do not blind `update-stack`) and verify:
   - `LambdaAuthorizerFunction` shows **Modify** (not Replace)
   - `LambdaAuthorizerSecurityGroup` shows **Add** (with inline egress rules for any populated `VpcCidr1-5`)
   - `LambdaAuthorizerRole` shows **Modify** (policy additions only)
4. **Smoke test post-deploy**: call the API with a real Azure AD token and confirm the authorizer returns Allow. If you see 401s, check Lambda CloudWatch logs for JWKS fetch errors — that almost always indicates a broken egress path to Azure AD.

## Template Parameters

### Lambda Authorizer Configuration
| Parameter | Type | Required | Sample Value | Description |
|-----------|------|----------|--------------|-------------|
| AppShortName | String | Yes | xyz | Application identifier for resource naming |
| EnvName | String | Yes | nprd | Environment name (e.g., nprd, prod) |
| LambdaS3bucket | String | Yes | apt-lambda-deployment | S3 bucket containing Lambda package |
| CodeZipFileName | String | Yes | LambdaAuthorizer.zip | Lambda function code zip file |
| LambdaRuntime | String | Yes | dotnet8 | Lambda runtime |
| LambdaHandler | String | Yes | Ihis.PopHealth.AdminPortal.LambdaAuthorizer::Ihis.PopHealth.AdminPortal.LambdaAuthorizer.Function::FunctionHandler | Lambda function handler |
| AzureAdClientId | String | Yes | 56d10777-fe7c-494b-a37b-88a50fb7cd29 | Azure AD application client ID |
| AzureAdTenantId | String | Yes | 6ef68169-639f-4d8f-8b7a-c981fab3c31b | Azure AD tenant ID |
| VpcId | String | **Yes (new in v4)** | vpc-02fb2e32bbb6ff24e | VPC ID where Lambda SG is created |
| LambdaSubnetIds | List | **Yes (new in v4)** | subnet-abc,subnet-def | Private subnets for Lambda ENIs (min 2 for HA) |
| VpcCidr1 | String | **Yes (new in v4)** | 10.193.0.0/16 | Primary VPC CIDR for SG egress rules |
| VpcCidr2-5 | String | No | "" | Additional CIDRs for shared-services / multi-CIDR VPC |

| ForwardProxyAddress | String | Yes | http://proxy.corp:8080 | Forward proxy address for Lambda egress to Azure AD |

### API Gateway Configuration
| Parameter | Type | Required | Sample Value | Description |
|-----------|------|----------|--------------|-------------|
| SwaggerBucket | String | Yes | my-swagger-bucket | S3 bucket containing Swagger file |
| SwaggerKey | String | Yes | path/to/swagger.json | Path to Swagger file in the bucket |
| ApigwVpceId | String | Yes | vpce-00ecd727fe52de81e | VPC Endpoint ID for API Gateway |
| APIName | String | Yes | fhir | Name of the API |
| APIDescription | String | No | "" | Description for the API (optional) |
| StageName | String | Yes | dev | API stage name |
| ApiGatewayClientCertificateId | String | No | abc123 | API Gateway client certificate ID for REST API stage backend authentication |
| CustomDomainName | String | No | api.seedideation.com | Custom domain for API |
| SSLCertificateArn | String | No | arn:aws:acm:ap-southeast-1:123456789012:certificate/5e10a9f8-f3b4-4e6b-8dd7-cfc26a0eaf08 | SSL certificate ARN |
| LambdaAuthorizerFunctionArn | String | No | arn:aws:lambda:ap-southeast-1:123456789012:function:fhir-nprd-LambdaAuthorizer | Lambda authorizer function ARN |
| AccessLogFormat | String | No | '$context.identity.sourceIp $context.identity.caller [$context.requestTime]' | Format string for access logs (leave empty to disable) |
| LogRetentionInDays | Number | No | 30 | Number of days to retain access logs |

## Monitoring and Logs

### Access Logging
- **Conditional CloudWatch Access Logs**: Enable or disable by setting the `AccessLogFormat` parameter
- **Custom Log Format**: Configurable format string using API Gateway context variables
- **Configurable Retention**: Set log retention period using `LogRetentionInDays` parameter

### Stage Settings
- Detailed CloudWatch metrics enabled
- Request/response logging enabled
- X-Ray tracing enabled
- Method-level logging configuration:
  - Log level: INFO (includes ERROR and INFO logs)
  - Detailed metrics
  - Data trace enabled for request/response logging

## Security Considerations

### Network Security
- Private API Gateway accessible only through VPC endpoint
- VPC endpoint policy restricting access
- No public internet exposure

### Authentication
- Lambda authorizer validates all requests
- Azure AD token validation
- Custom header authorization

### Authorization
- Request-based authorization model
- Configurable authorization caching
- Fine-grained access control

### Logging Security
- IAM role-based access control for logs
- Segregated logging per AWS account
- Secure log retention policies
- Option to disable access logging for sensitive APIs

## Maintenance and Updates

### Lambda Updates
- Upload new package to S3
- Update parameters if handler changes
- Deploy template with new parameters

### API Updates
- Update Swagger definition
- Upload to S3 bucket
- Update SwaggerBucket and SwaggerKey parameters
- Redeploy API Gateway template

### SSL Certificate Renewal
- Update certificate in ACM
- Update parameter with new ARN
- Redeploy API Gateway template

### Access Log Configuration
- To enable access logging: provide a valid format string in the `AccessLogFormat` parameter
- To disable access logging: set the `AccessLogFormat` parameter to an empty string
- Adjust retention period by changing the `LogRetentionInDays` parameter

## Common Issues and Troubleshooting

### Logging Issues
1. Missing Access Logs
   - Verify `AccessLogFormat` parameter is not empty
   - Check IAM role permissions
   - Confirm log group exists
   - Verify log format is valid

2. Missing Method Execution Logs
   - Verify stage settings
   - Check IAM role permissions
   - Confirm log level configuration

3. X-Ray Traces Not Appearing
   - Verify TracingEnabled setting in stage
   - Check IAM permissions
   - Validate X-Ray daemon configuration

### Authorization Failures
1. Token Validation
   - Check Azure AD configuration
   - Verify token format and claims
   - Review Lambda authorizer logs
   - Validate Azure AD endpoints

2. Lambda Authorizer
   - Check Lambda execution role
   - Verify environment variables
   - Review CloudWatch logs
   - Check proxy configuration

### Connectivity Issues
1. API Access
   - Verify VPC endpoint configuration
   - Check security group rules
   - Validate network routing
   - Confirm VPC endpoint policies

2. Custom Domain
   - Verify SSL certificate validity
   - Check DNS configuration
   - Validate base path mapping
   - Confirm domain name settings

## Swagger/OpenAPI S3 Configuration

To properly configure the Swagger/OpenAPI integration:

1. Upload your Swagger JSON file to an S3 bucket
2. In the CloudFormation parameters:
   - Set `SwaggerBucket` to your S3 bucket name
   - Set `SwaggerKey` to the path of the file within the bucket
3. Ensure the IAM role deploying the template has access to the S3 bucket
4. API Gateway will pull the Swagger definition directly from S3 during deployment
