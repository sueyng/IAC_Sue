# AMAZON MANAGED GRAFANA

**Amazon Managed Grafana** is a fully managed service for Grafana, a popular open-source analytics platform that enables you to query, visualize, and alert on your metrics, logs, and traces. For more information please visit this [site](https://aws.amazon.com/grafana/).

This template provisions the following resources:
* EC2: Prefix List
* Security Group
* IAM Role
* IAM Policy
* Grafana Workspace


Provisioning of this template is straight forward. see this [instruction](#how-to-provision-template)
## Parameters and its valid values

|ParameterKey  | ValueType | Allowed Values  | 
|---|---|---|
| AppShortName  |   <i>String</i>               |   e.g my-application  |
|   EnvName     |   <i>String</i>               |  nprd, nprd-dev, nprd-sit1, nprd-sit2, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b, prod, prod-a, prod-b |
|   VpcId           | <i>AWS::EC2::VPC::Id</i>  | e.g vpc-120324                |
|  AppSubnetIds |  <i>List<AWS::EC2::Subnet::Id></i>   | e.g subnet-123232,subnet-2345123,subnet-323122 |
| AuthProvider  |   <i>String</i>               |  AWS_SSO, SAML  |
## How to provision template

HIP Team will copy the parameters.json to the project's IAC Repository. Project team will update the parameters json base on the available [parameters](#parameters-and-its-valid-values) in their own project repository.