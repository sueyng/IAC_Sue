# AMAZON RELATIONAL DATABASE SERVICE PROXY

Amazon RDS Proxy provides connection pooling and helps reduce the load on database resources and impact of connection management by scaling connections efficiently. RDS Proxy can help applications be more resilient to database failures by automatically connecting to a new primary instance while preserving application connections.

This template provisions RDS Proxy with the prerequisites as below:
* IAM Role for Proxy
* Security Group for Proxy
* RDS Proxy
* Proxy Target Group

## Parameters and its valid values

|ParameterKey  | ValueType | Allowed Values  | Description |
|---|---|---|---|
| AppShortName | <i>String</i> | e.g my-application | Application short name |
| EnvName | <i>String</i> | nprd, nprd-dev, nprd-sit1, nprd-sit2, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b, prod, prod-a, prod-b | Environment name |
| VpcId | <i>AWS::EC2::VPC::Id</i> | e.g vpc-120324 | VPC ID where RDS Proxy will be deployed |
| DBSubnetIds | <i>List<AWS::EC2::Subnet::Id></i> | e.g subnet-123232,subnet-2345123,subnet-323122 | Subnet IDs where RDS Proxy will be deployed |
| DBInstanceIdentifier | <i>String</i> | e.g my-app-nprd-rdssql | The RDS instance identifier to associate with the proxy |
| VPCSubnetCidrAppAZ1 | <i>String</i> | e.g 10.0.1.0/24 | Application subnet CIDR in AZ1 |
| VPCSubnetCidrAppAZ2 | <i>String</i> | e.g 10.0.2.0/24 | Application subnet CIDR in AZ2 |
| VPCSubnetCidrAppAZ3 | <i>String</i> | e.g 10.0.3.0/24 | Application subnet CIDR in AZ3 |
| DeploymentServer | <i>String</i> | e.g 10.0.2.3/32 | Deployment server IP address |
| DBProxySecretArn | <i>String</i> | e.g arn:aws:secretsmanager:region:account:secret:name | ARN of the Secret containing RDS Proxy credentials |
| ProdDBPort | <i>String</i> | Default: 53341 | Database port for production |
| NProdDBPort | <i>String</i> | Default: 53331 | Database port for non-production |
| MaxConnectionsPercent | <i>Number</i> | 1-100 (Default: 100) | Maximum connections as a percentage |
| MaxIdleConnectionsPercent | <i>Number</i> | 1-100 (Default: 50) | Maximum idle connections as a percentage |

## How to provision template

HIP Team will copy the parameters.json to the project's IAC Repository. Project team will update the parameters json based on the available parameters in their own project repository.

## Important Notes

1. RDS Proxy supports specific database versions. For SQL Server, check AWS documentation for supported versions. https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.RDS_Fea_Regions_DB-eng.Feature.RDSProxy.html
2. The proxy must be in the same VPC as the database.
3. Applications will connect to the RDS Proxy endpoint instead of connecting directly to the RDS instance.
4. The secret in Secrets Manager must contain valid database credentials.


## Architecture Flow

```
Application --> RDS Proxy --> RDS Instance
```

The RDS Proxy acts as an intermediary between your application and the database, managing connection pooling and providing additional resilience to your database connections.

## Template Resources

This template creates the following resources:

### IAM Resources
* `DBProxyRole`: IAM role for RDS Proxy with permissions to access Secrets Manager
* Access policies for Secrets Manager

### Security Resources
* `RdsProxySecurityGroup`: Security group for RDS Proxy with inbound rules from application subnets

### RDS Proxy Resources
* `RDSProxy`: The main RDS Proxy resource
* `ProxyTargetGroup`: Target group associating the proxy with RDS instance

## Outputs

The template provides the following outputs:

| Output Name | Description |
|------------|-------------|
| RDSProxyEndpoint | The endpoint of the RDS Proxy |
| RDSProxyArn | The ARN of the RDS Proxy |
| RDSProxySecurityGroupId | The Security Group ID for the RDS Proxy |