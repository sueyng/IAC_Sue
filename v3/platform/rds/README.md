# AMAZON RELATIONAL DATABASE SERVICE

Amazon RDS is an easy to manage relational database service optimized for total cost of ownership. It is simple to set up, operate, and scale with demand. Amazon RDS automates the undifferentiated database management tasks, such as provisioning, configuring, backups, and patching. Provisioning of this template is straight forward. see this [instruction](#how-to-provision-template)

This template provisions RDS instance/CLuster (Standalone or Multi-AZ) with the prerequistics as below:
* KMS Key
* KMS Alias
* S3 Bucket
* IAM Role
* IAM Policy
* IAM Managed Policy
* RDS Subnet Group
* DB Parameter Group
* RDS Option Group
* RDS DB Instance

## Parameters and its valid values

|ParameterKey  | ValueType | Allowed Values  | 
|---|---|---|
| AppShortName  |   <i>String</i>               |   e.g my-application  |
|   EnvName     |   <i>String</i>               |  nprd, nprd-dev, nprd-sit1, nprd-sit2, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b, prod, prod-a, prod-b |
|   VpcId           | <i>AWS::EC2::VPC::Id</i>  | e.g vpc-120324                |
|  AppSubnetIds |  <i>List<AWS::EC2::Subnet::Id></i>   | e.g subnet-123232,subnet-2345123,subnet-323122 |
|AvailabilityZone|<i>AWS::EC2::AvailabilityZone::Name</i>|ap-southeast-1a,ap-southeast-1b,ap-southeast-1c|
|   VPCSubnetCidrAppAZ1     |   <i>String</i>   |   e.g 10.0.1.0/24     |
|   VPCSubnetCidrAppAZ2     |   <i>String</i>   |   e.g 10.0.2.0/24     |
|   VPCSubnetCidrAppAZ3     |   <i>String</i>   |   e.g 10.0.3.0/24     |
|   DBSubnetIds     |   <i>List<AWS::EC2::Subnet::Id></i>   |   e.g subnet-12321,subnet-23123,subnet-12321     |
|  DeploymentServer |<i>String</i>| e.g 10.0.2.3 |
|  MultiAZ |<i>String</i>| e.g true |
|   DBInstanceClass  | <i>String</i> | e.g db.m6i.xlarge |
|   DBEngine  | <i>String</i> | sqlserver-se, sqlserver-ee|
|   DBMajorEngineVersion  | <i>String</i> | e.g 16.00 |
|   RdsDBParameterGroupFamily  | <i>String</i> |  e.g sqlserver-se-16.0 |
|   EngineVersion  | <i>String</i> |  e.g 16.00.4095.4.v1 |
|   AllocatedStorage  | <i>String</i> | e.g 30 (in GiB )|
|   StorageType  | <i>String</i> | e.g db.t4g.medium |
|   StorageIops  | <i>String</i> | e.g 3000 |
|   MasterUsernameDev  | <i>String</i> | e.g admin |
|   MasterUserPasswordDev   | <i>String</i> | e.g dbadmin123 |
|   ProdDBPort   | <i>String</i> | e.g 53341 |
|   NProdDBPort   | <i>String</i> | e.g 53331 |

## How to provision template

HIP Team will copy the parameters.json to the project's IAC Repository. Project team will update the parameters json base on the available [parameters](#parameters-and-its-valid-values) in their own project repository.

# Amazon Relational Database Service (Read Replica)

Amazon RDS is an easy-to-manage relational database service optimized for total cost of ownership. It is simple to set up, operate, and scale with demand. 
Amazon RDS automates undifferentiated database management tasks, such as provisioning, configuring, backups, and patching. 
Provisioning this template is straightforward. See the instructions below.

This template provisions an RDS Read Replica with the following prerequisites:
 * RDS Parameter Group
 * RDS Read Replica Instance

## Parameters and Valid Values
|   Parameter   |   Key	Value Type  |   Allowed Values  |
|----|---|---|
|   AppShortName    | <i>String</i>	    |   e.g., my-application    |
|   EnvName         | <i>String</i>     |  nprd, nprd-dev, nprd-sit1, nprd-sit2, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b, prod, prod-a, prod-b |
|   ReadReplicaRdsDBParameterGroupFamily	|   <i>String</i>   |   e.g., sqlserver-ee-16.0 |
|   DBEngine    |   <i>String</i>	|   sqlserver-se, sqlserver-ee  |
|   ReadReplicaDBInstanceClass| <i>String</i>   |	e.g., db.m6i.xlarge |
|   SourceDBInstance    |   <i>String</i>   |	e.g., grm-nprd-uat-rdssql   |


## How to Provision Template
The HIP Team will copy the parameters.json to the project's IaC Repository. The project team will update the parameters.json based on the available parameters in their own project repository.
