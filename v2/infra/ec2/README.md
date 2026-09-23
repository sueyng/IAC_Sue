# EC2 Instance Template

**Amazon EC2** provides a wide selection of instance types optimized to fit different use cases. Instance types comprise varying combinations of CPU, memory, storage, and networking capacity and give you the flexibility to choose the appropriate mix of resources for your applications. Each instance type includes one or more instance sizes, allowing you to scale your resources to the requirements of your target workload. This template provisions `EC2 instance` base on the parameter values that will be passed using parametee file e.g `params.json`

This template provisions the following resources:
* IAM Role for EC2 instance
* EC2 Instance Profile
* EC2 Key Pair
* Lauch Template
* Security Group
* EC2 Instance
* EBS Volume



## Provisioning

Resource provisioning consist of sequential steps that must be observed diligently. Since prior steps are pre requisite to another.

Provisioning steps are as follows:
* Provision base components like launch template, ssh key pairs, roles and instance profiles `cf-ec2-launchTemplate.yaml`
* Provision security groups `cf-securitygroups.yaml`
* Finally provisioning of servers in form of EC2 `cf-ec2.yaml`

## Parameters and its valid values
### Launch template provisioning

|ParameterKey  | Value Type | Allowed Values  | 
|---|---|---|
| AppShortName  |  <i>String</i>        |      e.g checkout-app      | 
|   EnvName     |  <i>String</i>        |  nprd, nprd-dev, nprd-sit1, nprd-sit2, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b, prod, prod-a, prod-b |
|   VpcId       | <i>AWS::EC2::VPC::Id</i>  | e.g vpc-120324  |


### Security Groups
|ParameterKey  | Value Type | Allowed Values  | 
|---|---|---|
| AppShortName      |  <i>String</i>        |      e.g checkout-app      | 
|   EnvName         |  <i>String</i>        |  nprd, nprd-dev, nprd-sit1, nprd-sit2, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b, prod, prod-a, prod-b |
|   VpcId           | <i>AWS::EC2::VPC::Id</i>  | e.g vpc-120324                |
| Function          | <i>String</i>         |APP, WEB, DB, UTL, INT, RPT, SYS   |
|ALBSecurityGroupId | <i>String</i>         |e.g sg-12345                       |

### EC2 Instance
|ParameterKey  | Value Type | Allowed Values  | 
|---|---|---|
| AvailabilityZone  |  <i>String</i>        |    ap-southeast-1a, ap-southeast-1b, ap-southeast-1c      | 
|   EnvName         |  <i>String</i>        |  nprd, nprd-dev, nprd-sit1, nprd-sit2, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b, prod, prod-a, prod-b |
|   AMIId           |   <i>AWS::EC2::Image::Id</i>  | e.g ami-123213  |
|   InstanceName    |   <i>String</i>         | e.g My-Server-Name |
|   SubnetIdappAZ1  |   <i>AWS::EC2::Subnet::Id</i>      | e.g subnet-09941b39be5bcb170 |
|   InstanceType    |   <i>String</i>   |   e.g t2.micro        |
|   DataVolumeSize  |   <i>String</i>   |   e.g 20 (20 GiB)     |
|   OSVolumeSize    |   <i>String</i>   |   e.g 100 (in GiB)    |
|   Function        |   <i>String</i>   |   APP, UTL, DB, UTL, RPT, SYS     |
|   EC2InfraSecurityGroupID |   <i>String</i>   |   sg-123123   |
## How to use the template
* **HIP Team** will copy the parameters.json to the project's IAC Repository. Project team will update the parameters json base on the available [parameters](#parameters-and-its-valid-values) in their own project repository.

* Below is an example of how your directory would look like:
```
nprd-dev
 |_ parameters-ec2-launchTemplate.json
 |_ parameters-ec2-securitygroups.json
 |_ parameters-ec2.json
```