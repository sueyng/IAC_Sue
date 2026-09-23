# Release Notes: VPC Endpoint Infrastructure Templates

## Version Comparison: v1 vs v2 vs v3 vs v4 vs v5 vs v6

### General Updates
- **IaC Version Tag**:
  - Updated from `InfraPlatform-vpcendpoint-v1` through `InfraPlatform-vpcendpoint-v6`.

### Core Infrastructure (`cf-vpcendpoint.yaml`)
- **v2 Updates**:
  - Added support for **Multiple Subnets**:
    - Introduced `AppSubnetIds` parameter for specifying multiple subnets.
  - Enhanced **Security Group Rules**:
    - Added conditional rules for multiple VPC CIDRs (`VpcCidr1`, `VpcCidr2`, `VpcCidr3`).
  - Improved **Private DNS Configuration**:
    - Enabled `PrivateDnsEnabled` for all supported endpoints.
  - Introduced **New VPC Endpoints**:
    - Added support for `Elasticache`, `SES`, and `API Gateway` endpoints.

- **v3 Updates**:
  - Enhanced **Security Policies**:
    - Enforced TLS v1.2 for all connections.
    - Improved security group rules for hybrid connectivity scenarios.
  - Added support for **Additional VPC Endpoints**:
    - New endpoints include `Glue`, `Athena`, `DataSync`, `SNS`, `Batch`, and `CloudWatch Logs`.
  - Improved **Tagging**:
    - Added `IaCVersion` tag for better resource tracking.
  - Enhanced **Subnet Configuration**:
    - Improved handling of subnet IDs for production and non-production environments.

- **v4 Updates**:
  - Expanded **VPC CIDR Support** from 3 to 5:
    - Added `VpcCidr4` and `VpcCidr5` parameters for complex multi-VPC architectures
    - All security groups updated with conditional ingress/egress rules for VpcCidr4 and VpcCidr5
  - Use Cases:
    - Multi-VPC peering scenarios requiring broader security group rules
    - Hybrid cloud connectivity with multiple on-premises networks
    - Cross-region VPC connectivity patterns
  - Added **ACM VPC Endpoint** (`CreateACMEndpoint`) — backported enhancement:
    - Service: `com.amazonaws.{region}.acm`
    - Enables private ACM API calls (`ListCertificates`, `DescribeCertificate`, `RequestCertificate`) from inside the VPC
    - Uses main security group on port 443

- **v5 Updates (post-release patch — Firehose)**:
  - Added **Kinesis Data Firehose VPC Endpoint** (`CreateFirehoseEndpoint`):
    - Service: `com.amazonaws.{region}.kinesis-firehose`
    - Uses main security group (`VPCESecurityGroup`, port 443)
    - Default `false` — backward-compatible; existing v5 deployments are unaffected unless flag is opted in
    - **Condition slot**: added to second inner `!Or` group of `CreateMainSecurityGroup` (now 10/10; additional conditions must use another group)

- **v5 Updates**:
  - Enhanced **Security Policies**:
    - Enforced TLS v1.2 for all connections.
    - Improved security group rules for hybrid connectivity scenarios.
  - Added support for **Additional VPC Endpoints**:
    - New endpoints include `Glue`, `Athena`, `DataSync`, `SNS`, `Batch`, `CloudWatch Logs`, `StepFunction`, and `SES API`
  - Added **SES API Endpoint** (`CreateSESAPIEndpoint`):
    - Separate from existing SES SMTP endpoint (`CreateSESEndpoint`)
    - Uses main security group (`VPCESecurityGroup`, port 443) instead of dedicated SES security group (port 587)
    - Service name: `com.amazonaws.{region}.email` (vs SMTP's `com.amazonaws.{region}.email-smtp`)
  - Added **ACM VPC Endpoint** (`CreateACMEndpoint`):
    - Service: `com.amazonaws.{region}.acm`
    - Enables private ACM API calls (`ListCertificates`, `DescribeCertificate`, `RequestCertificate`) from inside the VPC
    - Uses main security group on port 443
    - **Condition restructure**: Added as third inner `!Or` group in `CreateMainSecurityGroup` condition (paired with `CreateSESAPI`) to stay within CloudFormation's 10-conditions-per-`Fn::Or` limit.
  - Improved **Tagging**:
    - Added `IaCVersion` tag for better resource tracking.
  - Enhanced **Subnet Configuration**:
    - Improved handling of subnet IDs for production and non-production environments.

- **v6 Updates**:
  - Added **Amazon EventBridge Scheduler VPC Endpoint** (`CreateSchedulerEndpoint`):
    - Service: `com.amazonaws.{region}.scheduler`
    - Uses the shared main security group (`VPCESecurityGroup`, port 443)
    - Uses the configured application subnets and enables private DNS
    - Default `false` — upgrading from v5 does not create the endpoint unless explicitly enabled
  - Added **Amazon EventBridge Event Bus VPC Endpoint** (`CreateEventBridgeEndpoint`):
    - Service: `com.amazonaws.{region}.events`
    - Uses the shared main security group (`VPCESecurityGroup`, port 443)
    - Uses the configured application subnets and enables private DNS
    - Default `false` — upgrading from v5 does not create the endpoint unless explicitly enabled
  - Added `CreateScheduler` and `CreateEventBridge` to the third inner `!Or` group of `CreateMainSecurityGroup`.
  - Updated all `IaCVersion` resource tags to `InfraPlatform-vpcendpoint-v6`.

### Available VPC Endpoints
| Service                  | v1 | v2 | v3 | v4 | v5 | v6 |
|--------------------------|----|----|----|----|----|----|
| Grafana                 | Yes | Yes | Yes | Yes | Yes | Yes |
| EKS                     | Yes | Yes | Yes | Yes | Yes | Yes |
| X-Ray                   | Yes | Yes | Yes | Yes | Yes | Yes |
| AMP (Prometheus)        | Yes | Yes | Yes | Yes | Yes | Yes |
| ECR (API and Docker)    | Yes | Yes | Yes | Yes | Yes | Yes |
| ELB                     | Yes | Yes | Yes | Yes | Yes | Yes |
| Secrets Manager         | Yes | Yes | Yes | Yes | Yes | Yes |
| Elasticache             | No  | Yes | Yes | Yes | Yes | Yes |
| SES SMTP                | No  | Yes | Yes | Yes | Yes | Yes |
| API Gateway             | No  | Yes | Yes | Yes | Yes | Yes |
| SQS                     | No  | No  | Yes | Yes | Yes | Yes |
| RDS                     | No  | No  | Yes | Yes | Yes | Yes |
| Lambda                  | No  | No  | Yes | Yes | Yes | Yes |
| S3                      | No  | No  | Yes | Yes | Yes | Yes |
| ECS                     | No  | No  | Yes | Yes | Yes | Yes |
| CloudFormation          | No  | No  | Yes | Yes | Yes | Yes |
| Glue                    | No  | No  | Yes | Yes | Yes | Yes |
| DataSync                | No  | No  | Yes | Yes | Yes | Yes |
| SNS                     | No  | No  | Yes | Yes | Yes | Yes |
| Batch                   | No  | No  | Yes | Yes | Yes | Yes |
| Athena                  | No  | No  | Yes | Yes | Yes | Yes |
| CloudWatch Logs         | No  | No  | Yes | Yes | Yes | Yes |
| Step Functions          | No  | No  | No  | No  | Yes | Yes |
| EventBridge Scheduler   | No  | No  | No  | No  | No  | Yes |
| EventBridge event buses | No  | No  | No  | No  | No  | Yes |
| SES API                 | No  | No  | No  | No  | Yes | Yes |
| ACM                     | No  | No  | No  | Yes | Yes | Yes |
| Kinesis Data Firehose   | No  | No  | No  | No  | Yes | Yes |


### Deployment Flow Updates
- **v2 Updates**:
  - Introduced a deployment order:
    1. Deploy security groups.
    2. Deploy VPC endpoints.
    3. Configure private DNS settings.

- **v3 Updates**:
  - Enhanced deployment documentation for hybrid connectivity and additional VPC endpoints.

- **v4 Updates**:
  - Updated parameter documentation for `VpcCidr4` and `VpcCidr5`.

### Documentation Updates
- **v2 Updates**:
  - Added detailed descriptions for new parameters (`AppSubnetIds`, `VpcCidr2`, `VpcCidr3`).
  - Updated troubleshooting guide for common issues with private DNS and security group configurations.

- **v3 Updates**:
  - Enhanced deployment guide with examples for hybrid connectivity and additional VPC endpoints.

- **v4 Updates**:
  - Added documentation for `VpcCidr4` and `VpcCidr5` parameters.
  - Added `CreateACMEndpoint` (backported) — ACM VPC endpoint (port 443)
  - Backfilled README documentation for `CreateCloudWatchLogsEndpoint` (pre-existing doc gap)

- **v5 Updates**:
  - Added `CreateStepFunctionEndpoint`
  - Added `CreateSESAPIEndpoint` — SES API endpoint (port 443) separate from SES SMTP endpoint (port 587)
  - Added `CreateACMEndpoint` — ACM VPC endpoint for private ACM API access (port 443)
  - Backfilled README documentation for `CreateCloudWatchLogsEndpoint` (pre-existing doc gap) and `VpcCidr4`/`VpcCidr5`

- **v6 Updates**:
  - Added `CreateSchedulerEndpoint` for private EventBridge Scheduler API access over port 443
  - Added `CreateEventBridgeEndpoint` for private EventBridge event-bus API access over port 443
  - Updated the parameter guide, supported-endpoint list, usage example, and security-group notes

## Summary of Key Changes
| Feature/Component    | v1          | v2                  | v3                      | v4                      | v5                      | v6                      |
|----------------------|-------------|---------------------|-------------------------|-------------------------|-------------------------|-------------------------|
| IaC Version          | vpcendpoint-v1 | vpcendpoint-v2   | vpcendpoint-v3          | vpcendpoint-v4          | vpcendpoint-v5          | vpcendpoint-v6          |
| Subnet Configuration | Single Subnet | Multiple Subnets | Enhanced Subnet Handling | Enhanced Subnet Handling | Enhanced Subnet Handling | Enhanced Subnet Handling |
| VPC CIDR Support     | Basic       | 3 CIDRs            | 3 CIDRs                 | 5 CIDRs                 | 5 CIDRs                 | 5 CIDRs                 |
| Security Group Rules | Basic       | Multi-VPC CIDR      | Hybrid Connectivity     | 5-CIDR Support          | 5-CIDR Support          | Shared HTTPS SG for Scheduler and EventBridge |
| Private DNS          | Basic       | Enabled             | Enhanced                | Enhanced                | Enhanced                | Enhanced                |
| VPC Endpoints        | 7 endpoints | 10 endpoints       | 22 endpoints            | 23 endpoints (+ACM)     | 26 endpoints (+ACM, +Firehose) | 28 endpoints (+Scheduler, +EventBridge) |
| Tagging              | Basic       | Basic               | Added `IaCVersion` Tag  | Updated to v4           | Updated to v5           | Updated to v6           |

For detailed changes, refer to the respective `README.md` files in the `v1`, `v2`, `v3`, `v4`, `v5`, and `v6` directories.
