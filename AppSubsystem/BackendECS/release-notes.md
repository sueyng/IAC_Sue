# Release Notes: BackendECS Infrastructure

## Version History

### General Updates
- **IaC Version Tag**:
  - Updated from `BackendECS-v1` to `BackendECS-v2`, `BackendECS-v3`, `BackendECS-v4` , `BackendECS-v5`, `BackendECS-v6`, `BackendECS-v7`, `BackendECS-v8`, `BackendECS-v9` across all templates.

### Core Infrastructure (CloudFormation Templates)
- **v2 Updates**:
  - Introduced separation of deployment pipelines:
    - **Infrastructure pipeline** for ALB, ECS Cluster, and ADOT Collector.
    - **Service pipeline** for independent ECS service deployments.
  - Added **SNS topics** for audit logging and related IAM permissions.
  - Enabled support for custom **ECR repository** for ADOT collector image.
  - Improved use of **SSM parameters** for referencing shared resources.

- **v3 Updates**:
  - Added optional **prefix list support** for ALB security groups (network security enhancement).
  - Further modularization and parameterization for easier maintenance.
  - Improved documentation and best practices for service deployment.
  - Continued comprehensive IAM permissions and SSM parameter usage.

- **v4 Updates**:
  - Aligned templates with latest AWS best practices for ECS, ALB, and observability.
  - Maintained and refined **ADOT integration** with OTLP protocol support (gRPC/HTTP).
  - Improved clarity and structure in templates and documentation.
  - Further refinements to security group and IAM policy management.

- **v5 Updates**:
  - Added **ElastiCache dedicated subnets** support for enhanced network security
  - Introduced **environment-based database ports** (Production: 53341, Non-production: 53331)
  - Enhanced **resource tagging** with standardized tags including version tracking
  - Improved **conditional security group rules** for ElastiCache access patterns
  - Comprehensive **backward compatibility** maintained with existing deployments
  - Simplified network configuration (removed AdditionalAppPrefixList parameter)

- **v6 Updates**:
  - Added **VpcCidr4 and VpcCidr5 parameters** for extended VPC CIDR support
  - Enhanced **multi-VPC connectivity** - now supports up to 5 VPC CIDR ranges (previously 3)
  - Improved **security group flexibility** for complex network topologies
  - Better support for **multi-VPC peering**, hybrid cloud, and cross-region architectures
  - All new parameters are optional with backward compatibility

- **v7 Updates**:
  - Added **BHasHCCSubnetCidrBCSAZ1,HasHCCSubnetCidrBCSAZ2 and BCSProxyPort parameters** for ECS service to connect BCS Proxy
  - Enhanced **connectivity to BCS Proxy** - now ECS service can connect to BCS Proxy
  - Added **IAM Policy for AWS Batch Job**
  - Broadened **Secrets Manager policy scope** from `${AppShortName}-${EnvName}-*` to `${AppShortName}*` for shared secrets across non-prod environments
  - Improved **security group flexibility** for complex network topologies
  - Better support for **multi-VPC peering**, hybrid cloud, and cross-region architectures
  - All new parameters are optional with backward compatibility

- **v8 Updates**:
  - Scoped **S3 permissions** in ECSTaskExtendedServicesPolicy from `arn:aws:s3:::*` to `arn:aws:s3:::${AppShortName}*` — limits S3 access to application-owned buckets only
  - Follows same least-privilege pattern applied to Secrets Manager scope in v7
  - Added **optional CloudFormation stack notifications** via new toggle `EnableStackNotifications` (yes/no, default: no) and `StackNotificationSNSTopicArn`. When enabled, nested stack events (ALB, ECS Cluster, ADOT) are published to the provided SNS topic. Addresses Checkmarx finding on disabled stack notifications.
  - **Recommended for NEW stack creation only.** Existing nested stacks (from v7) will NOT pick up notifications via stack update — `NotificationARNs` is a create-time-only property for nested stacks. Project teams can apply notifications to existing nested stacks manually via CloudFormation Console (Update → Notification options) or via CLI (`update-stack --use-previous-template --notification-arns <arn>`).
  - **Parent stack notifications**: CloudFormation does not let a stack self-configure its own notification target via template (AWS design constraint). Pass `--notification-arns <sns-arn>` on `aws cloudformation create-stack` / `update-stack`, or set "Notification options" in the Console.
  - Added **optional RDS Proxy egress** on ECS service security group via new toggle `UseRDSProxy` (yes/no, default: no) and `RDSProxyPort` (default: 1433). When enabled, opens egress on the proxy listener port to existing DB subnet CIDRs (`VPCSubnetCidrDBAZ1/2/3`) — RDS Proxy ENIs are deployed in the DB subnets so no new CIDR parameters are needed.

- **v9 Updates (post-release patch — ELB.4)**:
  - Added **`routing.http.drop_invalid_header_fields.enabled: "true"`** to `LoadBalancerAttributes` on **both ALBs** — remediates AWS Security Hub control **ELB.4** ("Application Load Balancer should be configured to drop invalid HTTP headers"). AWS defaults this attribute to `false`, so prior v9 deployments fail ELB.4 on both load balancers until they re-deploy with this patch.
    - `PrivateALB` in `cf-ecs-alb.yaml` (main application ALB)
    - `ADOTInternalALB` in `cf-ecs-adot-service.yaml` (ADOT collector ALB)
  - **Tag-only attribute change** — `LoadBalancerAttributes` is `Update requires: No interruption`. No ALB replacement, no ARN/DNS change, no listener/target-group impact, no downtime. CloudFormation issues a single `ModifyLoadBalancerAttributes` API call that applies live.
  - **Behavioral note** — after the patch, the ALB drops requests with malformed HTTP headers (RFC 7230 violations). Compliant clients are unaffected. Legacy SOAP/EDI integrations or homegrown HTTP clients that send non-RFC-compliant headers may see HTTP 400s — verify against ALB access logs / `RejectedConnectionCount` in non-prod first.

- **v9 Updates (post-release patch — S3 scope extension)**:
  - New optional **`AdditionalS3BucketArns`** parameter (default `""`) on `cf-ecs-cluster.yaml`, wired through `cf-backend-ecs-main.yaml`. Lets project teams grant ECS task S3 access to buckets not following `${AppShortName}*` (e.g. domain-named like `*.hcc.sg`) without unwinding the v8 scope tightening. `AllowedPattern` rejects bare `arn:aws:s3:::*` at deploy time. Stack update in-place — IAM policy only, no resource replacement.

- **v9 Updates (post-release patch — RDS Proxy IAM authentication)**:
  - New optional **`RDSProxyIAMDbUserArns`** parameter (default `""`) on `cf-ecs-cluster.yaml`, wired through `cf-backend-ecs-main.yaml`. When populated, ECS tasks receive `rds-db:connect` only for the supplied RDS Proxy `dbuser` ARN(s). Supports multiple comma-separated users. Empty default grants no `rds-db:connect` permission, so existing deployments are unchanged. Stack update in-place — IAM policy only, no resource replacement.

- **v9 Updates**:
  - Added **non-root container user** (ECS.20 Security Hub remediation) via new parameter `ContainerUser` (default `"1000"`). Applied via `User: <UID>` on `ContainerDefinitions` and gated by new `IsLinuxOS` condition so it only takes effect for Linux task definitions (Windows containers are unaffected).
  - Added **optional external-services egress** on ECS service security group via new parameter `ExternalServicesPrefixListId` (default `""`). When set, opens HTTPS (443) egress to a single customer-managed prefix list covering all external services the application calls (e.g. CAG, ESB).
  - **One prefix list, not per-service** — each prefix list reserves SG rule capacity equal to its `MaxEntries` and counts against the (default 60) rules-per-SG quota; using one list keeps SG rule budget free for future additions and centralises maintenance when external IPs change.

### Deployment Flow Updates
- **v2 Updates**:
  - Introduced a deployment order:
    1. Deploy core infrastructure (ALB, ECS Cluster, ADOT Collector).
    2. Deploy ECS services independently using the service pipeline.

- **v3 & v4 Updates**:
  - Enhanced deployment documentation for modular and secure deployments.
  - Added guidance for prefix list and OTLP protocol configuration.

- **v5 Updates**:
  - Introduced deployment order with ElastiCache subnet configuration options.
  - Enhanced guidance for environment-specific database port configurations.
  - Added comprehensive resource tagging strategy documentation.
  - Simplified network configuration documentation.

- **v6 Updates**:
  - Enhanced guidance for multi-VPC CIDR configurations (VpcCidr4 and VpcCidr5).
  - Updated security considerations for complex network topologies.
  - Improved documentation for enterprise multi-VPC architectures.

- **v7 Updates**:
  - Enhanced connectivity to BCS Proxy.
  - Updated security considerations for complex network topologies.
  - Improved documentation for enterprise multi-VPC architectures.

- **v8 Updates**:
  - Added optional pre-deployment step: provision SNS topic separately if `EnableStackNotifications=yes` is desired.
  - For new stack creation: set `EnableStackNotifications=yes` + `StackNotificationSNSTopicArn=<arn>`, and pass `--notification-arns <arn>` on the parent `create-stack` (or use Console "Notification options").
  - For v7→v8 upgrade on existing stacks: notifications must be applied manually to each existing nested stack via Console (Update → Notification options) or CLI (`update-stack --use-previous-template --notification-arns <arn>`).

- **v9 Updates**:
  - Optional pre-deployment step: project teams that need external-service connectivity must provision (or reuse) a customer-managed prefix list populated with the required external service IPs/CIDRs and pass its ID via `ExternalServicesPrefixListId`. Empty default leaves egress unchanged.
  - No new infrastructure ordering required — `ContainerUser` defaults to `"1000"` and applies automatically on first deploy or next service update (Linux containers only). Project teams using a custom container image that does not include UID 1000 can override `ContainerUser` to a UID that exists in their image.

### Documentation Updates
- **v2 Updates**:
  - Added detailed descriptions for infrastructure and service pipeline separation.
  - Updated troubleshooting guide for SSM and ECR integration.

- **v3 & v4 Updates**:
  - Enhanced deployment guide with security and observability best practices.
  - Added examples for configuring prefix lists and ADOT collector parameters.

- **v5 Updates**:
  - Comprehensive documentation updates for ElastiCache subnet configurations.
  - Enhanced troubleshooting guide with environment-specific port configurations.
  - Added resource tagging and naming convention documentation.

- **v6 Updates**:
  - Added VpcCidr4 and VpcCidr5 parameter documentation across all configuration files.
  - Updated README.md with extended VPC CIDR support details.
  - Enhanced security considerations section for multi-VPC architectures.
  - Updated resource-naming-table.md to v6 with new parameter details.

- **v7 Updates**:
  - Added BCSProxyCidr and BCSProxyPort parameters to ECS Service.

- **v8 Updates**:
  - Added new "Stack Notifications (new in v8)" section in `v8/README.md` covering toggle usage, create-time-only constraint, manual workaround for existing nested stacks, and parent-stack `--notification-arns` requirement.
  - Updated Infrastructure Stack Parameters table with `EnableStackNotifications` and `StackNotificationSNSTopicArn`.
  - Renamed release-notes header to "Version History" and split "Summary of Key Changes" into Legacy (v1–v4) and Current (v5–v8) tables for scalability.
  - Added migration notes for v7→v8 covering S3 scope tightening and stack notification limitations.

- **v9 Updates**:
  - Added `ContainerUser` and `ExternalServicesPrefixListId` rows to the ECS Service Stack Parameters table in `v9/README.md`.
  - Added a new bullet under "ECS Service Security Group Egress" describing the external-services HTTPS (443) prefix-list rule.
  - YAML parameter file (`v9/env/parameters-ecs-service.yaml`) reference appendix expanded with the rationale for using a single prefix list (SG rule quota) and where to find / create the customer-managed list.

## Summary of Key Changes

### Legacy Versions (v1 – v4)
| Feature/Component         | v1              | v2                         | v3                         | v4                                          |
|---------------------------|-----------------|----------------------------|----------------------------|---------------------------------------------|
| IaC Version               | BackendECS-v1   | BackendECS-v2              | BackendECS-v3              | BackendECS-v4                               |
| Deployment Pipeline       | Monolithic      | Modular (infra/service)    | Modular (infra/service)    | Modular (infra/service)                     |
| Audit Logging             | Not supported   | SNS topics supported       | SNS topics supported       | SNS topics supported                        |
| ADOT Collector            | Optional, basic | Optional, ECR support      | Optional, ECR support      | Optional, OTLP protocol, debug logging mode |
| ALB Security              | Basic           | Basic                      | Prefix list support        | Prefix list support                         |
| ElastiCache Configuration | VPC subnets only| VPC subnets only           | VPC subnets only           | VPC subnets only                            |
| Database Ports            | Static          | Static                     | Static                     | Static                                      |
| VPC CIDR Support          | Up to 3 CIDRs   | Up to 3 CIDRs              | Up to 3 CIDRs              | Up to 3 CIDRs                               |
| Resource Tagging          | Basic           | Basic                      | Basic                      | Basic                                       |
| Documentation             | Basic           | Improved, pipeline split   | Enhanced, security focus   | Best practices, observability               |
| SSM Parameter Usage       | Basic           | Improved                   | Comprehensive              | Comprehensive                               |

### Current Versions (v5 – v9)
| Feature/Component         | v5                                    | v6                                    | v7                                             | v8                                                                 | v9                                                                 |
|---------------------------|---------------------------------------|---------------------------------------|------------------------------------------------|--------------------------------------------------------------------|--------------------------------------------------------------------|
| IaC Version               | BackendECS-v5                         | BackendECS-v6                         | BackendECS-v7                                  | BackendECS-v8                                                      | BackendECS-v9                                                      |
| Deployment Pipeline       | Modular (infra/service)               | Modular (infra/service)               | Modular (infra/service)                        | Modular (infra/service)                                            | Modular (infra/service)                                            |
| Audit Logging             | SNS topics supported                  | SNS topics supported                  | SNS topics supported                           | SNS topics supported                                               | SNS topics supported                                               |
| ADOT Collector            | Optional, OTLP, debug logging         | Optional, OTLP, debug logging         | Optional, OTLP, debug logging                  | Optional, OTLP, debug logging                                      | Optional, OTLP, debug logging                                      |
| ALB Security              | Prefix list support                   | Prefix list support                   | Prefix list support                            | Prefix list support                                                | Prefix list support                                                |
| ElastiCache Configuration | VPC + dedicated subnets               | VPC + dedicated subnets               | VPC + dedicated subnets                        | VPC + dedicated subnets                                            | VPC + dedicated subnets                                            |
| Database Ports            | Environment-based (53341/53331)       | Environment-based (53341/53331)       | Environment-based (53341/53331)                | Environment-based (53341/53331)                                    | Environment-based (53341/53331)                                    |
| VPC CIDR Support          | Up to 3 CIDRs                         | **Up to 5 CIDRs (VpcCidr4/5)**        | Up to 5 CIDRs                                  | Up to 5 CIDRs                                                      | Up to 5 CIDRs                                                      |
| Resource Tagging          | Comprehensive with version tracking   | Comprehensive with version tracking   | Comprehensive with version tracking            | Comprehensive with version tracking                                | Comprehensive with version tracking                                |
| Additional Connectivity   | Not supported (simplified)            | Not supported (simplified)            | **BCS Proxy IP and Port**                      | BCS Proxy IP and Port + **optional RDS Proxy egress (`UseRDSProxy`)** | BCS Proxy IP and Port + RDS Proxy egress + **external services prefix list (`ExternalServicesPrefixListId`)** |
| Secrets Manager Scope     | `${AppShortName}-${EnvName}-*`        | `${AppShortName}-${EnvName}-*`        | **Broadened to `${AppShortName}*`**            | `${AppShortName}*` (+ `PutSecretValue`)                            | `${AppShortName}*` (+ `PutSecretValue`)                            |
| S3 Permission Scope       | `*`                                   | `*`                                   | `*`                                            | **Scoped to `${AppShortName}*`**                                   | Scoped to `${AppShortName}*` (+ optional `AdditionalS3BucketArns` for non-conforming buckets) |
| Stack Notifications       | Not supported                         | Not supported                         | Not supported                                  | **Optional SNS notifications on nested stacks (toggle, recommended for new stacks)** | Optional SNS notifications on nested stacks                        |
| Container User            | Root (default)                        | Root (default)                        | Root (default)                                 | Root (default)                                                     | **Non-root by default (UID 1000) — ECS.20 remediation, configurable via `ContainerUser`** |
| Documentation             | Comprehensive, ElastiCache configs    | Enhanced, multi-VPC architectures     | BCS Proxy connectivity                         | S3 scope + stack notifications                                     | Container user + external services prefix list                     |
| SSM Parameter Usage       | Comprehensive                         | Comprehensive                         | Comprehensive                                  | Comprehensive                                                      | Comprehensive                                                      |

## Migration Notes

### From v8 to v9
- **Backward Compatible**: No breaking changes — all v8 parameters work unchanged in v9.
- **Container User (ECS.20 remediation)**: New parameter `ContainerUser` defaults to `"1000"`. On the next service stack update, Linux task definitions will run as UID `1000` instead of root. **Verify your container image includes UID 1000** before updating production — most public base images (Amazon Linux, Debian, Ubuntu) include it; custom or scratch-based images may not. Override `ContainerUser` to a UID/GID present in your image, or set it to `"0"` to retain root behavior temporarily during migration.
- **Linux-only enforcement**: The `User:` field is gated by the new `IsLinuxOS` condition — Windows containers are unaffected.
- **External Services Prefix List** (`ExternalServicesPrefixListId`, default `""`): Existing v8 service stacks upgrade to v9 with no behavior change. Set this when the application calls outbound to external services (CAG, ESB, etc.) — pass the customer-managed prefix list ID and a single port-443 egress rule is added to the ECS task security group.
- **One prefix list, not per-service**: The egress rule consumes SG rule capacity proportional to the prefix list's `MaxEntries`. Project teams should populate one customer-managed list with all external service IPs rather than provisioning separate lists per service, to conserve the (default 60) rules-per-SG quota.
- **Deployment order**: No new prerequisite stacks. If using `ExternalServicesPrefixListId`, the customer-managed prefix list must exist in the same region/account before deploying the service stack.
- **IaCVersion tag bump** v8 → v9 across all four templates. Tag *value* change only — key `IaCVersion` unchanged — so the stack updates in-place via UpdateTags with no resource replacement and no downtime. If any external automation, dashboards, or cost-allocation queries filter on the literal v8 tag value, update them to `AppSubsystem-BackendECS-v9`.
- **S3 scope extension (post-release patch)**: New optional `AdditionalS3BucketArns` (default `""`). Set when the app uses buckets not following `${AppShortName}*` (e.g. domain-named like `*.hcc.sg`). Bare `arn:aws:s3:::*` rejected at deploy time. No behavior change if unset.

### From v7 to v8
- **Backward Compatible**: No breaking changes — all v7 parameters work unchanged in v8.
- **S3 Permission Scope Change**: ECS task S3 access is now restricted to `arn:aws:s3:::${AppShortName}*`. Any application reading/writing S3 buckets that do **not** start with `${AppShortName}` will need either (a) bucket migration to follow the convention, (b) an additional inline policy attached via the service template, or (c) **the v9 post-release patch** — populate the new `AdditionalS3BucketArns` parameter with the extra bucket ARNs (recommended; supports wildcards in prefix/suffix/middle). Validate with project teams before cutover.
- **Optional Stack Notifications** (`EnableStackNotifications`, default `no`): Existing v7 stacks can upgrade to v8 without providing an SNS topic.
- **Stack Notification Limitation**: Setting `EnableStackNotifications=yes` during v7→v8 upgrade will **not** apply notifications to existing nested stacks (`NotificationARNs` is a create-time-only property for nested stacks). Recommended for **new stack creation only**. For existing nested stacks, apply notifications manually:
  - **Console**: Update each nested stack → Use current template → edit "Notification options" → add SNS ARN.
  - **CLI**: `aws cloudformation update-stack --stack-name <nested-stack> --use-previous-template --notification-arns <sns-arn> --capabilities CAPABILITY_NAMED_IAM`
- **Parent Stack Notifications**: Configure separately at deploy time via Console "Notification options" or CLI `--notification-arns <arn>` — CloudFormation does not allow self-configuration via template.
- **Optional RDS Proxy Egress** (`UseRDSProxy`, default `no`; `RDSProxyPort`, default `1433`): Existing v7 service stacks upgrade to v8 with no behavior change. Set `UseRDSProxy=yes` only if the application connects via RDS Proxy — egress rules will be added to the existing DB subnet CIDRs (`VPCSubnetCidrDBAZ1/2/3`) on the proxy listener port.

### From v6 to v7
- **Backward Compatible**: No breaking changes — all existing v6 deployments continue to work.
- **New BCS Proxy Parameters**: `HasHCCSubnetCidrBCSAZ1`, `HasHCCSubnetCidrBCSAZ2`, `BCSProxyPort` added for ECS service connectivity to BCS Proxy (optional, with empty defaults).
- **Secrets Manager Scope Broadened**: Policy scope changed from `${AppShortName}-${EnvName}-*` to `${AppShortName}*` to allow shared secrets across non-prod environments.
- **AWS Batch IAM Permissions**: New batch job permissions added to ECS task role (no parameter changes required).

### From v5 to v6
- **Backward Compatible**: No breaking changes - all existing v5 deployments will continue to work
- **Optional Parameters**: VpcCidr4 and VpcCidr5 are optional with empty string defaults
- **Enhanced Multi-VPC Support**: Optionally add VpcCidr4 and VpcCidr5 for complex network architectures
- **Use Cases**: Multi-VPC peering, hybrid cloud, cross-region VPC connectivity
- **No Template Changes Required**: Existing stacks can be updated without parameter changes

### From v4 to v5
**Note**: v5 includes simplified network configuration compared to earlier development versions.
- All v5 features are optional with empty string defaults for backward compatibility
- Optionally add ElastiCache subnet parameters for enhanced network security
- Database ports will automatically use environment-appropriate values (53341/53331)
- All new resource tags will be applied automatically
- AdditionalAppPrefixList parameter is not included in v5 (use ElastiCache dedicated subnets or VPC-wide access)

For detailed changes, refer to the respective `README.md` files in the `v1`, `v2`, `v3`, `v4`, `v5`, `v6`, `v7`, `v8`, and `v9` directories.
