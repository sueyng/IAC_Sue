# RDS Postgres Deployment with AWS CloudFormation

## Overview

This repository provides an AWS CloudFormation template for deploying an RDS Postgres instance with secure configurations, including encryption, enhanced monitoring, and Multi-AZ support. This setup ensures high availability and optimal database performance across environments.

## Template Structure

```
rds/
└── rdspostgres/
    └── v1/
        ├── env/
        │   └── parameter-rds-postgres.json    (Parameter file for deployment)
        ├── cf-rds-postgres.yaml              (Main stack template)
        └── README.md                         (Documentation for deployment)

```
## Main Components
**cf-rds-postgres.yaml:**
CloudFormation template to provision the RDS Postgres setup, including:
RDS instance
Security groups
Subnet groups
IAM roles and KMS encryption
Fully parameterized for flexible deployment.

**parameter-rds-postgres.json:**
Defines the environment-specific parameters such as VPC ID, subnets, and RDS instance settings.

## Parameters and its valid values

|ParameterKey  | ValueType | Allowed Values  | 
|---|---|---|
| Parameter | Description | Example Value | Required |
|-----------|-------------|---------------|----------|
| AppShortName | Application name | "myapp" | Yes |
| EnvName | Environment name (supports multiple environments) | "nprd" | Yes |
| VpcId | VPC ID where the RDS will be deployed | "vpc-02fb2e32bbb6ff24e"| Yes |
| AvailabilityZone | Primary availability zone for RDS deployment | "ap-southeast-1a" | Yes |
| VPCSubnetCidrAppAZ1 | CIDR range for subnet in AZ1 | "10.0.102.0/24" | Yes |
| VPCSubnetCidrAppAZ2 | CIDR range for subnet in AZ2 | "10.0.103.0/24" | Yes |
| VPCSubnetCidrAppAZ3 | CIDR range for subnet in AZ3 | "10.0.104.0/24" | Optional |
| DBSubnetIds | List of subnet IDs for RDS | "subnet-054fa74f69bf99d68,subnet-04be9fd2348c74663" | Yes |
| DeploymentServer | CIDR block of the deployment server | "10.0.1.9/32" | Yes |
| MultiAZ | Enable Multi-AZ deployment | "false" | Yes |
| RdsDBParameterGroupFamily | Parameter group family for the DB	 | "postgres16" | Yes |
| DBInstanceClass | Instance type for RDS | "db.t3.xlarge" | Yes |
| DBEngine | Database engine | "postgres" | Yes |
| DBMajorEngineVersion | Major engine version | "16" | Yes |
| EngineVersion | Exact engine version | "16.6"	 | Yes |
| AllocatedStorage | Storage allocated for the RDS instance | "100" | Yes |
| RDSMaxAllocatedStorage | Maximum storage allocated for the RDS instance | "1000" | Yes |
| StorageType | Storage type (e.g., gp2, gp3) | "gp3" | Yes |
| StorageIops | IOPS for the storage | "3000" | Optional |

### Supported Environment Names
- Non-Production: nprd, nprd-dev, nprd-stg, nprd-sit1, nprd-sit2, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b
- Production: prod, prod-a, prod-b

## Important Notes
1. **Multi-AZ Deployment:**
Multi-AZ deployments improve availability and durability. Set MultiAZ to "true" for production environments.
For non-production environments, MultiAZ can be set to "false" to save costs.
2. **Engine Version and Parameter Group Family:**
Ensure that the EngineVersion matches the selected RdsDBParameterGroupFamily. For example, use postgres16 for engine version 16.x.
3. **Subnet and Availability Zone Configuration:**
Provide valid subnet IDs in DBSubnetIds that belong to the specified VPC and Availability Zones.
Ensure at least two subnets are in different Availability Zones for Multi-AZ deployments.
4. **KMS Encryption:**
The RDS instance is encrypted using KMS keys. Verify the KMS keys are properly configured and active.
Ensure permissions for the KMS key allow access to the RDS service.
The KMS key rotation policy is configured in accordance with the HIM-CSI&P Policy.
5. **Storage Scaling:**
Use AllocatedStorage for initial storage allocation.
Set RDSMaxAllocatedStorage to allow automated storage scaling based on database requirements.
6. **Enhanced Monitoring:**
Enable enhanced monitoring to get detailed metrics from CloudWatch.
Ensure the IAM role for enhanced monitoring has the required permissions.
7. **Database Port Configuration:**
Use ProdDBPort for production environments and NProdDBPort for non-production environments.
Ensure the database port is open in the RDS security group for allowed CIDR blocks.
8. **Backup and Retention:**
Backup retention is set based on environment:
Production: 35 days
Non-production: 7 days
Ensure sufficient space for automated backups.
9. **Monitoring and Maintenance:**
Regularly monitor logs and metrics for the RDS instance using CloudWatch.
Set the PreferredMaintenanceWindow to a suitable time to apply updates with minimal disruption.
10. **Security Group and Access:**
Restrict access to the RDS instance using the DeploymentServer and CIDR blocks defined in the security group.
Always follow the principle of least privilege for IAM roles and database users.
11. **IAM Role Permissions:**
Verify that the IAM roles used for the RDS instance, monitoring, and backups have the required permissions.
12. **Database Instance Identifiers:**
Use environment-specific identifiers for the RDS instance to easily distinguish between resources.

## Deployment Steps
- **Prepare the Environment:**
Ensure the VPC, subnets, and security groups exist as specified in the parameter file.
- **Edit the Parameter File:**
Update the parameter-rds-postgres.json file with environment-specific values.
- **Deploy Using AWS CLI:**
Execute the following command:
```
aws cloudformation deploy \
  --template-file cf-rds-postgres.yaml \
  --parameter-overrides file://parameter-rds-postgres.json \
  --stack-name RDSPostgresDeployment \
  --capabilities CAPABILITY_NAMED_IAM
```
- **Monitor the Stack:**
Track the stack creation process in the AWS Management Console
- **Validate Resources:**
Verify the RDS instance, security groups, and subnet groups are correctly deployed.
