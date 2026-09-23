# CloudWatch Alarms Summary Table

## Overview
This table provides a comprehensive overview of all critical and important CloudWatch alarms across all monitoring templates in the Observability folder.

## Alert Summary by Service

### 1. RDS Database Monitoring (rds-cf.yaml)

| Service Name | Metric Name | Threshold | Comparison Operator | Actions |
|-------------|-------------|-----------|-------------------|---------|
| RDS1 | CPUUtilization | 80% (configurable) | GreaterThanOrEqualToThreshold | Team1, Team2 SNS Topics |
| RDS1 | DatabaseConnections | 80 connections (configurable) | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| RDS1 | FreeableMemory | 2GB (configurable) | LessThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| RDS1 | FreeStorageSpace | 10GB (configurable) | LessThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| RDS2 | CPUUtilization | 80% (configurable) | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| RDS2 | DatabaseConnections | 80 connections (configurable) | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| RDS2 | FreeableMemory | 2GB (configurable) | LessThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| RDS2 | FreeStorageSpace | 10GB (configurable) | LessThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| RDS3 | CPUUtilization | 80% (configurable) | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| RDS3 | DatabaseConnections | 80 connections (configurable) | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| RDS3 | FreeableMemory | 2GB (configurable) | LessThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| RDS3 | FreeStorageSpace | 10GB (configurable) | LessThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |

### 2. API Gateway Monitoring (apigateway-cf.yaml)

| Service Name | Metric Name | Threshold | Comparison Operator | Actions |
|-------------|-------------|-----------|-------------------|---------|
| ApiGateway1 | 5XXError | 1 error | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| ApiGateway1 | 4XXError | 50 errors | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| ApiGateway1 | Latency | 5000ms | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| ApiGateway1 | IntegrationLatency | 4000ms | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| ApiGateway1 | Count (High Traffic) | 2000 requests/min | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| ApiGateway2 | 5XXError | 1 error | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| ApiGateway2 | 4XXError | 50 errors | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| ApiGateway2 | Latency | 5000ms | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| ApiGateway2 | IntegrationLatency | 4000ms | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| ApiGateway2 | Count (High Traffic) | 2000 requests/min | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |

### 3. ECS Service Monitoring (ecs-cf.yaml)

| Service Name | Metric Name | Threshold | Comparison Operator | Actions |
|-------------|-------------|-----------|-------------------|---------|
| **ECS Service1** | **🔴 CPUUtilization (Critical)** | 90% (configurable) | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| ECS Service1 | **🔴 MemoryUtilization (Critical)** | 90% (configurable) | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| ECS Service1 | **🔴 RunningTaskCount (Critical)** | <1 task (configurable) | LessThanThreshold | Team1, Team2, Team3 SNS Topics |
| ECS Service1 | **🔴 DesiredCount (Critical)** | <1 task (configurable) | LessThanThreshold | Team1, Team2, Team3 SNS Topics |
| ECS Service1 | **🟡 CPUUtilization (Warning)** | 80% (configurable) | GreaterThanOrEqualToThreshold | Team1, Team2 SNS Topics |
| ECS Service1 | **🟡 MemoryUtilization (Warning)** | 80% (configurable) | GreaterThanOrEqualToThreshold | Team1, Team2 SNS Topics |
| **ECS Service2** | **🔴 CPUUtilization (Critical)** | 90% (configurable) | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| ECS Service2 | **🔴 MemoryUtilization (Critical)** | 90% (configurable) | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| ECS Service2 | **🔴 RunningTaskCount (Critical)** | <1 task (configurable) | LessThanThreshold | Team1, Team2, Team3 SNS Topics |
| ECS Service2 | **🔴 DesiredCount (Critical)** | <1 task (configurable) | LessThanThreshold | Team1, Team2, Team3 SNS Topics |
| ECS Service2 | **🟡 CPUUtilization (Warning)** | 80% (configurable) | GreaterThanOrEqualToThreshold | Team1, Team2 SNS Topics |
| ECS Service2 | **🟡 MemoryUtilization (Warning)** | 80% (configurable) | GreaterThanOrEqualToThreshold | Team1, Team2 SNS Topics |
| **ECS Service3** | **🔴 CPUUtilization (Critical)** | 90% (configurable) | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| ECS Service3 | **🔴 MemoryUtilization (Critical)** | 90% (configurable) | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| ECS Service3 | **🔴 RunningTaskCount (Critical)** | <1 task (configurable) | LessThanThreshold | Team1, Team2, Team3 SNS Topics |
| ECS Service3 | **🔴 DesiredCount (Critical)** | <1 task (configurable) | LessThanThreshold | Team1, Team2, Team3 SNS Topics |
| ECS Service3 | **🟡 CPUUtilization (Warning)** | 80% (configurable) | GreaterThanOrEqualToThreshold | Team1, Team2 SNS Topics |
| ECS Service3 | **🟡 MemoryUtilization (Warning)** | 80% (configurable) | GreaterThanOrEqualToThreshold | Team1, Team2 SNS Topics |
| **ECS Cluster** | **🟡 CPUReservation** | 80% | GreaterThanOrEqualToThreshold | Team1, Team3 SNS Topics |
| ECS Cluster | **🟡 MemoryReservation** | 80% | GreaterThanOrEqualToThreshold | Team1, Team3 SNS Topics |

**Total ECS Monitoring**: Up to 20 alarms (18 service-level + 2 cluster-level)

### 4. SQS Queue Monitoring (sqs-alerts-cf.yaml)

| Service Name | Metric Name | Threshold | Comparison Operator | Actions |
|-------------|-------------|-----------|-------------------|---------|
| SQS Queue | ApproximateNumberOfMessages | 10 messages | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| SQS Queue | ApproximateAgeOfOldestMessage | 300 seconds | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| SQS DLQ | ApproximateNumberOfMessages | 1 message | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |

### 5. Glue Job Monitoring (glue-job-alerts-cf.yaml)

| Service Name | Metric Name | Threshold | Comparison Operator | Actions |
|-------------|-------------|-----------|-------------------|---------|
| Glue Job | glue.driver.aggregate.numFailedTasks | 1 failed task | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| Glue Job | glue.driver.aggregate.elapsedTime | 3600000ms (1 hour) | GreaterThanThreshold | Team1, Team2, Team3 SNS Topics |

### 6. Application Load Balancer Multi-Target Group (alb-cf.yaml)

| Service Name | Metric Name | Threshold | Comparison Operator | Actions |
|-------------|-------------|-----------|-------------------|---------|
| ALB1 | HTTPCode_ELB_5XX_Count | 5 errors | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| ALB1 TG1 | UnHealthyHostCount | 1 host | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| ALB1 TG1 | HTTPCode_Target_5XX_Count | 5 errors | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| ALB1 TG1 | TargetResponseTime | 3 seconds | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| ALB1 TG2 | UnHealthyHostCount | 1 host | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| ALB1 TG2 | HTTPCode_Target_5XX_Count | 5 errors | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| ALB1 TG2 | TargetResponseTime | 3 seconds | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| ALB1 TG3 | UnHealthyHostCount | 1 host | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| ALB1 TG3 | HTTPCode_Target_5XX_Count | 5 errors | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| ALB1 TG3 | TargetResponseTime | 3 seconds | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| ALB2 | HTTPCode_ELB_5XX_Count | 5 errors | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| ALB2 TG1 | UnHealthyHostCount | 1 host | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| ALB2 TG1 | HTTPCode_Target_5XX_Count | 5 errors | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| ALB2 TG1 | TargetResponseTime | 3 seconds | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| ALB2 TG2 | UnHealthyHostCount | 1 host | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| ALB2 TG2 | HTTPCode_Target_5XX_Count | 5 errors | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| ALB2 TG2 | TargetResponseTime | 3 seconds | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| ALB2 TG3 | UnHealthyHostCount | 1 host | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| ALB2 TG3 | HTTPCode_Target_5XX_Count | 5 errors | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| ALB2 TG3 | TargetResponseTime | 3 seconds | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| ALB3 | HTTPCode_ELB_5XX_Count | 5 errors | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| ALB3 TG1 | UnHealthyHostCount | 1 host | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| ALB3 TG1 | HTTPCode_Target_5XX_Count | 5 errors | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| ALB3 TG1 | TargetResponseTime | 3 seconds | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| ALB3 TG2 | UnHealthyHostCount | 1 host | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| ALB3 TG2 | HTTPCode_Target_5XX_Count | 5 errors | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| ALB3 TG2 | TargetResponseTime | 3 seconds | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| ALB3 TG3 | UnHealthyHostCount | 1 host | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| ALB3 TG3 | HTTPCode_Target_5XX_Count | 5 errors | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| ALB3 TG3 | TargetResponseTime | 3 seconds | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| ALB4 | HTTPCode_ELB_5XX_Count | 5 errors | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| ALB4 TG1 | UnHealthyHostCount | 1 host | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| ALB4 TG1 | HTTPCode_Target_5XX_Count | 5 errors | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| ALB4 TG1 | TargetResponseTime | 3 seconds | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| ALB4 TG2 | UnHealthyHostCount | 1 host | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| ALB4 TG2 | HTTPCode_Target_5XX_Count | 5 errors | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| ALB4 TG2 | TargetResponseTime | 3 seconds | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| ALB4 TG3 | UnHealthyHostCount | 1 host | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| ALB4 TG3 | HTTPCode_Target_5XX_Count | 5 errors | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| ALB4 TG3 | TargetResponseTime | 3 seconds | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |

### 7. ElastiCache Serverless Monitoring (elasticache-serverless-cf.yaml)

**Purpose**: Focused monitoring for single ElastiCache Serverless cache with essential alerts only

#### ElastiCache Serverless Cache Monitoring

| Service Name | Metric Name | Threshold | Comparison Operator | Actions |
|-------------|-------------|-----------|-------------------|---------|
| **Serverless Cache** | **🔴 ElastiCacheProcessingUnits (ECPU) - Critical** | 90% (fixed) | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| Serverless Cache | **🔴 DataStorage - Critical** | 1GB (fixed) | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| Serverless Cache | **🟡 ThrottledRequestCount - Important** | 5 requests (fixed) | GreaterThanOrEqualToThreshold | Team1, Team2 SNS Topics |

**Total ElastiCache Serverless Monitoring**: 3 focused alerts for single cache

**Alert Categories:**
- **🔴 Critical Alerts (2)**: ECPU >90%, Storage >1GB - Require immediate attention
- **🟡 Important Alerts (1)**: Throttled requests >5 - Performance monitoring

**Key Features:**
- **Fixed Thresholds**: Production-ready values, no configuration needed
- **Single Cache Focus**: Simplified monitoring for one serverless cache
- **Essential Alerts Only**: Critical and important alerts to prevent noise
- **Smart Routing**: Critical alerts go to all teams, important alerts to ops and dev teams

### 8. Lambda Function Monitoring (lambda-cf.yaml)

| Service Name | Metric Name | Threshold | Comparison Operator | Actions |
|-------------|-------------|-----------|-------------------|---------|
| Lambda1 | Errors | 5 errors (configurable) | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| Lambda1 | Duration | 30000ms (configurable) | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| Lambda1 | Throttles | 1 throttle (configurable) | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| Lambda1 | DeadLetterErrors | 1 error | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| Lambda1 | ConcurrentExecutions | 800 executions | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| Lambda2 | Errors | 5 errors (configurable) | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| Lambda2 | Duration | 30000ms (configurable) | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| Lambda2 | Throttles | 1 throttle (configurable) | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| Lambda2 | DeadLetterErrors | 1 error | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| Lambda2 | ConcurrentExecutions | 800 executions | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| Lambda3 | Errors | 5 errors (configurable) | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| Lambda3 | Duration | 30000ms (configurable) | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| Lambda3 | Throttles | 1 throttle (configurable) | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| Lambda3 | DeadLetterErrors | 1 error | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |
| Lambda3 | ConcurrentExecutions | 800 executions | GreaterThanOrEqualToThreshold | Team1, Team2, Team3 SNS Topics |

## SNS Topics (sns-cf.yaml)

| Topic Name | Purpose | Team Mapping |
|------------|---------|--------------|
| AppL2OpsSNSTopic | L2 Operations Team | Team1SNSTopicArn |
| AppL3SupportSNSTopic | L3 Support/Development Team | Team2SNSTopicArn |
| InfraL3SupportSNSTopic | Infrastructure/Platform Team | Team3SNSTopicArn |
| DbOpsSNSTopic | Database Operations Team | Additional Topic |
| SecurityOpsSNSTopic | Security Operations Team | Additional Topic |

## Alert Severity Classification

### Critical Alerts (Immediate Response Required)
- **RDS**: CPUUtilization > 80%, FreeStorageSpace < 10GB, FreeableMemory < 2GB
- **API Gateway**: 5XXError >= 1, Latency > 5000ms
- **SQS**: DLQ Messages >= 1
- **ALB**: UnHealthyHostCount >= 1, HTTPCode_Target_5XX_Count >= 5
- **Lambda**: Errors >= 5, DeadLetterErrors >= 1
- **ECS**: CPUUtilization > 90%, MemoryUtilization > 90%, RunningTaskCount < 1, DesiredCount < 1
- **ElastiCache Serverless**: ECPU > 90%, DataStorage > 1GB

### Important Alerts (Monitoring Required)
- **RDS**: DatabaseConnections > 80
- **API Gateway**: 4XXError >= 50, IntegrationLatency > 4000ms, Count (High Traffic) >= 2000 requests/min
- **SQS**: ApproximateNumberOfMessages >= 10, ApproximateAgeOfOldestMessage >= 300s
- **ALB**: TargetResponseTime >= 3s
- **Lambda**: Duration > 30000ms, Throttles >= 1, ConcurrentExecutions >= 800
- **Glue**: Failed Tasks >= 1, Excessive Duration > 1 hour
- **ECS**: CPUUtilization > 80%, MemoryUtilization > 80%
- **ElastiCache Serverless**: ThrottledRequestCount >= 5

## Configuration Notes

1. **Team-Based Notifications**: All alarms use Team1, Team2, and Team3 SNS topics with conditional logic
2. **Configurable Thresholds**: Most thresholds are configurable via CloudFormation parameters
3. **Production Retention**: Alarms in production environments have Retain deletion policy
4. **Missing Data Handling**: Most alarms treat missing data as "notBreaching"
5. **Evaluation Periods**: Most alarms use 2 evaluation periods for reliability

## Maintenance

- **Regular Review**: Thresholds should be reviewed quarterly based on actual usage patterns
- **Team Mappings**: SNS topic subscriptions should be maintained by respective teams
- **Alert Fatigue**: Monitor alarm frequency and adjust thresholds to reduce false positives
