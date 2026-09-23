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

## v5 (2025-06-02)

- **Enhanced Parameterization:** Added support for consolidated CIDR ranges for application subnets, enabling multiple environments to share the same RDS instance with proper network access.
- **Prefix List Support:** Introduced the `AdditionalAppPrefixList` parameter to allow specifying AWS Prefix List IDs for additional application networks, improving flexibility and security.
- **Expanded Parameter Table:** Updated and clarified parameter tables for both primary RDS and Read Replica templates, including examples and allowed values.
- **Read Replica Improvements:** The Read Replica template now automatically references the source DB instance identifier from the SSM Parameter Store created by the primary RDS template.
- **Documentation Updates:** Improved instructions for provisioning both the primary RDS and Read Replica templates, and clarified the use of new features.
- **General Enhancements:** Minor formatting and consistency improvements throughout the documentation.

---