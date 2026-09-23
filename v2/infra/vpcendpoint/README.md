# VPC ENDPOINT
A **VPC endpoint** enables customers to privately connect to supported AWS services and VPC endpoint services powered by AWS PrivateLink.

This template provisions the following resources:
* Security Group
* VPC Endpoint

A VPC endpoint enables customers to privately connect to supported AWS services and VPC endpoint services powered by AWS PrivateLink.

Provisioning of this template is straight forward. see this [instruction](#how-to-provision-template)
## Parameters and its valid values

|ParameterKey  | Value Type | Allowed Values  | 
|---|---|---|
| AppShortName  |   <i>String</i>               |   e.g my-application  |
|   AWSRegion   |   <i>String</i>               |   ap-southeast-1      | 
|   VpcId       |   <i>AWS::EC2::VPC::Id</i>    |   e.g vpc-120324      |
|   VpcCidr1    |   <i>String</i>               |   e.g 10.0.0.0/16     |
|   VpcCidr2    |   <i>String</i>               |   e.g 10.1.0.0/16     |
|  AppSubnetIds |  <i>List<AWS::EC2::Subnet::Id></i>   | e.g subnet-123232,subnet-2345123,subnet-323122 |
|   EnvName     |   <i>String</i>               |  nprd, nprd-dev, nprd-sit1, nprd-sit2, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b, prod, prod-a, prod-b |

## How to provision template

HIP Team will copy the parameters.json to the project's IAC Repository. Project team will update the parameters json base on the available [parameters](#parameters-and-its-valid-values) in their own project repository.