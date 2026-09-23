# AWS CloudWatch Monitoring Templates

This directory contains CloudFormation templates for comprehensive monitoring and alerting using CloudWatch alarms and SNS notifications.

## Templates Overview

### 1. SNS Topics Template (`sns-cf.yaml`)
Creates SNS topics for multi-team notifications following enterprise naming conventions.

**Features:**
- Multi-team SNS topics (L2 Ops, L3 Support, Infrastructure, Database, Security)
- Standardized naming: `<InstituteName>-<AppShortName>-<EnvName>-sns-<topic>`
- Enterprise tagging with IaCVersion tracking
- Production-aware deletion policies

**Topics Created:**
- L2 Operations alerts
- L3 Support/Development notifications
- Infrastructure/Platform alerts
- Database team notifications
- Security team alerts

### 2. ALB Monitoring Template (`alb-cf.yaml`)
Enhanced ALB monitoring supporting up to 4 ALBs with up to 3 target groups each for comprehensive load balancer monitoring.

**Features:**
- Multi-ALB support (up to 4 ALBs)
- Target group-specific alarms (5XX, 4XX, latency, healthy hosts, response time)
- Multi-team SNS notifications
- Production-aware policies
- Standardized tagging and naming conventions

**Alarms Per Target Group:**
- 5XX Error Count
- 4XX Error Count  
- Target Response Time
- Healthy Host Count
- Unhealthy Host Count

### 3. API Gateway Monitoring Template (`apigateway-cf.yaml`)
Comprehensive API Gateway monitoring with optional resource-specific integration support.

**Features:**
- API Gateway-level alarms (5XX, 4XX, latency, request count, cache hits)
- Optional backend integration monitoring per resource path
- Multi-team SNS notifications
- Resource/Route-specific monitoring (optional)

**API Gateway Alarms:**
- 5XX/4XX Error rates
- Latency and Integration Latency
- Request Count (High/Low traffic)
- Cache Hit Count

**Per Resource Path (Optional):**
- Integration Error monitoring
- Integration Latency tracking

### 4. ECS Service Monitoring Template (`ecs-cf.yaml`)
Comprehensive AWS ECS service monitoring supporting up to 3 ECS services within a cluster.

**Features:**
- Multi-service monitoring (up to 3 ECS services)
- Cluster-level resource monitoring
- Critical and Important alert categories
- Configurable CPU/Memory thresholds
- Task count monitoring
- Multi-team SNS notifications
- Production-aware policies

**ECS Service Alarms Per Service:**
- CPU Utilization (Critical & Warning)
- Memory Utilization (Critical & Warning)
- Running Task Count monitoring
- Desired Count monitoring

**ECS Cluster Alarms:**
- CPU Reservation monitoring
- Memory Reservation monitoring

**Alert Categories:**
- **🔴 CRITICAL**: CPU/Memory >90%, Task Count <1, Service unavailable
- **🟡 IMPORTANT**: CPU/Memory >80%, Cluster resource reservation >80%

### 5. Lambda Monitoring Template (`lambda-cf.yaml`)
Comprehensive AWS Lambda function monitoring supporting up to 3 Lambda functions.

**Features:**
- Multi-function monitoring (up to 3 Lambda functions)
- Comprehensive Lambda metrics coverage
- Multi-team SNS notifications
- Configurable thresholds per environment
- Production-aware policies

**Lambda Alarms Per Function:**
- Error Count monitoring
- Duration/Performance monitoring
- Throttle detection
- Dead Letter Queue errors
- Concurrent Executions monitoring

### 5. RDS Monitoring Template (`rds-cf.yaml`)
Comprehensive AWS RDS database monitoring supporting up to 3 RDS instances.

**Features:**
- Multi-instance monitoring (up to 3 RDS instances)
- Comprehensive RDS metrics coverage
- Multi-team SNS notifications  
- Configurable thresholds per metric
- Production-aware policies

**RDS Alarms Per Instance:**
- CPU Utilization monitoring
- Database Connections tracking
- Freeable Memory monitoring
- Free Storage Space alerts
- Read/Write Latency monitoring
- Swap Usage detection

**Alarm Purpose and Explanations:**

**CPU Utilization**: Monitors database server CPU usage. High CPU can indicate:
- Complex queries or inefficient query execution
- Insufficient instance sizing for workload
- Need for read replicas or connection pooling

**Database Connections**: Tracks active database connections. High connections can indicate:
- Application connection pool misconfiguration
- Connection leaks in application code
- Need to increase max_connections parameter or scale instance

**Freeable Memory**: Monitors available memory for database operations. Low memory can indicate:
- Need for larger instance class
- Inefficient queries using excessive memory
- Buffer pool sizing issues requiring tuning

**Free Storage Space**: Tracks available disk space. Low storage can indicate:
- Need for storage scaling or cleanup
- Log files consuming excessive space
- Data growth requiring capacity planning

**Read/Write Latency**: Monitors database I/O performance. High latency can indicate:
- Storage performance bottlenecks
- Need for Provisioned IOPS or different storage type
- Query optimization requirements

**Swap Usage**: Detects memory pressure causing swapping. Swap usage can indicate:
- Insufficient memory for workload
- Memory leaks or runaway processes
- Need for instance class upgrade

### 6. ElastiCache Monitoring Template (`elasticache-cf.yaml`)
Comprehensive AWS ElastiCache monitoring supporting both server-based clusters (Redis/Memcached) and serverless caches.

**Features:**
- Server-based cluster monitoring (up to 3 clusters)
- Serverless cache monitoring (up to 2 caches)
- Support for both Redis and Memcached
- Comprehensive ElastiCache metrics coverage
- Multi-team SNS notifications
- Configurable thresholds per metric
- Production-aware policies

**Server-Based Cluster Alarms (7 per cluster):**
- CPU Utilization monitoring
- Memory utilization tracking
- Cache hit ratio analysis
- Connection count monitoring
- Network throughput tracking
- Redis replication lag monitoring

**Serverless Cache Alarms (4 per cache):**
- ECPU (ElastiCache Processing Units) monitoring
- Data storage utilization
- Request success rate tracking
- Throttled request detection

**Alarm Purpose and Explanations:**

**CPU Utilization**: Monitors cache cluster CPU usage. High CPU can indicate:
- Complex operations or heavy computational workload
- Insufficient instance sizing for current demand
- Need for cluster scaling or read replicas

**Memory Utilization**: Tracks memory usage percentage. High memory can indicate:
- Cache size approaching capacity limits
- Need for memory optimization or larger instance types
- Potential eviction of cached data

**Cache Hit Ratio**: Monitors cache effectiveness. Low hit ratio can indicate:
- Inefficient caching strategy or short TTL values
- Cache warming needed after restarts
- Application not utilizing cache effectively

**Connection Count**: Tracks active client connections. High connections can indicate:
- Application connection pool misconfiguration
- Connection leaks in client applications
- Need for connection multiplexing or pooling

**Network Throughput**: Monitors data transfer rates. High throughput can indicate:
- Large object caching or bulk data operations
- Network bottlenecks requiring optimization
- Potential need for multiple AZ deployment

**Replication Lag** (Redis): Tracks synchronization delay between primary and replica. High lag can indicate:
- Network issues between availability zones
- Heavy write load overwhelming replication
- Need for read replica scaling or optimization

**ECPU Utilization** (Serverless): Monitors processing unit consumption. High ECPU can indicate:
- Workload approaching serverless capacity limits
- Need for capacity planning or optimization
- Complex operations requiring more processing power

**Data Storage** (Serverless): Tracks storage utilization. High storage can indicate:
- Data growth requiring capacity planning
- Large object sizes affecting storage efficiency
- Need for data lifecycle management

## Usage Examples

### 1. Deploy SNS Topics First
```bash
aws cloudformation create-stack \
  --stack-name MyApp-SNS-Topics \
  --template-body file://sns-cf.yaml \
  --parameters \
    ParameterKey=InstituteName,ParameterValue=ACME \
    ParameterKey=AppShortName,ParameterValue=MyApp \
    ParameterKey=EnvName,ParameterValue=prod
```

### 2. Deploy ALB Monitoring
```bash
aws cloudformation create-stack \
  --stack-name MyApp-ALB-Monitoring \
  --template-body file://alb-cf.yaml \
  --parameters \
    ParameterKey=AppShortName,ParameterValue=MyApp \
    ParameterKey=EnvName,ParameterValue=prod \
    ParameterKey=Alb1Name,ParameterValue=app/MyApp-ALB/1234567890123456 \
    ParameterKey=Alb1TargetGroup1Name,ParameterValue=MyApp-TG-Web \
    ParameterKey=Alb1TargetGroup2Name,ParameterValue=MyApp-TG-API \
    ParameterKey=Team1SNSTopicArn,ParameterValue=arn:aws:sns:us-east-1:123456789012:ACME-MyApp-prod-sns-l2ops \
    ParameterKey=Team2SNSTopicArn,ParameterValue=arn:aws:sns:us-east-1:123456789012:ACME-MyApp-prod-sns-l3support \
    ParameterKey=Team3SNSTopicArn,ParameterValue=arn:aws:sns:us-east-1:123456789012:ACME-MyApp-prod-sns-infra
```

### 3. Deploy API Gateway Monitoring
```bash
aws cloudformation create-stack \
  --stack-name MyApp-APIGW-Monitoring \
  --template-body file://apigateway-cf.yaml \
  --parameters \
    ParameterKey=AppShortName,ParameterValue=MyApp \
    ParameterKey=EnvName,ParameterValue=prod \
    ParameterKey=ApiGatewayName,ParameterValue=MyApp-API \
    ParameterKey=ApiGatewayStage,ParameterValue=prod \
    ParameterKey=ResourcePath1,ParameterValue=/api/v1/users \
    ParameterKey=ResourcePath2,ParameterValue=/api/v1/orders \
    ParameterKey=AlarmSNSTopicArn,ParameterValue=arn:aws:sns:us-east-1:123456789012:ACME-MyApp-prod-sns-l2ops \
    ParameterKey=Team1SNSTopicArn,ParameterValue=arn:aws:sns:us-east-1:123456789012:ACME-MyApp-prod-sns-l2ops \
    ParameterKey=Team2SNSTopicArn,ParameterValue=arn:aws:sns:us-east-1:123456789012:ACME-MyApp-prod-sns-l3support
```

### 4. Deploy ECS Service Monitoring
```bash
aws cloudformation create-stack \
  --stack-name MyApp-ECS-Monitoring \
  --template-body file://ecs-cf.yaml \
  --parameters \
    ParameterKey=AppShortName,ParameterValue=MyApp \
    ParameterKey=EnvName,ParameterValue=prod \
    ParameterKey=ECSClusterName,ParameterValue=MyApp-prod-cluster \
    ParameterKey=ECSService1Name,ParameterValue=MyApp-web-service \
    ParameterKey=ECSService2Name,ParameterValue=MyApp-api-service \
    ParameterKey=ECSService3Name,ParameterValue=MyApp-worker-service \
    ParameterKey=AlarmSNSTopicArn,ParameterValue=arn:aws:sns:us-east-1:123456789012:ACME-MyApp-prod-sns-l2ops \
    ParameterKey=Team1SNSTopicArn,ParameterValue=arn:aws:sns:us-east-1:123456789012:ACME-MyApp-prod-sns-l2ops \
    ParameterKey=Team2SNSTopicArn,ParameterValue=arn:aws:sns:us-east-1:123456789012:ACME-MyApp-prod-sns-l3support \
    ParameterKey=CPUUtilizationCriticalThreshold,ParameterValue=90 \
    ParameterKey=CPUUtilizationWarningThreshold,ParameterValue=80 \
    ParameterKey=MemoryUtilizationCriticalThreshold,ParameterValue=90 \
    ParameterKey=MemoryUtilizationWarningThreshold,ParameterValue=80 \
    ParameterKey=DesiredCountThreshold,ParameterValue=1 \
    ParameterKey=RunningTaskCountThreshold,ParameterValue=1
```

### 5. Deploy ElastiCache Monitoring
```bash
aws cloudformation create-stack \
  --stack-name MyApp-ElastiCache-Monitoring \
  --template-body file://elasticache-cf.yaml \
  --parameters \
    ParameterKey=AppShortName,ParameterValue=MyApp \
    ParameterKey=EnvName,ParameterValue=prod \
    ParameterKey=ElastiCacheCluster1Name,ParameterValue=MyApp-prod-redis-cluster-001 \
    ParameterKey=ElastiCacheCluster2Name,ParameterValue=MyApp-prod-memcached-cluster-001 \
    ParameterKey=ServerlessCache1Name,ParameterValue=MyApp-prod-serverless-redis \
    ParameterKey=ServerlessCache2Name,ParameterValue=MyApp-prod-serverless-memcached \
    ParameterKey=Team1SNSTopicArn,ParameterValue=arn:aws:sns:us-east-1:123456789012:ACME-MyApp-prod-sns-l2ops \
    ParameterKey=Team2SNSTopicArn,ParameterValue=arn:aws:sns:us-east-1:123456789012:ACME-MyApp-prod-sns-l3support \
    ParameterKey=Team3SNSTopicArn,ParameterValue=arn:aws:sns:us-east-1:123456789012:ACME-MyApp-prod-sns-infra \
    ParameterKey=CPUUtilizationThreshold,ParameterValue=80 \
    ParameterKey=MemoryUtilizationThreshold,ParameterValue=80 \
    ParameterKey=CacheHitRatioThreshold,ParameterValue=80 \
    ParameterKey=ConnectionCountThreshold,ParameterValue=100 \
    ParameterKey=ReplicationLagThreshold,ParameterValue=60 \
    ParameterKey=ServerlessECPUUtilizationThreshold,ParameterValue=80 \
    ParameterKey=ServerlessDataStorageThreshold,ParameterValue=1073741824
```

## Parameter Reference

### Common Parameters
- **AppShortName**: Application short name (used in resource naming)
- **EnvName**: Environment name (nprd, prod, prod-a, etc.)
- **AlarmSNSTopicArn**: Primary SNS topic for alarm notifications
- **Team1SNSTopicArn**: L2 Operations team notifications (optional)
- **Team2SNSTopicArn**: L3 Support/Development team notifications (optional)
- **Team3SNSTopicArn**: Infrastructure/Platform team notifications (optional)

### ALB-Specific Parameters
- **Alb1Name**: Primary ALB name (required)
- **Alb2Name, Alb3Name, Alb4Name**: Additional ALBs (optional)
- **Alb1TargetGroup1Name, Alb1TargetGroup2Name, Alb1TargetGroup3Name**: ALB 1 target group names (optional)
- **Alb2TargetGroup1Name, Alb2TargetGroup2Name, Alb2TargetGroup3Name**: ALB 2 target group names (optional)
- **Alb3TargetGroup1Name, Alb3TargetGroup2Name, Alb3TargetGroup3Name**: ALB 3 target group names (optional)
- **Alb4TargetGroup1Name, Alb4TargetGroup2Name, Alb4TargetGroup3Name**: ALB 4 target group names (optional)

### API Gateway-Specific Parameters
- **ApiGatewayName**: API Gateway name
- **ApiGatewayStage**: Stage name (default: prod)
- **ResourcePath1, ResourcePath2, ResourcePath3**: Resource paths for optional integration monitoring (e.g., /api/v1/users)

### ECS-Specific Parameters
- **ECSClusterName**: ECS cluster name for monitoring (required)
- **ECSService1Name**: Primary ECS service name (required)
- **ECSService2Name, ECSService3Name**: Additional ECS services (optional)
- **CPUUtilizationCriticalThreshold**: Critical CPU utilization threshold percentage (default: 90)
- **CPUUtilizationWarningThreshold**: Warning CPU utilization threshold percentage (default: 80)
- **MemoryUtilizationCriticalThreshold**: Critical memory utilization threshold percentage (default: 90)
- **MemoryUtilizationWarningThreshold**: Warning memory utilization threshold percentage (default: 80)
- **DesiredCountThreshold**: Minimum desired count threshold (default: 1)
- **RunningTaskCountThreshold**: Minimum running task count threshold (default: 1)

### ElastiCache-Specific Parameters
- **ElastiCacheCluster1Name**: Primary ElastiCache cluster name (optional)
- **ElastiCacheCluster2Name, ElastiCacheCluster3Name**: Additional clusters (optional)
- **ServerlessCache1Name, ServerlessCache2Name**: Serverless cache names (optional)
- **CPUUtilizationThreshold**: CPU utilization threshold percentage (default: 80)
- **MemoryUtilizationThreshold**: Memory utilization threshold percentage (default: 80)
- **NetworkBytesInThreshold**: Network bytes in threshold per second (default: 100MB)
- **NetworkBytesOutThreshold**: Network bytes out threshold per second (default: 100MB)
- **CacheHitRatioThreshold**: Cache hit ratio threshold percentage (default: 80)
- **ConnectionCountThreshold**: Current connections threshold (default: 100)
- **ReplicationLagThreshold**: Redis replication lag threshold in seconds (default: 60)
- **ServerlessDataStorageThreshold**: Serverless data storage threshold in bytes (default: 1GB)
- **ServerlessECPUUtilizationThreshold**: Serverless ECPU utilization threshold (default: 80)

### Lambda-Specific Parameters
- **Lambda1FunctionName**: Primary Lambda function name (required)
- **Lambda2FunctionName, Lambda3FunctionName**: Additional Lambda functions (optional)
- **ErrorThreshold**: Lambda error count threshold (default: 5)
- **DurationThreshold**: Lambda duration threshold in milliseconds (default: 30000)
- **ThrottleThreshold**: Lambda throttle count threshold (default: 1)

### RDS-Specific Parameters
- **RDSInstanceIdentifier1**: Primary RDS instance identifier (required)
- **RDSInstanceIdentifier2, RDSInstanceIdentifier3**: Additional RDS instances (optional)
- **CPUThreshold**: CPU utilization threshold percentage (default: 80)
- **DatabaseConnectionsThreshold**: Database connections threshold (default: 80)
- **FreeableMemoryThreshold**: Freeable memory threshold in bytes (default: 2147483648 = 2GB)
- **FreeStorageSpaceThreshold**: Free storage space threshold in bytes (default: 10737418240 = 10GB)
- **ReadLatencyThreshold**: Read latency threshold in seconds (default: 0.2)
- **WriteLatencyThreshold**: Write latency threshold in seconds (default: 0.2)
- **ErrorThreshold**: Error count threshold (default: 5)
- **DurationThreshold**: Duration threshold in milliseconds (default: 30000)
- **ThrottleThreshold**: Throttle count threshold (default: 1)

### SNS-Specific Parameters
- **InstituteName**: Institute/Organization name for SNS topic naming

## Environment Support

All templates support the following environments:
- **Non-Production**: nprd, nprd-dev, nprd-sit1, nprd-sit2, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b
- **Production**: prod, prod-a, prod-b

Production environments have enhanced retention policies to prevent accidental deletion.

## Naming Conventions

### Resource Names
- **ALB Alarms**: `{AppShortName}-{EnvName}-{ALBName}-{MetricType}`
- **ALB Target Group Alarms**: `{AppShortName}-{EnvName}-{TargetGroupName}-{MetricType}`
- **Lambda Alarms**: `{AppShortName}-{EnvName}-{FunctionName}-{MetricType}`
- **API Gateway Alarms**: `{AppShortName}-{EnvName}-{ApiGatewayName}-{MetricType}`
- **ECS Service Alarms**: `{AppShortName}-{EnvName}-{ServiceName}-{MetricType}-{Severity}`
- **ECS Cluster Alarms**: `{AppShortName}-{EnvName}-{ClusterName}-{MetricType}`
- **RDS Alarms**: `{AppShortName}-{EnvName}-{RDSInstanceIdentifier}-{MetricType}`
- **SNS Topics**: `{InstituteName}-{AppShortName}-{EnvName}-sns-{TeamType}`

### Tags
All resources include standardized tags:
- **Name**: Descriptive resource name
- **IaCVersion**: Template version (e.g., Observability-ALB-v1)

## Alarm Thresholds

### ALB Alarms
- **5XX Errors**: ≥ 1 error in 2 periods (1 minute each)
- **4XX Errors**: ≥ 50 errors in 2 periods (1 minute each)
- **Target Response Time**: ≥ 5 seconds average over 5 minutes
- **Healthy Hosts**: < 1 healthy host for 2 periods (1 minute each)

### API Gateway Alarms
- **5XX Errors**: ≥ 1 error in 2 periods (1 minute each)
- **4XX Errors**: ≥ 50 errors in 2 periods (1 minute each)
- **Latency**: ≥ 5 seconds average over 5 minutes
- **Integration Latency**: ≥ 4 seconds average over 5 minutes
- **High Traffic**: ≥ 1000 requests in 1 minute
- **Low Traffic**: < 1 request in 15 minutes (3 periods of 5 minutes)

### Lambda Alarms
- **Errors**: ≥ ErrorThreshold (default: 5) in 2 periods (1 minute each)
- **Duration**: ≥ DurationThreshold (default: 30 seconds) average over 5 minutes
- **Throttles**: ≥ ThrottleThreshold (default: 1) in 1 period (1 minute)
- **Dead Letter Errors**: ≥ 1 error in 1 period (1 minute)
- **Concurrent Executions**: ≥ 800 concurrent executions for 2 periods (1 minute each)

### ECS Service Alarms
- **🔴 CPU Utilization Critical**: ≥ CPUUtilizationCriticalThreshold (default: 90%) average over 5 minutes for 2 periods
- **🟡 CPU Utilization Warning**: ≥ CPUUtilizationWarningThreshold (default: 80%) average over 5 minutes for 3 periods
- **🔴 Memory Utilization Critical**: ≥ MemoryUtilizationCriticalThreshold (default: 90%) average over 5 minutes for 2 periods
- **🟡 Memory Utilization Warning**: ≥ MemoryUtilizationWarningThreshold (default: 80%) average over 5 minutes for 3 periods
- **🔴 Running Task Count**: < RunningTaskCountThreshold (default: 1) for 2 periods (5 minutes each)
- **� Desired Task Count**: < DesiredCountThreshold (default: 1) for 2 periods (5 minutes each)

### ECS Cluster Alarms
- **🟡 CPU Reservation**: ≥ 80% average over 5 minutes for 2 periods
- **🟡 Memory Reservation**: ≥ 80% average over 5 minutes for 2 periods

### RDS Alarms
- **CPU Utilization**: ≥ CPUThreshold (default: 80%) average over 5 minutes for 2 periods
- **Database Connections**: ≥ DatabaseConnectionsThreshold (default: 80) average over 5 minutes for 2 periods
- **Freeable Memory**: ≤ FreeableMemoryThreshold (default: 2GB) average over 5 minutes for 2 periods
- **Free Storage Space**: ≤ FreeStorageSpaceThreshold (default: 10GB) average over 5 minutes for 2 periods
- **Read Latency**: ≥ ReadLatencyThreshold (default: 0.2 seconds) average over 5 minutes for 2 periods
- **Write Latency**: ≥ WriteLatencyThreshold (default: 0.2 seconds) average over 5 minutes for 2 periods
- **Swap Usage**: ≥ 256MB for 2 periods (5 minutes each)

### ElastiCache Alarms
- **CPU Utilization**: ≥ CPUUtilizationCriticalThreshold (default: 90%) average over 5 minutes for 2 periods
- **Memory Utilization**: ≥ MemoryUtilizationCriticalThreshold (default: 90%) average over 5 minutes for 2 periods
- **ECPU Utilization**: ≥ ECPUUtilizationThreshold (default: 80%) average over 5 minutes for 2 periods
- **Data Storage**: ≥ DataStorageThreshold (default: 80%) average over 5 minutes for 2 periods
- **Cache Hit Ratio**: < 80% average over 5 minutes for 2 periods
- **Connection Count**: ≥ 1000 for 2 periods (5 minutes each)
- **Network Throughput**: < 1 MBps for 2 periods (5 minutes each)
- **Replication Lag**: > 1 second for 2 periods (5 minutes each)

## Multi-Team Notifications

The templates support routing different alarm types to different teams:
- **Team 1** (L2 Operations): Operational alerts, immediate response required
- **Team 2** (L3 Support/Development): Application-level issues, development team attention
- **Team 3** (Infrastructure/Platform): Infrastructure-level alerts, platform team attention

Teams can be configured independently per alarm type, allowing for flexible notification routing.

## Production Considerations

- **Deletion Policies**: Production resources use `Retain` policy to prevent accidental deletion
- **Update Policies**: Production resources use `Retain` policy for CloudFormation updates
- **Alarm Periods**: Optimized for production workloads with appropriate evaluation periods
- **Thresholds**: Set for production-level traffic and performance expectations

## Integration with Monitoring Strategy

These templates are designed to integrate with enterprise monitoring strategies:
1. **Deploy SNS topics** first to establish notification channels
2. **Deploy resource-specific monitoring** (ALB, API Gateway) referencing SNS topics
3. **Configure team subscriptions** to SNS topics based on operational responsibility
4. **Customize thresholds** based on application-specific SLAs and performance requirements

## Troubleshooting

### Common Issues
1. **SNS Topic ARN Format**: Ensure SNS topic ARNs are complete and correctly formatted
2. **Resource Names**: Verify ALB, API Gateway, Lambda function, ECS service/cluster, and RDS instance names match actual AWS resources
3. **ALB Names**: Use the exact ALB names as they appear in AWS Console (format: app/name/id for LoadBalancer dimension)
4. **Target Group Names**: Use actual target group names as they appear in AWS Console
5. **ECS Service Names**: Use actual ECS service names and cluster names as they appear in AWS Console
6. **RDS Instance Identifiers**: Use the actual RDS DB instance identifiers, not the DB cluster identifiers
7. **Permissions**: Ensure CloudFormation has permissions to create CloudWatch alarms and reference SNS topics

### Validation
- Use AWS CLI to validate templates before deployment
- Test SNS notifications after deployment
- Verify alarm states in CloudWatch console
- Check CloudFormation events for any deployment issues
