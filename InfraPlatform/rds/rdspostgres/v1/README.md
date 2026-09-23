# RDS PostgreSQL Infrastructure Template (v1)

## Overview

This AWS CloudFormation template deploys a PostgreSQL RDS instance with comprehensive security features, encryption, enhanced monitoring, and Multi-AZ support. The template is designed for enterprise-grade deployments with production-ready configurations.

## Template Structure

```
InfraPlatform/rds/rdspostgres/v1/
├── cf-rds-postgres.yaml           # Main CloudFormation template
├── env/
│   └── parameters-rds-postgres.json  # Environment-specific parameters
├── README.md                      # This documentation
└── artifacts/                     # Additional deployment artifacts
```

## Architecture Components

### Security & Encryption
- **KMS Encryption Keys**: 
  - Dedicated encryption key for RDS instance and backups
  - Separate encryption key for Performance Insights monitoring
  - Custom key aliases for easy identification
- **S3 Bucket**: Secure storage for RDS-related files with encryption and access policies
- **Security Groups**: Restrictive ingress rules based on environment and subnet CIDRs

### Database Infrastructure
- **RDS PostgreSQL Instance**: Configurable instance class, storage, and Multi-AZ deployment
- **Subnet Groups**: Cross-AZ subnet configuration for high availability
- **Parameter Groups**: Database-specific parameter configurations
- **Enhanced Monitoring**: CloudWatch integration with dedicated IAM role

### IAM & Access Control
- **Enhanced Monitoring Role**: Dedicated role for RDS monitoring services
- **S3 Access Role**: IAM role with policies for S3 and KMS access
- **Managed Policies**: Granular permissions for RDS operations

## Parameters

### Core Parameters

| Parameter | Type | Description | Example Value | Required |
|-----------|------|-------------|---------------|----------|
| AppShortName | String | Application identifier for resource naming | "healthb" | Yes |
| EnvName | String | Environment designation | "nprd" | Yes |
| VpcId | AWS::EC2::VPC::Id | Target VPC for RDS deployment | "vpc-02fb2e32bbb6ff24e" | Yes |
| AvailabilityZone | AWS::EC2::AvailabilityZone::Name | Primary AZ for single-AZ deployments | "ap-southeast-1a" | Yes |

### Network Configuration

| Parameter | Type | Description | Example Value | Required |
|-----------|------|-------------|---------------|----------|
| VPCSubnetCidrAppAZ1 | String | Application subnet CIDR for AZ1 | "10.0.102.0/24" | Yes |
| VPCSubnetCidrAppAZ2 | String | Application subnet CIDR for AZ2 | "10.0.103.0/24" | Yes |
| VPCSubnetCidrAppAZ3 | String | Application subnet CIDR for AZ3 | "10.0.104.0/24" | No |
| DBSubnetIds | List<AWS::EC2::Subnet::Id> | Database subnet IDs | ["subnet-054fa74f", "subnet-04be9fd2"] | Yes |
| DeploymentServer | String | Deployment server CIDR for DB access | "10.0.1.9/32" | Yes |

### Database Configuration

| Parameter | Type | Description | Example Value | Required |
|-----------|------|-------------|---------------|----------|
| MultiAZ | String | Enable Multi-AZ deployment | "true" or "false" | Yes |
| DBInstanceClass | String | RDS instance type | "db.m6i.xlarge" | Yes |
| DBEngine | String | Database engine | "postgres" | Yes |
| DBMajorEngineVersion | String | Major engine version | "16" | Yes |
| EngineVersion | String | Specific engine version | "16.10" | Yes |
| RdsDBParameterGroupFamily | String | Parameter group family | "postgres16" | Yes |

### Storage Configuration

| Parameter | Type | Description | Example Value | Required |
|-----------|------|-------------|---------------|----------|
| AllocatedStorage | String | Initial storage allocation (GB) | "100" | Yes |
| RDSMaxAllocatedStorage | String | Maximum storage for auto-scaling (GB) | "1000" | Yes |
| StorageType | String | Storage type | "gp3" | Yes |
| StorageIops | String | Provisioned IOPS (for io1/io2/gp3) | "3000" | No |

### Security Configuration

| Parameter | Type | Description | Default Value | Required |
|-----------|------|-------------|---------------|----------|
| MasterUsernameDev | String | Master username for database | "dbadmin" | Yes |
| MasterUserPasswordDev | String | Master password for database | "dbadmin123" | Yes |
| ProdDBPort | String | Database port for production | "53341" | Yes |
| NProdDBPort | String | Database port for non-production | "53331" | Yes |

## Environment Support

### Supported Environment Names
- **Non-Production**: nprd, nprd-dev, nprd-sit1, nprd-sit2, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b
- **Production**: prod, prod-a, prod-b

## Key Features

### Security Features
- **Encryption at Rest**: KMS encryption for RDS instance and backups
- **Encryption in Transit**: SSL/TLS enforcement
- **Network Security**: VPC-based deployment with restrictive security groups
- **Access Control**: IAM roles with least-privilege principles
- **S3 Security**: Bucket policies enforcing HTTPS and TLS 1.2+

### High Availability & Backup
- **Multi-AZ Support**: Configurable for high availability
- **Automated Backups**: Environment-based retention (7 days non-prod, 35 days prod)
- **Point-in-Time Recovery**: Available within backup retention period
- **Maintenance Windows**: Scheduled maintenance during low-usage periods

### Monitoring & Performance
- **Enhanced Monitoring**: 60-second CloudWatch metrics
- **Performance Insights**: Enabled with KMS encryption
- **CloudWatch Logs**: PostgreSQL and upgrade logs exported
- **Custom Metrics**: Available through CloudWatch integration

### Storage & Scaling
- **Auto-Scaling**: Configurable maximum storage limits
- **Storage Types**: Support for gp2, gp3, io1, io2
- **IOPS Configuration**: Provisioned IOPS for high-performance workloads
- **Storage Encryption**: KMS-based encryption at rest

## Resource Naming Convention

All resources follow the pattern: `{AppShortName}-{EnvName}-{ResourceType}`

Examples:
- RDS Instance: `healthb-nprd-rdspostg`
- Security Group: `healthb-nprd-sg-Rds-DB-PostgreSQL`
- KMS Key Alias: `healthb-nprd-rdssqlserver-encryption`
- S3 Bucket: `healthb-nprd-rdssql-s3store`

## Deployment Guide

### Prerequisites
- AWS CLI configured with appropriate permissions
- VPC and subnets already created
- Parameters file prepared with environment-specific values

### Deployment Steps

1. **Prepare Parameters File**
   ```bash
   cp env/parameters-rds-postgres.json env/parameters-{environment}.json
   # Edit the parameters file with your environment values
   ```

2. **Validate Template**
   ```bash
   aws cloudformation validate-template \
     --template-body file://cf-rds-postgres.yaml
   ```

3. **Deploy Stack**
   ```bash
   aws cloudformation deploy \
     --template-file cf-rds-postgres.yaml \
     --parameter-overrides file://env/parameters-{environment}.json \
     --stack-name {AppShortName}-{EnvName}-rds-postgres \
     --capabilities CAPABILITY_NAMED_IAM \
     --region ap-southeast-1
   ```

4. **Monitor Deployment**
   ```bash
   aws cloudformation describe-stacks \
     --stack-name {AppShortName}-{EnvName}-rds-postgres \
     --query 'Stacks[0].StackStatus'
   ```

### Post-Deployment Verification

1. **Check RDS Instance Status**
   ```bash
   aws rds describe-db-instances \
     --db-instance-identifier {AppShortName}-{EnvName}-rdspostg
   ```

2. **Verify Security Groups**
   ```bash
   aws ec2 describe-security-groups \
     --group-names {AppShortName}-{EnvName}-sg-Rds-DB-PostgreSQL
   ```

3. **Check SSM Parameters**
   ```bash
   aws ssm get-parameter \
     --name {AppShortName}-{EnvName}-parameter-RDSInstanceName
   ```

## Configuration Notes

### Multi-AZ Deployment
- **Production**: Always set `MultiAZ: "true"` for high availability
- **Non-Production**: Can use `MultiAZ: "false"` for cost savings
- **Note**: Multi-AZ requires subnets in different availability zones

### Storage Configuration
- **gp3 Storage**: Recommended for balanced performance and cost
- **Provisioned IOPS**: Use for high-performance workloads (io1/io2)
- **Auto-Scaling**: Set `RDSMaxAllocatedStorage` higher than `AllocatedStorage`

### Security Considerations
- **Database Ports**: Different ports for prod (53341) and non-prod (53331)
- **Network Access**: Limited to specified CIDR blocks
- **Encryption**: All data encrypted at rest and in transit
- **Deletion Protection**: Enabled by default (can be modified for non-prod)

### Backup Strategy
- **Automated Backups**: Daily backups during preferred backup window
- **Manual Snapshots**: Create before major changes
- **Cross-Region Backups**: Consider for disaster recovery (manual setup)

## Troubleshooting

### Common Issues

1. **KMS Key Permissions**
   - Ensure RDS service has access to KMS keys
   - Check key policies and IAM roles

2. **Subnet Configuration**
   - Verify subnets are in different AZs for Multi-AZ
   - Check subnet group configuration

3. **Security Group Rules**
   - Verify CIDR blocks match your network configuration
   - Check port accessibility from application subnets

4. **Storage IOPS**
   - Ensure IOPS value is compatible with storage type and size
   - Check AWS limits for IOPS based on storage size

### Monitoring and Maintenance

1. **Regular Tasks**
   - Monitor CloudWatch metrics and alarms
   - Review Performance Insights for query optimization
   - Check automated backup status
   - Monitor storage utilization

2. **Maintenance Windows**
   - Default: Saturday 18:00-19:00 UTC
   - Plan major version upgrades during low-usage periods
   - Test parameter group changes in non-production first

## Tags and Compliance

All resources are tagged with:
- `IaCVersion`: "InfraPlatform-rdspostgres-v1"
- Backup tags for automated backup solutions
- Environment and application identification tags

## Support and Updates

For questions or issues:
- Review CloudFormation stack events for detailed error messages
- Check AWS documentation for RDS PostgreSQL best practices
- Consult with infrastructure team for environment-specific configurations
