# AMAZON RELATIONAL DATABASE SERVICE PROXY - COMPREHENSIVE RDS ENGINE SUPPORT

Amazon RDS Proxy provides connection pooling and helps reduce the load on database resources and impact of connection management by scaling connections efficiently. RDS Proxy can help applications be more resilient to database failures by automatically connecting to a new primary instance while preserving application connections.

**Version 3 Enhancement**: This template now supports ALL RDS engines compatible with RDS Proxy, including:
- **MySQL Family**: MySQL 5.6+, MySQL 5.7+, MySQL 8.0+, MariaDB 10.2+
- **Aurora MySQL**: Aurora MySQL 5.6+, Aurora MySQL 5.7+, Aurora MySQL 8.0+
- **PostgreSQL Family**: PostgreSQL 10.11+, 11.6+, 12.4+, 13.x+, 14.x+, 15.x+
- **Aurora PostgreSQL**: Aurora PostgreSQL 10.11+, 11.6+, 12.4+, 13.x+, 14.x+, 15.x+
- **SQL Server Family**: SQL Server 2019+, 2022+ (Standard, Enterprise, Express, Web editions)

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
| DatabaseEngine | *String* | MYSQL, POSTGRESQL, SQLSERVER | Database engine family for RDS Proxy. MYSQL supports MySQL/MariaDB/Aurora MySQL, POSTGRESQL supports PostgreSQL/Aurora PostgreSQL, SQLSERVER supports SQL Server (Default: SQLSERVER) |
| RDSEngineType | *String* | MySQL, MariaDB, Aurora-MySQL, PostgreSQL, Aurora-PostgreSQL, SQL-Server | Specific RDS engine type for documentation and tagging (Default: SQL-Server) |
| VpcId | *AWS::EC2::VPC::Id* | e.g vpc-120324 | VPC ID where RDS Proxy will be deployed |
| DBSubnetIds | *List\<AWS::EC2::Subnet::Id\>* | e.g subnet-123232,subnet-2345123,subnet-323122 | Subnet IDs where RDS Proxy will be deployed |
| DBInstanceIdentifier | *String* | e.g my-app-nprd-rdssql | The RDS instance identifier to associate with the proxy |
| VPCSubnetCidrAppAZ1 | *String* | e.g 10.0.1.0/24 | Application subnet CIDR in AZ1 |
| VPCSubnetCidrAppAZ2 | *String* | e.g 10.0.2.0/24 | Application subnet CIDR in AZ2 |
| VPCSubnetCidrAppAZ3 | *String* | e.g 10.0.3.0/24 | Application subnet CIDR in AZ3 (optional) |
| DeploymentServer | *String* | e.g 10.0.2.3/32 | Deployment server IP address |
| DBProxySecretArn | *String* | e.g arn:aws:secretsmanager:region:account:secret:name | ARN of the Secret containing RDS Proxy credentials |
| RDSProxyPort | *String* | 1433, 3306, 5432 (Default: 1433) | Port the RDS Proxy listens on for client connections (ingress) - dropdown selection |
| ProdDBPort | *String* | 53341 (locked) | RDS instance port for production (egress) - DO NOT CHANGE |
| NProdDBPort | *String* | 53331 (locked) | RDS instance port for non-production (egress) - DO NOT CHANGE |
| MaxConnectionsPercent | *Number* | 1-100 (Default: 100) | Maximum connections as a percentage |
| MaxIdleConnectionsPercent | *Number* | 1-100 (Default: 50) | Maximum idle connections as a percentage |
| RDSInstanceSecurityGroupId | *AWS::EC2::SecurityGroup::Id* | e.g sg-0abc123def | Security Group ID of the target RDS instance |
| VPCEndpointSecurityGroupId | *AWS::EC2::SecurityGroup::Id* | e.g sg-0xyz789ghi | Security Group ID for VPC Endpoints (Secrets Manager, KMS, CloudWatch Logs) |

## How to provision template

HIP Team will copy the parameters.json to the project's IAC Repository. Project team will update the parameters json based on the available parameters in their own project repository.

## Important Notes

1. RDS Proxy supports specific database versions. For each engine family, check AWS documentation for supported versions. https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.RDS_Fea_Regions_DB-eng.Feature.RDSProxy.html
2. The proxy must be in the same VPC as the database.
3. Applications will connect to the RDS Proxy endpoint on the configurable `RDSProxyPort` (default: 1433 for SQL Server) instead of connecting directly to the RDS instance.
4. The secret in Secrets Manager must contain valid database credentials for the specified database engine.
5. **Port Configuration (v2.1 Enhancement)**: The template uses separate ports for ingress and egress:
   - **Ingress (App → Proxy)**: Configurable via `RDSProxyPort` (default: 1433 for SQL Server, 3306 for MySQL, 5432 for PostgreSQL)
   - **Egress (Proxy → RDS)**: Fixed ports 53331/53341 (locked values, cannot be changed)

## Usage Examples

### Example 1: SQL Server RDS Proxy (Default)
```yaml
DatabaseEngine: "SQLSERVER"
RDSEngineType: "SQL-Server"
DBInstanceIdentifier: "myapp-prod-sqlserver"
RDSProxyPort: "1433"        # Client connection port
ProdDBPort: "53341"         # RDS instance port (locked)
NProdDBPort: "53331"        # RDS instance port (locked)
```

### Example 2: MySQL RDS Proxy
```yaml
DatabaseEngine: "MYSQL"
RDSEngineType: "MySQL"
DBInstanceIdentifier: "myapp-prod-mysql"
RDSProxyPort: "3306"        # Client connection port  
ProdDBPort: "53341"         # RDS instance port (locked)
NProdDBPort: "53331"        # RDS instance port (locked)
```

### Example 3: MariaDB RDS Proxy
```yaml
DatabaseEngine: "MYSQL"
RDSEngineType: "MariaDB"
DBInstanceIdentifier: "myapp-prod-mariadb"
RDSProxyPort: "3306"        # Client connection port
ProdDBPort: "53341"         # RDS instance port (locked)
NProdDBPort: "53331"        # RDS instance port (locked)
```

### Example 4: Aurora MySQL RDS Proxy
```yaml
DatabaseEngine: "MYSQL"
RDSEngineType: "Aurora-MySQL"
DBInstanceIdentifier: "myapp-prod-aurora-mysql-cluster"
RDSProxyPort: "3306"        # Client connection port
ProdDBPort: "53341"         # RDS instance port (locked)
NProdDBPort: "53331"        # RDS instance port (locked)
```

### Example 5: PostgreSQL RDS Proxy
```yaml
DatabaseEngine: "POSTGRESQL"
RDSEngineType: "PostgreSQL"
DBInstanceIdentifier: "myapp-prod-postgres"
RDSProxyPort: "5432"        # Client connection port
ProdDBPort: "53341"         # RDS instance port (locked)
NProdDBPort: "53331"        # RDS instance port (locked)
```

### Example 6: Aurora PostgreSQL RDS Proxy
```yaml
DatabaseEngine: "POSTGRESQL"
RDSEngineType: "Aurora-PostgreSQL"
DBInstanceIdentifier: "myapp-prod-aurora-postgres-cluster"
RDSProxyPort: "5432"        # Client connection port
ProdDBPort: "53341"         # RDS instance port (locked)
NProdDBPort: "53331"        # RDS instance port (locked)
```
ProdDBPort: "5432"
NProdDBPort: "5432"
```

## Important Notes

1. **Multi-Engine Support**: RDS Proxy now supports MySQL, PostgreSQL, and SQL Server engines. Specify the engine using the `DatabaseEngine` parameter.
2. RDS Proxy supports specific database versions for each engine. Check AWS documentation for supported versions: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.RDS_Fea_Regions_DB-eng.Feature.RDSProxy.html
3. The proxy must be in the same VPC as the database.
4. Applications will connect to the RDS Proxy endpoint instead of connecting directly to the RDS instance.
5. The secret in Secrets Manager must contain valid database credentials for the specified database engine.

## Engine-Specific Considerations

### MySQL Family (MYSQL Engine Family)
- **Default Port**: 3306
- **Supported Engines**:
  - **MySQL**: 5.6.10a+, 5.7.16+, 8.0.16+
  - **MariaDB**: 10.2.11+, 10.3.13+, 10.4.8+, 10.5.9+, 10.6.5+
  - **Aurora MySQL**: 5.6.10a+, 5.7.12+, 8.0.mysql_aurora.3.02.0+
- **Secret Format**: Username/password authentication
- **Connection Pooling**: Excellent performance for high-concurrency OLTP workloads
- **Notes**: Supports both MySQL and MariaDB instances seamlessly

### PostgreSQL Family (POSTGRESQL Engine Family)
- **Default Port**: 5432
- **Supported Engines**:
  - **PostgreSQL**: 10.11+, 11.6+, 12.4+, 13.3+, 14.2+, 15.2+
  - **Aurora PostgreSQL**: 10.11+, 11.6+, 12.4+, 13.3+, 14.2+, 15.2+
- **Secret Format**: Username/password authentication
- **Connection Pooling**: Optimized for PostgreSQL's connection model and prepared statements
- **Notes**: Full support for both RDS PostgreSQL and Aurora PostgreSQL

### SQL Server Family (SQLSERVER Engine Family)
- **Default Port**: 1433
- **Supported Engines**:
  - **SQL Server 2019**: Standard, Enterprise, Express, Web editions
  - **SQL Server 2022**: Standard, Enterprise, Express, Web editions (latest versions)
- **Secret Format**: Username/password authentication (SQL Server Authentication)
- **Connection Pooling**: Optimized for SQL Server's connection characteristics
- **Notes**: 
  - Custom ports (like 53341/53331) are commonly used in enterprise environments
  - Windows Authentication is not supported; use SQL Server Authentication
  - Supports Multi-AZ deployments

## RDS Proxy Compatibility Matrix

| RDS Engine | Engine Family | RDSEngineType | Default Port | Supported Versions | Notes |
|------------|---------------|---------------|--------------|-------------------|-------|
| MySQL | MYSQL | MySQL | 3306 | 5.6.10a+, 5.7.16+, 8.0.16+ | Standard MySQL instances |
| MariaDB | MYSQL | MariaDB | 3306 | 10.2.11+, 10.3.13+, 10.4.8+, 10.5.9+, 10.6.5+ | Uses MySQL engine family |
| Aurora MySQL | MYSQL | Aurora-MySQL | 3306 | 5.6.10a+, 5.7.12+, 8.0.mysql_aurora.3.02.0+ | Aurora MySQL clusters |
| PostgreSQL | POSTGRESQL | PostgreSQL | 5432 | 10.11+, 11.6+, 12.4+, 13.3+, 14.2+, 15.2+ | Standard PostgreSQL instances |
| Aurora PostgreSQL | POSTGRESQL | Aurora-PostgreSQL | 5432 | 10.11+, 11.6+, 12.4+, 13.3+, 14.2+, 15.2+ | Aurora PostgreSQL clusters |
| SQL Server | SQLSERVER | SQL-Server | 1433 | 2019+, 2022+ (Std, Ent, Exp, Web) | All SQL Server editions |

### Unsupported RDS Engines
- **Oracle Database**: RDS Proxy does not support Oracle databases
- **Amazon DocumentDB**: Not an RDS engine, uses different proxy solutions  
- **Amazon Neptune**: Graph database, not supported by RDS Proxy
- **Amazon Timestream**: Time series database, not supported by RDS Proxy

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
| RDS Instance SG | Inbound | DB Port | RDS Proxy SG | Allow inbound from RDS Proxy |
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
  Port 1433/3306/5432    Port 1433/3306/5432(in)  Port 53331/53341
   (RDSProxyPort)       Port 53331/53341 (out)    (ProdDBPort/
                                                   NProdDBPort)
```

The RDS Proxy acts as an intermediary between your application and the database, managing connection pooling and providing additional resilience to your database connections.

**Traffic Flow:**
1. Application connects to RDS Proxy on configurable port via `RDSProxyPort` (1433 for SQL Server, 3306 for MySQL, 5432 for PostgreSQL)
2. RDS Proxy connects to RDS Instance on port **53331** (non-prod) or **53341** (prod) - these are locked values

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
      DB Port                 DB Port                  DB Port
```

The RDS Proxy acts as an intermediary between your application and the database, managing connection pooling and providing additional resilience to your database connections.

## Template Resources

This template creates the following resources:

### IAM Resources
* `DBProxyRole`: IAM role for RDS Proxy with permissions to access Secrets Manager

### Security Resources
* `RdsProxySecurityGroup`: Security group for RDS Proxy with the following rules:

| Direction | Port | Source/Destination | Description |
|-----------|------|-------------------|-------------|
| Inbound | DB Port | App Subnet AZ1 CIDR | Allow inbound from App AZ1 |
| Inbound | DB Port | App Subnet AZ2 CIDR | Allow inbound from App AZ2 |
| Inbound | DB Port | App Subnet AZ3 CIDR (if provided) | Allow inbound from App AZ3 |
| Inbound | DB Port | Deployment Server IP | Allow inbound from Deployment Server |
| Outbound | DB Port | RDS Instance SG | Allow outbound to RDS Instance |
| Outbound | 443 | VPC Endpoint SG | Allow outbound to AWS Services via VPC Endpoints |

### RDS Proxy Resources
* `RDSProxy`: The main RDS Proxy resource configured with TLS requirement and Secrets Manager authentication
* `ProxyTargetGroup`: Target group associating the proxy with RDS instance

## Resource Tagging

All resources are tagged with `IaCVersion: InfraPlatform-rdsproxy-v3`

## Outputs

The template provides the following outputs:

| Output Name | Description |
|------------|-------------|
| RDSProxyEndpoint | The endpoint of the RDS Proxy |
| RDSProxyArn | The ARN of the RDS Proxy |
| RDSProxySecurityGroupId | The Security Group ID for the RDS Proxy |
| DatabaseEngine | The database engine family configured for this RDS Proxy |
| RDSEngineType | The specific RDS engine type configured |
| EngineDefaultPort | The default port for the configured database engine |
| EngineDescription | Description of the configured database engine family |
| SupportedEngines | List of all supported engines in this family |

## Version History

| Version | Changes |
|---------|---------|
| v3 (synced with v2.1) | **Comprehensive RDS Engine Support + v2.1 Enhancements**: Added support for ALL RDS engines compatible with RDS Proxy including MySQL, MariaDB, Aurora MySQL, PostgreSQL, Aurora PostgreSQL, and SQL Server families. Enhanced with engine-specific documentation, tagging, and configuration examples. **NEW from v2.1**: Added `RDSProxyPort` parameter for separate ingress port configuration (default: 1433). Added `AllowedValues` constraint on `ProdDBPort` and `NProdDBPort` to prevent misconfiguration. Ingress rules now use `RDSProxyPort`, egress rules use `ProdDBPort`/`NProdDBPort`. |
| v2 | Added security group egress rules for tightened security (RDS Instance, VPC Endpoints) |
| v1 | Initial release |