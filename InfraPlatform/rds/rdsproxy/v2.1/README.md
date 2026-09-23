# AMAZON RELATIONAL DATABASE SERVICE PROXY

Amazon RDS Proxy provides connection pooling and helps reduce the load on database resources and impact of connection management by scaling connections efficiently. RDS Proxy can help applications be more resilient to database failures by automatically connecting to a new primary instance while preserving application connections.

This template provisions RDS Proxy with the prerequisites as below:
* IAM Role for Proxy
* Security Group for Proxy (with tightened ingress and egress rules)
* RDS Proxy
* Proxy Target Group

## Parameters and its valid values

|ParameterKey  | ValueType | Allowed Values  | Description |
|---|---|---|---|
| AppShortName | *String* | e.g my-application | Application short name |
| EnvName | *String* | nprd, nprd-dev, nprd-dev1, nprd-dev2, nprd-sit1, nprd-sit2, nprd-sit3, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-sit-c, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-uat-c, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b, nprd-pp-c, prod, prod-a, prod-b, prod-c | Environment name |
| VpcId | *AWS::EC2::VPC::Id* | e.g vpc-120324 | VPC ID where RDS Proxy will be deployed |
| DBSubnetIds | *List\<AWS::EC2::Subnet::Id\>* | e.g subnet-123232,subnet-2345123,subnet-323122 | Subnet IDs where RDS Proxy will be deployed |
| DBInstanceIdentifier | *String* | e.g my-app-nprd-rdssql | The RDS instance identifier to associate with the proxy |
| VPCSubnetCidrAppAZ1 | *String* | e.g 10.0.1.0/24 | Application subnet CIDR in AZ1 |
| VPCSubnetCidrAppAZ2 | *String* | e.g 10.0.2.0/24 | Application subnet CIDR in AZ2 |
| VPCSubnetCidrAppAZ3 | *String* | e.g 10.0.3.0/24 | Application subnet CIDR in AZ3 (optional) |
| DeploymentServer | *String* | e.g 10.0.2.3/32 | Deployment server IP address |
| DBProxySecretArn | *String* | e.g arn:aws:secretsmanager:region:account:secret:name | ARN of the Secret containing RDS Proxy credentials |
| RDSProxyPort | *String* | Default: 1433 | Port the RDS Proxy listens on for client connections (ingress) |
| ProdDBPort | *String* | 53341 (locked) | RDS instance port for production (egress) - DO NOT CHANGE |
| NProdDBPort | *String* | 53331 (locked) | RDS instance port for non-production (egress) - DO NOT CHANGE |
| MaxConnectionsPercent | *Number* | 1-100 (Default: 100) | Maximum connections as a percentage |
| MaxIdleConnectionsPercent | *Number* | 1-100 (Default: 50) | Maximum idle connections as a percentage |
| RDSInstanceSecurityGroupId | *AWS::EC2::SecurityGroup::Id* | e.g sg-0abc123def | Security Group ID of the target RDS instance |
| VPCEndpointSecurityGroupId | *AWS::EC2::SecurityGroup::Id* | e.g sg-0xyz789ghi | Security Group ID for VPC Endpoints (Secrets Manager, KMS, CloudWatch Logs) |

## How to provision template

HIP Team will copy the parameters.json to the project's IAC Repository. Project team will update the parameters json based on the available parameters in their own project repository.

## Important Notes

1. RDS Proxy supports specific database versions. For SQL Server, check AWS documentation for supported versions. https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.RDS_Fea_Regions_DB-eng.Feature.RDSProxy.html
2. The proxy must be in the same VPC as the database.
3. Applications will connect to the RDS Proxy endpoint on port 1433 (RDSProxyPort) instead of connecting directly to the RDS instance.
4. The secret in Secrets Manager must contain valid database credentials.
5. **Port Configuration (v2.1)**: The template uses separate ports for ingress and egress:
   - **Ingress (App → Proxy)**: Port 1433 (configurable via `RDSProxyPort`)
   - **Egress (Proxy → RDS)**: Port 53331/53341 (locked values, cannot be changed)

## Prerequisites

### VPC Endpoints Required

The following VPC Endpoints must be configured with the shared VPC Endpoint Security Group:

| VPC Endpoint Service | Purpose |
|---------------------|---------|
| `com.amazonaws.{region}.secretsmanager` | Retrieve database credentials |
| `com.amazonaws.{region}.kms` | Decrypt secrets (if using CMK encryption) |
| `com.amazonaws.{region}.logs` | CloudWatch Logs for debug logging |

### Security Group Configuration Required

After deploying this template, ensure the following security group rules are configured:

| Security Group | Rule Type | Port | Source/Destination | Description |
|----------------|-----------|------|-------------------|-------------|
| RDS Instance SG | Inbound | 53331/53341 | RDS Proxy SG | Allow inbound from RDS Proxy |
| VPC Endpoint SG | Inbound | 443 | RDS Proxy SG | Allow inbound from RDS Proxy |

## Architecture Flow

```
                                          ┌──────────────────────┐
                                          │    VPC Endpoints     │
                                          │  (Secrets Manager,   │
                                          │   KMS, CloudWatch)   │
                                          └──────────┬───────────┘
                                                     │
                                                     │ HTTPS (443)
                                                     │
┌─────────────────┐      ┌─────────────────┐      ┌──┴──────────────┐
│   Application   │      │    RDS Proxy    │      │   RDS Instance  │
│                 ├─────►│                 ├─────►│                 │
│                 │      │                 │      │                 │
└─────────────────┘      └─────────────────┘      └─────────────────┘
    Port 1433            Port 1433 (in)           Port 53331/53341
  (RDSProxyPort)       Port 53331/53341 (out)      (ProdDBPort/
                                                   NProdDBPort)
```

The RDS Proxy acts as an intermediary between your application and the database, managing connection pooling and providing additional resilience to your database connections.

**Traffic Flow:**
1. Application connects to RDS Proxy on port **1433** (standard SQL Server port)
2. RDS Proxy connects to RDS Instance on port **53331** (non-prod) or **53341** (prod)

## Template Resources

This template creates the following resources:

### IAM Resources
* `DBProxyRole`: IAM role for RDS Proxy with permissions to access Secrets Manager

### Security Resources
* `RdsProxySecurityGroup`: Security group for RDS Proxy with the following rules:

| Direction | Port | Source/Destination | Description |
|-----------|------|-------------------|-------------|
| Inbound | 1433 (RDSProxyPort) | App Subnet AZ1 CIDR | Allow inbound from App AZ1 |
| Inbound | 1433 (RDSProxyPort) | App Subnet AZ2 CIDR | Allow inbound from App AZ2 |
| Inbound | 1433 (RDSProxyPort) | App Subnet AZ3 CIDR (if provided) | Allow inbound from App AZ3 |
| Inbound | 1433 (RDSProxyPort) | Deployment Server IP | Allow inbound from Deployment Server |
| Outbound | 53331/53341 (ProdDBPort/NProdDBPort) | RDS Instance SG | Allow outbound to RDS Instance |
| Outbound | 443 | VPC Endpoint SG | Allow outbound to AWS Services via VPC Endpoints |

### RDS Proxy Resources
* `RDSProxy`: The main RDS Proxy resource configured with TLS requirement and Secrets Manager authentication
* `ProxyTargetGroup`: Target group associating the proxy with RDS instance

## Resource Tagging

All resources are tagged with `IaCVersion: InfraPlatform-rdsproxy-v2.1`

## Outputs

The template provides the following outputs:

| Output Name | Description |
|------------|-------------|
| RDSProxyEndpoint | The endpoint of the RDS Proxy |
| RDSProxyArn | The ARN of the RDS Proxy |
| RDSProxySecurityGroupId | The Security Group ID for the RDS Proxy |

## Version History

| Version | Changes |
|---------|---------|
| v2.1 | Added `RDSProxyPort` parameter for separate ingress port configuration (default: 1433). Added `AllowedValues` constraint on `ProdDBPort` and `NProdDBPort` to prevent misconfiguration. Ingress rules now use `RDSProxyPort`, egress rules use `ProdDBPort`/`NProdDBPort`. |
| v2 | Added security group egress rules for tightened security (RDS Instance, VPC Endpoints) |
| v1 | Initial release |