# VPC ENDPOINT
A **VPC endpoint** enables customers to privately connect to supported AWS services and VPC endpoint services powered by AWS PrivateLink.

This template provisions the following resources:
* Security Group
* VPC Endpoint

A VPC endpoint enables customers to privately connect to supported AWS services and VPC endpoint services powered by AWS PrivateLink.

Provisioning of this template is straight forward. See this [instruction](#how-to-provision-template)

## Parameters and its valid values

|ParameterKey  | Value Type | Allowed Values  | Description | Mandatory |
|---|---|---|---|---|
| AppShortName  |   <i>String</i>               |   e.g my-application  | Short name for your application | Yes |
|   AWSRegion   |   <i>String</i>               |   ap-southeast-1      | AWS Region | Yes |
|   VpcId       |   <i>AWS::EC2::VPC::Id</i>    |   e.g vpc-120324     | VPC ID | Yes |
|   VpcCidr1    |   <i>String</i>               |   e.g 10.0.0.0/16    | Primary VPC CIDR Range | Yes |
|   VpcCidr2    |   <i>String</i>               |   e.g 10.1.0.0/16    | Secondary VPC CIDR Range | Yes |
|   VpcCidr3    |   <i>String</i>               |   e.g 10.2.0.0/16    | Optional Third VPC CIDR Range | No |
|   VpcCidr4    |   <i>String</i>               |   e.g 10.3.0.0/16    | Optional Fourth VPC CIDR Range | No |
|   VpcCidr5    |   <i>String</i>               |   e.g 10.4.0.0/16    | Optional Fifth VPC CIDR Range | No |
|  AppSubnetIds |  <i>List<AWS::EC2::Subnet::Id></i>   | e.g subnet-123232,subnet-2345123,subnet-323122 | List of subnet IDs | Yes |
|   EnvName     |   <i>String</i>               |  nprd, nprd-dev, nprd-sit1, nprd-sit2, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b, prod, prod-a, prod-b | Environment name | Yes |
| CreateGrafanaEndpoint | <i>String</i> | true, false | Enable Grafana endpoint | No (defaults to false) |
| CreateEKSEndpoint | <i>String</i> | true, false | Enable EKS endpoint | No (defaults to false) |
| CreateXRayEndpoint | <i>String</i> | true, false | Enable X-Ray endpoint | No (defaults to false) |
| CreateAMPEndpoint | <i>String</i> | true, false | Enable AMP endpoint | No (defaults to false) |
| CreateECREndpoints | <i>String</i> | true, false | Enable ECR endpoints | No (defaults to false) |
| CreateELBEndpoint | <i>String</i> | true, false | Enable ELB endpoint | No (defaults to false) |
| CreateSecretsEndpoint | <i>String</i> | true, false | Enable Secrets Manager endpoint | No (defaults to false) |
| CreateElasticacheEndpoint | <i>String</i> | true, false | Enable Elasticache endpoint | No (defaults to false) |
| CreateSESEndpoint | <i>String</i> | true, false | Enable SES endpoint | No (defaults to false) |
| CreateAPIGatewayEndpoint | <i>String</i> | true, false | Enable API Gateway endpoint | No (defaults to false) |
| CreateSQSEndpoint | <i>String</i> | true, false | Enable SQS endpoint | No (defaults to false) |
| CreateRDSEndpoint | <i>String</i> | true, false | Enable RDS endpoint | No (defaults to false) |
| CreateLambdaEndpoint | <i>String</i> | true, false | Enable Lambda endpoint | No (defaults to false) |
| CreateS3Endpoint | <i>String</i> | true, false | Enable S3 endpoint | No (defaults to false) |
| CreateECSEndpoint | <i>String</i> | true, false | Enable ECS endpoint | No (defaults to false) |
| CreateCloudFormationEndpoint | <i>String</i> | true, false | Enable CloudFormation endpoint | No (defaults to false) |
| CreateGlueEndpoint | <i>String</i> | true, false | Enable Glue endpoint | No (defaults to false) |
| CreateDataSyncEndpoint | <i>String</i> | true, false | Enable DataSync endpoint | No (defaults to false) |
| CreateSNSEndpoint | <i>String</i> | true, false | Enable SNS endpoint | No (defaults to false) |
| CreateBatchEndpoint | <i>String</i> | true, false | Enable Batch endpoint | No (defaults to false) |
| CreateAthenaEndpoint | <i>String</i> | true, false | Enable Athena endpoint | No (defaults to false) |
| CreateCloudWatchLogsEndpoint | <i>String</i> | true, false | Enable CloudWatch Logs endpoint | No (defaults to false) |
| CreateACMEndpoint | <i>String</i> | true, false | Enable AWS Certificate Manager (ACM) endpoint | No (defaults to false) |

## Available VPC Endpoints

This template supports the following VPC endpoints:

| Service | Parameter | Description |
|---|---|---|
| Grafana | CreateGrafanaEndpoint | Creates endpoints for Grafana and Grafana Workspace |
| EKS | CreateEKSEndpoint | Creates endpoint for Amazon Elastic Kubernetes Service |
| X-Ray | CreateXRayEndpoint | Creates endpoint for AWS X-Ray |
| AMP | CreateAMPEndpoint | Creates endpoint for Amazon Managed Service for Prometheus |
| ECR | CreateECREndpoints | Creates endpoints for Amazon Elastic Container Registry (API and Docker) |
| ELB | CreateELBEndpoint | Creates endpoint for Elastic Load Balancing |
| Secrets Manager | CreateSecretsEndpoint | Creates endpoint for AWS Secrets Manager |
| Elasticache | CreateElasticacheEndpoint | Creates endpoint for Amazon Elasticache |
| SES | CreateSESEndpoint | Creates endpoint for Amazon Simple Email Service |
| API Gateway | CreateAPIGatewayEndpoint | Creates endpoint for Amazon API Gateway |
| SQS | CreateSQSEndpoint | Creates endpoint for Amazon Simple Queue Service |
| RDS | CreateRDSEndpoint | Creates endpoint for Amazon Relational Database Service |
| Lambda | CreateLambdaEndpoint | Creates endpoint for AWS Lambda |
| S3 | CreateS3Endpoint | Creates endpoint for Amazon Simple Storage Service |
| ECS | CreateECSEndpoint | Creates endpoint for Amazon Elastic Container Service |
| CloudFormation | CreateCloudFormationEndpoint | Creates endpoint for AWS CloudFormation |
| Glue | CreateGlueEndpoint | Creates endpoint for AWS Glue |
| DataSync | CreateDataSyncEndpoint | Creates endpoint for AWS DataSync |
| SNS | CreateSNSEndpoint | Creates endpoint for Amazon Simple Notification Service |
| Batch | CreateBatchEndpoint | Creates endpoint for AWS Batch |
| Athena | CreateAthenaEndpoint | Creates endpoint for Amazon Athena |
| CloudWatch Logs | CreateCloudWatchLogsEndpoint | Creates endpoint for Amazon CloudWatch Logs |
| ACM | CreateACMEndpoint | Creates endpoint for AWS Certificate Manager (`com.amazonaws.{region}.acm`) |

## How to provision template

HIP Team will copy the parameters.json to the project's IAC Repository. Project team will update the parameters json base on the available [parameters](#parameters-and-its-valid-values) in their own project repository.

### Example Usage

To enable specific endpoints, set their corresponding parameters to "true" in the parameters.json file. For example:

```json
{
    "ParameterKey": "VpcCidr1",
    "ParameterValue": "10.193.0.0/16"
},
{
    "ParameterKey": "VpcCidr2",
    "ParameterValue": "10.194.0.0/16"
},
{
    "ParameterKey": "VpcCidr3",
    "ParameterValue": "10.195.0.0/16"
},
{
    "ParameterKey": "CreateGlueEndpoint",
    "ParameterValue": "true"
},
{
    "ParameterKey": "CreateAthenaEndpoint",
    "ParameterValue": "true"
}
```

### Important Notes
1. VpcCidr1 and VpcCidr2 are mandatory parameters
2. VpcCidr3, VpcCidr4, VpcCidr5 are optional and can be left empty if not needed
3. All endpoint creation parameters default to "false" if not specified
4. Security group rules will automatically include all specified CIDR ranges
5. All mandatory parameters must be provided when deploying the template
6. For optional parameters, you can either omit them or provide their default values
7. RDS endpoint uses its own dedicated security group for custom port configuration
8. Most endpoints use the main security group with standard HTTPS (443) access
