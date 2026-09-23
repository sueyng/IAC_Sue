# Private API Gateway with Lambda Authorizer Infrastructure

This CloudFormation template set deploys a private API Gateway infrastructure with Lambda authorizer integration, custom domain support, and Azure AD authentication. The system provides secure API access within a VPC using endpoint integration.

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
| ForwardProxyAddress | String | Yes | http://hisproxydefp.gut.hcc.com.sg:4000 | Forward proxy address |

### API Gateway Configuration
| Parameter | Type | Required | Sample Value | Description |
|-----------|------|----------|--------------|-------------|
| SwaggerBucket | String | Yes | my-swagger-bucket | S3 bucket containing Swagger file |
| SwaggerKey | String | Yes | path/to/swagger.json | Path to Swagger file in the bucket |
| ApigwVpceId | String | Yes | vpce-00ecd727fe52de81e | VPC Endpoint ID for API Gateway |
| APIName | String | Yes | fhir | Name of the API |
| APIDescription | String | No | "" | Description for the API (optional) |
| StageName | String | Yes | dev | API stage name |
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
