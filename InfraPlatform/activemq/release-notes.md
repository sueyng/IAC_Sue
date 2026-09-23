# Release Notes: ActiveMQ Infrastructure

## v9 — Secrets Manager Generated Broker Password (June 2026)

**Security Enhancement**: Adds optional generated Secrets Manager password support for the ActiveMQ broker user.

- **New Resource**:
  - `ActiveMQCredentialSecret` (AWS::SecretsManager::Secret) — created when `MQPassword` is empty
- **Parameter Behavior**:
  - No additional password-source parameter introduced
  - Leave `MQPassword` empty for generated Secrets Manager password
  - Provide `MQPassword` only for v8-compatible upgrades / fallback where the existing broker password must be preserved
- **Backward Compatibility**:
  - `MQPassword` is retained for projects that need to preserve the existing broker password during upgrade
  - Existing v8 projects can keep their current `MQPassword` value to avoid changing the broker user password
- **Generated Secret Behavior**:
  - Secret name: `{AppShortName}-{EnvName}-activemq-credentials`
  - Secret keys: `username`, `password`
  - Generated password excludes comma, colon, and equal sign to comply with Amazon MQ ActiveMQ password restrictions

**Important**: This provides secure day-one password generation, not full automatic password rotation. Updating only the Secrets Manager secret value does not automatically update the Amazon MQ broker user password. Future password changes require an operational runbook to update both Amazon MQ and Secrets Manager.

Clearing `MQPassword` during an existing broker upgrade changes the broker user password to the generated Secrets Manager password. The change may require a broker reboot or the next maintenance window before the new password is active. Plan downtime for `SINGLE_INSTANCE` brokers.

## v8 — KMS Encryption at Rest (March 2026)

**Checkmarx Remediation**: Addresses high severity finding `AmazonMQ Broker Encryption Disabled`.

- **New Resources**:
  - `ActiveMQKMSKey` (AWS::KMS::Key) — Customer-managed symmetric key with automatic annual rotation
  - `ActiveMQKMSKeyAlias` (AWS::KMS::Alias) — `alias/{AppShortName}-{EnvName}-activemq`
- **Broker Encryption**: `EncryptionOptions` added to broker with `UseAwsOwnedKey: false`
- **KMS Key Policy**: Root account access + Amazon MQ service access (`mq.amazonaws.com`)
- **No New Parameters**: KMS key is created within the template — v7 parameter files are fully compatible
- **Deprecation Note**: `mq.t2.micro` removed from parameter file examples (deprecated by AWS, use `mq.t3.micro` or higher)

**⚠️ Important**: Encryption is an **immutable day-one setting** for Amazon MQ. It cannot be enabled on existing brokers. Existing unencrypted brokers must be recreated with a migration plan. See v8 README for migration guide.

## v7 — VPC CIDR Expansion

- Added `VpcCidr4` and `VpcCidr5` parameters for additional VPC CIDR ranges
- Extended security group egress rules with conditional logic for CIDRs 4 and 5
- All v6 features retained

## Previous Versions

### Latest Updates (September 2025)

### v5 and v6 - FirstMQDeployment Parameter Enhancement

**Added Conditional Log Resource Policy Management** to both v5 and v6 templates:

- **New Parameter**: `FirstMQDeployment` (String, default: "false")
  - Controls creation of the `AmazonMQLogResourcePolicy` resource
  - Prevents deployment conflicts when multiple ActiveMQ stacks exist in the same AWS account
  - Set to `"true"` for the **first** ActiveMQ deployment in an AWS account
  - Set to `"false"` for **subsequent** deployments

- **New Condition**: `IsFirstMQDeployment`
  - Applied to the `AmazonMQLogResourcePolicy` resource
  - Only creates the log resource policy when `FirstMQDeployment=true`

- **Enhanced Documentation**:
  - Updated README files for both v5 and v6 with detailed guidance
  - Added decision matrix for parameter usage
  - Included troubleshooting steps for common deployment errors
  - Added commands for manual policy verification and creation

**Benefits**:
- ✅ Eliminates "resource already exists" errors
- ✅ Allows multiple ActiveMQ deployments per AWS account
- ✅ User-controlled approach with clear decision guidance
- ✅ Backward compatible (defaults to safe behavior)

## Version Comparison: v4 vs v5 vs v6

### General Updates
- **IaC Version Tag**:
  - Updated from `InfraPlatform-ActiveMQ-v4` to `InfraPlatform-ActiveMQ-v5` and maintained in `v6`.

### Core Infrastructure (`cf-activemq.yaml`)
- **v5 Updates**:
  - Added support for **Deployment Modes**:
    - `SINGLE_INSTANCE` and `ACTIVE_STANDBY_MULTI_AZ` deployment modes.
    - Configurable via the `DeploymentMode` parameter.
  - Enhanced **Engine Version**:
    - Added support for specifying the ActiveMQ engine version via the `EngineVersion` parameter.
    - Default version updated to `5.18.2`.
  - Improved **Security Group Rules**:
    - Added ingress rule for port `8162` to allow access from the `DeploymentServer01` IP.
  - Enhanced **Subnet Configuration**:
    - Added conditional logic for single-instance and multi-AZ deployments.
    - Improved handling of `VPCSubnetIdappAZ1`, `VPCSubnetIdappAZ2`, and `VPCSubnetIdappAZ3`.
  - Enhanced **Logging**:
    - Enabled both general and audit logs for the ActiveMQ broker.

- **v6 Updates**:
  - Added support for **VPC CIDR Configuration**:
    - New parameters: `VpcCidr1`, `VpcCidr2`, and `VpcCidr3` for flexible network configuration.
    - Added conditional logic with `HasVpcCidr2` and `HasVpcCidr3` for optional CIDR configurations.
  - Enhanced **Security Group Egress Rules**:
    - Improved outbound traffic control with dynamic CIDR configurations.
    - Added conditional security group egress rules for different CIDR ranges.
  - Improved **CloudFormation Template**:
    - Expanded resource definition with better production retention policies.  - Added **Scheduler Support**:
    - Added `EnableScheduler` parameter to toggle ActiveMQ scheduler functionality.

### Parameters and Configuration
- **New Parameters in v5**:
  - `DeploymentMode`: Allows selection of `SINGLE_INSTANCE` or `ACTIVE_STANDBY_MULTI_AZ`.
  - `EngineVersion`: Specifies the ActiveMQ engine version (default: `5.18.2`).
  - `InstanceType`: Allows configuration of the broker instance type (e.g., `mq.m5.large`).
  - `DeploymentServer01`: Specifies the IP address of the deployment server for secure access.

- **Additional Parameters in v6**:
  - `VpcCidr1`: Specifies the primary VPC CIDR IP range.
  - `VpcCidr2`: Specifies the secondary VPC CIDR IP range.
  - `VpcCidr3`: Specifies the tertiary VPC CIDR IP range.
  - `EnableScheduler`: Toggle to enable/disable ActiveMQ scheduler support (boolean).
  - `HCCVpceCidr`: Referenced in conditional logic for hybrid cloud connectivity.

### Security Enhancements
- **v5 Updates**:
  - Enforced TLS v1.2 for all connections.
  - Improved security group rules to restrict access to specific subnets and deployment servers.

### Deployment Flow Updates
- **v5 Updates**:
  - Introduced a deployment order:
    1. Configure the `parameters-activemq.json` file with the new parameters.
    2. Deploy the CloudFormation stack using the Azure DevOps pipeline.
    3. Verify the ActiveMQ broker setup in the AWS Management Console.

### Documentation Updates
- **v5 Updates**:
  - Added detailed descriptions for new parameters (`DeploymentMode`, `EngineVersion`, `InstanceType`, `DeploymentServer01`).
  - Updated provisioning instructions to include steps for configuring single-instance and multi-AZ deployments.
  - Enhanced troubleshooting guide for common issues with deployment and configuration.

## Logging Troubleshooting and Best Practices (v6)

- Broker logging is enabled by default (`General: true`, `Audit: true`). Log groups are automatically created in CloudWatch Logs for each broker instance.
- If log groups are created but remain empty:
  - Ensure the broker is running and healthy in the AWS Console.
  - Generate broker activity (connect a client, send messages).
  - Check for restrictive Service Control Policies (SCPs) or IAM policies that may block CloudWatch Logs actions (`logs:CreateLogGroup`, `logs:CreateLogStream`, `logs:PutLogEvents`).
  - Review the broker's monitoring tab for errors or warnings.
  - Wait a few minutes for log delivery, then refresh CloudWatch Logs.

For more details, see the README in the v6 directory.

## Summary of Key Changes

### v4 to v7

| Feature/Component | v4 | v5 | v6 | v7 |
|---|---|---|---|---|
| IaC Version | InfraPlatform-ActiveMQ-v4 | InfraPlatform-ActiveMQ-v5 | InfraPlatform-ActiveMQ-V6 | InfraPlatform-ActiveMQ-V7 |
| Deployment Modes | ACTIVE_STANDBY_MULTI_AZ | SINGLE + MULTI_AZ | SINGLE + MULTI_AZ | SINGLE + MULTI_AZ |
| Instance Type | mq.t2.micro | Configurable | Configurable | Configurable |
| VPC CIDR Configuration | Not available | Not available | CIDRs 1-3 | CIDRs 1-5 |
| Scheduler Support | Not available | Not available | EnableScheduler parameter | EnableScheduler parameter |
| Log Policy Management | Fixed policy creation | Conditional via FirstMQDeployment | Conditional via FirstMQDeployment | Conditional via FirstMQDeployment |
| KMS Encryption | Not available | Not available | Not available | Not available |
| Secrets Manager Password | Not available | Not available | Not available | Not available |
| Multi-Stack Support | No | Yes | Yes | Yes |

### v8 onwards

| Feature/Component | v8 | v9 |
|---|---|---|
| IaC Version | InfraPlatform-ActiveMQ-V8 | InfraPlatform-ActiveMQ-V9 |
| Deployment Modes | SINGLE + MULTI_AZ | SINGLE + MULTI_AZ |
| Instance Type | Configurable (t2.micro deprecated) | Configurable (t2.micro deprecated) |
| VPC CIDR Configuration | CIDRs 1-5 | CIDRs 1-5 |
| Scheduler Support | EnableScheduler parameter | EnableScheduler parameter |
| Log Policy Management | Conditional via FirstMQDeployment | Conditional via FirstMQDeployment |
| KMS Encryption | Customer-managed KMS key | Customer-managed KMS key |
| Secrets Manager Password | Not available | Optional generated secret |
| Multi-Stack Support | Yes | Yes |

For detailed changes, refer to the respective `README.md` files in each version directory.
