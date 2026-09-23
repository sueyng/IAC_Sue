# Amazon Relational Database Service (RDS)

Amazon RDS is a fully managed relational database service that simplifies database setup, operation, and scaling. It automates common administrative tasks such as provisioning, configuration, backups, and patching, helping you optimize for total cost of ownership.

This template provisions an RDS instance (Standalone or Multi-AZ) along with the following prerequisites:
- KMS Keys (for RDS Encryption & Performance Monitoring, with key rotation policy per HIM-CSI&P Policy)
- KMS Aliases
- S3 Buckets (for Audit & Native Backup)
- IAM Roles & Policies
- RDS Subnet Group
- DB Parameter Group
- RDS Option Group
- RDS DB Instance
- Security Groups
- SSM Parameter Store

---

## Parameters and Valid Values

| ParameterKey              | ValueType                        | Allowed Values/Example                                                                 |
|-------------------------- |----------------------------------|---------------------------------------------------------------------------------------|
| AppShortName              | <i>String</i>                    | e.g. my-application                                                                   |
| EnvName                   | <i>String</i>                    | nprd, nprd-dev, nprd-sit1, nprd-sit2, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b, prod, prod-a, prod-b |
| VpcId                     | <i>AWS::EC2::VPC::Id</i>         | e.g. vpc-0d99a0c727b301d67                                                            |
| AvailabilityZone          | <i>AWS::EC2::AvailabilityZone::Name</i> | ap-southeast-1a, ap-southeast-1b, ap-southeast-1c                              |
| VPCSubnetCidrAppAZ1       | <i>String</i>                    | e.g. 10.1.128.0/20 (consolidated range supported)                                     |
| VPCSubnetCidrAppAZ2       | <i>String</i>                    | e.g. 10.1.144.0/20 (consolidated range supported)                                     |
| VPCSubnetCidrAppAZ3       | <i>String</i>                    | e.g. 10.1.160.0/20 (consolidated range supported)                                     |
| DBSubnetCidrAZ1           | <i>String</i>                    | e.g. 10.1.0.0/20                                                                      |
| DBSubnetCidrAZ2           | <i>String</i>                    | e.g. 10.1.16.0/20                                                                     |
| DBSubnetCidrAZ3           | <i>String</i>                    | e.g. 10.1.32.0/20                                                                     |
| DBSubnetIds               | <i>List<AWS::EC2::Subnet::Id></i>| e.g. subnet-08170d48a795103d2,subnet-083fba964c347656f,subnet-0e54709c5b9c524e1       |
| DeploymentServer          | <i>String</i>                    | e.g. 10.53.26.197/32                                                                  |
| AdditionalAppPrefixList   | <i>String</i>                    | (Optional) AWS Prefix List ID for additional application networks (e.g., pl-0abc123def456789) |
| MultiAZ                   | <i>String</i>                    | true/false                                                                            |
| RdsDBParameterGroupFamily | <i>String</i>                    | e.g. sqlserver-ee-16.0                                                                |
| DBInstanceClass           | <i>String</i>                    | e.g. db.m6i.xlarge                                                                    |
| DBEngine                  | <i>String</i>                    | sqlserver-se, sqlserver-ee                                                            |
| DBMajorEngineVersion      | <i>String</i>                    | e.g. 16.00                                                                            |
| EngineVersion             | <i>String</i>                    | e.g. 16.00.4095.4.v1                                                                  |
| AllocatedStorage          | <i>String</i>                    | e.g. 100 (in GiB)                                                                     |
| RDSMaxAllocatedStorage    | <i>String</i>                    | e.g. 1000 (in GiB)                                                                    |
| StorageType               | <i>String</i>                    | e.g. gp3                                                                              |
| StorageIops               | <i>String</i>                    | e.g. 3000                                                                             |
| MasterUsernameDev         | <i>String</i>                    | e.g. dbadmin                                                                          |
| MasterUserPasswordDev     | <i>String</i>                    | e.g. dbadmin123                                                                       |
| ProdDBPort                | <i>String</i>                    | e.g. 53341                                                                            |
| NProdDBPort               | <i>String</i>                    | e.g. 53331                                                                            |
| UseExistingOptionGroup    | <i>String</i>                    | true/false                                                                            |
| ExistingOptionGroupName   | <i>String</i>                    | Name of existing option group if UseExistingOptionGroup is true                        |
| VpcCidr1                  | <i>String</i>                    | e.g. 10.193.0.0/16 (VPC CIDR for egress rules)                                       |
| VpcCidr2                  | <i>String</i>                    | (Optional) Additional VPC CIDR for egress rules                                       |
| VpcCidr3                  | <i>String</i>                    | (Optional) Additional VPC CIDR for egress rules                                       |
| VpcCidr4                  | <i>String</i>                    | (Optional) Additional VPC CIDR for egress rules                                       |
| VpcCidr5                  | <i>String</i>                    | (Optional) Additional VPC CIDR for egress rules                                       |
| S3PrefixListId            | <i>String</i>                    | (Optional) S3 VPC Endpoint Prefix List ID                                             |
| HCCVpceCidr               | <i>String</i>                    | (Optional) HCC VPC Endpoint Subnet CIDR e.g. 10.48.42.0/24                            |
| PreferredBackupWindow     | <i>String</i>                    | (Optional) Daily backup window in UTC, e.g. 16:00-17:00 (default: 16:00-17:00)        |
| RDSAllowedS3Bucket1       | <i>String</i>                    | (Optional) S3 bucket name to allow in RDS IAM policy                                  |
| RDSAllowedS3Bucket2       | <i>String</i>                    | (Optional) S3 bucket name to allow in RDS IAM policy                                  |
| RDSAllowedS3Bucket3       | <i>String</i>                    | (Optional) S3 bucket name to allow in RDS IAM policy                                  |
| RDSAllowedS3Bucket4       | <i>String</i>                    | (Optional) S3 bucket name to allow in RDS IAM policy                                  |

---

## How to Provision the Template

1. The HIP Team will copy the `parameters.json` file to your project's IaC repository.
2. The project team should update the `parameters.json` file based on the available [parameters](#parameters-and-valid-values) for their environment.

---

## New Features

### Consolidated CIDR Ranges
Support for consolidated CIDR ranges for application subnets allows multiple environments to share the same RDS instance while maintaining proper network access.

### Prefix List Support
Specify an optional AWS Prefix List ID for additional application networks. This allows access from multiple network ranges without modifying the template. Create a prefix list in your AWS account with the required CIDR ranges, then specify the prefix list ID in the `AdditionalAppPrefixList` parameter.

### RDS Allowed S3 Buckets
Optional parameters `RDSAllowedS3Bucket1` through `RDSAllowedS3Bucket4` allow the RDS IAM policy to access additional S3 buckets for native backup/restore operations or data migration purposes. When specified, the RDS role will have read/write access to these buckets in addition to the stack's own S3 bucket.

### Configurable Backup Window
The `PreferredBackupWindow` parameter allows customization of the daily automated backup window without modifying the template. This is useful when backup windows need to be adjusted for operational requirements.

---

# Amazon RDS Read Replica

This template can also provision an RDS Read Replica with the following prerequisites:
- RDS Parameter Group
- RDS Read Replica Instance

## Parameters and Valid Values for Read Replica

| Parameter                        | Value Type        | Allowed Values/Example                                                                 |
|-----------------------------------|------------------|---------------------------------------------------------------------------------------|
| AppShortName                      | <i>String</i>    | e.g. grm                                                                              |
| EnvName                           | <i>String</i>    | nprd, nprd-dev, nprd-sit1, nprd-sit2, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b, prod, prod-a, prod-b |
| ReadReplicaRdsDBParameterGroupFamily | <i>String</i> | e.g. sqlserver-ee-16.0                                                                |
| DBEngine                          | <i>String</i>    | sqlserver-se, sqlserver-ee                                                            |
| ReadReplicaDBInstanceClass        | <i>String</i>    | e.g. db.m6i.xlarge                                                                    |

---

## How to Provision the Read Replica Template

1. The HIP Team will copy the `parameters.json` file to your project's IaC repository.
2. The project team should update the `parameters.json` file based on the available parameters for their environment.

> **Note:**  
> The Read Replica will automatically use the source DB instance identifier from the SSM Parameter Store created by the primary RDS instance template.

---

# Release Notes

## v5.1 (2026-01-28)

- **Security Group Egress Enhancement:** Enabled explicit egress rules on the RDS security group restricting outbound traffic to TCP 443 only for specified VPC CIDRs, S3 VPC endpoint, and HCC VPC endpoint. This replaces the default allow-all egress rule with least-privilege outbound access.
- **Extended VPC CIDR Support:** Added `VpcCidr4` and `VpcCidr5` parameters to support up to 5 VPC CIDR ranges for egress rules (up from 3 in v5).
- **Parameterized Backup Window:** Added `PreferredBackupWindow` parameter to allow customization of the daily automated backup window without template modification. Default remains `16:00-17:00` UTC.
- **RDS Allowed S3 Buckets:** Replaced `DataMigrationBucket1` and `DataMigrationBucket2` with `RDSAllowedS3Bucket1` through `RDSAllowedS3Bucket4`, expanding support from 2 to 4 external S3 buckets in the RDS IAM policy for native backup/restore operations.
- **No Breaking Changes:** All existing resource logical names, ingress rules, and other configurations remain identical to v5. Existing deployments can adopt the new parameters without impact.

## v5 (2025-06-02)

- **Enhanced Parameterization:** Added support for consolidated CIDR ranges for application subnets, enabling multiple environments to share the same RDS instance with proper network access.
- **Prefix List Support:** Introduced the `AdditionalAppPrefixList` parameter to allow specifying AWS Prefix List IDs for additional application networks, improving flexibility and security.
- **Expanded Parameter Table:** Updated and clarified parameter tables for both primary RDS and Read Replica templates, including examples and allowed values.
- **Read Replica Improvements:** The Read Replica template now automatically references the source DB instance identifier from the SSM Parameter Store created by the primary RDS template.
- **Documentation Updates:** Improved instructions for provisioning both the primary RDS and Read Replica templates, and clarified the use of new features.
- **General Enhancements:** Minor formatting and consistency improvements throughout the documentation.

---