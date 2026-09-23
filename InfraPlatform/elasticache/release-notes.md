# Release Notes: ElastiCache Infrastructure Templates

## Version Comparison: v1 vs v2 vs v3 vs v4

### General Updates
- **IaC Version Tag**:
  - Updated from `InfraPlatform-ElastiCache-v1` to `InfraPlatform-ElastiCache-v3`.

### Core Infrastructure (`cf-elasticache.yaml`)
- **v2 Updates**:
  - Added support for **CloudWatch Logs**:
    - Enabled slow-log and engine-log delivery to CloudWatch.
  - Enhanced **Security Group Rules**:
    - Added conditional rules for multi-AZ deployments.
  - Improved **Subnet Configuration**:
    - Added support for `AppSubnetIds` for better flexibility.
  - Updated **Redis Engine**:
    - Default engine version updated to `7.0`.

- **v3 Updates**:
  - Enhanced **Logging**:
    - Added support for JSON log format in CloudWatch.
  - Improved **Security Policies**:
    - Enforced TLS v1.2 for all connections.
  - Enhanced **Replication Group**:
    - Added support for `LogDeliveryConfigurations` for slow-log and engine-log.
  - Updated **IAM Tags**:
    - Added `IaCVersion` tag for better resource tracking.
  - Added **Valkey Support**:
    - Introduced template for Valkey engine (`cf-elasticache-valkey.yaml`).
    - Support for Valkey 8.0 engine version.
    - Parameter group support for `default.valkey8.cluster.on`.

- **v4 Updates**:
  - **Enhanced Network Security**:
    - Added `AdditionalAppPrefixList` parameter for flexible additional application network access.
    - Standardized security group rules across all ElastiCache templates.
    - Extended VPC CIDR support from 3 to 5 ranges (added `VpcCidr4` and `VpcCidr5`) for multi-VPC peering, hybrid cloud connectivity, and cross-region networking patterns.
  - **Improved Template Consistency**:
    - Consistent prefix list support across serverless and instance-based templates.
    - Enhanced parameter documentation and examples.

### Serverless Infrastructure (`cf-elasticache-serverless.yaml`)
- **v2 Updates**:
  - Introduced **Serverless Cache**:
    - Added support for Redis serverless deployments.
    - Configurable parameters for `MaxCacheDataStorage` and `MaxCacheECPUPerSecond`.
  - Added **User and User Group Management**:
    - Support for creating Redis users and user groups.
  - Enhanced **Snapshot Management**:
    - Added parameters for `SnapshotRetentionLimit` and `DailySnapshotTime`.

- **v3 Updates**:
  - Enhanced **Security Group Rules**:
    - Added support for `HCCVpceCidr` for hybrid connectivity.
    - Improved conditional rules for S3 VPC endpoint access.
  - Improved **Cache Usage Limits**:
    - Enhanced configuration for `MaxCacheDataStorage` and `MaxCacheECPUPerSecond`.
  - Updated **IAM Policies**:
    - Enhanced permissions for serverless cache access.

- **v4 Updates**:
  - **Enhanced Network Configuration**:
    - Added prefix list-based access controls for additional application networks.
    - Maintained backward compatibility with existing subnet-based configurations.
    - Extended VPC CIDR support from 3 to 5 ranges (added `VpcCidr4` and `VpcCidr5`) for multi-VPC peering, hybrid cloud connectivity, and cross-region networking patterns.
  - **Consistent Security Patterns**:
    - Standardized security group configurations across serverless and instance-based deployments.
    - Added conditional prefix list support for enhanced network security.
    - Added managed policies for connecting to serverless cache.
  - Added **Valkey Serverless Support**:
    - Introduced template for Valkey serverless deployments (`cf-elasticache-serverless-valkey.yaml`).
    - Support for Valkey serverless with equivalent configuration options to Redis serverless.
    - Valkey user and user group management.

### Valkey Infrastructure
- **v3 Introductions**:
  - **Instance-based Valkey** (`cf-elasticache-valkey.yaml`):
    - Support for Valkey 8.0 engine with traditional instance deployments.
    - Enhanced security with TLS encryption (transit and at-rest).
    - CloudWatch integration with JSON log format for slow-log and engine-log.
    - Multi-AZ support with primary and replica nodes.
  - **Serverless Valkey** (`cf-elasticache-serverless-valkey.yaml`):
    - Fully managed serverless deployment option for Valkey.
    - Configurable cache usage limits and ECPU settings.
    - IAM authentication support with user and user group management.
    - Enhanced security group rules for hybrid connectivity.

### Deployment Flow Updates
- **v2 Updates**:
  - Introduced a deployment order:
    1. Deploy security groups.
    2. Deploy ElastiCache resources.
    3. Configure CloudWatch logging.

- **v3 Updates**:
  - Enhanced deployment documentation for hybrid connectivity and serverless cache configurations.

### Documentation Updates
- **v2 Updates**:
  - Added detailed descriptions for new parameters (`MaxCacheDataStorage`, `SnapshotRetentionLimit`, `DailySnapshotTime`).
  - Updated troubleshooting guide for common issues with serverless cache.

- **v3 Updates**:
  - Enhanced deployment guide with examples for hybrid connectivity and S3 endpoint configurations.
  - Added Valkey-specific documentation and configuration examples.
  - Migration guidelines for moving from Redis to Valkey deployments.

- **v4 Updates**:
  - Enhanced network configuration documentation with prefix list examples.
  - Updated security best practices to include both subnet-based and prefix list-based access control.
  - Added troubleshooting guide for prefix list configurations across all templates.

## Summary of Key Changes
| Feature/Component         | v1                                   | v2                                   | v3                                   | v4                                   |
|---------------------------|---------------------------------------|---------------------------------------|---------------------------------------|---------------------------------------|
| IaC Version               | InfraPlatform-ElastiCache-v1         | InfraPlatform-ElastiCache-v2         | InfraPlatform-ElastiCache-v3         | InfraPlatform-ElastiCache-v4         |
| CloudWatch Logs           | Not supported                        | Slow-log and engine-log              | JSON log format                      | JSON log format                      |
| Serverless Cache          | Not supported                        | Supported                            | Enhanced with hybrid connectivity    | Enhanced with hybrid connectivity    |
| Security Group Rules      | Basic                                | Multi-AZ support                     | S3 VPC endpoint and hybrid connectivity | **Enhanced with standardized prefix lists** |
| Additional Networks       | Not supported                        | Not supported                        | Prefix list support (serverless only) | **Prefix list support (all templates)** |
| VPC CIDR Range Support    | VpcCidr1/2/3                         | VpcCidr1/2/3                         | VpcCidr1/2/3                         | **VpcCidr1/2/3/4/5**                 |
| Redis Engine Version      | 6.x                                  | 7.0                                  | 7.0                                  | 7.0                                  |
| Snapshot Management       | Not supported                        | Supported                            | Supported                            | Supported                            |
| Valkey Support            | Not supported                        | Not supported                        | Instance-based and Serverless        | Instance-based and Serverless        |
| Valkey Engine Version     | Not supported                        | Not supported                        | 8.0                                  | 8.0                                  |
| Network Configuration     | Basic subnet-based                   | Enhanced multi-AZ                    | Prefix lists + hybrid connectivity  | **Enhanced with standardized prefix lists** |
| Parameter Table Consistency | Not included                       | Not included                         | Improved across all templates        | Consistent across all templates      |

For detailed changes, refer to the respective `README.md` files in the `v1`, `v2`, `v3`, and `v4` directories.