# Release Notes: DataLoading-BatchJob Infrastructure

## Post-Release Patch - Optional SQS Send Permissions (June 2026)

Applies to v6 and v7.

- **New Parameters**:
  - `SQSQueueArns`: Optional comma-delimited SQS queue ARN(s) the batch job container can send messages to.
  - `SQSCustomerManagedKmsKeyArns`: Optional comma-delimited customer-managed KMS key ARN(s) for encrypted SQS queues.
- **IAM Policy Update**:
  - Adds conditional SQS permissions to `BatchJobPolicy`, which is attached to `BatchJobRole` and used by the running batch container.
  - SQS permissions granted: `sqs:SendMessage`, `sqs:GetQueueUrl`, and `sqs:GetQueueAttributes`.
  - Adds conditional KMS permissions only when `SQSCustomerManagedKmsKeyArns` is provided.
  - KMS permissions granted: `kms:GenerateDataKey` and `kms:Decrypt`.
  - `BatchExecutionPolicy` is unchanged.
- **Backward Compatibility**:
  - Both parameters default to empty.
  - Existing deployments are not impacted unless project teams provide SQS/KMS values.
  - Leave `SQSCustomerManagedKmsKeyArns` empty when the SQS queue uses AWS managed key `alias/aws/sqs`.

## Version 7.1 (v7.1) - Latest

### Key Changes in v7.1

#### 1. External Services Prefix List Egress
- **New Parameter**:
  - `ExternalServicesPrefixListId` (Type: `String`, Default: `""`)
  - Managed prefix list ID for external services reached over HTTPS (CAG, ESB, etc.)
- **New Condition**:
  - `HasExternalServicesPrefixListId`: True when `ExternalServicesPrefixListId` is provided
- **New Security Group Egress Rule**:
  - Port 443 (TCP) to `DestinationPrefixListId: !Ref ExternalServicesPrefixListId`
  - Added alongside the existing S3 prefix list rule in `BatchSecurityGroup.SecurityGroupEgress`
  - Rule is omitted entirely (`AWS::NoValue`) when the parameter is empty
- **Driver**: Projects calling shared enterprise endpoints (CAG, ESB) need egress to a centrally-managed prefix list instead of maintaining per-project CIDR lists that change over time.

### Migration from v7 to v7.1
- **No breaking changes.** `ExternalServicesPrefixListId` defaults to empty — existing parameter files deploy unchanged and produce the same security group rules as v7.
- **No resource replacement.** Adding the parameter only appends one conditional egress rule to the existing `BatchSecurityGroup`.
- To enable, set `ExternalServicesPrefixListId` in the environment parameters file (see `v7.1/Env/parameters-dataloading.yaml`).
- **Prefix list entry limits apply.** Each prefix list referenced by a security group consumes entries against the SG rule quota — confirm headroom before enabling on security groups that already carry many rules.

### Use Cases Better Suited for v7.1
- **Batch jobs calling CAG / ESB or other shared enterprise endpoints** where destination IPs are centrally managed.
- **All v7 use cases continue to apply** (ECS.20 non-root container, HCC Forward Proxy, ElastiCache Redis, SES SMTP, Step Functions, multi-secret).

---

## Version 7 (v7)

### Key Changes in v7

#### 1. ECS.20 Remediation — Non-Root Container User
- **New Parameter**:
  - `ContainerUser` (Type: `String`, Default: `"1000"`)
  - `AllowedPattern: "^(?!0$)(?!0:0$)[0-9]+(:[0-9]+)?$"` — blocks root (`0` and `0:0`)
  - Accepts UID-only (e.g. `1000`) or UID:GID (e.g. `1000:1000`)
- **`User: !Ref ContainerUser` injected into `BatchJobDefinition.ContainerProperties`**:
  - Forces Fargate to run the batch container as a non-root user.
  - Pairs with the existing `ReadonlyRootFilesystem: true` (carried over from v6) to satisfy AWS Security Hub control **ECS.20** (Containers should not run with elevated privileges).
- **Driver**: HCC compliance scope — Security Hub ECS.20 is no longer optional for accounts under central monitoring.

#### 2. IaC Version Tag
- Value bumped to `AppSubsystem-BatchJob-v7` across all previously-tagged resources.
- Tag added in-template to `DataLoadingLogGroup` and `BatchJobDefinition`.
- `BatchComputeEnvironment` and `BatchJobQueue` are tagged out-of-band — their CFN `Tags` property requires resource replacement, blocked by custom names. Apply via `aws batch tag-resource` after deploy. See README for details.
- `BatchSchedule`, `S3EventRule`, and `*Policy` resources cannot be tagged via CFN (resource-type limitation).

### Migration from v6 to v7

#### CloudFormation-side (low risk)
- **No breaking parameter changes.** `ContainerUser` has `Default: "1000"`, so existing parameter files do **not** need to be updated to upgrade the stack.
- **No resource replacement.** AWS Batch handles `BatchJobDefinition` updates as a **new revision** (existing in-flight jobs continue with the old revision; next submitted job picks up the latest definition).
- **No new security group rules.** Optional SQS/KMS IAM statements are inactive unless `SQSQueueArns` or `SQSCustomerManagedKmsKeyArns` is provided.

#### Runtime-side (must verify per project)
- **The container image MUST run cleanly as UID 1000** (or whatever value the project sets `ContainerUser` to). This is the **only real upgrade risk**.
- Pre-upgrade checklist for project teams:
  1. Inspect Dockerfile — does it have a `USER` directive? If not, the image runs as root by default.
  2. Test locally: `docker run --user 1000:1000 --read-only <image> <cmd>` should complete without permission errors.
  3. Confirm app writes only to `/tmp` or mounted volumes (compatible with `ReadonlyRootFilesystem: true`).
  4. If the image needs a different UID (e.g. nginx-base uses `100:100`), override: `ContainerUser: "100:100"` in parameters file.
- **First job submission after upgrade is the integration test.** Submit one job in non-prod, watch CloudWatch Logs to confirm clean startup before promoting to prod.

#### Common failure modes if image isn't UID-1000-ready
| Symptom | Cause | Fix |
|---|---|---|
| `Permission denied` on app log path or work dir | App writes to a path owned by root | `RUN chown 1000:1000 /path` in Dockerfile, or override `ContainerUser` |
| `Operation not permitted` binding port < 1024 | Non-root can't bind privileged ports | Re-bind to port ≥ 1024 (rarely applies to batch jobs) |
| Container exits immediately with no log | Entrypoint script needs root | Refactor entrypoint to drop privileges before app start |

### Use Cases Better Suited for v7
- **HCC compliance accounts**: Required when Security Hub ECS.20 is in scope.
- **Hardened workloads**: Defense-in-depth — pairs non-root execution with the existing read-only root filesystem.
- **All v6 use cases continue to apply** (HCC Forward Proxy, ElastiCache Redis, SES SMTP, Step Functions, multi-secret).

---

## Version 6 (v6)

### Key Changes in v6

#### 1. HCC Forward Proxy Support
- **Replaced BCS Proxy** with HCC Forward Proxy configuration:
  - Changed `EnableBCSProxy` from `yes/no` to `true/false` for consistency
  - Removed `BCSProxySubnet` and `BCSProxyPort` parameters
  - Added `HCCProxyPort` parameter (default: 4000)
  - Added separate prod/nprd proxy subnet CIDRs (2 subnets per environment):
    - `ProdHCCProxyCidr1`, `ProdHCCProxyCidr2` for production environments
    - `NprdHCCProxyCidr1`, `NprdHCCProxyCidr2` for non-production environments
  - Automatic prod/nprd CIDR selection based on `EnvName`

- **New Conditions**:
  - `EnableBCSProxy`: True when EnableBCSProxy is `true`
  - `HasProdHCCProxyCidr1`, `HasProdHCCProxyCidr2`: True when respective prod CIDRs provided
  - `HasNprdHCCProxyCidr1`, `HasNprdHCCProxyCidr2`: True when respective nprd CIDRs provided
  - `HasHCCProxyCidr1`, `HasHCCProxyCidr2`: Compound conditions combining EnableBCSProxy + environment + CIDR availability

#### 2. ElastiCache Redis Egress
- **New Security Group Egress Rules**:
  - Port range 6379-6380 (Redis + TLS) to VPC CIDRs (VpcCidr1-5)
  - Optional dedicated ElastiCache subnet CIDRs for environments where cache subnets differ from VPC CIDRs

- **New Parameters**:
  - `ElastiCacheSubnetAZ1`: Dedicated ElastiCache subnet CIDR AZ1
  - `ElastiCacheSubnetAZ2`: Dedicated ElastiCache subnet CIDR AZ2
  - `ElastiCacheSubnetAZ3`: Dedicated ElastiCache subnet CIDR AZ3

- **New Conditions**:
  - `HasElastiCacheSubnetAZ1`, `HasElastiCacheSubnetAZ2`, `HasElastiCacheSubnetAZ3`

#### 3. SES SMTP Egress
- **New Security Group Egress Rules**:
  - Port 587 (SMTP submission) to VPC CIDRs (VpcCidr1-5) for email notification support
  - Rules follow the same conditional pattern as HTTPS (443) — VpcCidr1 always, VpcCidr2-5 conditional

#### 4. Step Functions Permissions
- **BatchJobPolicy Updated**:
  - Added IAM permissions for AWS Step Functions:
    - `states:StartExecution`, `states:DescribeExecution`, `states:StopExecution`
    - `states:ListExecutions`, `states:ListStateMachineVersions`, `states:ListStateMachines`
  - Scoped to `arn:aws:states:${Region}:${AccountId}:stateMachine:*`

#### 5. Security Group Egress Summary (v6)
| Port(s) | Protocol | Destination | Condition | Description |
|----------|----------|-------------|-----------|-------------|
| 443 | TCP | VpcCidr1-5 | VpcCidr1 always; 2-5 conditional | HTTPS to VPC CIDRs |
| DB Port* | TCP | VPCSubnetCidrDBAZ1-3 | AZ1/AZ2 always; AZ3 conditional | Database access |
| 443 | TCP | S3PrefixListId | Conditional | S3 VPC endpoint |
| 443 | TCP | HCCVpceCidr | Conditional | HCC VPC endpoint |
| HCCProxyPort | TCP | ProdHCCProxyCidr1/2 or NprdHCCProxyCidr1/2 | EnableBCSProxy + CIDR provided | HCC Forward Proxy |
| 587 | TCP | VpcCidr1-5 | VpcCidr1 always; 2-5 conditional | SES SMTP submission |
| 6379-6380 | TCP | VpcCidr1-5 | VpcCidr1 always; 2-5 conditional | ElastiCache Redis + TLS |
| 6379-6380 | TCP | ElastiCacheSubnetAZ1-3 | Conditional | ElastiCache dedicated subnets |

*DB Port: prod = 53341, nprd = 53331 (auto-selected based on EnvName)

### Migration from v5 to v6
- **Breaking Changes**:
  - `EnableBCSProxy` changed from `yes/no` to `true/false` — update parameter files
  - `BCSProxySubnet` and `BCSProxyPort` parameters removed — replace with `HCCProxyPort`, `ProdHCCProxyCidr1/2`, `NprdHCCProxyCidr1/2`
- **New Egress Rules**: SES SMTP (587) and ElastiCache Redis (6379-6380) added to security group — review if acceptable in your environment
- **Optional Parameters**: Add `ElastiCacheSubnetAZ1/2/3` if using dedicated ElastiCache subnets
- **Step Functions**: New IAM permissions added — no action needed unless restricting IAM policies

### Use Cases Better Suited for v6
- **HCC Forward Proxy**: When batch jobs need external API access via corporate proxy with separate prod/nprd subnets
- **ElastiCache Redis**: When batch jobs need to read from or write to Redis cache
- **SES Email Notifications**: When batch jobs send email notifications via Amazon SES SMTP
- **Step Functions Orchestration**: When batch jobs need to trigger or interact with Step Functions workflows
- **Multi-Environment Proxy**: When production and non-production environments use different proxy subnets

---

## Version 5 (v5)

### Key Changes in v5

#### 1. Extended VPC CIDR Support
- **Additional VPC CIDRs**:
  - Added support for `VpcCidr4` and `VpcCidr5` parameters
  - Now supports **up to 5 VPC CIDR ranges** (previously 3)
  - Enhanced security group rules for multi-VPC architectures
  - All new parameters are optional with empty string defaults

- **Multi-VPC Connectivity**:
  - **Enhanced Network Flexibility**: Better support for complex network topologies with multiple VPC peerings
  - **Expanded HTTPS Egress**: Security group egress rules now support up to 5 VPC CIDR ranges
  - **Enterprise Network Support**: Improved support for hybrid cloud and cross-region VPC connectivity
  - **Conditional Rules**: Security group rules automatically created only for provided VPC CIDRs

- **New Conditions**:
  - Added conditions: `HasVpcCidr4`, `HasVpcCidr5`
  - Enhanced conditional logic for VPC CIDR-based security group rules

#### 2. Use Cases for Additional VPC CIDRs
- **Multi-VPC Peering**: Connect to 4-5 different VPCs
- **Complex Network Topologies**: Enterprise architectures with multiple network segments
- **Hybrid Cloud**: Additional on-premises network ranges via VPN/Direct Connect
- **Cross-Region VPC Peering**: Additional VPC CIDRs from other AWS regions

#### 3. Backward Compatibility
- All existing parameters from v4 remain unchanged
- Existing deployments can upgrade without parameter changes
- VpcCidr4 and VpcCidr5 are optional with safe defaults (empty strings)
- No breaking changes to security group configurations

### Migration from v4 to v5
- **No Breaking Changes**: v4 deployments continue to work without modifications
- **Optional Parameters**: Add `VpcCidr4` and `VpcCidr5` to parameter files only if additional VPC CIDRs are needed
- **Parameter File Updates**: Update `parameters-dataloading.yaml` to include new optional VPC CIDR parameters
- **Benefits**: Enhanced multi-VPC connectivity without impacting existing deployments

---

## Version 4 (v4)

### Key Changes in v4

#### 1. Enhanced Secrets Management
- **Multi-Secret Support**:
  - Added support for **up to 5 additional secrets** beyond the primary database secret (6 secrets total)
  - New parameters for additional secrets:
    - `AdditionalSecret2Name` through `AdditionalSecret5Name` - Secret names from AWS Secrets Manager
    - `AdditionalSecret2EnvVarName` through `AdditionalSecret5EnvVarName` - Customizable environment variable names
  - All additional secret parameters are optional with empty string defaults
  - Default environment variable names: `ADDITIONAL_SECRET_2`, `ADDITIONAL_SECRET_3`, `ADDITIONAL_SECRET_4`, `ADDITIONAL_SECRET_5`

- **Improved IAM Policies**:
  - **Granular Secret Access Control**: IAM permissions automatically configured for each provided secret
  - **BatchJobPolicy Updates**: Added conditional statements for each additional secret with `GetSecretValue` and `DescribeSecret` permissions
  - **BatchExecutionPolicy Updates**: Added conditional statements for each additional secret to support container startup
  - **Conditional Permission Assignment**: Only secrets that are configured receive IAM permissions

- **Enhanced Batch Job Definition**:
  - **Conditional Secrets Injection**: Secrets section only created when at least one secret is provided (`HasAnySecret` condition)
  - **Flexible Secret Configuration**: Each additional secret is conditionally added based on its parameter
  - **Customizable Environment Variable Names**: Each secret can have a custom environment variable name for flexibility
  - **Seamless Integration**: Secrets are injected as environment variables at container runtime

- **New Secret-Related Conditions**:
  - Added conditions: `HasAdditionalSecret2`, `HasAdditionalSecret3`, `HasAdditionalSecret4`, `HasAdditionalSecret5`
  - Added `HasAnySecret` condition to control Secrets section creation
  - Enhanced conditional logic for secret injection and IAM permission assignment

#### 2. Customizable Environment Variables
- **Customizable Environment Variables**:
  - Added support for **customizable environment variable parameters** matching ECS service pattern
  - New parameter `EnvVarConnectionStringSecretName` for database connection string secrets
  - Added three pairs of custom environment variable parameters:
    - `EnvVar1Name` and `EnvVar1Value`
    - `EnvVar2Name` and `EnvVar2Value`
    - `EnvVar3Name` and `EnvVar3Value`
  - All new parameters are optional with empty string defaults for backward compatibility

- **Enhanced Environment Variable Configuration**:
  - **Conditional Environment Variable Inclusion**: Environment variables are only included when their corresponding name parameters are provided
  - **`AwsSecretPrefix` Environment Variable**: Set when `EnvVarConnectionStringSecretName` is provided
  - **Custom Environment Variables**: Up to 3 additional environment variables can be configured dynamically
  - **ECS Service Consistency**: Environment variable pattern now matches ECS service template for unified configuration approach

- **Additional Template Conditions**:
  - Added conditions: `HasEnvVar1Name`, `HasEnvVar2Name`, `HasEnvVar3Name`, `HasEnvVarConnectionStringSecretName`
  - Enhanced conditional logic for environment variable inclusion
  - Maintains all existing conditions from v3

#### 3. Backward Compatibility
- All existing parameters from v3 remain unchanged
- Existing deployments can upgrade without parameter changes
- Primary database secret (`DatabaseSecretName`) continues to work as before
- New additional secret and environment variable parameters are optional with safe defaults

### Migration from v3 to v4
  - Added support for **customizable environment variable parameters** matching ECS service pattern
  - New parameter `EnvVarConnectionStringSecretName` for database connection string secrets
  - Added three pairs of custom environment variable parameters:
    - `EnvVar1Name` and `EnvVar1Value`
    - `EnvVar2Name` and `EnvVar2Value`
    - `EnvVar3Name` and `EnvVar3Value`
  - All new parameters are optional with empty string defaults for backward compatibility

- **Enhanced Environment Variable Configuration**:
  - **Conditional Environment Variable Inclusion**: Environment variables are only included when their corresponding name parameters are provided
  - **`AwsSecretPrefix` Environment Variable**: Set when `EnvVarConnectionStringSecretName` is provided
  - **Custom Environment Variables**: Up to 3 additional environment variables can be configured dynamically
  - **ECS Service Consistency**: Environment variable pattern now matches ECS service template for unified configuration approach

- **Improved Template Conditions**:
  - Added new conditions: `HasEnvVar1Name`, `HasEnvVar2Name`, `HasEnvVar3Name`, `HasEnvVarConnectionStringSecretName`
  - Enhanced conditional logic for environment variable inclusion
  - Maintains all existing conditions from v3

- **Backward Compatibility**:
  - All existing parameters from v3 remain unchanged
  - Existing deployments can upgrade without parameter changes
  - New environment variable parameters are optional with safe defaults

### Migration from v3 to v4
- **Parameter Changes**:
  - No breaking changes - all v3 parameters remain the same
  - New optional secret parameters can be added for multi-service integration
  - New optional environment variable parameters can be added for custom configuration
  - Existing deployments will continue to work without any modifications

- **Benefits of Upgrade**:
  - **Multi-Service Integration**: Support for multiple external services requiring separate credentials
  - **Better Secret Isolation**: Separate secrets for different purposes (database, API keys, OAuth tokens, etc.)
  - **Easier Secret Rotation**: Individual secrets can be rotated independently
  - **Improved Security Posture**: Granular IAM permissions for each secret
  - **Flexible Configuration**: Customizable environment variable names for secrets and plain-text config
  - **Enhanced Application Configuration**: Up to 3 custom environment variables for application-specific settings
  - **ECS Service Consistency**: Environment variable patterns match ECS service templates
  - **Simplified Secret Management**: No need to bundle multiple credentials in a single secret

### Use Cases Better Suited for v4
- **Multi-Service Integration**: When batch jobs need to access multiple external services with different credentials
- **Microservices Architecture**: When integrating with multiple microservices requiring separate API keys
- **Third-Party API Access**: When accessing multiple third-party APIs (payment gateways, notification services, etc.)
- **Storage Access**: When accessing multiple storage services with different credentials
- **OAuth Integration**: When using OAuth tokens for external service authentication
- **Database and API Combined**: When needing both database credentials and API keys
- **Secret Rotation**: When different secrets need to be rotated on different schedules
- **Application-Specific Configuration**: When batch jobs need custom environment variables
- **Database Connection Management**: When using connection string secrets
- **Multi-Environment Consistency**: When maintaining consistent patterns across ECS services and batch jobs
- **Dynamic Configuration**: When environment variables need to be configured differently across deployments

## Version 3 (v3)

### Key Changes in v3
- **Conditional S3 Event Monitoring**:
  - **`InputPrefix` parameter** is now used conditionally with smart logic
  - When `InputPrefix` is provided, S3 events monitor only files with that prefix
  - When `InputPrefix` is empty or not provided, S3 events monitor the entire bucket
  - Provides flexibility for both targeted and broad file monitoring scenarios

- **Enhanced Resource Tagging**:
  - Added `IaCVersion: AppSubsystem-BatchJob-v3` tag to all taggable resources
  - Improves resource identification, cost tracking, and governance
  - Helps with version-specific resource management

- **Smart Environment Variables**:
  - `S3_INPUT_PREFIX` environment variable is conditionally set based on `InputPrefix` parameter
  - When `InputPrefix` is provided, `S3_INPUT_PREFIX` is set for the container
  - When `InputPrefix` is empty, `S3_INPUT_PREFIX` is not set, reducing unnecessary variables

- **Intelligent S3 Event Pattern**:
  - EventBridge rule uses conditional logic for object key filtering
  - When `InputPrefix` is specified, event pattern includes prefix filtering
  - When `InputPrefix` is empty, event pattern monitors all objects in the bucket
  - Eliminates need for separate templates for different monitoring scenarios

### Migration from v2 to v3
- **Parameter Changes**:
  - `InputPrefix` parameter is still available but now optional and works conditionally
  - If migrating from v2, existing `InputPrefix` values will continue to work
  - For new deployments, `InputPrefix` can be left empty for bucket-wide monitoring

- **Benefits of Upgrade**:
  - Conditional logic provides more flexibility than previous versions
  - Single template handles both prefix-specific and bucket-wide monitoring
  - Better resource tracking with version tags
  - Smarter environment variable management reduces container complexity

### Use Cases Better Suited for v3
- **Flexible File Monitoring**: When you need the option to process files from specific prefixes OR entire bucket
- **Conditional Configuration**: When you want to deploy the same template with different monitoring behaviors
- **Unified Template Management**: When you want one template that handles multiple monitoring scenarios

## Version 2 (v2)

### Key Changes in v2
- **SNS notifications** — configurable via `SNSTopicName`; success/failure events
- **S3 bucket policies** — enforced TLS v1.2+; added `S3PrefixListId` support for VPC endpoint access
- **Security group** — fine-grained outbound rules for database and S3 access
- **EventBridge Scheduler** — added `FlexibleTimeWindow`; improved retry strategy
- **Batch job definition** — added `SNS_TOPIC_ARN` env var; improved CloudWatch logging
- **IAM** — added SNS publish permissions; multi-secret support in Secrets Manager access

## Summary of Key Changes Across Versions

> **Bold** = first version where the feature was introduced or significantly changed.

### 1. Identity & Tagging
| Feature             | v1–v5                              | v6                              | v7                                                                          |
|---------------------|------------------------------------|---------------------------------|-----------------------------------------------------------------------------|
| IaC Version tag     | Legacy `DataLoading-BatchJob-v*` (retired) | **`AppSubsystem-BatchJob-v6`** (renamed naming scheme) | **`AppSubsystem-BatchJob-v7`**                                              |
| Resource Tagging    | v3+: tag set on 4 resources        | 4 resources                     | **Extended to 8 resources** (added log group, compute env, queue, job def)  |

> **Note on legacy tag naming:** versions v1–v5 used the `DataLoading-BatchJob-v*` tag value. The naming scheme was unified to `AppSubsystem-BatchJob-v*` starting at v6. If you have stacks deployed from v1–v5, the legacy tag value persists on those resources until they're upgraded — keep this in mind when filtering Resource Groups, Cost Explorer, or Security Hub findings.

### 2. Compute & Container
| Feature                | v1–v3                                   | v4                                   | v5–v6                          | v7                                       |
|------------------------|-----------------------------------------|--------------------------------------|--------------------------------|------------------------------------------|
| Batch Job Definition   | Basic (v2: +SNS_TOPIC_ARN, logging)     | **Multi-secret + custom env vars**   | Multi-secret + custom env vars | **+ Non-root `User` (ECS.20)**           |
| Container User         | Root (default)                          | Root (default)                       | Root (default)                 | **Non-root via `ContainerUser` (default `1000`)** |
| Environment Variables  | S3_BUCKET_NAME, DB_SECRET_NAME (v2: +SNS_TOPIC_ARN, S3_INPUT_PREFIX; v3: conditional S3_INPUT_PREFIX) | **3 custom + AwsSecretPrefix** | 3 custom + AwsSecretPrefix | 3 custom + AwsSecretPrefix |

### 3. Triggers & Events
| Feature                | v1            | v2                              | v3                                          | v4–v7                                |
|------------------------|---------------|---------------------------------|---------------------------------------------|--------------------------------------|
| EventBridge Scheduler  | Basic         | **Flexible time windows + retries** | Flexible time windows + retries         | (unchanged from v2)                  |
| S3 Event Monitoring    | Prefix-based  | Prefix-based with validation    | **Conditional (prefix or entire bucket)**   | (unchanged from v3)                  |
| `InputPrefix` Parameter| Supported     | Supported with validation       | **Conditionally used**                      | (unchanged from v3)                  |
| SNS Notifications      | Not supported | **Supported**                   | Supported                                   | (unchanged from v2)                  |

### 4. Secrets & IAM
| Feature              | v1–v3                  | v4                                       | v5                                | v6                                       | v7                          |
|----------------------|------------------------|------------------------------------------|-----------------------------------|------------------------------------------|-----------------------------|
| Secrets Support      | 1 database secret      | **Up to 6 secrets total**                | Up to 6 secrets total             | Up to 6 secrets total                    | Up to 6 secrets total       |
| Secret Env Var Names | Fixed (DB_SECRET_NAME) | **Customizable for additional secrets**  | Customizable for additional       | Customizable for additional              | Customizable for additional |
| IAM Policies         | Basic (v2: enhanced)   | **Granular per-secret permissions**      | Granular per-secret               | **+ Step Functions permissions**         | +Step Functions permissions |

### 5. Networking & Egress
| Feature                  | v1                | v2                            | v3                            | v4                  | v5                                  | v6                                                  | v7                                                  |
|--------------------------|-------------------|-------------------------------|-------------------------------|---------------------|-------------------------------------|-----------------------------------------------------|-----------------------------------------------------|
| VPC CIDRs                | Up to 3           | Up to 3                       | Up to 3                       | Up to 3             | **Up to 5**                         | Up to 5                                             | Up to 5                                             |
| Security Group Rules     | Basic outbound    | **Fine-grained outbound**     | Fine-grained outbound         | Fine-grained outbound | Extended VPC CIDRs (5)            | **+ SES SMTP, Redis, HCC Proxy**                    | +SES SMTP, Redis, HCC Proxy                         |
| Proxy Support            | Not supported     | Not supported                 | Not supported                 | **BCS Proxy (yes/no)** | BCS Proxy (yes/no)               | **HCC Forward Proxy (true/false, prod/nprd split)** | HCC Forward Proxy (true/false, prod/nprd split)     |
| ElastiCache Redis Egress | Not supported     | Not supported                 | Not supported                 | Not supported       | Not supported                       | **Ports 6379-6380 + dedicated subnets**             | Ports 6379-6380 + dedicated subnets                 |
| SES SMTP Egress          | Not supported     | Not supported                 | Not supported                 | Not supported       | Not supported                       | **Port 587 to VPC CIDRs**                           | Port 587 to VPC CIDRs                               |
| S3 Bucket Policies       | Basic             | **Enforced TLS v1.2 + prefix list** | Enforced TLS v1.2 + prefix list | (unchanged from v2) | (unchanged from v2)               | (unchanged from v2)                                 | (unchanged from v2)                                 |

## Detailed Secrets Support Comparison

| Version | Database Secret | Additional Secrets | Total Secrets | Customizable Env Var Names | IAM Granularity |
|---------|----------------|-------------------|---------------|---------------------------|-----------------|
| v1      | ✓              | ✗                 | 1             | ✗                         | Basic           |
| v2      | ✓              | ✗                 | 1             | ✗                         | Basic           |
| v3      | ✓              | ✗                 | 1             | ✗                         | Basic           |
| v4      | ✓              | ✓ (up to 5)       | 6             | ✓ (for additional)        | Per-secret      |
| v5      | ✓              | ✓ (up to 5)       | 6             | ✓ (for additional)        | Per-secret      |
| v6      | ✓              | ✓ (up to 5)       | 6             | ✓ (for additional)        | Per-secret      |
| v7      | ✓              | ✓ (up to 5)       | 6             | ✓ (for additional)        | Per-secret      |

## Version Recommendation Guide

**Choose v7 (Latest) if you need:**
- ECS.20 compliance — non-root container execution (HCC compliance scope)
- All v6 features plus hardened container runtime
- Container image already runs cleanly as UID 1000 (or you're prepared to override `ContainerUser`)

**Choose v6 if you need:**
- HCC Forward Proxy with separate prod/nprd proxy subnets
- ElastiCache Redis connectivity from batch jobs
- SES SMTP egress for email notifications
- Step Functions orchestration from batch jobs
- Container image cannot run as non-root and modifying it isn't feasible right now

**Choose v5 if you need:**
- Extended VPC CIDR support (up to 5) without v6 breaking changes
- Stable proxy configuration using BCS Proxy (yes/no)

**Choose v4 if you need:**
- Multiple external service integrations requiring separate credentials
- Better secret isolation and independent rotation
- Granular IAM permissions for different secrets
- Customizable environment variable names for secrets
- Custom environment variables for application configuration
- Consistency with ECS service patterns
- Multi-service architecture with various API keys

**Choose v3 if you need:**
- Flexible S3 monitoring (prefix-specific OR bucket-wide)
- Resource tagging for governance
- Simple single-secret configuration
- Legacy compatibility

**Choose v2 if you need:**
- SNS notifications
- Basic secret management
- Stable production deployment without latest features

For detailed changes, refer to the respective `README.md` files in the `v1`, `v2`, `v3`, `v4`, `v5`, `v6`, and `v7` directories.
