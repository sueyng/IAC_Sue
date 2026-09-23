# FrontendSPA with Lambda Reverse Proxy, Private API Gateway, and Application Load Balancer

## Version 6

**IaC Version Tag:** `AppSubsystem-SPAIntranet-v6`

### Changes from v5.1
- **ELB.4 Security Hub remediation** *(post-release patch)*: `ALB` in `cf-alb-vpce.yaml` now sets `routing.http.drop_invalid_header_fields.enabled: "true"` in `LoadBalancerAttributes`. ALB rejects requests with malformed HTTP headers (RFC 7230 violations). **Stack update applies live — no ALB replacement, no DNS change, no downtime.** Compliant clients unaffected; legacy non-RFC clients may see HTTP 400s — verify in non-prod first.
- **Lambda VPC Attachment (Mandatory)**: The `LambdaS3ReverseProxy` function is now VPC-attached to enhance network security posture. Lambda security group is provisioned with least-privilege egress (HTTPS to S3 Gateway Endpoint and VPC CIDR only).
- **New mandatory parameters** on the Lambda nested stack:
  - `VpcId` — VPC where the Lambda SG is created
  - `LambdaSubnetIds` — private subnet IDs where Lambda ENIs are provisioned (min 2 for HA)
  - `VpcCidr1` — primary VPC CIDR (for Interface Endpoint egress)
  - `S3PrefixListId` — S3 Gateway Endpoint prefix list ID (for S3 egress)
- **New optional parameters** on the Lambda nested stack (for multi-VPC/shared-services patterns):
  - `VpcCidr2`, `VpcCidr3`, `VpcCidr4`, `VpcCidr5` — each non-empty value adds a conditional `AWS::EC2::SecurityGroupEgress` rule on the Lambda SG (HTTPS 443 to the CIDR)
- **Main template changes**: `VpcCidr1` and `S3PrefixListId` are now MANDATORY (previously optional). `VpcCidr1`–`VpcCidr5` and `S3PrefixListId` are all passed through to the Lambda nested stack (matches the existing pass-through pattern to the ALB nested stack).
- **Optional CloudFormation Stack Notifications**: New toggle-based parameters on `cf-intranet-frontend-spa-main.yaml` to enable SNS notifications on nested stacks (Lambda, API Gateway, ALB).
  - `EnableStackNotifications` — `yes` / `no` (default: `no`)
  - `StackNotificationSNSTopicArn` — SNS topic ARN (required when toggle is `yes`)
  - Recommended for NEW stack creation only. See [Stack Notifications](#stack-notifications-new-in-v6) section.
- **Optional API Gateway Access Logging**: New parameters on `cf-intranet-frontend-spa-main.yaml` to enable API Gateway access logs via CloudWatch. Addresses Checkmarx finding on missing stage `AccessLogSetting`. Follows the same pattern as `AppSubsystem/APIGateway/PrivateApi/v3`.
  - `ApiGwAccessLogFormat` — JSON format string (default `""` — disables access logging)
  - `ApiGwLogRetentionInDays` — log retention in days (default `30`)
  - When `ApiGwAccessLogFormat` is non-empty, a CloudWatch log group `/aws/apigateway/${APIName}-access-logs` is created and wired to the stage via `AccessLogSetting`.
- **Optional API Gateway Response Compression**: New parameters on `cf-intranet-frontend-spa-main.yaml` to enable gzip compression on API responses. Addresses Checkmarx finding "API Gateway with invalid compression".
  - `ApiGwEnableCompression` — `yes` / `no` (default: `no` — safe initial deployment; project teams should audit client gzip handling before enabling, especially .NET `HttpClient` with `AutomaticDecompression`)
  - `ApiGwMinimumCompressionSize` — minimum response size in bytes to trigger compression (default: `10240` = 10 KB; only used when toggle is `yes`)
  - When `ApiGwEnableCompression: yes`, `MinimumCompressionSize` is applied to the `PrivateApi` RestApi; responses ≥ threshold are gzipped, smaller payloads pass through.
  - When `no`, the property is omitted from the RestApi (no gateway compression; matches v6 original behavior). Checkmarx finding remains open and requires security team suppression approval until enabled.
  - Application layer already supports compression — gateway compression is defense-in-depth.
- **APIGateway.2 Security Hub remediation** *(post-release patch)*: New optional `ApiGatewayClientCertificateId` parameter lets project teams attach a console-managed API Gateway client certificate to the REST API stage via `ClientCertificateId` for backend authentication. Project teams own certificate creation and rotation outside CloudFormation. Leave empty to preserve existing behavior; provide a certificate ID to remediate APIGateway.2.
- **IaC Version Tag** bumped to `AppSubsystem-SPAIntranet-v6` across all resources in `cf-lambda-s3reverseproxy.yaml`.
- **Parameter file hygiene**: env YAML file `parameters-intranet-frontend-spa-main.yaml` aligned with template — added missing keys `LambdaRuntime`, `LambdaHandler`, `LambdaLogRetentionInDays`, `ALBSslPolicy` (pre-existing drift from earlier versions; template defaults were being used silently).

### ⚠️ Pre-deployment requirement (v6)
The target VPC MUST have the following endpoints provisioned before deployment, otherwise the Lambda will hang on first invocation:
- **S3 Gateway VPC Endpoint** (`com.amazonaws.{region}.s3`) — free, required for S3 access
- **CloudWatch Logs Interface Endpoint** (`com.amazonaws.{region}.logs`) — required for log writes
- **X-Ray Interface Endpoint** (`com.amazonaws.{region}.xray`) — required (`TracingConfig: Active` is enabled on the Lambda)

### Upgrade path (v5.1 → v6)
- `VpcConfig` is an **updatable** Lambda property — no function replacement, rolling update.
- No downtime expected; brief overlap between VPC-less and VPC-attached versions during update.
- Lambda IAM role already has `ec2:CreateNetworkInterface/DeleteNetworkInterface/DescribeNetworkInterfaces` permissions (carried over from v5.1), so no IAM changes required.
- A new `LambdaSecurityGroup` resource will be created on upgrade.
- Project teams **MUST provide**: `VpcCidr1` and `S3PrefixListId` (previously optional) — otherwise v6 deployment fails parameter validation.
- ENI cleanup on stack deletion can take 20–40 minutes — plan accordingly.

## Stack Notifications (new in v6)

v6 introduces optional CloudFormation stack event notifications via SNS on all 3 nested stacks (Lambda, API Gateway, ALB).

### How it works
- Set `EnableStackNotifications: yes` and provide `StackNotificationSNSTopicArn`.
- Nested stacks (`Lambdas3ReverseProxyStack`, `PrivateApiGatewayStack`, `ALBtoVPCEStack`) are configured with the SNS topic via the `NotificationARNs` property.
- The SNS topic is **not provisioned by this template** — project teams must create the topic separately and pass its ARN.

### Recommendation
- **Turn ON for NEW stack creation.** Notifications will apply to all newly created nested stacks.
- **Existing stacks**: see limitations below before flipping the toggle on.

### ⚠️ Limitations

**1. Existing nested stacks will NOT be updated automatically**
The `NotificationARNs` property on a nested stack resource is honored by CloudFormation only at **child stack creation time**. If you upgrade an existing v5.1 deployment to v6 and set `EnableStackNotifications=yes`, the parent stack will accept the change, but the already-created nested stacks will NOT pick up the new SNS topic.

**Workaround for existing stacks** — update each nested stack manually:
- **CloudFormation Console**: select the nested stack → *Update* → *Use current template* → on the next page, edit *Notification options* → add the SNS topic ARN. Alternatively use *Stack actions* → *Create change set* with current template and add the notification ARN there.
- **AWS CLI**:
  ```bash
  aws cloudformation update-stack \
    --stack-name <nested-stack-name> \
    --use-previous-template \
    --notification-arns <sns-topic-arn> \
    --capabilities CAPABILITY_NAMED_IAM
  ```

**2. Parent stack is not configured by this template**
CloudFormation does not allow a stack to self-configure its own notification target via the template — this is an AWS design constraint (the `NotificationARNs` property only exists on the `AWS::CloudFormation::Stack` resource type for nested/child stacks).

To enable notifications on the **parent stack**, configure it at deploy time:
- **CloudFormation Console**: when creating/updating the parent stack, expand *Notification options* and add the SNS topic ARN.
- **AWS CLI**: pass `--notification-arns <sns-topic-arn>` on `aws cloudformation create-stack` or `update-stack`.

### Backward compatibility
The toggle defaults to `no`, so existing v5.1 deployments upgrading to v6 are not forced to provide an SNS topic. Notifications can be added incrementally (see Workaround above).

## Version 5.1

**IaC Version Tag:** `AppSubsystem-SPAIntranet-v5.1`

### Changes from v5
- **Public ALB Ingress via Prefix List**: Added `PrefixListIdInternet` parameter to control inbound traffic on internet-facing ALB using a managed prefix list.
- **Configurable TLS Policy**: Added `ALBSslPolicy` parameter for HTTPS listener. Supports TLS 1.3, TLS 1.2, and post-quantum (PQ) policies. Default: `ELBSecurityPolicy-TLS13-1-2-2021-06`.

## Overview

This project deploys a frontend SPA infrastructure with the following key components:

1. **Lambda Reverse Proxy**: Handles requests and routes them to S3 or other resources
2. **Private API Gateway**: Secures API communication within a VPC
3. **Application Load Balancer (ALB)**: Balances traffic between endpoints or Lambda functions with optional S3 file upload support

## Architecture Flow

```
+----------------+       +------------------+       +----------------+       +------------------+       +----------------+
|    ALB         |       |   API Gateway    |       |    VPC Link    |       |      NLB         |       |   Backend      |
|                |------>|   (Private)      |------>|                |------>|                  |------>|   Services     |
|                |       |                  |       |                |       |                  |       |                |
+----------------+       +------------------+       +----------------+       +------------------+       +----------------+
        |
        |                +------------------+
        |                |   S3 VPC         |
        +--------------->|   Endpoint       |  (Optional File Upload Feature)
                         |                  |
                         +------------------+
```

### Flow:
1. Client → ALB: API request through private API
2. API GW → VPC Link: Route request through VPC Link
3. VPC Link → NLB: Forward to Network Load Balancer
4. NLB → Backend Services: Distribute traffic to backend services
5. (Optional) ALB → S3 VPC Endpoint: Route file upload requests using path-based routing

## Template Structure

```
FrontendSPA/
└── Intranet/
    ├── artifacts/
    │   ├── apispec/
    │   │   └── swagger-frontend.json
    │   └── lambda/
    │       └── s3ReverseProxy.zip
    ├── env/
    │   └── parameters-intranet-frontend-spa-main.yaml    (Main stack parameters)
    ├── cf-private-apigw.yaml
    ├── cf-lambda-s3reverseproxy.yaml
    ├── cf-alb-vpce.yaml
    ├── cf-intranet-frontend-spa-main.yaml
    └── README.md
```

### Template Main Components
- cf-intranet-frontend-spa-main.yaml: Main CloudFormation template to execute nested stacks.

- cf-private-apigw.yaml: CloudFormation template for the private API Gateway.

- cf-lambda-s3reverseproxy.yaml: Template to configure Lambda as a reverse proxy for S3.

- cf-alb-vpce.yaml: Template to set up the ALB and target groups.

- **parameters-intranet-frontend-spa-main.yaml: Parameter file for deployment.**

## Features

1. **Lambda Reverse Proxy**

        Processes requests routed from the ALB.
        Deployed as a serverless function with adjustable runtime.
        Logs managed with configurable retention.

2. **Private API Gateway**

        Secure API access through VPC Endpoint.
        Optional custom domain support with SSL certificate integration.
        Optional stage client certificate support for backend authentication.
        Stage-based configuration for development and production environments.

3. **Application Load Balancer**

        Routes traffic to Lambda reverse proxy or backend services.
        Supports internet-facing or internal schemes for public or private access.
        Configurable subnets, VPC, and security groups.

4. **Security Features**

        Enforces HTTPS-only connections.
        Configurable AWS Prefix List for inbound traffic (both internal and internet-facing ALB).
        Configurable TLS policy via `ALBSslPolicy` parameter (default: TLS 1.3 with TLS 1.2 fallback, includes post-quantum options).
        Comprehensive logging and monitoring setup.

## Parameter Configuration

### Main Stack Parameters (parameters-intranet-frontend-spa-main.yaml)
| Parameter | Description | Example Value | Required |
|-----------|-------------|---------------|----------|
| AppShortName | Application identifier | "apt" | Yes |
| EnvName | Environment name | "nprd" | Yes |
| LambdaS3bucket | Lambda code bucket | "apt-lambda-artifact" | Yes |
| CodeZipFileName | Lambda function code zip file | "s3ReverseProxy-v2.zip" | Yes |
| LambdaRuntime | Runtime for Lambda function | "nodejs20.x" | No |
| LambdaHandler | Lambda function handler | "index.mjs.handler" | No |
| FrontendSPABucketName | Frontend assets bucket | "frontend.seedideation.com" | Yes |
| LambdaLogRetentionInDays | Number of days to retain Lambda logs | 14 | No |
| SwaggerFile | API spec location | "fhir-apigw-swagger/Frontendportal-api-swagger.json" | Yes |
| ApigwVpceId | VPC Endpoint ID for API Gateway (execute-api) | "vpce-0123456789abcdef0" | Yes |
| APIName | API Gateway name | "fhir" | Yes |
| StageName | API Gateway stage | "dev" | Yes |
| ApiGatewayClientCertificateId | API Gateway client certificate ID for REST API stage backend authentication | "abc123" | No |
| CustomDomainName | Custom domain for API Gateway | "api.example.com" | No |
| SSLCertificateArn | SSL certificate ARN for custom domain | "arn:aws:acm:region:account:certificate/id" | No |
| AdditionalCertArn | Additional SSL certificate ARN for ALB HTTPS listener | "arn:aws:acm:region:account:certificate/id" | Yes |
| LambdaAuthorizerFunctionArn | Lambda authorizer function ARN | "arn:aws:lambda:region:account:function:authorizer" | No |
| ApiGwAccessLogFormat | JSON format string for API Gateway access logs (empty disables logging) | `'{"requestId":"$context.requestId","ip":"$context.identity.sourceIp","status":"$context.status"}'` | No |
| ApiGwLogRetentionInDays | API Gateway access log retention in days | 30 | No |
| ALBName | Name for Application Load Balancer | "frontend-alb" | Yes |
| ALBScheme | ALB type (internal/internet-facing) | "internal" | Yes |
| ALBSslPolicy | ELB Security Policy for HTTPS listener (TLS 1.2+ only) | "ELBSecurityPolicy-TLS13-1-2-2021-06" | No |
| VpcId | VPC ID for ALB deployment | "vpc-0123456789abcdef0" | Yes |
| IngressSubnetIds | Subnet IDs for ALB deployment (comma-separated) | "subnet-123,subnet-456" | Yes |
| VPCEndpointIP1 | VPC Interface Endpoint IP - AZ1 | "10.0.0.1" | Yes |
| VPCEndpointIP2 | VPC Interface Endpoint IP - AZ2 | "10.0.1.1" | No |
| VPCEndpointIP3 | VPC Interface Endpoint IP - AZ3 | "10.0.2.1" | No |
| PrefixListIdIntranet | Prefix List ID for intranet traffic (internal ALB) | "pl-0123456789abcdef0" | No |
| PrefixListIdInternet | Prefix List ID for internet traffic (internet-facing ALB) | "pl-0123456789abcdef0" | No |
| EnableS3Upload | Enable S3 upload functionality through ALB | "false" | No |
| S3EndpointIP1 | S3 VPC Interface Endpoint IP - AZ1 | "10.0.0.2" | No* |
| S3EndpointIP2 | S3 VPC Interface Endpoint IP - AZ2 | "10.0.1.2" | No* |
| S3EndpointIP3 | S3 VPC Interface Endpoint IP - AZ3 | "10.0.2.2" | No |
| S3UploadPath | Path pattern for S3 upload route | "/appartifacts/*" | No |

*Required if EnableS3Upload is set to "true"

### Network Security Parameters
Additional network security parameters are available in the YAML parameter files for fine-grained control:

| Parameter | Description | Required |
|-----------|-------------|----------|
| VpcCidr1 | Primary VPC CIDR block for security group rules (ALB + Lambda SG egress to Interface Endpoints) | **Yes** (v6) |
| VpcCidr2 | Secondary VPC CIDR block — optional, adds conditional egress rule on Lambda SG when set | No |
| VpcCidr3 | Tertiary VPC CIDR block — optional, adds conditional egress rule on Lambda SG when set | No |
| VpcCidr4 | Quaternary VPC CIDR block — optional, adds conditional egress rule on Lambda SG when set | No |
| VpcCidr5 | Quinary VPC CIDR block — optional, adds conditional egress rule on Lambda SG when set | No |
| S3PrefixListId | S3 Gateway Endpoint prefix list ID — required by Lambda SG egress to S3 | **Yes** (v6) |

These parameters support up to 5 VPC CIDR ranges for complex multi-VPC architectures, VPC peering, and hybrid cloud connectivity. Configure these in `parameters-alb-vpce.yaml` and `parameters-intranet-frontend-spa-main.yaml`.


### Supported Environment Names
- Non-Production: nprd, nprd-dev, nprd-stg, nprd-sit1, nprd-sit2, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b
- Production: prod, prod-a, prod-b

## Important Notes

1. Regional Limitations:
Custom domain ACM certificates must be in the same region as the API Gateway.
2. Subnets:
Ensure that subnets provided for ALB are in the same VPC and span at least two Availability Zones.
3. Lambda Handler:
Ensure the handler matches the entry point in the uploaded Lambda code.
4. Environment Names:
Consistent naming conventions ensure smooth deployment across environments.

## Migration from v5 to v5.1

1. Add `PrefixListIdInternet` and `ALBSslPolicy` to your parameter file (ALBSslPolicy defaults to `ELBSecurityPolicy-TLS13-1-2-2021-06` if not specified)
2. **If using internet-facing ALB**: Create a managed prefix list with the required inbound CIDRs and provide `PrefixListIdInternet` value **before** updating the stack. Without this, all inbound traffic to the public ALB will be blocked after the update.
   - **If using internal ALB**: No impact. The private ALB ingress is unchanged.
   - To provision prefix lists via CloudFormation, refer to `InfraPlatform/prefixlist/v1` template.
3. Update the stack with the new templates

