# FrontendSPA with Lambda Reverse Proxy, Private API Gateway, and Application Load Balancer

## Version 7.1 (Security Enhancement — TLS 1.3 / Configurable Security Policy)

**IaC Version Tag:** `AppSubsystem-SPAIntranet-v7.1`

Five changes in v7.1, all scoped to `cf-private-apigw.yaml` (`cf-lambda-authorizer.yaml` is unchanged):

  - ⛔ **No direct migration from `TLS_1_2` to `SecurityPolicy_*`**: a v7 stack with a custom domain cannot be upgraded to v7.1 and switched from `TLS_1_2` to a `SecurityPolicy_*` value in the same or a later deployment — the update fails with "domain name already exists" and rolls back. Do not delete the custom domain or the stack to work around this; contact the **SEET Infra team** for assistance.
  - IaC Version Tag bumped to `AppSubsystem-SPAIntranet-v7.1`.

1. **`SecurityPolicy` parameterized** — was hardcoded `TLS_1_2` on the custom domain name in v7.
   - New optional param `ApiSecurityPolicy` (`Default: 'TLS_1_2'`), `AllowedValues`-enforced by CloudFormation:
     - Legacy: `TLS_1_2`
     - Enhanced (TLS 1.3, optionally with FIPS/PFS/post-quantum cipher suites): `SecurityPolicy_TLS13_1_2_2021_06`, `SecurityPolicy_TLS13_1_2_PQ_2025_09`, `SecurityPolicy_TLS13_1_2_FIPS_PQ_2025_09`, `SecurityPolicy_TLS13_1_2_PFS_PQ_2025_09`, `SecurityPolicy_TLS13_1_3_2025_09`, `SecurityPolicy_TLS13_1_3_FIPS_2025_09`
   - Default `TLS_1_2` already satisfies PCI DSS 4.0 / NIST SP 800-52 Rev.2 / HIPAA baselines — move to an enhanced value only when a specific compliance driver requires TLS 1.3 or FIPS/post-quantum ciphers.

2. **Custom domain name resource type selected by `ApiSecurityPolicy`** — two conditional resources, only one is ever created:

   | `ApiSecurityPolicy` | Logical ID | Resource type | Condition |
   |---|---|---|---|
   | `TLS_1_2` | `ApiGatewayDomainName` | `AWS::ApiGatewayV2::DomainName` (same logical ID and type as v7) | `EnableCustomDomainLegacy` |
   | `SecurityPolicy_*` | `ApiGatewayDomainNameEnhanced` | `AWS::ApiGateway::DomainName` | `EnableCustomDomainEnhanced` |

   - `AWS::ApiGatewayV2::DomainName`'s `SecurityPolicy` only supports `TLS_1_0`/`TLS_1_2` per AWS's CloudFormation resource schema — it cannot enable TLS 1.3.
   - `AWS::ApiGateway::DomainName` (the classic REST API custom domain resource — **not** `AWS::ApiGateway::DomainNameV2`, which is scoped to private-endpoint-type domain names) was extended by AWS in Nov 2025 with the enhanced `SecurityPolicy_*` values for `REGIONAL` custom domain names.
   - CloudFormation does not allow a conditional `Type` or duplicate logical IDs, which is why two logical IDs are used.
   - `ApiGatewayBasePathMapping` and the `PrivateApi` metadata select whichever domain resource exists via `!If [IsLegacyTlsPolicy, ...]`. `Ref` on either resource returns the domain name string.

3. **New `EndpointAccessMode` parameter** (`BASIC` | `STRICT`, default `BASIC`).
   - Applied only when `ApiSecurityPolicy` is an enhanced (`SecurityPolicy_`-prefixed) value; omitted entirely for `TLS_1_2`.
   - **BASIC**: standard behavior, no extra validation — use for first rollout of an enhanced policy on a live API.
   - **STRICT**: adds a check that the request arrived via the endpoint type the domain declares (`REGIONAL`); rejects otherwise — use for regulated/sensitive workloads once traffic under `BASIC` has been verified.
   - Recommended rollout: deploy with an enhanced `ApiSecurityPolicy` + `EndpointAccessMode: BASIC` first, verify traffic/access logs, then switch to `STRICT`. Mode changes can take up to 15 minutes to fully propagate.

4. **New `ApiSecurityPolicy` / `EndpointAccessMode` also applied directly to `PrivateApi`.**
   - `AWS::ApiGateway::RestApi` carries its own independent `SecurityPolicy`/`EndpointAccessMode` properties, separate from the custom domain name's — these are two different TLS termination points.
   - Both must be set for the chosen policy to take effect end-to-end: setting it only on the custom domain leaves the API's own native endpoint (reached directly via the VPC endpoint, bypassing the custom domain) on its default `TLS_1_2`.
   - `SecurityPolicy` is always set on `PrivateApi`; `EndpointAccessMode` only for enhanced policies.

## Version 7

**IaC Version Tag:** `AppSubsystem-SPAIntranet-v7`

### Changes from v6
- **Additional path routing with optional transforms**: `cf-alb-vpce.yaml` now supports two optional extra S3 listener rules and one optional backend listener rule.
  - `S3AdditionalPathPattern1` creates listener rule priority `11`.
  - `S3AdditionalPathPattern2` creates listener rule priority `12`.
  - `BackendAdditionalPathPattern1` creates listener rule priority `13`.
  - S3 additional path rules forward to the existing `S3TargetGroup` and require `EnableS3Upload=true`.
  - Backend additional path rule forwards to the existing `ALBTG` and does not require `EnableS3Upload=true`.
  - Each rule can optionally apply host-header rewrite and URL rewrite transforms.
  - Ensure the ALB listener does not already have manually-created rules using priorities `11`, `12`, or `13` before enabling these paths.
  - Leave the new parameters empty to preserve v6 routing behavior.

### Changes inherited from v6
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
  - Recommended for NEW stack creation only. See [Stack Notifications](#stack-notifications-introduced-in-v6) section.
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
- **APIGateway.2 Security Hub remediation** *(post-release patch)*: New optional `ApiGatewayClientCertificateId` parameter lets project teams attach a console-managed API Gateway client certificate to the REST API stage via `ClientCertificateId` for backend authentication. Project teams own certificate creation and rotation outside CloudFormation. Leave empty to clear/unset any certificate previously attached to the stage; provide a certificate ID to remediate APIGateway.2.
- **IaC Version Tag** is `AppSubsystem-SPAIntranet-v7` for this version.
- **Parameter file hygiene**: env YAML file `parameters-intranet-frontend-spa-main.yaml` aligned with template — added missing keys `LambdaRuntime`, `LambdaHandler`, `LambdaLogRetentionInDays`, `ALBSslPolicy` (pre-existing drift from earlier versions; template defaults were being used silently).

### Pre-deployment requirement (since v6)
The target VPC MUST have the following endpoints provisioned before deployment, otherwise the Lambda will hang on first invocation:
- **S3 Gateway VPC Endpoint** (`com.amazonaws.{region}.s3`) — free, required for S3 access
- **CloudWatch Logs Interface Endpoint** (`com.amazonaws.{region}.logs`) — required for log writes
- **X-Ray Interface Endpoint** (`com.amazonaws.{region}.xray`) — required (`TracingConfig: Active` is enabled on the Lambda)

### Upgrade path (v5.1 or v6 to v7)
- `VpcConfig` is an **updatable** Lambda property — no function replacement, rolling update.
- No downtime expected; brief overlap between VPC-less and VPC-attached versions during update.
- Lambda IAM role already has `ec2:CreateNetworkInterface/DeleteNetworkInterface/DescribeNetworkInterfaces` permissions (carried over from v5.1), so no IAM changes required.
- A new `LambdaSecurityGroup` resource will be created on upgrade.
- Project teams upgrading from v5.1 **MUST provide**: `VpcCidr1` and `S3PrefixListId` (previously optional) — otherwise v7 deployment fails parameter validation.
- Project teams upgrading from v6 can leave all new v7 S3 additional path parameters empty to keep existing ALB routing behavior.
- ENI cleanup on stack deletion can take 20–40 minutes — plan accordingly.

## Stack Notifications (introduced in v6)

v6 introduced optional CloudFormation stack event notifications via SNS on all 3 nested stacks (Lambda, API Gateway, ALB), and v7 carries the same behavior forward.

### How it works
- Set `EnableStackNotifications: yes` and provide `StackNotificationSNSTopicArn`.
- Nested stacks (`Lambdas3ReverseProxyStack`, `PrivateApiGatewayStack`, `ALBtoVPCEStack`) are configured with the SNS topic via the `NotificationARNs` property.
- The SNS topic is **not provisioned by this template** — project teams must create the topic separately and pass its ARN.

### Recommendation
- **Turn ON for NEW stack creation.** Notifications will apply to all newly created nested stacks.
- **Existing stacks**: see limitations below before flipping the toggle on.

### ⚠️ Limitations

**1. Existing nested stacks will NOT be updated automatically**
The `NotificationARNs` property on a nested stack resource is honored by CloudFormation only at **child stack creation time**. If you upgrade an existing v5.1 or v6 deployment to v7 and set `EnableStackNotifications=yes`, the parent stack will accept the change, but the already-created nested stacks will NOT pick up the new SNS topic.

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
The toggle defaults to `no`, so existing deployments upgrading to v7 are not forced to provide an SNS topic. Notifications can be added incrementally (see Workaround above).

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
| S3DownloadPath | Path pattern for S3 download route | "/Download/*" | No |
| S3AdditionalPathPattern1 | Optional additional S3 path rule, priority 11 | "/mobile/appartifact/*" | No |
| S3AdditionalPathPattern1HostHeaderRewriteRegex | Optional host-header rewrite regex for additional rule 1 | "^(.+)$" | No |
| S3AdditionalPathPattern1HostHeaderRewriteReplace | Optional host-header rewrite replacement for additional rule 1 | "s3.ap-southeast-1.amazonaws.com" | No |
| S3AdditionalPathPattern1UrlRewriteRegex | Optional URL rewrite regex for additional rule 1 | "^/mobile/appartifact/(.*)$" | No |
| S3AdditionalPathPattern1UrlRewriteReplace | Optional URL rewrite replacement for additional rule 1 | "/appartifact/$1" | No |
| S3AdditionalPathPattern2 | Optional additional S3 path rule, priority 12 | "/path2/*" | No |
| S3AdditionalPathPattern2HostHeaderRewriteRegex | Optional host-header rewrite regex for additional rule 2 | "^(.+)$" | No |
| S3AdditionalPathPattern2HostHeaderRewriteReplace | Optional host-header rewrite replacement for additional rule 2 | "s3.ap-southeast-1.amazonaws.com" | No |
| S3AdditionalPathPattern2UrlRewriteRegex | Optional URL rewrite regex for additional rule 2 | "^/path2/(.*)$" | No |
| S3AdditionalPathPattern2UrlRewriteReplace | Optional URL rewrite replacement for additional rule 2 | "/$1" | No |
| BackendAdditionalPathPattern1 | Optional additional backend path rule, priority 13 | "/path3/*" | No |
| BackendAdditionalPathPattern1HostHeaderRewriteRegex | Optional host-header rewrite regex for backend additional rule 1 | "^(.+)$" | No |
| BackendAdditionalPathPattern1HostHeaderRewriteReplace | Optional host-header rewrite replacement for backend additional rule 1 | "api.example.com" | No |
| BackendAdditionalPathPattern1UrlRewriteRegex | Optional URL rewrite regex for backend additional rule 1 | "^/path3/(.*)$" | No |
| BackendAdditionalPathPattern1UrlRewriteReplace | Optional URL rewrite replacement for backend additional rule 1 | "/$1" | No |

*Required if EnableS3Upload is set to "true"

For each additional path rule, host-header rewrite regex/replacement must be provided as a pair. URL rewrite regex/replacement must also be provided as a pair. If only the path pattern is provided, the rule forwards to its target group without transforms.

### Network Security Parameters
Additional network security parameters are available in the YAML parameter files for fine-grained control:

| Parameter | Description | Required |
|-----------|-------------|----------|
| VpcCidr1 | Primary VPC CIDR block for security group rules (ALB + Lambda SG egress to Interface Endpoints) | **Yes** (since v6) |
| VpcCidr2 | Secondary VPC CIDR block — optional, adds conditional egress rule on Lambda SG when set | No |
| VpcCidr3 | Tertiary VPC CIDR block — optional, adds conditional egress rule on Lambda SG when set | No |
| VpcCidr4 | Quaternary VPC CIDR block — optional, adds conditional egress rule on Lambda SG when set | No |
| VpcCidr5 | Quinary VPC CIDR block — optional, adds conditional egress rule on Lambda SG when set | No |
| S3PrefixListId | S3 Gateway Endpoint prefix list ID — required by Lambda SG egress to S3 | **Yes** (since v6) |

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

