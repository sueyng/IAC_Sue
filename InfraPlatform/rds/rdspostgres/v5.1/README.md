# PostgreSQL Deployment with AWS CloudFormation

## Overview

This repository provides an AWS CloudFormation template for deploying a PostgreSQL instance with secure configurations, including encryption, enhanced monitoring, and Multi-AZ support. This setup ensures high availability and optimal database performance across environments.

## Template Structure

```
rds/
└── rdspostgres/
    └── v5.1/
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
| VPCSubnetCidrAppAZ4 | CIDR range for subnet in AZ4 | "10.0.105.0/24" | Optional |
| VPCSubnetCidrAppAZ5 | CIDR range for subnet in AZ5 | "10.0.106.0/24" | Optional |
| VPCSubnetCidrAppAZ6 | CIDR range for subnet in AZ6 | "10.0.107.0/24" | Optional |
| DBSubnetIds | List of subnet IDs for PostgreSQL | "subnet-054fa74f69bf99d68,subnet-04be9fd2348c74663" | Yes |
| DBSubnetCidrAZ1 | DB Subnet CIDR for AZ1 | "10.1.2.16/28" | Yes |
| DBSubnetCidrAZ2 | DB Subnet CIDR for AZ2 | "10.1.2.0/28" | Yes |
| DBSubnetCidrAZ3 | DB Subnet CIDR for AZ3 (optional) | "10.1.3.0/28" | Optional |
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
| VpcCidr4 | VPC CIDR 4 IP Range | "10.3.0.0/16" | Optional |
| VpcCidr5 | VPC CIDR 5 IP Range | "10.4.0.0/16" | Optional |
| S3PrefixListId | S3 PrefixList ID | "pl-12345678" | Optional |
| HCCVpceCidr | HCC VPC Endpoint Subnet CIDR | "10.3.0.0/24" | Optional |
| AdditionalAppPrefixList | Additional Application Networks Prefix List ID | "pl-87654321" | Optional |
| KMSKeyRotationPeriod | Number of days for KMS key rotation period | "365" | No |
| **UseExistingSubnetGroup** (NEW v5.1) | Toggle to reuse an existing subnet group instead of creating a new one. `'true'` for v3/v4/v5 → v5.1 upgrade; `'false'` for greenfield. | "false" | No (default `'false'`) |
| **ExistingSubnetGroupName** (NEW v5.1) | Name of existing DB subnet group (used when `UseExistingSubnetGroup='true'`). For v3 upgrade, provide the v3 subnet group name. | "myapp-prod-subnetgroup" | Required if toggle is `'true'` |

### Supported Environment Names
- **Non-Production:** nprd, nprd-dev, nprd-sit1, nprd-sit2, nprd-sit3, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-sit-c, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-uat-c, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b, nprd-pp-c
- **Production:** prod, prod-a, prod-b, prod-c

## Upgrading from v3/v4/v5 to v5.1

### Why this section exists
v5.1 changed the DB subnet group naming convention from
`${AppShortName}-${EnvName}-subnetgroup` (v3/v4/v5) to
`${AppShortName}-${EnvName}-postgres-subnetgroup` (v5.1, disambiguates from rdssql).

`DBSubnetGroupName` is **immutable** on `AWS::RDS::DBInstance`. A naïve template upgrade
without using the toggle below would force **DBInstance replacement** — total data loss
in non-prod, retained-but-orphaned in prod.

### Greenfield (no existing v3/v4/v5 deployment)
Leave both new params at their defaults — a new subnet group with the v5.1 standard
name will be provisioned:
```yaml
UseExistingSubnetGroup: "false"      # default
ExistingSubnetGroupName: ""          # default
```

### v3/v4/v5 → v5.1 upgrade (existing deployment with data)
Set the toggle ON and provide the existing subnet group name:
```yaml
UseExistingSubnetGroup: "true"
ExistingSubnetGroupName: "myapp-prod-subnetgroup"   # ← your existing v3 subnet group
```

**What CloudFormation will do during the update:**

| Resource | Action shown in changeset | Actual effect |
|----------|---------------------------|---------------|
| `pgsqldbsubnetgroup` | `Remove` (with Retain note in production) | Production: AWS resource preserved (orphaned from CFN management). Non-prod: deleted (only safe if the subnet group was created OUTSIDE this stack) |
| `pgsqlinstance` | `Modify` with `Replacement: False` | `DBSubnetGroupName` resolves to the same string as before → no replacement, no modification, zero downtime |

### Once on the override
Do **not** switch `UseExistingSubnetGroup` back to `'false'` later — it would force
DBInstance replacement. Project teams stay on the override for the life of that DB.
New databases created from v5.1 onward should use the default (greenfield) path.

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