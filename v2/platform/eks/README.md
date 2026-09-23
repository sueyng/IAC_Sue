# ELASTIC KUBERNETES SERVICE

**Amazon Elastic Kubernetes Service** (Amazon EKS) is a managed service that eliminates the need to install, operate, and maintain your own Kubernetes control plane on Amazon Web Services (AWS). Kubernetes is an open-source system that automates the management, scaling, and deployment of containerized applications. For more information visit this [site](https://docs.aws.amazon.com/eks/latest/userguide/what-is-eks.html). 
Provisioning of this template is straight forward. see this [instruction](#how-to-provision-template)


This template provisions the following resources:
* Fargate Profile
* Network Load Balancer
* Load Balancer: Target Group
* Load Balancer: Listener
* KMS Key
* KMS Alias
* Secret Manager: Secret
* IAM Managed Policy
* IAM Role
* Security Group
* Security Group: Ingress
* EKS Cluster
* EKS Add on


## Parameters and its valid values
Parameter values for `cf-eks-fp` template
### EKS Fargate Profile
|ParameterKey  | ValueType | Allowed Values  | 
|---|---|---|
| AppShortName  |   <i>String</i>               |   e.g my-application  |
|   EnvName     |   <i>String</i>               |  nprd, nprd-dev, nprd-sit1, nprd-sit2, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b, prod, prod-a, prod-b |
| FargateProfileName |  <i>String</i>          |  e.g my-app-fp        |
| NameSpaces         |  <i>String</i>          | e.g namespace1,namespace2  |
|  AppSubnetIds |  <i>List<AWS::EC2::Subnet::Id></i>   | e.g subnet-123232,subnet-2345123,subnet-323122 |

### EKS Cluster
Parameter values for `cf-eks` template
|ParameterKey  | ValueType | Allowed Values  | 
|---|---|---|
| AppShortName  |   <i>String</i>               |   e.g my-application  |
|   EnvName     |   <i>String</i>               |  nprd, nprd-dev, nprd-sit1, nprd-sit2, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b, prod, prod-a, prod-b |
|  AppSubnetIds |  <i>List<AWS::EC2::Subnet::Id></i>   | e.g subnet-123232,subnet-2345123,subnet-323122 |
| AWSRegion |   <i>String</i> | ap-southeast-1 |
|   VpcId           | <i>AWS::EC2::VPC::Id</i>  | e.g vpc-120324        |
|   VPCSubnetCidrAppAZ1     |   <i>String</i>   |   e.g 10.0.1.0/24     |
|   VPCSubnetCidrAppAZ2     |   <i>String</i>   |   e.g 10.0.2.0/24     |
|   VPCSubnetCidrAppAZ3     |   <i>String</i>   |   e.g 10.0.3.0/24     |
|   AppIngressNodePort      |   <i>String</i>   |   e.g 8080            |
|   AppIngressNodePort      |   <i>String</i>   |   e.g 8080            |
|   HIPDeploymentServer01   |   <i>String</i>   |   e.g 10.0.2.4        |
|   HIPDeploymentServer02   |   <i>String</i>   |   e.g 10.0.2.5        |
|   DeploymentServerUTL01   |   <i>String</i>   |   e.g 10.0.2.8        |

### Network Load Balancer, Transit Gateway and Application Load Balancer 
Parameter values for `cf-nlb-tg-alb` template
|ParameterKey  | ValueType | Allowed Values  | 
|---|---|---|
| AppShortName  |   <i>String</i>               |   e.g my-application  |
|   EnvName     |   <i>String</i>               |  nprd, nprd-dev, nprd-sit1, nprd-sit2, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b, prod, prod-a, prod-b |
|  AppSubnetIds |  <i>List<AWS::EC2::Subnet::Id></i>   | e.g subnet-123232,subnet-2345123,subnet-323122 |
|   VpcId           | <i>AWS::EC2::VPC::Id</i>  | e.g vpc-120324        |
|   Function        |   <i>String</i>   |   APP, UTL, DB, UTL, RPT, SYS |
|   IngressALBArn   |   <i>String</i>   |   e.g arn:aws:elasticloadbalancing:us-west-2:123456789012:loadbalancer/app/example-lb/1   |
## How to provision template

* HIP Team will copy the parameters.json to the project's IAC Repository. Project team will update the parameters json base on the available [parameters](#parameters-and-its-valid-values) in their own project repository.

* Below is an example of how your directory would look like:
```
nprd-dev
 |_ parameters-eks-fp.json
 |_ parameters-eks.json
 |_ parameters-nlb-tg-alb.json
```