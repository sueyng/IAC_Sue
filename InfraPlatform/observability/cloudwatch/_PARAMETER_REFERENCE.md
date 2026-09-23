# CloudWatch Alerting Templates - Parameter Reference

## Overview
This document provides a comprehensive reference for all configurable parameters across the CloudWatch alerting templates. Use this guide to understand what parameters are available for each service and how to configure them properly.

## Common Parameters (All Templates)

### Environment Configuration
| Parameter | Type | Required | Description | Default | Allowed Values |
|-----------|------|----------|-------------|---------|----------------|
| `AppShortName` | String | Yes | Application short name | - | Any string |
| `EnvName` | String | Yes | Environment name | - | nprd, nprd-dev, nprd-sit1, nprd-sit2, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b, prod, prod-a, prod-b |

### SNS Topic Configuration (Team-Based Notifications)
| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `Team1SNSTopicArn` | String | No | SNS Topic ARN for Team 1 notifications (e.g., L2 Operations) | "" |
| `Team2SNSTopicArn` | String | No | SNS Topic ARN for Team 2 notifications (e.g., L3 Support/Development) | "" |
| `Team3SNSTopicArn` | String | No | SNS Topic ARN for Team 3 notifications (e.g., Infrastructure/Platform) | "" |

---

## 1. RDS Database Monitoring (rds-cf.yaml)

### Database Instance Parameters
| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `RDS1Name` | String | Yes | RDS Database 1 name for monitoring | - |
| `RDS2Name` | String | No | RDS Database 2 name for monitoring | "" |
| `RDS3Name` | String | No | RDS Database 3 name for monitoring | "" |

### Configurable Thresholds
| Parameter | Type | Required | Description | Default | Recommended Values |
|-----------|------|----------|-------------|---------|-------------------|
| `CPUThreshold` | Number | No | CPU utilization threshold (%) | 80 | 70-90 |
| `DatabaseConnectionsThreshold` | Number | No | Database connections threshold | 80 | 50-100 |
| `FreeableMemoryThreshold` | Number | No | Freeable memory threshold (bytes) | 2147483648 | 1GB-4GB |
| `FreeStorageSpaceThreshold` | Number | No | Free storage space threshold (bytes) | 10737418240 | 5GB-20GB |

### Example Parameter Configuration
```yaml
Parameters:
  AppShortName: "myapp"
  EnvName: "prod"
  RDS1Name: "myapp-prod-db-primary"
  RDS2Name: "myapp-prod-db-replica"
  CPUThreshold: 85
  DatabaseConnectionsThreshold: 90
  FreeableMemoryThreshold: 1073741824  # 1GB in bytes
  FreeStorageSpaceThreshold: 5368709120  # 5GB in bytes
  Team1SNSTopicArn: "arn:aws:sns:us-east-1:123456789012:ops-team"
  Team2SNSTopicArn: "arn:aws:sns:us-east-1:123456789012:dev-team"
  Team3SNSTopicArn: "arn:aws:sns:us-east-1:123456789012:infra-team"
```

---

## 2. API Gateway Monitoring (apigateway-cf.yaml)

### API Gateway Instance Parameters
| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `ApiGateway1Name` | String | Yes | API Gateway 1 name for monitoring | - |
| `ApiGateway1Stage` | String | No | API Gateway 1 stage for monitoring | "prod" |
| `ApiGateway2Name` | String | No | API Gateway 2 name for monitoring | "" |
| `ApiGateway2Stage` | String | No | API Gateway 2 stage for monitoring | "prod" |

### Resource Path Parameters
| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `ResourcePath1` | String | No | API Gateway resource path 1 for monitoring (e.g., /api/v1/users) | "" |
| `ResourcePath2` | String | No | API Gateway resource path 2 for monitoring (e.g., /api/v1/orders) | "" |
| `ResourcePath3` | String | No | API Gateway resource path 3 for monitoring (e.g., /api/v1/products) | "" |

### Fixed Thresholds (Not Configurable)
| Metric | Threshold | Period | Evaluation Periods |
|--------|-----------|--------|-------------------|
| 5XXError | 1 error | 60s | 2 |
| 4XXError | 50 errors | 60s | 2 |
| Latency | 5000ms | 300s | 2 |
| IntegrationLatency | 4000ms | 300s | 2 |
| Count (High Traffic) | 2000 requests | 60s | 2 |

### Example Parameter Configuration
```yaml
Parameters:
  AppShortName: "myapi"
  EnvName: "prod"
  ApiGateway1Name: "myapi-prod-gateway"
  ApiGateway1Stage: "prod"
  ApiGateway2Name: "myapi-prod-gateway-v2"
  ApiGateway2Stage: "prod"
  ResourcePath1: "/api/v1/users"
  ResourcePath2: "/api/v1/orders"
  ResourcePath3: "/api/v1/products"
  Team1SNSTopicArn: "arn:aws:sns:us-east-1:123456789012:ops-team"
  Team2SNSTopicArn: "arn:aws:sns:us-east-1:123456789012:dev-team"
  Team3SNSTopicArn: "arn:aws:sns:us-east-1:123456789012:infra-team"
```

---

## 3. ECS Service Monitoring (ecs-cf.yaml)

### ECS Cluster and Service Parameters
| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `ECSClusterName` | String | Yes | ECS Cluster name for monitoring | - |
| `ECSService1Name` | String | Yes | ECS Service 1 name for monitoring | - |
| `ECSService2Name` | String | No | ECS Service 2 name for monitoring | "" |
| `ECSService3Name` | String | No | ECS Service 3 name for monitoring | "" |

### Configurable Thresholds
| Parameter | Type | Required | Description | Default | Recommended Values |
|-----------|------|----------|-------------|---------|-------------------|
| `CPUUtilizationCriticalThreshold` | Number | No | CPU utilization critical threshold (%) | 90 | 85-95 |
| `CPUUtilizationWarningThreshold` | Number | No | CPU utilization warning threshold (%) | 80 | 70-85 |
| `MemoryUtilizationCriticalThreshold` | Number | No | Memory utilization critical threshold (%) | 90 | 85-95 |
| `MemoryUtilizationWarningThreshold` | Number | No | Memory utilization warning threshold (%) | 80 | 70-85 |
| `DesiredCountThreshold` | Number | No | Minimum desired count threshold | 1 | 1-5 |
| `RunningTaskCountThreshold` | Number | No | Minimum running task count threshold | 1 | 1-5 |

### Fixed Thresholds (Not Configurable)
| Metric | Threshold | Period | Evaluation Periods |
|--------|-----------|--------|-------------------|
| CPUReservation (Cluster) | 80% | 300s | 2 |
| MemoryReservation (Cluster) | 80% | 300s | 2 |

### Complete Monitoring Coverage
**Per Service Alarms (applies to Service 1, 2, 3):**
- 🔴 **4 Critical Alarms**: CPU Critical (≥90%), Memory Critical (≥90%), Running Task Count (<1), Desired Count (<1)
- 🟡 **2 Important Alarms**: CPU Warning (≥80%), Memory Warning (≥80%)

**Cluster Level Alarms:**
- 🟡 **2 Important Alarms**: CPU Reservation (≥80%), Memory Reservation (≥80%)

**Total Coverage**: Up to 20 alarms (18 service-level + 2 cluster-level)

### Alert Categories
- **🔴 CRITICAL**: Service CPU/Memory >90%, Task Count <1, Service unavailable
- **🟡 IMPORTANT**: Service CPU/Memory >80%, Cluster reservation >80%

### Example Parameter Configuration
```yaml
Parameters:
  AppShortName: "myapp"
  EnvName: "prod"
  ECSClusterName: "myapp-prod-cluster"
  ECSService1Name: "myapp-prod-web-service"
  ECSService2Name: "myapp-prod-api-service"
  ECSService3Name: "myapp-prod-worker-service"
  CPUUtilizationCriticalThreshold: 90
  CPUUtilizationWarningThreshold: 80
  MemoryUtilizationCriticalThreshold: 90
  MemoryUtilizationWarningThreshold: 80
  DesiredCountThreshold: 1
  RunningTaskCountThreshold: 1
  Team1SNSTopicArn: "arn:aws:sns:us-east-1:123456789012:ops-team"
  Team2SNSTopicArn: "arn:aws:sns:us-east-1:123456789012:dev-team"
  Team3SNSTopicArn: "arn:aws:sns:us-east-1:123456789012:infra-team"
```

---

## 4. Application Load Balancer (alb-cf.yaml)

### ALB Instance Parameters
| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `Alb1Name` | String | Yes | ALB 1 name for monitoring | - |
| `Alb1TargetGroup1Name` | String | No | ALB 1 Target Group 1 name | "" |
| `Alb1TargetGroup2Name` | String | No | ALB 1 Target Group 2 name | "" |
| `Alb1TargetGroup3Name` | String | No | ALB 1 Target Group 3 name | "" |
| `Alb2Name` | String | No | ALB 2 name for monitoring | "" |
| `Alb2TargetGroup1Name` | String | No | ALB 2 Target Group 1 name | "" |
| `Alb2TargetGroup2Name` | String | No | ALB 2 Target Group 2 name | "" |
| `Alb2TargetGroup3Name` | String | No | ALB 2 Target Group 3 name | "" |
| `Alb3Name` | String | No | ALB 3 name for monitoring | "" |
| `Alb3TargetGroup1Name` | String | No | ALB 3 Target Group 1 name | "" |
| `Alb3TargetGroup2Name` | String | No | ALB 3 Target Group 2 name | "" |
| `Alb3TargetGroup3Name` | String | No | ALB 3 Target Group 3 name | "" |
| `Alb4Name` | String | No | ALB 4 name for monitoring | "" |
| `Alb4TargetGroup1Name` | String | No | ALB 4 Target Group 1 name | "" |
| `Alb4TargetGroup2Name` | String | No | ALB 4 Target Group 2 name | "" |
| `Alb4TargetGroup3Name` | String | No | ALB 4 Target Group 3 name | "" |

### Fixed Thresholds (Not Configurable)
| Metric | Threshold | Period | Evaluation Periods |
|--------|-----------|--------|-------------------|
| HTTPCode_ELB_5XX_Count | 5 errors | 60s | 1 |
| TargetResponseTime | 3 seconds | 300s | 2 |

### Example Parameter Configuration
```yaml
Parameters:
  AppShortName: "webapp"
  EnvName: "prod"
  Alb1Name: "webapp-prod-alb-public"
  Alb1TargetGroup1Name: "webapp-prod-tg-frontend"
  Alb1TargetGroup2Name: "webapp-prod-tg-api"
  Alb2Name: "webapp-prod-alb-internal"
  Alb2TargetGroup1Name: "webapp-prod-tg-backend"
```

---

## 5. Application Load Balancer Multi-Target Group (alb-cf.yaml)

### Supports Multiple ALBs with Multiple Target Groups

### Fixed Thresholds (Not Configurable)
| Metric | Threshold | Period | Evaluation Periods |
|--------|-----------|--------|-------------------|
| HTTPCode_ELB_5XX_Count | 1 error | 60s | 1 |
| UnHealthyHostCount | 1 host | 60s | 1 |
| HTTPCode_Target_5XX_Count | 5 errors | 60s | 2 |
| TargetResponseTime | 3 seconds | 300s | 2 |

---

## 6. Lambda Function Monitoring (lambda-cf.yaml)

### Lambda Function Parameters
| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `Lambda1Name` | String | Yes | Lambda function 1 name for monitoring | - |
| `Lambda2Name` | String | No | Lambda function 2 name for monitoring | "" |
| `Lambda3Name` | String | No | Lambda function 3 name for monitoring | "" |

### Configurable Thresholds
| Parameter | Type | Required | Description | Default | Recommended Values |
|-----------|------|----------|-------------|---------|-------------------|
| `ErrorThreshold` | Number | No | Error count threshold | 5 | 1-10 |
| `DurationThreshold` | Number | No | Duration threshold (ms) | 30000 | 10000-60000 |
| `ThrottleThreshold` | Number | No | Throttle count threshold | 1 | 1-5 |
| `ConcurrentExecutionThreshold` | Number | No | Concurrent execution threshold | 800 | 500-1000 |

### Example Parameter Configuration
```yaml
Parameters:
  AppShortName: "myapp"
  EnvName: "prod"
  Lambda1Name: "myapp-prod-processor"
  Lambda2Name: "myapp-prod-scheduler"
  Lambda3Name: "myapp-prod-notifier"
  ErrorThreshold: 3
  DurationThreshold: 25000
  ThrottleThreshold: 2
  ConcurrentExecutionThreshold: 900
```

---

## 7. SQS Queue Monitoring (sqs-alerts-cf.yaml)

### SQS Queue Parameters
| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `InstituteName` | String | Yes | Institute name | - |
| `SQSQueueName` | String | Yes | SQS queue name for monitoring | - |

### Fixed Thresholds (Not Configurable)
| Metric | Threshold | Period | Evaluation Periods |
|--------|-----------|--------|-------------------|
| ApproximateNumberOfMessages | 10 messages | 300s | 2 |
| ApproximateAgeOfOldestMessage | 300 seconds | 300s | 2 |
| ApproximateNumberOfMessages (DLQ) | 1 message | 300s | 1 |

### Example Parameter Configuration
```yaml
Parameters:
  InstituteName: "myorg"
  AppShortName: "myapp"
  EnvName: "prod"
  SQSQueueName: "myapp-prod-processing-queue"
```

---

## 8. Glue Job Monitoring (glue-job-alerts-cf.yaml)

### Glue Job Parameters
| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `InstituteName` | String | Yes | Institute name | - |
| `GlueJobName` | String | Yes | Glue job name for monitoring | - |

### Fixed Thresholds (Not Configurable)
| Metric | Threshold | Period | Evaluation Periods |
|--------|-----------|--------|-------------------|
| glue.driver.aggregate.numFailedTasks | 1 failed task | 300s | 1 |
| glue.driver.aggregate.elapsedTime | 3600000ms (1 hour) | 300s | 1 |

### Example Parameter Configuration
```yaml
Parameters:
  InstituteName: "myorg"
  AppShortName: "dataprocessing"
  EnvName: "prod"
  GlueJobName: "myorg-dataprocessing-prod-etl-job"
```

---

## 9. SNS Topics (sns-cf.yaml)

### SNS Topic Parameters
| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `InstituteName` | String | Yes | Institute name | - |

### Pre-defined Topic Names
| Topic Logical ID | Topic Name Pattern | Purpose |
|------------------|-------------------|---------|
| `AppL2OpsSNSTopic` | `{InstituteName}-{AppShortName}-{EnvName}-L2-Ops-SNS-Topic` | L2 Operations Team |
| `AppL3SupportSNSTopic` | `{InstituteName}-{AppShortName}-{EnvName}-L3-Support-SNS-Topic` | L3 Support/Development Team |
| `InfraL3SupportSNSTopic` | `{InstituteName}-{AppShortName}-{EnvName}-Infra-L3-Support-SNS-Topic` | Infrastructure/Platform Team |
| `DbOpsSNSTopic` | `{InstituteName}-{AppShortName}-{EnvName}-DB-Ops-SNS-Topic` | Database Operations Team |
| `SecurityOpsSNSTopic` | `{InstituteName}-{AppShortName}-{EnvName}-Security-Ops-SNS-Topic` | Security Operations Team |

### Example Parameter Configuration
```yaml
Parameters:
  InstituteName: "myorg"
  AppShortName: "myapp"
  EnvName: "prod"
```

---

## 10. ElastiCache Monitoring (elasticache-cf.yaml)

### Server-Based ElastiCache Clusters (Redis/Memcached)

### ElastiCache Cluster Parameters
| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `ElastiCacheCluster1Name` | String | No | ElastiCache cluster 1 name for monitoring | "" |
| `ElastiCacheCluster2Name` | String | No | ElastiCache cluster 2 name for monitoring | "" |
| `ElastiCacheCluster3Name` | String | No | ElastiCache cluster 3 name for monitoring | "" |

### ElastiCache Serverless Parameters
| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `ServerlessCache1Name` | String | No | ElastiCache Serverless cache 1 name for monitoring | "" |
| `ServerlessCache2Name` | String | No | ElastiCache Serverless cache 2 name for monitoring | "" |

### Configurable Thresholds
| Parameter | Type | Required | Description | Default | Recommended Values |
|-----------|------|----------|-------------|---------|-------------------|
| `CPUUtilizationThreshold` | Number | No | CPU utilization threshold percentage | 80 | 70-90 |
| `MemoryUtilizationThreshold` | Number | No | Memory utilization threshold percentage | 80 | 70-90 |
| `NetworkBytesInThreshold` | Number | No | Network bytes in threshold per second | 100000000 | 50MB-200MB |
| `NetworkBytesOutThreshold` | Number | No | Network bytes out threshold per second | 100000000 | 50MB-200MB |
| `CacheHitRatioThreshold` | Number | No | Cache hit ratio threshold percentage | 80 | 75-95 |
| `ConnectionCountThreshold` | Number | No | Current connections threshold | 100 | 50-500 |
| `ReplicationLagThreshold` | Number | No | Redis replication lag threshold (seconds) | 60 | 30-300 |
| `ServerlessDataStorageThreshold` | Number | No | Serverless data storage threshold (bytes) | 1073741824 | 500MB-5GB |
| `ServerlessECPUUtilizationThreshold` | Number | No | Serverless ECPU utilization threshold | 80 | 70-90 |

### Monitoring Metrics Coverage

#### Server-Based Clusters (7 alarms per cluster)
- **CPUUtilization**: Critical performance metric
- **DatabaseMemoryUsagePercentage**: Memory usage monitoring
- **CacheHitRate**: Cache efficiency monitoring
- **CurrConnections**: Connection pool monitoring
- **NetworkBytesIn/Out**: Network throughput monitoring
- **ReplicationLag**: Redis replication health (Redis-specific)

#### Serverless Caches (4 alarms per cache)
- **ElastiCacheProcessingUnits (ECPU)**: Processing capacity utilization
- **DataStorage**: Storage utilization monitoring
- **SuccessfulRequestCount**: Request success rate
- **ThrottledRequestCount**: Throttling monitoring

### Example Parameter Configuration
```yaml
Parameters:
  AppShortName: "myapp"
  EnvName: "prod"
  # Server-based clusters
  ElastiCacheCluster1Name: "myapp-prod-redis-cluster-001"
  ElastiCacheCluster2Name: "myapp-prod-memcached-cluster-001"
  ElastiCacheCluster3Name: ""
  # Serverless caches
  ServerlessCache1Name: "myapp-prod-serverless-redis"
  ServerlessCache2Name: "myapp-prod-serverless-memcached"
  # Thresholds
  CPUUtilizationThreshold: 80
  MemoryUtilizationThreshold: 80
  NetworkBytesInThreshold: 100000000
  NetworkBytesOutThreshold: 100000000
  CacheHitRatioThreshold: 80
  ConnectionCountThreshold: 100
  ReplicationLagThreshold: 60
  ServerlessDataStorageThreshold: 1073741824
  ServerlessECPUUtilizationThreshold: 80
```

### Deployment Commands
```bash
# Deploy ElastiCache monitoring
aws cloudformation deploy \
  --template-file cloudwatch/elasticache-cf.yaml \
  --stack-name myapp-prod-elasticache-monitoring \
  --parameter-overrides file://cloudwatch/elasticache-parameters.json \
  --capabilities CAPABILITY_IAM

# Update stack with new parameters
aws cloudformation update-stack \
  --stack-name myapp-prod-elasticache-monitoring \
  --template-body file://cloudwatch/elasticache-cf.yaml \
  --parameters file://cloudwatch/elasticache-parameters.json
```

### Troubleshooting

#### Common Issues
- **No metrics available**: Ensure ElastiCache clusters/caches exist and are running
- **High false positives**: Adjust thresholds based on actual workload patterns
- **Missing replication lag**: ReplicationLag metric only applies to Redis clusters
- **Serverless metrics delay**: Serverless metrics may have higher latency

#### Metric-Specific Notes
- **CacheHitRate**: Monitor trends over time, sudden drops indicate issues
- **NetworkBytes**: Spikes may indicate data dump operations or backup processes
- **ReplicationLag**: Only relevant for Redis clusters with read replicas
- **ECPU**: Serverless-specific metric representing processing units consumed
- **ThrottledRequests**: Indicates capacity limits reached in serverless

---

## Parameter Validation and Best Practices

### 1. Naming Conventions
- Use kebab-case for resource names (e.g., `myapp-prod-db-primary`)
- Keep names under 64 characters
- Include environment in the name for clarity

### 2. Threshold Recommendations
- **Development/Test**: Use higher thresholds to reduce noise
- **Production**: Use lower thresholds for faster detection
- **Review quarterly**: Adjust based on actual usage patterns

### 3. SNS Topic Configuration
- At minimum, configure Team1SNSTopicArn for critical alerts
- Use Team2SNSTopicArn for development/application teams
- Use Team3SNSTopicArn for infrastructure teams

### 4. Environment-Specific Configuration
```yaml
# Development
ErrorThreshold: 10
CPUThreshold: 90

# Production
ErrorThreshold: 3
CPUThreshold: 80
```

### 5. Parameter File Examples
Create separate parameter files for each environment:

**parameters-dev.json**
```json
{
  "AppShortName": "myapp",
  "EnvName": "nprd-dev",
  "RDS1Name": "myapp-dev-db",
  "CPUThreshold": 90,
  "ErrorThreshold": 10,
  "Team1SNSTopicArn": "arn:aws:sns:us-east-1:123456789012:dev-ops-team"
}
```

**parameters-prod.json**
```json
{
  "AppShortName": "myapp",
  "EnvName": "prod",
  "RDS1Name": "myapp-prod-db-primary",
  "RDS2Name": "myapp-prod-db-replica",
  "CPUThreshold": 80,
  "ErrorThreshold": 3,
  "Team1SNSTopicArn": "arn:aws:sns:us-east-1:123456789012:ops-team",
  "Team2SNSTopicArn": "arn:aws:sns:us-east-1:123456789012:dev-team",
  "Team3SNSTopicArn": "arn:aws:sns:us-east-1:123456789012:infra-team"
}
```

## Deployment Commands

### Using AWS CLI
```bash
# Deploy RDS monitoring
aws cloudformation deploy \
  --template-file rds-cf.yaml \
  --stack-name myapp-prod-rds-monitoring \
  --parameter-overrides file://parameters-prod.json

# Deploy API Gateway monitoring
aws cloudformation deploy \
  --template-file apigateway-cf.yaml \
  --stack-name myapp-prod-api-monitoring \
  --parameter-overrides file://parameters-prod.json

# Deploy ECS monitoring
aws cloudformation deploy \
  --template-file ecs-cf.yaml \
  --stack-name myapp-prod-ecs-monitoring \
  --parameter-overrides file://parameters-prod.json

# Deploy ALB monitoring
aws cloudformation deploy \
  --template-file alb-cf.yaml \
  --stack-name myapp-prod-alb-monitoring \
  --parameter-overrides file://parameters-prod.json

# Deploy ElastiCache monitoring
aws cloudformation deploy \
  --template-file cloudwatch/elasticache-cf.yaml \
  --stack-name myapp-prod-elasticache-monitoring \
  --parameter-overrides file://cloudwatch/elasticache-parameters.json \
  --capabilities CAPABILITY_IAM
```

### Using Parameter Files
Store parameters in separate files for each environment and service to maintain consistency and enable automation.
