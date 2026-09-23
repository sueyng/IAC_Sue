# Release Notes: RDS SQL Server Infrastructure Templates

## Current Version: v6.1 (Production Ready)

The SQL Server RDS infrastructure templates provide enterprise-grade Microsoft SQL Server database solutions with comprehensive security, monitoring, and high availability features.

## Version Overview

| Version | Release Date | Status | Key Features |
|---------|--------------|--------|--------------|
| **v6.1** | **2026** | **Current/Stable** | **Expanded RDS Event Subscription Categories** |
| v6 | 2024 | Archived | TDE, Advanced Monitoring, Multi-VPC Support |
| v5 | 2023 | Archived | GP3 Storage, Prefix Lists, Enhanced Security |
| v4 | 2022 | Archived | Performance Insights, Hybrid Connectivity |
| v3 | 2021 | Archived | Read Replicas, Enhanced IAM |
| v2 | 2020 | Archived | Multi-AZ, KMS Encryption |
| v1 | 2019 | Archived | Basic RDS Implementation |

---

## Version 6 Features (Current Release)

### 🚀 Enhanced CloudWatch Monitoring
- **CPU Utilization Monitoring**: Configurable threshold-based alerting (default: 80%)
- **Database Connection Monitoring**: Active connection tracking (default threshold: 500)
- **Storage Space Monitoring**: Configurable low storage alerts with byte-level precision
- **Latency Monitoring**: Read/write latency tracking (default threshold: 0.05s)
- **Queue Depth Monitoring**: Disk I/O queue monitoring (default threshold: 5)
- **SNS Integration**: Centralized alarm notifications via SNS topics

### 🔐 Advanced Security Features
- **Transparent Data Encryption (TDE)**: Optional at-rest encryption for SQL Server Enterprise Edition
- **Dual KMS Encryption**: Separate keys for RDS data and monitoring encryption
- **Automatic Key Rotation**: Configurable KMS key rotation periods (default: 365 days)
- **Enhanced Network Security**: Multi-VPC CIDR support and AWS Prefix List integration
- **Granular Access Control**: Least-privilege security group configurations

### 🌐 Advanced Network Configuration
- **Multi-VPC Support**: Configure up to 3 different VPC CIDR ranges
- **AWS Prefix Lists**: Flexible network access control using managed prefix lists
- **HCC VPC Endpoints**: Specialized configuration for hybrid cloud connectivity
- **S3 Prefix List Integration**: Secure S3 access patterns for backup and audit operations
- **Consolidated CIDR Ranges**: Support for shared RDS instances across multiple environments

### ⚡ Performance and Storage Enhancements
- **GP3 Storage**: Latest generation storage with independent IOPS scaling
- **Storage Auto-scaling**: Automatic storage expansion based on usage patterns
- **Configurable Memory Management**: Custom max server memory settings for SQL Server
- **Performance Insights**: Enhanced monitoring with KMS-encrypted data
- **IOPS Flexibility**: Independent IOPS configuration (3,000-16,000 IOPS)

### 🗄️ Database Engine Support
- **SQL Server Editions**: Support for both Standard Edition (SE) and Enterprise Edition (EE)
- **Latest Engine Version**: SQL Server 2022 (16.00.4095.4.v1)
- **Parameter Group Optimization**: Version-specific parameter group families
- **Option Group Management**: Support for advanced SQL Server features and configurations

### 📊 Monitoring and Observability
- **CloudWatch Integration**: Comprehensive metrics and log exports
- **Enhanced Monitoring**: Detailed instance-level metrics with 1-second granularity
- **Custom Dashboards**: Pre-configured monitoring dashboards
- **Audit Logging**: Integrated S3-based audit log management
- **Performance Baselines**: Automated performance baseline establishment

---

## Version 6.1 Features (Current Release)

### 🔔 Expanded Event Subscription Coverage
- **`RdsInstanceEventSubscription`**: Added `maintenance` to the monitored event categories for `db-instance` (alongside `configuration change`, `failover`, `failure`, `low storage`, `recovery`, `restoration`).
- **`RdsSecurityGroupSubscription`**: Added `failure` to the monitored event categories for `db-security-group` (alongside `configuration change`).
- **KMS Key Rotation**: Confirmed `EnableKeyRotation: true` remains active on both `RDSEncryptionKmsKey` and `RDSmonitoringEncryptionKmsKey` (carried over from v6, no functional change).

---

## Technical Improvements in v6
### Conditional Event Subscription Logic (2025)
- Added parameters: `CreateEnhancedMonitoringLogGroups`, `CreateEventSubscriptions`, `UseExistingParameterGroup`, `ExistingParameterGroupName`, `KMSKeyRotationPeriod` for advanced toggling and configuration.
- Event subscription resources (SNS) are now conditionally created using combined conditions in the CloudFormation template.
- Updated `parameter-rds-sql.json` to include all new parameters for conditional logic and feature toggles.
- Improved documentation in README for new parameters and event subscription logic, including how to use combined conditions for resource creation.
- Ensured CloudFormation template uses only boolean conditions in `Fn::And` logic for compliance and reliability.

### CloudFormation Template Enhancements
- **Fixed Resource Dependencies**: Resolved invalid `Tags` property on KMS Alias resources
- **YAML Structure Improvements**: Corrected formatting and validation issues
- **Enhanced Error Handling**: Improved resource dependency management
- **Conditional Logic**: Better handling of optional features and configurations

### Parameter Management
- **Expanded Parameter Set**: 25+ configurable parameters for comprehensive customization
- **Parameter Validation**: Enhanced validation rules and constraints
- **Environment-Specific Configuration**: Separate settings for production and non-production
- **SSM Integration**: Automatic parameter store integration for application connectivity

### Deployment and Operations
- **Simplified Deployment**: Streamlined CloudFormation deployment process
- **Migration Support**: Comprehensive migration guide from previous versions
- **Testing Framework**: Built-in validation and testing capabilities
- **Documentation**: Enhanced README with deployment guides and troubleshooting

---

## Migration Information

### Upgrading from v6 to v6.1
1. **No Parameter Changes**: No new parameters are required; `CreateEventSubscriptions` and `RdsEventSNSTopicArn` continue to control event subscription creation.
2. **Event Category Review**: Existing `RdsEventSNSTopicArn` subscribers will start receiving `maintenance` notifications for `db-instance` and `failure` notifications for `db-security-group`.
3. **Testing**: Validate SNS notification delivery for the newly added event categories after upgrade.

### Upgrading from v5 to v6
1. **Parameter Updates**: Add new v6 parameters to your parameter files
2. **SNS Topic Configuration**: Set up SNS topic for CloudWatch alarm notifications
3. **Network Review**: Review enhanced security group configurations
4. **TDE Planning**: Consider enabling Transparent Data Encryption for enhanced security
5. **Testing**: Validate connectivity and performance after upgrade

### Breaking Changes in v6
- **New Required Parameters**: Several monitoring and security parameters are now required
- **Enhanced Security**: Stricter network access controls may affect existing connections
- **Engine Version**: Default version updated to SQL Server 2022
- **Resource Dependencies**: Updated CloudFormation dependencies may affect stack updates

### Compatibility Matrix
- **AWS Regions**: All commercial AWS regions
- **Instance Classes**: Support for latest generation instance types (M6i, R6i, etc.)
- **Storage Types**: GP3, GP2, IO1, IO2 storage types supported
- **Engine Versions**: SQL Server 2019, 2022 supported

---

## Historical Releases

### v6 (2024)
- TDE, advanced CloudWatch monitoring, and dual KMS encryption keys
- Multi-VPC CIDR support and AWS Prefix List integration
- Conditional RDS event subscriptions (db-instance, db-snapshot, db-parameter-group, db-security-group)

### v5 (2023)
- GP3 storage type support
- Prefix list network integration
- Enhanced parameterization for consolidated CIDR ranges
- Improved documentation and deployment guides

### v4 (2022)
- Performance Insights with encryption
- Hybrid connectivity enhancements
- Advanced option group management
- Engine version updates to SQL Server 2019

### v3 (2021)
- Read replica support introduction
- Enhanced IAM roles and policies
- Custom parameter group management
- Improved backup retention configuration

### v2 (2020)
- Multi-AZ deployment support
- KMS encryption for data at rest
- S3 bucket integration for audit and backup
- Enhanced security group management

### v1 (2019)
- Initial RDS SQL Server template
- Basic configuration and deployment
- Standard security and networking
- Foundation for future enhancements

---

## Support and Documentation

### Current Documentation
- **README.md**: Comprehensive deployment and configuration guide
- **Parameter Reference**: Detailed parameter descriptions and examples
- **Architecture Diagrams**: Visual representation of deployed infrastructure
- **Troubleshooting Guide**: Common issues and resolution steps

### Best Practices
- **Security**: Enable TDE for sensitive workloads
- **Monitoring**: Configure all CloudWatch alarms with appropriate thresholds
- **Networking**: Use prefix lists for complex network configurations
- **Storage**: Plan storage scaling based on workload growth patterns
- **Backup**: Implement comprehensive backup and disaster recovery strategies

For detailed configuration and deployment instructions, refer to the v6 README.md file.
    - Introduced `AdditionalAppPrefixList` parameter for additional application networks.

- **v6 Updates**:
  - **Enhanced CloudWatch Monitoring**:
    - Added 6 comprehensive CloudWatch alarms (CPU, Connections, Queue Depth, Write/Read Latency, Low Storage).
    - Configurable storage threshold monitoring via `RdsFreeStorageThresholdBytes`.
    - SNS integration for alarm notifications via `RdsEventSNSTopicArn`.
  - **Transparent Data Encryption (TDE)**:
    - Optional TDE support for SQL Server databases via `OptionGroupEnableTDE`.
  - **Advanced Network Configuration**:
    - Multiple VPC CIDR support (`VpcCidr1`, `VpcCidr2`, `VpcCidr3`).
    - S3 Prefix List integration via `S3PrefixListId`.
    - HCC VPC Endpoint subnet configuration via `HCCVpceCidr`.
  - **Parameter Group Enhancements**:
    - Configurable max server memory for SQL Server via `ParameterGroupMaxServerMemoryMB`.
  - **Enhanced Security and Encryption**:
    - Automatic KMS key rotation with configurable period via `KMSKeyRotationPeriod`.
    - Separate KMS keys for RDS and monitoring encryption.
  - **Bug Fixes**:
    - Fixed invalid `Tags` property on KMS Alias resources.
    - Corrected YAML formatting issues in CloudFormation template.
    - Improved resource dependency management.

### Deployment Flow Updates
- **v2 Updates**:
  - Introduced a deployment order:
    1. Deploy security groups.
    2. Deploy KMS keys and IAM roles.
    3. Deploy RDS instance.

- **v5 Updates**:
  - Enhanced deployment documentation for hybrid connectivity and gp3 storage configurations.

- **v6 Updates**:
  - Added deployment considerations for CloudWatch alarms and SNS topic configuration.
  - Enhanced parameter validation and error handling.

### Documentation Updates
- **v2 Updates**:
  - Added detailed descriptions for new parameters (`MultiAZ`, `RDSEncryptionKmsKey`, `DBAuditS3Bucket`).
  - Updated troubleshooting guide for common issues with KMS encryption and S3 configurations.

- **v5 Updates**:
  - Enhanced deployment guide with examples for hybrid connectivity and gp3 storage configurations.

- **v6 Updates**:
  - Comprehensive README updates with all new parameters and features.
  - Added migration guide from previous versions.
  - Enhanced documentation for CloudWatch monitoring and alerting.
  - Added storage threshold configuration examples and byte-to-GB conversion guide.

## Summary of Key Changes
| Feature/Component         | v1                                   | v2                                   | v3                                   | v4                                   | v5                                   | v6                                   |
|---------------------------|---------------------------------------|---------------------------------------|---------------------------------------|---------------------------------------|---------------------------------------|---------------------------------------|
| IaC Version               | InfraPlatform-rdssql-v1              | InfraPlatform-rdssql-v2              | InfraPlatform-rdssql-v3              | InfraPlatform-rdssql-v4              | InfraPlatform-rdssql-v5              | InfraPlatform-rdssql-v6              |
| Multi-AZ Deployment       | Not supported                        | Supported                            | Supported                            | Supported                            | Supported                            | Supported                            |
| Read Replica              | Not supported                        | Not supported                        | Supported                            | Supported                            | Supported                            | Supported                            |
| KMS Key Rotation          | Not supported                        | Supported                            | Supported                            | Supported                            | Supported                            | Enhanced (Configurable Period)      |
| Storage Type              | gp2                                  | gp2                                  | gp2                                  | gp2                                  | gp3                                  | gp3                                  |
| Performance Insights      | Not supported                        | Not supported                        | Supported                            | Enhanced                             | Enhanced                             | Enhanced                             |
| Backup Retention          | Fixed (7 days)                       | Configurable                         | Configurable                         | Configurable                         | Configurable                         | Configurable                         |
| Engine Version            | 14.x                                 | 14.x                                 | 15.x                                 | 15.00.4316.3.v1                      | 15.00.4316.3.v1                      | 16.00.4095.4.v1 (Updated)           |
| CloudWatch Monitoring     | Basic                                | Basic                                | Basic                                | Basic                                | Enhanced                             | Comprehensive (6 Alarms)            |
| TDE Support               | Not supported                        | Not supported                        | Not supported                        | Not supported                        | Not supported                        | Supported                            |
| Network Configuration     | Basic                                | Enhanced                             | Enhanced                             | Enhanced                             | Enhanced                             | Advanced (Multi-VPC, Prefix Lists)  |
| Storage Monitoring        | Not available                        | Not available                        | Not available                        | Not available                        | Not available                        | Configurable Thresholds              |

## Latest Release Details

### v6 (2025-06-19)

#### New Features
- **Comprehensive CloudWatch Monitoring**: Added 6 specialized CloudWatch alarms for proactive monitoring
- **Transparent Data Encryption (TDE)**: Optional TDE support for enhanced data security
- **Advanced Network Configuration**: Multi-VPC CIDR support and prefix list integration
- **Configurable Storage Alerts**: Customizable low storage threshold monitoring
- **Parameter Group Enhancements**: Configurable max server memory settings
- **Enhanced Security**: Automatic KMS key rotation with configurable periods

#### Bug Fixes
- Fixed invalid `Tags` property on AWS::KMS::Alias resources
- Corrected YAML formatting issues in CloudFormation template
- Improved resource dependency management and error handling

#### Breaking Changes
- Multiple new required parameters added
- Enhanced security configurations may affect existing connectivity
- Updated default engine version to 16.00.4095.4.v1

#### Migration Guide
1. Update parameter files with new required parameters
2. Configure CloudWatch alarm SNS topic
3. Test connectivity after deployment
4. Review and adjust security group configurations

For detailed changes, refer to the respective `README.md` files in the `v1`, `v2`, `v3`, `v4`, `v5`, and `v6` directories.