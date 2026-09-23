# AMAZON RELATIONAL DATABASE SERVICE

Amazon RDS is an easy to manage relational database service optimized for total cost of ownership. It is simple to set up, operate, and scale with demand. Amazon RDS automates the undifferentiated database management tasks, such as provisioning, configuring, backups, and patching. Provisioning of this template is straight forward. see this [instruction](#how-to-provision-template)

This template provisions RDS instance (Standalone or Multi-AZ) with the prerequisites as below:
* KMS Keys (RDS Encryption & Performance Monitoring)
* KMS Aliases
* S3 Buckets (Audit & Native Backup)
* IAM Roles & Policies
* RDS Subnet Group
* DB Parameter Group
* RDS Option Group
* RDS DB Instance
* Security Groups
* SSM Parameter Store

## Parameters and its valid values

|ParameterKey  | ValueType | Allowed Values/Example  | 
|---|---|---|
| AppShortName  |   <i>String</i>               |   e.g my-application  |
|   EnvName     |   <i>String</i>               |  nprd, nprd-dev, nprd-sit1, nprd-sit2, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b, prod, prod-a, prod-b |
| VpcId | <i>AWS::EC2::VPC::Id</i> | e.g vpc-0d99a0c727b301d67 |
| AvailabilityZone | <i>AWS::EC2::AvailabilityZone::Name</i> | ap-southeast-1a, ap-southeast-1b, ap-southeast-1c |
| VPCSubnetCidrAppAZ1 | <i>String</i> | e.g 10.1.128.0/20 |
| VPCSubnetCidrAppAZ2 | <i>String</i> | e.g 10.1.144.0/20 |
| VPCSubnetCidrAppAZ3 | <i>String</i> | e.g 10.1.160.0/20 |
| DBSubnetCidrAZ1 | <i>String</i> | e.g 10.1.0.0/20 |
| DBSubnetCidrAZ2 | <i>String</i> | e.g 10.1.16.0/20 |
| DBSubnetCidrAZ3 | <i>String</i> | e.g 10.1.32.0/20 |
| DBSubnetIds | <i>List<AWS::EC2::Subnet::Id></i> | e.g subnet-08170d48a795103d2,subnet-083fba964c347656f,subnet-0e54709c5b9c524e1 |
| DeploymentServer | <i>String</i> | e.g 10.53.26.197/32 |
| MultiAZ | <i>String</i> | true/false |
| RdsDBParameterGroupFamily | <i>String</i> | e.g sqlserver-ee-16.0 |
| DBInstanceClass | <i>String</i> | e.g db.m6i.xlarge |
| DBEngine | <i>String</i> | sqlserver-se, sqlserver-ee |
| DBMajorEngineVersion | <i>String</i> | e.g 16.00 |
| EngineVersion | <i>String</i> | e.g 16.00.4095.4.v1 |
| AllocatedStorage | <i>String</i> | e.g 100 (in GiB) |
| RDSMaxAllocatedStorage | <i>String</i> | e.g 1000 (in GiB) |
| StorageType | <i>String</i> | e.g gp3 |
| StorageIops | <i>String</i> | e.g 3000 |
| MasterUsernameDev | <i>String</i> | e.g dbadmin |
| MasterUserPasswordDev | <i>String</i> | e.g dbadmin123 |
| ProdDBPort | <i>String</i> | e.g 53341 |
| NProdDBPort | <i>String</i> | e.g 53331 |
| UseExistingOptionGroup | <i>String</i> | true/false |
| ExistingOptionGroupName | <i>String</i> | Name of existing option group if UseExistingOptionGroup is true |

## How to provision template

HIP Team will copy the parameters.json to the project's IAC Repository. Project team will update the parameters json base on the available [parameters](#parameters-and-its-valid-values) in their own project repository.

# Amazon Relational Database Service (Read Replica)

This template provisions an RDS Read Replica with the following prerequisites:
* RDS Parameter Group
* RDS Read Replica Instance

## Parameters and Valid Values for Read Replica

|Parameter|Value Type|Allowed Values/Example|
|---|---|---|
|AppShortName|<i>String</i>|e.g grm|
|EnvName|<i>String</i>|nprd, nprd-dev, nprd-sit1, nprd-sit2, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b, prod, prod-a, prod-b|
|ReadReplicaRdsDBParameterGroupFamily|<i>String</i>|e.g sqlserver-ee-16.0|
|DBEngine|<i>String</i>|sqlserver-se, sqlserver-ee|
|ReadReplicaDBInstanceClass|<i>String</i>|e.g db.m6i.xlarge|

## How to Provision Read Replica Template

The HIP Team will copy the parameters.json to the project's IaC Repository. The project team will update the parameters.json based on the available parameters in their own project repository.

Note: The Read Replica will automatically use the source DB instance identifier from SSM Parameter Store that was created by the primary RDS instance template.