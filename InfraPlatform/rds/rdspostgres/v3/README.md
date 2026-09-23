# PostgreSQL Deployment with AWS CloudFormation

## Overview

This repository provides an AWS CloudFormation template for deploying a PostgreSQL instance with secure configurations, including encryption, enhanced monitoring, and Multi-AZ support. This setup ensures high availability and optimal database performance across environments.

## Template Structure

```
rds/
└── rdspostgres/
    └── v3/
        ├── env/
        │   └── parameter-pgsql-postgres.json    (Parameter file for deployment)
        ├── cf-rds-postgres.yaml                (Main stack template)
        └── README.md                           (Documentation for deployment)

```
## Main Components
**cf-rds-postgres.yaml:**
CloudFormation template to provision the PostgreSQL setup, including:
PostgreSQL RDS instance
Security groups
Subnet groups
IAM roles and KMS encryption
Fully parameterized for flexible deployment.

**parameter-pgsql-postgres.json:**
Defines the environment-specific parameters such as VPC ID, subnets, and PostgreSQL instance settings.

## Parameters and its valid values

| ParameterKey | Description | Example Value | Required |
|--------------|-------------|---------------|----------|
| AppShortName | Application name | "myapp" | Yes |
| EnvName | Environment name (supports multiple environments) | "nprd" | Yes |
| VpcId | VPC ID where the RDS will be deployed | "vpc-02fb2e32bbb6ff24e" | Yes |
| AvailabilityZone | Primary availability zone for RDS deployment | "ap-southeast-1a" | Yes |
| VPCSubnetCidrAppAZ1 | CIDR range for subnet in AZ1 | "10.0.102.0/24" | Yes |
| VPCSubnetCidrAppAZ2 | CIDR range for subnet in AZ2 | "10.0.103.0/24" | Yes |
| VPCSubnetCidrAppAZ3 | CIDR range for subnet in AZ3 | "10.0.104.0/24" | Optional |
| DBSubnetIds | List of subnet IDs for PostgreSQL | "subnet-054fa74f69bf99d68,subnet-04be9fd2348c74663" | Yes |
| DeploymentServer | CIDR block of the deployment server | "10.0.1.9/32" | Yes |
| MultiAZ | Enable Multi-AZ deployment | "false" | Yes |
| PgsqlDBParameterGroupFamily | Parameter group family for the DB | "postgres16" | Yes |
| PgsqlDBInstanceClass | Instance type for PostgreSQL | "db.t3.xlarge" | Yes |
| PgsqlDBEngine | Database engine | "postgres" | Yes |
| PgsqlDBMajorEngineVersion | Major engine version (numeric only, no periods) | "16" | Yes |
| PgsqlEngineVersion | Exact engine version | "16.4" | Yes |
| PgsqlAllocatedStorage | Storage allocated for the PostgreSQL instance | "100" | Yes |
| PgsqlMaxAllocatedStorage | Maximum storage allocated for the PostgreSQL instance | "1000" | Yes |
| PgsqlStorageType | Storage type (e.g., gp2, gp3) | "gp3" | Yes |
| PgsqlStorageIops | IOPS for the storage | "3000" | Optional |
| EnableIAMDatabaseAuthentication | Enable IAM database authentication | "false" | No |
| VpcCidr1 | VPC CIDR 1 IP Range | "10.0.0.0/16" | Optional |
| VpcCidr2 | VPC CIDR 2 IP Range | "10.1.0.0/16" | Optional |
| VpcCidr3 | VPC CIDR 3 IP Range | "10.2.0.0/16" | Optional |
| S3PrefixListId | S3 PrefixList ID | "pl-12345678" | Optional |
| HCCVpceCidr | HCC VPC Endpoint Subnet CIDR | "10.3.0.0/24" | Optional |
| KMSKeyRotationPeriod | Number of days for KMS key rotation period | "365" | No |

### Supported Environment Names
- **Non-Production:** nprd, nprd-dev, nprd-sit1, nprd-sit2, nprd-sit3, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-sit-c, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-uat-c, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b, nprd-pp-c
- **Production:** prod, prod-a, prod-b, prod-c

## Important Notes

1. **Multi-AZ Deployment:**
   - Multi-AZ deployments improve availability and durability. Set MultiAZ to "true" for production environments.
   - For non-production environments, MultiAZ can be set to "false" to save costs.

2. **Engine Version and Parameter Group Family:**
   - Ensure that the PgsqlEngineVersion matches the selected PgsqlDBParameterGroupFamily. For example, use postgres16 for engine version 16.x.

3. **Subnet and Availability Zone Configuration:**
   - Provide valid subnet IDs in DBSubnetIds that belong to the specified VPC and Availability Zones.
   - Ensure at least two subnets are in different Availability Zones for Multi-AZ deployments.

4. **KMS Encryption:**
   - The PostgreSQL instance is encrypted using KMS keys. Verify the KMS keys are properly configured and active.
   - Ensure permissions for the KMS key allow access to the RDS service.
   - The KMS key rotation policy is configured in accordance with the HIM-CSI&P Policy.
   - Default rotation period is 365 days and can be customized via the KMSKeyRotationPeriod parameter.

5. **Storage Scaling:**
   - Use PgsqlAllocatedStorage for initial storage allocation.
   - Set PgsqlMaxAllocatedStorage to allow automated storage scaling based on database requirements.

6. **Enhanced Monitoring:**
   - Enable enhanced monitoring to get detailed metrics from CloudWatch.
   - Ensure the IAM role for enhanced monitoring has the required permissions.

7. **Database Port Configuration:**
   - Use PgsqlProdDBPort for production environments and PgsqlNProdDBPort for non-production environments.
   - Ensure the database port is open in the PostgreSQL security group for allowed CIDR blocks.

8. **Backup and Retention:**
   - Backup retention is set based on environment:
     - Production: 35 days
     - Non-production: 7 days
   - Ensure sufficient space for automated backups.

9. **Monitoring and Maintenance:**
   - Regularly monitor logs and metrics for the PostgreSQL instance using CloudWatch.
   - Set the PreferredMaintenanceWindow to a suitable time to apply updates with minimal disruption.

10. **Security Group and Access:**
    - Restrict access to the PostgreSQL instance using the DeploymentServer and CIDR blocks defined in the security group.
    - Always follow the principle of least privilege for IAM roles and database users.

11. **IAM Database Authentication:**
    - Set EnableIAMDatabaseAuthentication to "true" to enable IAM database authentication for enhanced security.
    - When enabled, users can authenticate to the database using their IAM credentials instead of database passwords.
    - Default value is "false" to maintain backward compatibility.

12. **IAM Role Permissions:**
    - Verify that the IAM roles used for the PostgreSQL instance, monitoring, and backups have the required permissions.

13. **Database Instance Identifiers:**
    - Use environment-specific identifiers for the PostgreSQL instance to easily distinguish between resources.

14. **Network Configuration:**
    - Configure VPC CIDR ranges (VpcCidr1, VpcCidr2, VpcCidr3) for proper network access control.
    - Use S3PrefixListId to allow access to Amazon S3 endpoints if required.
    - Configure HCCVpceCidr if HCC VPC endpoint access is needed.

## Deployment Steps

1. **Prepare the Environment:**
   - Ensure the VPC, subnets, and security groups exist as specified in the parameter file.

2. **Edit the Parameter File:**
   - Update the parameter-pgsql-postgres.json file with environment-specific values.

3. **Deploy Using AWS CLI:**
   - Execute the following command:
   ```bash
   aws cloudformation deploy \
     --template-file cf-rds-postgres.yaml \
     --parameter-overrides file://parameter-pgsql-postgres.json \
     --stack-name PostgreSQLDeployment \
     --capabilities CAPABILITY_NAMED_IAM
   ```

4. **Monitor the Stack:**
   - Track the stack creation process in the AWS Management Console.

5. **Validate Resources:**
   - Verify the PostgreSQL instance, security groups, and subnet groups are correctly deployed.