# Release Notes: FrontendSPA-Intranet Infrastructure

## Version History

### General Updates
- **IaC Version Tag**:
  - Updated from `FrontendSPA-Intranet-v1` to `FrontendSPA-Intranet-v7.1`.

### Core Infrastructure (`cf-intranet-frontend-spa-main.yaml`)
- **v1.1 Updates**:
  - Added `PrefixListIdInternet` parameter to control inbound traffic on internet-facing ALB via managed prefix list.
  - Added explicit **security group egress rules** restricting outbound to specific VPC CIDRs and optional S3/HCC endpoints.
  - Added `ALBSslPolicy` parameter for configurable TLS security policy (TLS 1.2+ only).
  - Enabled ALB deletion protection.
  - Fixed Lambda `LambdaRuntime` and `LambdaHandler` parameters not being referenced by Lambda resource.

- **v2 Updates**:
  - Added support for **custom domain names** with SSL certificates for API Gateway.
  - Enhanced **Lambda Reverse Proxy**:
    - Updated runtime to `nodejs20.x`.
    - Configurable log retention via `LambdaLogRetentionInDays`.
  - Improved **security group rules** for ALB and Lambda.

- **v3 Updates**:
  - Introduced **S3 VPC Endpoint Integration**:
    - Configurable via `S3EndpointIP1`, `S3EndpointIP2`, and `S3EndpointIP3`.
    - Added `EnableS3Upload` parameter for optional file upload support.
  - Enhanced **API Gateway**:
    - Added support for additional SSL certificates.
    - Improved VPC endpoint integration for private API Gateway.
  - Enhanced **cache configuration** for ALB.

- **v4 Updates**:
  - Added support for **S3 download paths** via `S3DownloadPath` parameter.
  - Enhanced **VPC CIDR configuration**:
    - Added `VpcCidr1`, `VpcCidr2`, and `VpcCidr3` parameters.
  - Improved **security policies**:
    - Enforced TLS v1.2 for all connections.
    - Added `HCCVpceCidr` for hybrid connectivity scenarios.

- **v5 Updates**:
  - Extended **VPC CIDR support**:
    - Added `VpcCidr4` and `VpcCidr5` parameters.
    - Now supports **up to 5 VPC CIDR ranges** (previously 3).
  - Enhanced **multi-VPC connectivity**:
    - Better support for complex network topologies with multiple VPC peerings.
    - Improved support for hybrid cloud and cross-region VPC connectivity.
  - Enhanced **security group flexibility**:
    - Expanded security group rules to accommodate additional VPC CIDR ranges.
    - Better support for enterprise multi-VPC architectures.

- **v5.1 Updates**:
  - Added `PrefixListIdInternet` parameter to control inbound traffic on internet-facing ALB via managed prefix list.
  - Addresses CxOne security finding on public ALB `0.0.0.0/0` ingress rule.

- **v6 Updates (post-release patch — ELB.4)**:
  - Added **`routing.http.drop_invalid_header_fields.enabled: "true"`** to `ALB.LoadBalancerAttributes` in `cf-alb-vpce.yaml` — remediates AWS Security Hub control **ELB.4** ("Application Load Balancer should be configured to drop invalid HTTP headers"). AWS defaults this attribute to `false`, so prior v6 deployments fail ELB.4 until they re-deploy with this patch.
  - **Tag-only attribute change** — `LoadBalancerAttributes` is `Update requires: No interruption`. No ALB replacement, no ARN/DNS change, no listener/target-group impact, no downtime. CloudFormation issues a single `ModifyLoadBalancerAttributes` API call that applies live.
  - **Behavioral note** — after the patch, the ALB drops requests with malformed HTTP headers (RFC 7230 violations). Compliant clients are unaffected. Legacy SOAP/EDI integrations or homegrown HTTP clients that send non-RFC-compliant headers may see HTTP 400s — verify against ALB access logs / `RejectedConnectionCount` in non-prod first.

- **v6 Updates (post-release patch — APIGateway.2)**:
  - Added optional **`ApiGatewayClientCertificateId`** parameter to `cf-intranet-frontend-spa-main.yaml` and pass-through to `cf-private-apigw.yaml`.
  - When provided, `cf-private-apigw.yaml` attaches the project-managed API Gateway client certificate to the REST API stage via `ClientCertificateId`, remediating AWS Security Hub control **APIGateway.2** ("API Gateway REST API stages should be configured to use SSL certificates for backend authentication").
  - Default is `""`; when empty, CloudFormation passes `ClientCertificateId: ""` so a stack update can clear/unset any certificate previously attached to the stage.
  - Certificate creation and rotation remain project-owned outside CloudFormation, typically from the API Gateway console.

- **v7 Updates**:
  - Duplicated the clean v6 baseline into `v7` so v6 remains unchanged.
  - Added two optional S3 ALB listener rules via `S3AdditionalPathPattern1` and `S3AdditionalPathPattern2`.
  - Added one optional backend ALB listener rule via `BackendAdditionalPathPattern1`.
  - S3 rules use priorities `11` and `12`, forward to the existing `S3TargetGroup`, and require `EnableS3Upload=true`.
  - Backend rule uses priority `13`, forwards to the existing `ALBTG`, and does not require `EnableS3Upload=true`.
  - Each additional rule supports optional host-header rewrite and URL rewrite transforms. Regex/replacement values must be provided as pairs.
  - Defaults are empty, so existing behavior is preserved unless project teams opt in.

- **v6 Updates**:
  - **Lambda VPC Attachment (Mandatory)**: `LambdaS3ReverseProxy` is now VPC-attached via `VpcConfig` to enhance network security posture.
  - **Lambda Security Group created in-template** (`LambdaSecurityGroup` resource) with least-privilege egress:
    - HTTPS (443) to S3 Gateway Endpoint (via `S3PrefixListId`) only
    - HTTPS (443) to `VpcCidr1` only (for CloudWatch Logs / X-Ray Interface Endpoint ENIs)
    - **Conditional** HTTPS (443) egress per non-empty `VpcCidr2`/`VpcCidr3`/`VpcCidr4`/`VpcCidr5` (via separate `AWS::EC2::SecurityGroupEgress` resources) — for shared-services VPC or multi-VPC peering patterns.
    - No `0.0.0.0/0` egress.
  - **Typed AWS parameter types**: `LambdaSubnetIds: List<AWS::EC2::Subnet::Id>` and `VpcId: AWS::EC2::VPC::Id` for deploy-time validation + Console dropdowns.
  - New mandatory parameters on `cf-lambda-s3reverseproxy.yaml`: `VpcId`, `LambdaSubnetIds`, `VpcCidr1`, `S3PrefixListId`.
  - New optional parameters on `cf-lambda-s3reverseproxy.yaml`: `VpcCidr2`, `VpcCidr3`, `VpcCidr4`, `VpcCidr5` (default `""`).
  - `VpcCidr1` and `S3PrefixListId` on `cf-intranet-frontend-spa-main.yaml` are now mandatory (previously optional). All 5 CIDRs (`VpcCidr1`–`VpcCidr5`) and `S3PrefixListId` are passed through to the Lambda nested stack.
  - **Optional CloudFormation Stack Notifications**: New toggle `EnableStackNotifications` (yes/no, default: no) and `StackNotificationSNSTopicArn`. When enabled, nested stack events (Lambda, API Gateway, ALB) are published to the provided SNS topic.
    - Recommended for NEW stack creation only. Existing nested stacks (from v5.1) will NOT pick up notifications via stack update — `NotificationARNs` is a create-time-only property for nested stacks. Project teams can apply notifications to existing nested stacks manually via CloudFormation Console (Update → Notification options) or via CLI (`update-stack --use-previous-template --notification-arns <arn>`).
    - Parent stack notifications: pass `--notification-arns <sns-arn>` on `aws cloudformation create-stack` / `update-stack`, or set "Notification options" in the Console (AWS design constraint — template cannot self-configure its own notification target).
  - **Optional API Gateway Access Logging**: Added `AccessLogFormat` + `LogRetentionInDays` parameters on `cf-private-apigw.yaml`, with corresponding pass-through params `ApiGwAccessLogFormat` + `ApiGwLogRetentionInDays` on `cf-intranet-frontend-spa-main.yaml`. When `ApiGwAccessLogFormat` is non-empty, a CloudWatch log group `/aws/apigateway/${APIName}-access-logs` is created and wired to the stage via `AccessLogSetting`. Addresses Checkmarx finding on missing stage access log settings. Follows the same pattern as `AppSubsystem/APIGateway/PrivateApi/v3`.
  - **Optional API Gateway Response Compression**: Added `EnableCompression` (yes/no, default `no`) + `MinimumCompressionSize` (default `10240`) parameters on `cf-private-apigw.yaml`, with corresponding pass-through params `ApiGwEnableCompression` + `ApiGwMinimumCompressionSize` on `cf-intranet-frontend-spa-main.yaml`. When enabled, `MinimumCompressionSize` is applied to the `PrivateApi` — responses ≥10 KB are gzipped. When `no`, the property is omitted from the RestApi (matches original v6 behavior). Addresses Checkmarx finding "API Gateway with invalid compression". Default `no` — project teams should audit client gzip handling (esp. .NET `HttpClient` `AutomaticDecompression`) before enabling. Application layer already supports compression; gateway compression is defense-in-depth.
  - **Parameter file hygiene**: env YAML file `parameters-intranet-frontend-spa-main.yaml` aligned with template — added missing keys `LambdaRuntime`, `LambdaHandler`, `LambdaLogRetentionInDays`, `ALBSslPolicy` (pre-existing drift from earlier versions; template defaults were being used silently).
  - IaC Version tag bumped to `AppSubsystem-SPAIntranet-v6`.

- **Version 7.1** (Configurable and support SecurityPolicy from harcoded TLS_1_2)
  - Implemented configurable Security Policy on API Gateway and customDomain
  - Support TLS1.3 (SecurityPolicy_*) by implemented new logical ID `ApiGatewayDomainNameEnhanced`, only apply for new project, required seek SEET Infra Team advise for existing project migration from TLS_1_2 to `SecurityPolicy_*`
  - ⛔ **No direct migration from `TLS_1_2` to `SecurityPolicy_*`**: a v7 stack with a custom domain cannot be upgraded to v7.1 and switched from `TLS_1_2` to a `SecurityPolicy_*` value in the same or a later deployment — the update fails with "domain name already exists" and rolls back. Do not delete the custom domain or the stack to work around this; contact the **SEET Infra team** for assistance.

### Security Enhancements
- **v1.1 Updates**:
  - Replaced public ALB `0.0.0.0/0` ingress with managed prefix list (`PrefixListIdInternet`).
  - Added explicit security group egress rules (VPC CIDRs, S3, HCC endpoints).
  - Configurable TLS security policy via `ALBSslPolicy` parameter.

- **v2 Updates**:
  - Enforced HTTPS-only access for all S3 buckets.
  - Updated ALB Listener to use `ELBSecurityPolicy-TLS13-1-2-2021-06`.

- **v3 Updates**:
  - Added AWS Prefix List support for inbound traffic (`PrefixListIdIntranet`).

- **v4 Updates**:
  - Enhanced security group rules for S3 and ALB.
  - Added conditional access for S3 download paths.

- **v5 Updates**:
  - Enhanced security group rules to support up to 5 VPC CIDR ranges.
  - Improved network security for multi-VPC architectures.

- **v5.1 Updates**:
  - Replaced public ALB `0.0.0.0/0` ingress with managed prefix list (`PrefixListIdInternet`).
  - Addresses CxOne security finding.

- **v6 Updates**:
  - Lambda `S3ReverseProxy` moved into a private VPC via `VpcConfig` (mandatory `VpcId` + `LambdaSubnetIds`).
  - Security group created in-template with **least-privilege egress** — HTTPS (443) only to S3 prefix list and VPC CIDR(s). No `0.0.0.0/0` egress.
  - Lambda no longer has direct public internet egress — relies on VPC endpoints for S3/CloudWatch Logs/X-Ray.
  - Pre-deployment requirement: VPC must have S3 Gateway Endpoint, CloudWatch Logs Interface Endpoint, and X-Ray Interface Endpoint.
  - Optional API Gateway stage client certificate support via `ApiGatewayClientCertificateId` for APIGateway.2 backend authentication remediation. Empty default clears/unsets any certificate previously attached to the stage.

- **v7.1 Updates**:
  - `api gateway` + `customdomain` to support SecurityPolicy_* (TLS 1.3).

### Deployment Flow Updates
- **v2 Updates**:
  - Introduced a deployment order:
    1. Deploy S3 bucket policies.
    2. Deploy Lambda Reverse Proxy.
    3. Deploy API Gateway and ALB.

- **v3 Updates**:
  - Added support for S3 upload functionality with path-based routing.

- **v4 Updates**:
  - Enhanced deployment documentation for S3 download paths and VPC CIDR configurations.

- **v7 Updates**:
  - Additional S3 path listener rules are optional. Project teams should provide only the required path slots and leave unused transform fields empty.

### Documentation Updates
- **v2 Updates**:
  - Added detailed descriptions for new parameters (`CustomDomainName`, `LambdaLogRetentionInDays`).
  - Updated troubleshooting guide for common issues with API Gateway and ALB configurations.

- **v3 Updates**:
  - Enhanced deployment guide with examples for S3 VPC endpoint integration.

- **v4 Updates**:
  - Added examples for configuring S3 download paths and hybrid connectivity.

- **v5 Updates**:
  - Added documentation for VpcCidr4 and VpcCidr5 parameters.
  - Enhanced README with Network Security Parameters section.

## Summary of Key Changes

### Legacy Versions (v1 – v4)
| Feature/Component         | v1              | v1.1            | v2              | v3              | v4              |
|---------------------------|-----------------|-----------------|-----------------|-----------------|-----------------|
| IaC Version               | v1              | v1.1            | v2              | v3              | v4              |
| Lambda Runtime            | nodejs14.x      | nodejs20.x      | nodejs20.x      | nodejs20.x      | nodejs20.x      |
| Lambda Deployment         | No VPC          | No VPC          | No VPC          | No VPC          | No VPC          |
| S3 VPC Endpoint           | Not supported   | Not supported   | Not supported   | Supported       | Supported       |
| S3 Upload Path            | Not supported   | Not supported   | Not supported   | Supported       | Supported       |
| S3 Download Path          | Not supported   | Not supported   | Not supported   | Not supported   | Supported       |
| VPC CIDR Configuration    | Basic           | Enhanced egress | Basic           | Basic           | Up to 3         |
| Public ALB Ingress        | 0.0.0.0/0       | Prefix List     | 0.0.0.0/0       | 0.0.0.0/0       | 0.0.0.0/0       |
| Private ALB Ingress       | Basic           | Prefix List     | Basic           | Prefix List     | Prefix List     |
| Stack Notifications       | Not supported   | Not supported   | Not supported   | Not supported   | Not supported   |

### Current Versions (v5 – v7)
| Feature/Component         | v5                              | v5.1                            | v6                                                                       | v7                                                                       |
|---------------------------|---------------------------------|---------------------------------|--------------------------------------------------------------------------|--------------------------------------------------------------------------|
| IaC Version               | v5                              | v5.1                            | v6                                                                       | **v7**                                                                   |
| Lambda Runtime            | nodejs20.x                      | nodejs20.x                      | nodejs20.x                                                               | nodejs20.x                                                               |
| Lambda Deployment         | No VPC                          | No VPC                          | **VPC-attached (mandatory)** — VpcConfig with in-template SG             | VPC-attached (same as v6)                                                 |
| Lambda Security Group     | N/A                             | N/A                             | **In-template `LambdaSecurityGroup`** with least-privilege egress        | Same as v6                                                               |
| Lambda SG Egress          | N/A                             | N/A                             | **HTTPS → S3 prefix list + VpcCidr1 (mandatory); VpcCidr2-5 (optional)** | Same as v6                                                               |
| S3 VPC Endpoint           | Supported                       | Supported                       | Supported                                                                | Supported                                                                |
| S3 Upload Path            | Supported                       | Supported                       | Supported                                                                | Supported                                                                |
| S3 Download Path          | Supported                       | Supported                       | Supported                                                                | Supported                                                                |
| Additional Path Rules     | Not supported                   | Not supported                   | Not supported                                                            | **2 optional S3 rules + 1 optional backend rule with transforms**         |
| VPC CIDR Configuration    | **Up to 5 (VpcCidr4/5 added)**  | Up to 5                         | Up to 5 (VpcCidr1 + S3PrefixListId now MANDATORY)                        | Same as v6                                                               |
| Public ALB Ingress        | 0.0.0.0/0                       | **Prefix List**                 | Prefix List                                                              | Prefix List                                                              |
| Private ALB Ingress       | Prefix List                     | Prefix List                     | Prefix List                                                              | Prefix List                                                              |
| Typed Parameters          | Mostly String                   | Mostly String                   | **`List<AWS::EC2::Subnet::Id>` + `AWS::EC2::VPC::Id`** for Lambda VPC    | Same as v6                                                               |
| ALB TLS Policy            | Fixed                           | **Configurable via `ALBSslPolicy`** | Configurable                                                         | Configurable                                                             |
| Stack Notifications       | Not supported                   | Not supported                   | **Optional toggle — SNS notifications on nested stacks**                 | Same as v6                                                               |
| API Gateway Client Certificate | Not supported              | Not supported                   | **Optional `ApiGatewayClientCertificateId` for REST API stage backend authentication** | Same as v6                                                      |

For detailed changes, refer to the respective `README.md` files in each version directory.
