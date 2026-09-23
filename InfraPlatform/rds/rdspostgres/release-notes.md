# Release Notes: PostgreSQL Infrastructure Templates

## Version 5.2 (Latest) - May 2026

### Template: `cf-rds-postgres.yaml`

#### Changes from v5.1
- **Extended DB Subnet CIDR Support**: Added optional DB subnet CIDR parameters for AZ4, AZ5, and AZ6, completing full parity with the existing application subnet AZ1–6 pattern

#### New Parameters Added (v5.2)
- **`DBSubnetCidrAZ4`**: Database Subnet CIDR for AZ4
  - Type: String, Default: "" (empty)
  - Purpose: Optional administrative access from AZ4
  - Conditionally applied when provided
  - Example: "10.1.4.0/28"

- **`DBSubnetCidrAZ5`**: Database Subnet CIDR for AZ5
  - Type: String, Default: "" (empty)
  - Purpose: Optional administrative access from AZ5
  - Conditionally applied when provided
  - Example: "10.1.5.0/28"

- **`DBSubnetCidrAZ6`**: Database Subnet CIDR for AZ6
  - Type: String, Default: "" (empty)
  - Purpose: Optional administrative access from AZ6
  - Conditionally applied when provided
  - Example: "10.1.6.0/28"

#### Enhanced Security Group Features (v5.2)
- **Full 6-AZ DB Subnet Coverage**:
  - **Database Subnets**: DBSubnetCidrAZ1–6 for administrative access (AZ1/2 always applied; AZ3–6 conditional)
  - **Application Subnets**: VPCSubnetCidrAppAZ1–6 unchanged
  - All other ingress/egress rules unchanged from v5.1

- **New Conditions**:
  - `HasDBSubnetCidrAZ4`, `HasDBSubnetCidrAZ5`, `HasDBSubnetCidrAZ6` — mirrors the existing `HasDBSubnetCidrAZ3` pattern

#### Migration and Compatibility (v5.2)
- **100% Backward Compatible**: All existing v5.1 deployments unaffected; new parameters default to empty
- **Zero Breaking Changes**: Existing stacks continue operating normally without any parameter changes

#### IaC Version Update
- **Updated Tag**: `InfraPlatform-rdspostg-v5.2`
- **Template Location**: `InfraPlatform/rds/rdspostgres/v5.2/`

---

## Version 5.1 - April 2026

### Template: `cf-rds-postgres.yaml`

#### Major Changes from v5.0
- **Enhanced Network Flexibility Integration**: Combined modern V5 architecture with proven V3.1 network features
- **Database Subnet Access Support**: Integrated database subnet CIDR parameters for administrative access
- **Additional Application Networks**: Added prefix list support for extended network connectivity
- **Comprehensive Parameter Documentation**: Enhanced parameter files with both JSON and YAML formats
- **Unified Architecture**: Best of both V5 (modern infrastructure) and V3.1 (network flexibility)

#### New Parameters Added (v5.1)
- **`DBSubnetCidrAZ1`**: Database Subnet CIDR for AZ1
  - Type: String, Default: "" (empty)
  - Purpose: Administrative and monitoring tool access from AZ1
  - Example: "10.1.2.16/28"

- **`DBSubnetCidrAZ2`**: Database Subnet CIDR for AZ2
  - Type: String, Default: "" (empty)
  - Purpose: Administrative and monitoring tool access from AZ2
  - Example: "10.1.2.0/28"

- **`DBSubnetCidrAZ3`**: Database Subnet CIDR for AZ3
  - Type: String, Default: "" (empty)
  - Purpose: Optional administrative access from AZ3
  - Conditionally applied when provided

- **`AdditionalAppPrefixList`**: Additional Application Networks Prefix List
  - Type: String, Default: "" (empty)
  - Purpose: Flexible network access via AWS managed prefix lists
  - Supports additional application networks beyond standard app subnets

#### Enhanced Security Group Features (v5.1)
- **Multi-Layer Network Access**:
  - **Application Subnets**: VPCSubnetCidrAppAZ1-6 (supports up to 6 AZs)
  - **Database Subnets**: DBSubnetCidrAZ1-3 for administrative access
  - **Extended Networks**: AdditionalAppPrefixList for prefix list-based access
  - **VPC CIDR Ranges**: VpcCidr1-5 for complex network topologies
  - **Deployment Server**: Dedicated deployment server access

- **Advanced Conditional Logic**:
  - Added `HasDBSubnetCidrAZ3` and `HasAdditionalAppPrefixList` conditions
  - Backward compatible with all existing V5 deployments
  - Optional parameters ensure zero breaking changes

#### Architecture Benefits (v5.1)
- **Best of Both Worlds**: 
  - V5 modern infrastructure (6 AZ support, 5 VPC CIDRs, enhanced monitoring)
  - V3.1 proven network flexibility (DB subnet access, prefix list support)
  - Combined without architecture conflicts or breaking changes

- **Network Versatility**:
  - Application layer connectivity through standard app subnets
  - Database administration through DB subnet access
  - Extended connectivity via prefix lists
  - Multi-VPC and hybrid cloud support

#### Parameter File Enhancements (v5.1)
- **Dual Format Support**:
  - Enhanced JSON parameter file with DB subnet and prefix list parameters
  - New YAML parameter file with comprehensive inline documentation
  - Quick start guide and parameter reference in YAML format
  - Ready-to-deploy examples with proper defaults

- **Documentation Integration**:
  - Updated README.md with complete parameter descriptions
  - Enhanced usage guidelines and deployment instructions
  - Parameter reference table with examples and requirements

#### Migration and Compatibility (v5.1)
- **100% Backward Compatible**: All existing V5 deployments unaffected
- **Incremental Adoption**: New parameters are optional with empty defaults
- **Zero Breaking Changes**: Existing stacks continue operating normally
- **Progressive Enhancement**: Teams can adopt new networking features gradually

#### IaC Version Update
- **Updated Tag**: `InfraPlatform-rdspostg-v5.1`
- **Template Location**: `InfraPlatform/rds/rdspostgres/v5.1/`

---

## Version 3.1 - March 2026

### Template: `cf-rds-postgres.yaml`

#### Major Changes from v3.0
- **Enhanced Security Group Configuration**: Extended inbound access patterns to align with RDS SQL v6 template
- **Database Subnet Access**: Added support for database subnet CIDR ranges for administrative access
- **Flexible Network Access**: Added optional prefix list support for additional application networks
- **Parameter Alignment**: Updated parameter file with all required parameters for enhanced networking

#### New Parameters Added (v3.1)
- **`DBSubnetCidrAZ1`**: Database Subnet CIDR for AZ1
  - Type: String
  - Default: "" (empty string)
  - **Required**: CIDR range for database administration access from AZ1
  - Example: "10.1.2.16/28"

- **`DBSubnetCidrAZ2`**: Database Subnet CIDR for AZ2  
  - Type: String
  - Default: "" (empty string)
  - **Required**: CIDR range for database administration access from AZ2
  - Example: "10.1.2.0/28"

- **`DBSubnetCidrAZ3`**: Database Subnet CIDR for AZ3
  - Type: String
  - Default: "" (empty string)
  - **Optional**: CIDR range for database administration access from AZ3
  - Conditionally applied when provided

- **`AdditionalAppPrefixList`**: Additional Application Networks Prefix List
  - Type: String  
  - Default: "" (empty string)
  - **Optional**: Prefix List ID for additional application networks
  - Provides flexible network access through AWS managed prefix lists

#### Enhanced Security Group Features (v3.1)
- **Extended Inbound Rules**: 
  - **App Subnet Access**: VPCSubnetCidrAppAZ1/2/3 (existing functionality)
  - **NEW - DB Subnet Access**: DBSubnetCidrAZ1/2/3 for administrative and monitoring tools
  - **NEW - Additional Networks**: AdditionalAppPrefixList for flexible prefix list-based access
  - **Deployment Server Access**: Maintained existing deployment server access

- **Conditional Logic Enhancement**:
  - Added `HasDBSubnetCidrAZ3` condition for optional third AZ DB subnet access
  - Added `HasAdditionalAppPrefixList` condition for optional prefix list access
  - Maintains backward compatibility with existing deployments

#### Network Architecture Alignment (v3.1)
- **RDS SQL Pattern Compliance**: Security group configuration now matches RDS SQL v6 inbound patterns
- **Multi-Layer Access Control**: 
  - Application layer: App subnet access for application connectivity
  - Database layer: DB subnet access for administration and monitoring
  - Extended networks: Prefix list access for additional application networks
- **Operational Flexibility**: Supports both direct application access and administrative access patterns

#### Parameter File Updates (v3.1)
- Updated `parameter-pgsql-postgres.json` with new parameters:
  - `DBSubnetCidrAZ1`: "10.1.2.16/28"
  - `DBSubnetCidrAZ2`: "10.1.2.0/28"  
  - `DBSubnetCidrAZ3`: ""
  - `AdditionalAppPrefixList`: ""
- All new parameters ready for deployment with sample values
- Maintains backward compatibility for existing deployments

#### Migration and Compatibility (v3.1)
- **Backward Compatible**: Existing v3.0 deployments unaffected
- **Template Migration**: New parameters optional - existing stacks continue operating
- **Parameter Enhancement**: Additional parameters provide extended functionality without breaking changes
- **Gradual Adoption**: Teams can adopt new networking features incrementally

#### IaC Version Update
- **Updated Tag**: `InfraPlatform-rdspostg-v3.1`
- **Template Location**: `InfraPlatform/rds/rdspostgres/v3.1/`

---

## Version 5.0 - November 2025

### Template: `cf-rds-postgres.yaml`

#### Major Changes from v4.0
- **Extended VPC CIDR Support**: Increased from 4 to 5 VPC CIDR ranges for complex multi-VPC architectures
- **Enhanced Network Flexibility**: Additional VPC CIDR parameter for advanced hybrid cloud and cross-region connectivity patterns

#### New Parameters Added (v5.0)
- **`VpcCidr5`**: Fifth VPC CIDR range for extended network access control
  - Type: String
  - Default: "" (empty string)
  - Optional parameter for additional VPC CIDR configuration
  - Supports complex multi-VPC peering and hybrid cloud scenarios

#### Enhanced Features (v5.0)
- **Extended VPC CIDR Support**: 
  - Now supports up to 5 VPC CIDR ranges (VpcCidr1-5) for complex network topologies
  - Conditional egress rules automatically configured when VPC CIDRs are provided
  - Enables multi-VPC peering scenarios requiring broad security group rules
  - Supports hybrid cloud connectivity with multiple on-premises networks
  - Facilitates cross-region VPC connectivity patterns
  - Maintains backward compatibility with existing configurations

#### Updated Security Group Configuration (v5.0)
- **Extended Egress Rules**: Additional egress rule for VpcCidr5 with HTTPS (port 443) access
- **Condition Logic**: Added HasVpcCidr5 condition for proper conditional resource creation

#### Parameter File Updates (v5.0)
- Updated `parameter-pgsql-postgres.yaml` with VpcCidr5 parameter
- New parameter initialized with empty string value for backward compatibility
- Ready for deployment with or without additional network configuration

#### IaC Version Update
- **New Tag**: `InfraPlatform-rdspostg-v5`
- **Template Location**: `InfraPlatform/rds/rdspostgres/v5/`

---

## Version 4.0 - September 2025

### Template: `cf-rds-postgres.yaml`

#### Major Changes from v3.0
- **Enhanced Network Flexibility**: Extended support for additional VPC CIDR ranges and application subnet configurations
- **Expanded Subnet Coverage**: Increased application subnet support from 3 to 6 availability zones
- **Improved Security Group Rules**: Added conditional ingress and egress rules for extended network configuration
- **Parameter File Enhancement**: Updated parameter templates to support new network configurations

#### New Parameters Added (v4.0)
- **`VpcCidr4`**: Fourth VPC CIDR range for extended network access control
  - Type: String
  - Default: "" (empty string)
  - Optional parameter for additional VPC CIDR configuration
  
- **Extended App Subnet Parameters**:
  - **`VPCSubnetCidrAppAZ4`**: CIDR range for application subnet in AZ4
  - **`VPCSubnetCidrAppAZ5`**: CIDR range for application subnet in AZ5  
  - **`VPCSubnetCidrAppAZ6`**: CIDR range for application subnet in AZ6
  - Type: String for all
  - Default: "" (empty string) for all
  - Optional parameters for extended multi-AZ application deployment

#### Enhanced Features (v4.0)
- **Extended VPC CIDR Support**: 
  - Now supports up to 4 VPC CIDR ranges (VpcCidr1-4) for complex network topologies
  - Conditional egress rules automatically configured when VPC CIDRs are provided
  - Maintains backward compatibility with existing 3 CIDR configurations

- **Expanded Application Subnet Support**:
  - Increased from 3 to 6 application subnet parameters (VPCSubnetCidrAppAZ1-6)
  - Conditional ingress rules for PostgreSQL database access from all configured app subnets
  - Supports complex multi-AZ application architectures

#### Updated Security Group Configuration (v4.0)
- **Enhanced Ingress Rules**: Conditional rules for app subnets AZ4-6 with proper condition handling
- **Extended Egress Rules**: Additional egress rule for VpcCidr4 with HTTPS (port 443) access
- **Condition Logic**: Added HasVpcCidr4, HasVPCSubnetCidrAppAZ4-6 conditions for proper conditional resource creation

#### Parameter File Updates (v4.0)
- Updated `parameter-pgsql-postgres.json` with new parameters
- All new parameters initialized with empty string values for backward compatibility
- Ready for deployment with or without additional network configuration

#### IaC Version Update
- **New Tag**: `InfraPlatform-rdspostg-v4` (Note: Shortened from pgsql to rdspostg for tag length compliance)
- **Template Location**: `InfraPlatform/rds/rdspostgres/v4/`

---

## Version 3.0 - August 2025

### Template: `cf-rds-postgres.yaml`

#### Major Changes from v2.0
- **Comprehensive Naming Convention Update**: All resource names changed from "rds" to "pgsql" for better PostgreSQL identification
- **Parameter Standardization**: All database-related parameters now use "Pgsql" prefix for consistency
- **Lowercase Resource Names**: All CloudFormation resource identifiers converted to lowercase following best practices
- **Enhanced Template Organization**: Improved readability and maintainability of the CloudFormation template

#### Updated Parameter Names (v3.0)
- `RdsDBParameterGroupFamily` → `PgsqlDBParameterGroupFamily`
- `DBInstanceClass` → `PgsqlDBInstanceClass`
- `DBEngine` → `PgsqlDBEngine`
- `DBMajorEngineVersion` → `PgsqlDBMajorEngineVersion`
- `EngineVersion` → `PgsqlEngineVersion`
- `AllocatedStorage` → `PgsqlAllocatedStorage`
- `RDSMaxAllocatedStorage` → `PgsqlMaxAllocatedStorage`
- `StorageType` → `PgsqlStorageType`
- `StorageIops` → `PgsqlStorageIops`

#### New Parameters Added (v3.0)
- **`EnableIAMDatabaseAuthentication`**: Enable IAM database authentication for enhanced security
  - Type: String (true/false)
  - Default: 'false'
  - Allows users to authenticate using IAM credentials instead of database passwords
  - Maintains backward compatibility with default false value

#### Updated Resource Names (v3.0)
All CloudFormation resource identifiers now use lowercase convention:
- `pgsqlencryptionkmskey` - Primary encryption key for PostgreSQL
- `pgsqlmonitoringencryptionkmskey` - Monitoring data encryption key
- `dbcombineds3bucket` - Secure S3 storage with access policies
- `pgsqldbsecuritygroup` - Network access control
- `pgsqlinstance` - PostgreSQL database instance
- `pgsqldbsubnetgroup` - Cross-AZ subnet configuration
- `pgsqldbparametergroup` - Database parameter customization
- `dbenhancedmonitoringrole` - Enhanced monitoring permissions
- `dbcombineds3role` - S3 and KMS access role
- `combineddbpolicy` - Comprehensive managed policy

#### New Features (v3.0)
- **Consistent PostgreSQL Branding**: All resources clearly identified as PostgreSQL-specific
- **IAM Database Authentication Support**: Optional IAM-based authentication for enhanced security posture
- **Improved Documentation**: Updated README and parameter files to reflect new naming and IAM authentication feature
- **Parameter File Update**: New `parameter-pgsql-postgres.json` with updated parameter keys
- **Template Validation**: Ensured all references updated consistently throughout template

#### Enhanced Security Features (v3.0)
- **IAM Database Authentication**: 
  - Eliminates the need for database passwords when enabled
  - Leverages AWS IAM for authentication and authorization
  - Provides centralized access control through IAM policies
  - Supports audit trails through AWS CloudTrail
  - Optional feature with backward compatibility

#### IaC Version Update
- **New Tag**: `InfraPlatform-pgsql-v3`
- **Template Location**: `InfraPlatform/rds/rdspostgres/v3/`

---

## Version 2.0 - July 2025

### Template: `cf-rds-postgres.yaml`

#### Major Changes from v1.0
- **Enhanced Security Configuration**: Added multi-VPC CIDR support and S3 endpoint rules
- **KMS Key Rotation**: Enabled automatic KMS key rotation with configurable periods
- **Storage Optimization**: Updated from gp2 to gp3 storage type for better performance
- **Extended Monitoring**: Enhanced CloudWatch integration and monitoring capabilities
- **Engine Version Update**: Updated default PostgreSQL version from 15.10 to 16.4

#### New Features (v2.0)
- **Advanced Network Security**: 
  - Multi-VPC CIDR ranges support (VpcCidr1, VpcCidr2, VpcCidr3)
  - S3 prefix list integration for endpoint access
  - HCC VPC endpoint subnet configuration
- **Enhanced KMS Management**:
  - Configurable KMS key rotation periods
  - Improved key policies and management
- **Storage Improvements**:
  - Default gp3 storage type
  - Enhanced IOPS configuration options
- **Monitoring Enhancements**:
  - Improved Performance Insights configuration
  - Enhanced CloudWatch logs integration

#### Updated Parameters (v2.0)
- Added `KMSKeyRotationPeriod` for configurable key rotation
- Added `VpcCidr1`, `VpcCidr2`, `VpcCidr3` for network configuration
- Added `S3PrefixListId` for S3 endpoint access
- Added `HCCVpceCidr` for VPC endpoint configuration
- Updated `EngineVersion` default from '15.10' to '16.4'

#### IaC Version Update
- **Tag**: `InfraPlatform-rdspostgres-v2`
- **Template Location**: `InfraPlatform/rds/rdspostgres/v2/`

---

## Version 1.0 - June 2025

### Template: `cf-rds-postgres.yaml`

#### Initial Release Features
- **Complete PostgreSQL RDS Infrastructure**: End-to-end deployment of PostgreSQL RDS with security, monitoring, and backup configurations
- **Dual KMS Encryption**: 
  - Dedicated KMS key for RDS instance and backup encryption
  - Separate KMS key for Performance Insights monitoring data
  - Manual key aliases for identification
- **Comprehensive Security**:
  - VPC-based deployment with restrictive security groups
  - S3 bucket for RDS-related files with enforced HTTPS and TLS 1.2+
  - Environment-specific database ports (prod: 53341, non-prod: 53331)
  - Deletion protection enabled by default
- **Enhanced Monitoring & Performance**:
  - CloudWatch enhanced monitoring with 60-second intervals
  - Performance Insights with retention period based on environment
  - PostgreSQL and upgrade logs exported to CloudWatch
  - Dedicated IAM role for monitoring services
- **Flexible Storage Configuration**:
  - Support for gp2, gp3, io1, io2 storage types
  - Basic storage configuration with IOPS support
  - Fixed storage allocation
- **Multi-Environment Support**:
  - Production and non-production environment configurations
  - Environment-specific backup retention (35 days prod, 7 days non-prod)
  - Conditional Multi-AZ deployment support
- **IAM & Access Management**:
  - Dedicated IAM roles for RDS and monitoring services
  - Managed policies with least-privilege access
  - S3 and KMS permissions properly scoped

#### Resource Components (v1.0)
1. **Encryption & Security**:
   - `RDSEncryptionKmsKey` - Primary encryption key for RDS (no rotation)
   - `RDSmonitoringEncryptionKmsKey` - Monitoring data encryption key
   - `DBCombinedS3Bucket` - Secure S3 storage with access policies
   - `RdsDBSecurityGroup` - Basic network access control

2. **Database Infrastructure**:
   - `RDSInstance` - PostgreSQL database instance
   - `RdsDBSubnetGroup` - Cross-AZ subnet configuration
   - `RdsDBParameterGroup` - Database parameter customization

3. **IAM & Permissions**:
   - `DBEnhancedMonitoringRole` - Enhanced monitoring permissions
   - `DBCombinedS3Role` - S3 and KMS access role
   - `CombinedDBPolicy` - Comprehensive managed policy

#### Initial Configuration (v1.0)
- **Engine Support**: PostgreSQL 15.10 with family-specific parameter groups
- **Instance Classes**: Flexible instance sizing from t3 to high-performance classes
- **Storage Type**: Default gp2 storage
- **Network Security**: Basic CIDR-based access control for application subnets
- **Backup Strategy**: Environment-appropriate retention periods with automated scheduling
- **Maintenance Windows**: Saturday 18:00-19:00 UTC default
- **KMS Encryption**: Manual key rotation (EnableKeyRotation: false)

#### Environment Support (v1.0)
- **Production Environments**: prod, prod-a, prod-b, prod-c
  - 35-day backup retention
  - Extended Performance Insights retention (31 days)
  - Enhanced security configurations
- **Non-Production Environments**: nprd, nprd-dev, nprd-sit*, nprd-uat*, nprd-pt, nprd-pp*
  - 7-day backup retention
  - Standard Performance Insights retention (7 days)
  - Cost-optimized configurations

#### Initial Naming Conventions (v1.0)
All resources follow mixed-case naming with RDS/DB prefixes:
- `RDSEncryptionKmsKey`, `RDSInstance`, `RdsDBSecurityGroup`
- Environment and application identification
- Resource tracking and management

#### Tags and Compliance (v1.0)
- **IaC Version**: `InfraPlatform-rdspostgres-v1`
- **Backup Tags**: Automated backup solution integration
- **Environment Tags**: Clear environment identification
- **Retention Policies**: Production resources with retain policies

---

## Future Enhancements (Planned)
- **Version 4.0 Features**:
  - Enhanced IAM database authentication capabilities
  - Advanced security group rules with additional VPC CIDR support
  - Additional KMS key management features
  - Enhanced monitoring and alerting capabilities
  - Cross-region backup support
  - Advanced parameter group configurations

## Migration Notes
### v2.0 to v3.0 Migration
- **Parameter Name Changes**: Update parameter files to use new "Pgsql" prefixed parameter names
- **Resource Name Updates**: All resources now use lowercase naming convention
- **IAM Authentication**: Optional new feature - can be enabled post-migration
- **Backward Compatibility**: Template maintains functional compatibility with proper parameter updates

### v1.0 to v2.0 Migration
- **KMS Key Rotation**: New automatic rotation feature (requires key recreation)
- **Storage Type**: Migration from gp2 to gp3 recommended for better performance
- **Network Configuration**: New optional VPC CIDR parameters
- **Engine Version**: Update PostgreSQL from 15.10 to 16.4

### Initial Deployment (Greenfield)
- Designed for greenfield deployments
- Migration from existing RDS instances requires careful planning
- Backup and restore procedures available for data migration

## Support Information
- **Template Location**: `InfraPlatform/rds/rdspostgres/v{1,2,3}/`
- **Documentation**: Complete README with deployment guides
- **Parameter Examples**: Environment-specific parameter files included
- **Validation**: Template validation and verification procedures documented

---

**Last Updated**: November 2025  
**Template Version**: v5.0  
**IaC Version Tag**: InfraPlatform-rdspostg-v5

## Summary of Key Changes Across Versions
| Feature/Component         | v1.0                                 | v2.0                                 | v3.0                                   | v4.0                                   | v5.0                                   |
|---------------------------|--------------------------------------|--------------------------------------|----------------------------------------|----------------------------------------|----------------------------------------|
| IaC Version               | InfraPlatform-rdspostgres-v1         | InfraPlatform-rdspostgres-v2         | InfraPlatform-pgsql-v3                 | InfraPlatform-rdspostg-v4              | **InfraPlatform-rdspostg-v5**          |
| Resource Naming           | RDS prefix (mixed case)              | RDS prefix (mixed case)              | pgsql prefix (lowercase)               | pgsql prefix (lowercase)               | pgsql prefix (lowercase)               |
| Parameter Naming          | DB/RDS prefix (mixed case)           | DB/RDS prefix (mixed case)           | Pgsql prefix                           | Pgsql prefix                           | Pgsql prefix                           |
| VPC CIDR Support          | Basic (3 AZ subnets)                 | Up to 3 VPC CIDRs                   | Up to 3 VPC CIDRs                     | Up to 4 VPC CIDRs                     | **Up to 5 VPC CIDRs (Extended)**      |
| App Subnet Support        | 3 AZ subnets                         | 3 AZ subnets                         | 3 AZ subnets                           | 6 AZ subnets                           | 6 AZ subnets                           |
| Security Group Rules      | Basic CIDR                           | Multi-VPC CIDR and S3 endpoint rules | Multi-VPC CIDR and S3 endpoint rules  | Extended multi-VPC and 6 AZ rules     | **Extended 5 VPC CIDRs and 6 AZ rules** |
| KMS Key Rotation          | Manual (disabled)                    | Automatic (configurable)             | Automatic (configurable)               | Automatic (configurable)               | Automatic (configurable)               |
| IAM Database Auth         | Not supported                        | Not supported                        | Supported                              | Supported                              | Supported                              |
| Storage Type              | gp2 default                          | gp3 default                          | gp3 default                            | gp3 default                            | gp3 default                            |
| Storage Scaling           | Fixed allocation                     | Auto-scaling supported               | Auto-scaling supported                 | Auto-scaling supported                 | Auto-scaling supported                 |
| Engine Version Default    | 15.10                                | 16.4                                 | 16.4                                   | 16.4                                   | 16.4                                   |
| Network Configuration     | Basic                                | Advanced (VPC CIDRs, S3, HCC)       | Advanced (VPC CIDRs, S3, HCC)         | Enhanced (4 VPCs, 6 AZs, S3, HCC)     | **Enhanced (5 VPCs, 6 AZs, S3, HCC)** |
| Authentication Methods    | Password-based only                  | Password-based only                  | Password + IAM authentication          | Password + IAM authentication          | Password + IAM authentication          |

### Key Evolution Highlights
- **v1.0**: Foundation release with basic PostgreSQL RDS deployment and manual KMS key management
- **v2.0**: Enhanced security with advanced network rules, automatic KMS rotation, and multi-VPC CIDR support
- **v3.0**: Naming standardization (RDS→pgsql, mixed-case→lowercase), IAM authentication, and improved parameter structure
- **v4.0**: Extended network flexibility with 4 VPC CIDR support and 6 application subnet zones for complex architectures
- **v5.0**: Further extended VPC CIDR support to 5 ranges for complex multi-VPC, hybrid cloud, and cross-region connectivity

For detailed changes, refer to the respective `README.md` files in the `v1`, `v2`, `v3`, `v4`, and `v5` directories.