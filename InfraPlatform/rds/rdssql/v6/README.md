# Amazon RDS SQL Server Infrastructure Template v6

This CloudFormation template provides enterprise-ready Microsoft SQL Server RDS infrastructure with advanced security, monitoring, and high availability features. The template supports both SQL Server Standard Edition (SE) and Enterprise Edition (EE) with comprehensive configuration options.

## Architecture Overview

This template creates a complete SQL Server RDS infrastructure including:

### Core Database Resources
- **RDS SQL Server Instance**: Multi-AZ or single-AZ deployment with configurable instance class and storage
- **DB Subnet Group**: Multi-AZ subnet configuration for high availability
- **DB Parameter Group**: Optimized SQL Server parameters with configurable memory settings
- **Option Group**: Support for Transparent Data Encryption (TDE) and other SQL Server features

### Security and Encryption
- **KMS Encryption Keys**: Separate keys for RDS encryption and performance monitoring with automatic rotation
- **Security Groups**: Granular network access control with support for multiple VPC CIDRs and prefix lists
- **IAM Roles**: Least-privilege access for monitoring, audit logging, and S3 backup operations

### Storage and Backup
- **S3 Buckets**: Dedicated buckets for audit logs and native SQL Server backups
- **Storage Auto-scaling**: Configurable storage with automatic scaling capabilities
- **Backup Configuration**: Automated backups with customizable retention periods

### Monitoring and Alerting
- **CloudWatch Alarms**: Comprehensive monitoring for CPU, connections, latency, and storage
- **Performance Insights**: Enhanced monitoring for SQL Server performance analysis
- **SNS Integration**: Configurable alerting through SNS topics

### Parameter Store Integration
- **Connection Details**: Automatic storage of database connection information in SSM Parameter Store
- **Configuration Management**: Centralized parameter management for applications

## Template Parameters

### Application & Feature Toggles

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `AppShortName` | String | Short name for the application | `myapp` |
| `EnvName` | String | Environment name | `nprd`, `prod`, `prod-a` |
| `CreateEnhancedMonitoringLogGroups` | String (`true`/`false`) | Toggle creation of CloudWatch log groups for RDS monitoring | `true` |
| `CreateEventSubscriptions` | String (`true`/`false`) | Toggle creation of RDS event subscription resources | `true` |
| `UseExistingParameterGroup` | String (`true`/`false`) | Use an existing DB parameter group | `false` |
| `ExistingParameterGroupName` | String | Name of existing parameter group | `""` |
| `KMSKeyRotationPeriod` | Number | KMS key rotation period (days) | `365` |

### Network Configuration

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `VpcId` | AWS::EC2::VPC::Id | Target VPC for deployment | `vpc-0d99a0c727b301d67` |
| `AvailabilityZone` | AWS::EC2::AvailabilityZone::Name | Primary availability zone | `ap-southeast-1a` |
| `VPCSubnetCidrAppAZ1` | String | Application subnet CIDR for AZ1 | `10.1.128.0/20` |
| `VPCSubnetCidrAppAZ2` | String | Application subnet CIDR for AZ2 | `10.1.144.0/20` |
| `VPCSubnetCidrAppAZ3` | String | Application subnet CIDR for AZ3 | `10.1.160.0/20` |
| `DBSubnetCidrAZ1` | String | Database subnet CIDR for AZ1 | `10.1.0.0/20` |
| `DBSubnetCidrAZ2` | String | Database subnet CIDR for AZ2 | `10.1.16.0/20` |
| `DBSubnetCidrAZ3` | String | Database subnet CIDR for AZ3 | `10.1.32.0/20` |
| `DBSubnetIds` | List<AWS::EC2::Subnet::Id> | Database subnet IDs | `subnet-08170d48a795103d2,subnet-083fba964c347656f` |
| `VpcCidr1` | String | Primary VPC CIDR range | `10.0.0.0/16` |
| `VpcCidr2` | String | Secondary VPC CIDR range (optional) | `10.1.0.0/16` |
| `VpcCidr3` | String | Tertiary VPC CIDR range (optional) | `10.2.0.0/16` |
| `AdditionalAppPrefixList` | String | AWS Prefix List for additional networks | `pl-0abc123def456789` |
| `DeploymentServer` | String | Deployment server IP/CIDR | `10.53.26.197/32` |

### Event Subscription Logic

- Event subscription resources are now conditionally created using the parameters `CreateEventSubscriptions` and `RdsEventSNSTopicArn`.
- Combined conditions ensure resources are only created when both toggles are enabled and an SNS topic ARN is provided.
- See template `Conditions:` block for details.
## Template Parameters

### Application & Feature Toggles

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `AppShortName` | String | Short name for the application | `myapp` |
| `EnvName` | String | Environment name | `nprd`, `prod`, `prod-a` |
| `CreateEnhancedMonitoringLogGroups` | String (`true`/`false`) | Toggle creation of CloudWatch log groups for RDS monitoring | `true` |
| `CreateEventSubscriptions` | String (`true`/`false`) | Toggle creation of RDS event subscription resources | `true` |
| `UseExistingParameterGroup` | String (`true`/`false`) | Use an existing DB parameter group | `false` |
| `ExistingParameterGroupName` | String | Name of existing parameter group | `""` |
| `KMSKeyRotationPeriod` | Number | KMS key rotation period (days) | `365` |

### Network Configuration

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `VpcId` | AWS::EC2::VPC::Id | Target VPC for deployment | `vpc-0d99a0c727b301d67` |
| `AvailabilityZone` | AWS::EC2::AvailabilityZone::Name | Primary availability zone | `ap-southeast-1a` |
| `VPCSubnetCidrAppAZ1` | String | Application subnet CIDR for AZ1 | `10.1.128.0/20` |
| `VPCSubnetCidrAppAZ2` | String | Application subnet CIDR for AZ2 | `10.1.144.0/20` |
| `VPCSubnetCidrAppAZ3` | String | Application subnet CIDR for AZ3 | `10.1.160.0/20` |
| `DBSubnetCidrAZ1` | String | Database subnet CIDR for AZ1 | `10.1.0.0/20` |
| `DBSubnetCidrAZ2` | String | Database subnet CIDR for AZ2 | `10.1.16.0/20` |
| `DBSubnetCidrAZ3` | String | Database subnet CIDR for AZ3 | `10.1.32.0/20` |
| `DBSubnetIds` | List<AWS::EC2::Subnet::Id> | Database subnet IDs | `subnet-08170d48a795103d2,subnet-083fba964c347656f` |
| `VpcCidr1` | String | Primary VPC CIDR range | `10.0.0.0/16` |
| `VpcCidr2` | String | Secondary VPC CIDR range (optional) | `10.1.0.0/16` |
| `VpcCidr3` | String | Tertiary VPC CIDR range (optional) | `10.2.0.0/16` |
| `AdditionalAppPrefixList` | String | AWS Prefix List for additional networks | `pl-0abc123def456789` |
| `DeploymentServer` | String | Deployment server IP/CIDR | `10.53.26.197/32` |

### Event Subscription Logic

- Event subscription resources are now conditionally created using the parameters `CreateEventSubscriptions` and `RdsEventSNSTopicArn`.
 Combined conditions ensure resources are only created when both toggles are enabled and an SNS topic ARN is provided.
 See template `Conditions:` block for details.
| `S3PrefixListId` | String | S3 service prefix list ID | `pl-6fa54006` |
| `HCCVpceCidr` | String | HCC VPC Endpoint subnet CIDR | `10.48.42.0/24` |

### Database Configuration

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `MultiAZ` | String | Enable Multi-AZ deployment | `true`, `false` |
| `DBEngine` | String | SQL Server engine edition | `sqlserver-se`, `sqlserver-ee` |
| `DBMajorEngineVersion` | String | SQL Server major version | `16.00` |
| `EngineVersion` | String | Complete SQL Server version | `16.00.4095.4.v1` |
| `DBInstanceClass` | String | RDS instance class | `db.m6i.xlarge` |
| `RdsDBParameterGroupFamily` | String | Parameter group family | `sqlserver-ee-16.0` |
| `MasterUsernameDev` | String | Master username for non-prod | `dbadmin` |
| `MasterUserPasswordDev` | String | Master password for non-prod | `dbadmin123` |
| `ProdDBPort` | String | Database port for production | `53341` |
| `NProdDBPort` | String | Database port for non-production | `53331` |

### Storage Configuration

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `AllocatedStorage` | String | Initial storage allocation (GiB) | `100` |
| `RDSMaxAllocatedStorage` | String | Maximum storage for auto-scaling (GiB) | `1000` |
| `StorageType` | String | Storage type | `gp3` |
| `StorageIops` | String | Provisioned IOPS | `3000` |
| `RdsFreeStorageThresholdBytes` | String | Low storage alarm threshold (bytes) | `21474836480` |

### Advanced Configuration

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `UseExistingOptionGroup` | String | Use existing option group | `true`, `false` |
| `ExistingOptionGroupName` | String | Name of existing option group | `my-option-group` |
| `OptionGroupEnableTDE` | String | Enable Transparent Data Encryption | `true`, `false` |
| `ParameterGroupMaxServerMemoryMB` | String | Max server memory in MB | `204800` |
| `KMSKeyRotationPeriod` | Number | KMS key rotation period (days) | `365` |

### Monitoring Configuration

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `RdsEventSNSTopicArn` | String | SNS topic for RDS event notifications | `arn:aws:sns:ap-southeast-1:123456789012:rds-events` |

## Deployment Guide

### Prerequisites

1. **VPC Infrastructure**: Ensure your VPC and subnets are properly configured
2. **IAM Permissions**: Verify CloudFormation deployment permissions
3. **KMS Permissions**: Ensure permissions for KMS key creation and management
4. **SNS Topic**: Create SNS topic for RDS event notifications (optional)

### Deployment Steps

1. **Parameter Configuration**
   ```bash
   # Copy the parameters template
   cp parameters.json.template parameters.json
   
   # Update parameters.json with your environment-specific values
   ```

2. **Template Validation**
   ```bash
   aws cloudformation validate-template --template-body file://cf-rds-sql.yaml
   ```

3. **Stack Deployment**
   ```bash
   aws cloudformation create-stack \
     --stack-name my-app-rds-sql \
     --template-body file://cf-rds-sql.yaml \
     --parameters file://parameters.json \
     --capabilities CAPABILITY_IAM
   ```

4. **Verify Deployment**
   ```bash
   aws cloudformation describe-stacks --stack-name my-app-rds-sql
   ```

### Post-Deployment Configuration

1. **Database Connection**: Retrieve connection details from SSM Parameter Store
2. **Monitoring Setup**: Verify CloudWatch alarms are properly configured
3. **Security Groups**: Review and adjust security group rules if needed
4. **Backup Verification**: Confirm automated backup settings

## Key Features in v6

### Enhanced CloudWatch Monitoring
- **CPU Utilization Monitoring**: Configurable threshold (default: 80%)
- **Database Connection Monitoring**: Track active connections (default threshold: 500)
- **Storage Monitoring**: Low storage space alerts with configurable thresholds
- **Latency Monitoring**: Read/write latency tracking (default threshold: 0.05s)
- **Queue Depth Monitoring**: Disk queue monitoring (default threshold: 5)

### Advanced Security Features
- **Transparent Data Encryption (TDE)**: Optional at-rest encryption for SQL Server
- **KMS Key Rotation**: Automatic key rotation with configurable periods
- **Dual KMS Keys**: Separate keys for RDS encryption and monitoring data
- **Enhanced Network Security**: Support for multiple VPC CIDRs and prefix lists

### Storage and Performance
- **Storage Auto-scaling**: Automatic storage scaling based on usage
- **GP3 Storage Support**: Latest generation storage with configurable IOPS
- **Performance Insights**: Enhanced monitoring for SQL Server performance
- **Configurable Memory Settings**: Custom max server memory configuration

### Multi-Environment Support
- **Environment-based Configuration**: Different ports and settings per environment
- **Consolidated CIDR Support**: Shared RDS instances across multiple environments
- **Prefix List Integration**: Flexible network access control

## Configuration Notes

### SQL Server Edition Selection
- **Standard Edition (`sqlserver-se`)**: Cost-effective for most workloads
- **Enterprise Edition (`sqlserver-ee`)**: Advanced features including TDE, advanced analytics

### Storage Sizing Guidelines
- **Initial Storage**: Start with 100-500 GiB based on expected data size
- **Max Auto-scaling**: Set 2-3x initial storage for growth headroom
- **IOPS Configuration**: GP3 allows independent IOPS scaling (3,000-16,000 IOPS)

### Memory Configuration
- **Max Server Memory**: Should be 70-80% of instance RAM
- **Instance Class Selection**: Choose based on CPU and memory requirements
- **Example**: `db.m6i.xlarge` (4 vCPU, 16 GiB RAM) → Max Memory ~12,800 MB

### Network Security Best Practices
- **Database Ports**: Use non-standard ports for additional security
- **CIDR Ranges**: Implement least-privilege network access
- **Prefix Lists**: Use prefix lists for complex network configurations

### Backup and Disaster Recovery
- **Multi-AZ Deployment**: Recommended for production workloads
- **Automated Backups**: Configured with appropriate retention periods
- **S3 Native Backups**: Additional backup capability for SQL Server

## Troubleshooting

### Common Issues

1. **Parameter Group Conflicts**
   - Ensure parameter group family matches SQL Server version
   - Verify max server memory doesn't exceed instance capacity

2. **Network Connectivity**
   - Check security group rules and CIDR configurations
   - Verify subnet group spans multiple AZs for Multi-AZ deployments

3. **Storage Issues**
   - Monitor CloudWatch alarms for storage space
   - Verify auto-scaling configuration is appropriate

4. **TDE Configuration**
   - Ensure Enterprise Edition is selected for TDE
   - Verify option group configuration is correct

### Monitoring and Diagnostics
- **CloudWatch Logs**: Monitor RDS error logs for issues
- **Performance Insights**: Use for query-level performance analysis
- **SNS Notifications**: Configure for proactive issue detection

---

## New Features in v6

### Enhanced CloudWatch Monitoring and Alerting
This version includes comprehensive CloudWatch alarms for monitoring RDS performance and health:
- **CPU Utilization Alarm**: Monitors high CPU usage (threshold: 80%)
- **Database Connections Alarm**: Monitors high database connections (threshold: 500)
- **Queue Depth Alarm**: Monitors high disk queue depth (threshold: 5)
- **Write Latency Alarm**: Monitors high write latency (threshold: 0.05 seconds)
- **Read Latency Alarm**: Monitors high read latency (threshold: 0.05 seconds)
- **Low Storage Alarm**: Monitors low free storage space (configurable threshold via `RdsFreeStorageThresholdBytes`)

All alarms are configured to send notifications to the specified SNS topic (`RdsEventSNSTopicArn`).

### Transparent Data Encryption (TDE) Support
- Optional TDE encryption can be enabled via the `OptionGroupEnableTDE` parameter
- When enabled, provides additional encryption for SQL Server databases

### Advanced Network Configuration
- Support for multiple VPC CIDR ranges (`VpcCidr1`, `VpcCidr2`, `VpcCidr3`)
- S3 Prefix List support for secure S3 access (`S3PrefixListId`)
- HCC VPC Endpoint subnet configuration (`HCCVpceCidr`)

### Parameter Group Enhancements
- Configurable max server memory for SQL Server instances (`ParameterGroupMaxServerMemoryMB`)
- Automatic parameter group family selection based on engine version

### Enhanced Security and Encryption
- Automatic KMS key rotation with configurable period (`KMSKeyRotationPeriod`)
- Separate KMS keys for RDS encryption and monitoring encryption
- Enhanced security group rules for granular network access control

---

## New Features

### Consolidated CIDR Ranges
Support for consolidated CIDR ranges for application subnets allows multiple environments to share the same RDS instance while maintaining proper network access.

### Storage Monitoring Configuration
The `RdsFreeStorageThresholdBytes` parameter allows you to configure the threshold for low storage alerts:
- **Default Value**: 21474836480 bytes (20 GB)
- **Purpose**: Triggers CloudWatch alarm when free storage space falls below this threshold
- **Format**: Value must be specified in bytes
- **Example Values**:
  - 10 GB = 10737418240 bytes
  - 20 GB = 21474836480 bytes (default)
  - 50 GB = 53687091200 bytes

### Prefix List Support
Specify an optional AWS Prefix List ID for additional application networks. This allows access from multiple network ranges without modifying the template. Create a prefix list in your AWS account with the required CIDR ranges, then specify the prefix list ID in the `AdditionalAppPrefixList` parameter.

---

---

## Important Notes for v6

### CloudFormation Template Fixes
- **Fixed**: Removed invalid `Tags` property from `RDSEncryptionKmsKeyAlias` resource (AWS::KMS::Alias does not support Tags)
- **Fixed**: Corrected YAML formatting issues in template structure
- **Enhanced**: Improved error handling and resource dependencies

### Breaking Changes
- **New Required Parameters**: Several new parameters have been added that may require updates to existing parameter files
- **Enhanced Security**: Additional security group rules and network configurations may affect connectivity

### Migration from Previous Versions
When upgrading from v5 or earlier versions:
1. Review and update your parameter files to include new required parameters
2. Test connectivity after deployment due to enhanced security configurations
3. Update monitoring and alerting configurations to leverage new CloudWatch alarms
4. Consider enabling TDE encryption for enhanced data security

### Performance and Monitoring
- Enhanced monitoring provides better visibility into RDS performance
- New alarms help proactively identify performance issues
- Configurable thresholds allow customization based on workload requirements

---

## Read Replica Configuration

The template supports provisioning RDS Read Replicas for read scaling and disaster recovery scenarios.

### Read Replica Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `AppShortName` | String | Application short name | `myapp` |
| `EnvName` | String | Environment name | `nprd`, `prod` |
| `ReadReplicaRdsDBParameterGroupFamily` | String | Parameter group family for replica | `sqlserver-ee-16.0` |
| `DBEngine` | String | SQL Server engine edition | `sqlserver-se`, `sqlserver-ee` |
| `ReadReplicaDBInstanceClass` | String | Instance class for read replica | `db.m6i.large` |

### Read Replica Deployment

1. **Primary Database**: Deploy primary RDS instance first
2. **Parameter Configuration**: Update read replica parameters
3. **Replica Deployment**: Deploy read replica template
   ```bash
   aws cloudformation create-stack \
     --stack-name my-app-rds-sql-replica \
     --template-body file://cf-rds-sql-read-replica.yaml \
     --parameters file://read-replica-parameters.json
   ```

### Read Replica Features
- **Automatic Source Detection**: Reads source DB identifier from SSM Parameter Store
- **Independent Scaling**: Separate instance class for read workloads
- **Cross-AZ Support**: Can be deployed in different AZ from primary
- **Read-only Access**: Automatically configured for read-only operations

---

## Release Notes

## Version 6 (Current)
**Release Date**: 2024

### New Features
- **Enhanced CloudWatch Monitoring**: Added comprehensive monitoring with 6 different CloudWatch alarms
- **Transparent Data Encryption (TDE)**: Optional TDE support for SQL Server databases
- **Advanced Network Configuration**: Support for multiple VPC CIDRs and prefix lists
- **Configurable Storage Alerts**: Customizable low storage threshold monitoring
- **Parameter Group Enhancements**: Configurable max server memory settings
- **Enhanced Security**: Improved encryption with automatic KMS key rotation

### Bug Fixes
- Fixed invalid `Tags` property on KMS Alias resources
- Corrected YAML formatting issues in CloudFormation template
- Improved resource dependency management

### Breaking Changes
- Added multiple new required parameters
- Enhanced security configurations may affect existing connectivity

### Migration Guide
1. Update parameter files with new required parameters
2. Test connectivity after deployment
3. Configure CloudWatch alarm SNS topic
4. Review and adjust security group configurations

---

## v5 (2025-06-02)

- **Enhanced Parameterization:** Added support for consolidated CIDR ranges for application subnets, enabling multiple environments to share the same RDS instance with proper network access.
- **Prefix List Support:** Introduced the `AdditionalAppPrefixList` parameter to allow specifying AWS Prefix List IDs for additional application networks, improving flexibility and security.
- **Expanded Parameter Table:** Updated and clarified parameter tables for both primary RDS and Read Replica templates, including examples and allowed values.
- **Read Replica Improvements:** The Read Replica template now automatically references the source DB instance identifier from the SSM Parameter Store created by the primary RDS template.
- **Documentation Updates:** Improved instructions for provisioning both the primary RDS and Read Replica templates, and clarified the use of new features.
- **General Enhancements:** Minor formatting and consistency improvements throughout the documentation.

---