# Release Notes: AWS Database Migration Service (DMS) Infrastructure Templates

## Version 1.0 (Current) - January 2025

### Template: `cf-rds-dms.yaml`

#### Initial Release Features
- **AWS Secrets Manager Integration**: Secure credential management for database connections
- **SQL Server to PostgreSQL Migration**: Complete DMS setup for heterogeneous database migration
- **Production-Ready Security**: Environment-specific port configurations (prod: 53341, nprd: 53331)
- **Comprehensive IAM Management**: Dedicated service roles with least-privilege access

#### Key Parameters (v1.0)
- **`SourceSecretArn`**: AWS Secrets Manager ARN for source database credentials
  - Type: String (Required)
  - Purpose: Secure SQL Server connection credentials
  
- **`TargetSecretArn`**: AWS Secrets Manager ARN for target database credentials
  - Type: String (Required)
  - Purpose: Secure PostgreSQL connection credentials

#### Core DMS Infrastructure
- **Migration Resources**:
  - `DMSReplicationInstance` - Primary DMS replication instance
  - `DMSSourceEndpoint` - SQL Server source database endpoint
  - `DMSTargetEndpoint` - PostgreSQL target database endpoint
  - `DMSReplicationTask` - Migration task with table mappings

- **Security & Access**:
  - `DMSServiceRole` - IAM service role for DMS operations
  - `DMSAccessForEndpointRole` - Dedicated role for endpoint access
  - VPC security group configurations for network access control

#### AWS Secrets Manager Integration (v1.0)
- **Secure Credential Storage**: 
  - Dynamic reference: `{{resolve:secretsmanager:${SecretArn}:SecretString:username}}`
  - Password retrieval: `{{resolve:secretsmanager:${SecretArn}:SecretString:password}}`
  - Zero hardcoded credentials in templates

#### Environment Support (v1.0)
- **Production Environments**: prod, prod-a, prod-b, prod-c (Port 53341)
- **Non-Production Environments**: nprd, nprd-dev, nprd-sit*, nprd-uat*, nprd-pt, nprd-pp* (Port 53331)

#### Migration Capabilities
- **Full Load Migration**: Complete initial data transfer
- **Change Data Capture**: Ongoing replication for minimal downtime
- **Data Transformation**: Built-in transformation rules for data type conversion
- **Table Selection**: Flexible table inclusion/exclusion rules

---

## Deployment Information

### Prerequisites
- Source SQL Server database accessible from DMS subnet
- Target PostgreSQL database created and accessible
- AWS Secrets Manager secrets created with proper credential structure
- VPC and subnet configuration completed

### Secret Structure
**Source/Target Database Secret**:
```json
{
  "username": "database_user",
  "password": "secure_password_here"
}
```

### Parameter File Configuration
Updated `parameters.json` with Secret ARN references:
- Removed plain-text password parameters
- Environment-specific Secret ARN configuration
- Enhanced security through credential isolation

---

## Support Information
- **Template Location**: `InfraPlatform/rds/rdsdms/v1/`
- **Documentation**: Complete README with deployment guides
- **IaC Version Tag**: `InfraPlatform-rdsdms-v1`
- **Security Model**: AWS Secrets Manager + IAM Service Roles + VPC Isolation

---

**Last Updated**: January 2025  
**Template Version**: v1.0  
**Migration Type**: SQL Server → PostgreSQL  
**Security**: AWS Secrets Manager Integration

## Future Enhancements (Planned)
- **Version 2.0 Features**:
  - Multi-source database support (Oracle, MySQL)
  - Advanced transformation and data filtering
  - Cross-region replication support
  - Enhanced monitoring with CloudWatch integration
  - Schema conversion tool integration

For detailed implementation instructions, refer to the `README.md` file in the `v1` directory.