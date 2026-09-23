# AWS SQS Template Guide

## 📋 Overview

The AWS SQS template (`cf-sqs.yaml`) is a CloudFormation template for creating Standard SQS queues with optional Dead Letter Queue support. It provides a standardized approach to deploying message queues for asynchronous processing across any AWS project.

## 🗂️ Template Files

| File | Purpose |
|------|---------|
| `cf-sqs.yaml` | CloudFormation template for creating Standard SQS queues |
| `parameters-sqs.json` | Parameter configuration file |

## 🎯 Use Cases

This template can be used for any project requiring:
- **Asynchronous Message Processing** - Decoupling application components
- **Event-Driven Architecture** - Processing events from various sources
- **Batch Processing** - Collecting messages for batch operations
- **Lambda Integration** - Event source for Lambda functions
- **Microservices Communication** - Reliable message passing between services

## 📋 Template Parameters

### parameters-sqs.json

```json
[
  {
    "ParameterKey": "AppShortName",
    "ParameterValue": "myapp"
  },
  {
    "ParameterKey": "EnvName",
    "ParameterValue": "nprd"
  },
  {
    "ParameterKey": "QueueName",
    "ParameterValue": "processing"
  },
  {
    "ParameterKey": "QueueDescription",
    "ParameterValue": "Standard SQS Queue for message processing"
  },
  {
    "ParameterKey": "EnableDeadLetterQueue",
    "ParameterValue": "true"
  },
  {
    "ParameterKey": "EnableServerSideEncryption",
    "ParameterValue": "true"
  }
]
```

### Core Parameters

| Parameter | Required | Example Value | Description |
|-----------|----------|---------------|-------------|
| `AppShortName` | **Mandatory** | `myapp` | Application or project identifier |
| `EnvName` | **Mandatory** | `nprd`, `prod` | Environment name |
| `QueueName` | **Mandatory** | `processing`, `notifications` | Descriptive name of the queue |
| `QueueDescription` | Optional | `Standard SQS Queue for message processing` | Human-readable description |

### Queue Configuration

| Parameter | Required | Default Value | Range | Description |
|-----------|----------|---------------|-------|-------------|
| `VisibilityTimeoutSeconds` | Optional | `300` | 0-43200 | Time messages are invisible after being received |
| `MessageRetentionPeriod` | Optional | `1209600` | 60-1209600 | How long messages are retained (14 days default) |
| `MaxReceiveCount` | Optional | `5` | 1-1000 | Attempts before moving to dead letter queue |
| `DelaySeconds` | Optional | `0` | 0-900 | Delay before messages become available |
| `ReceiveMessageWaitTimeSeconds` | Optional | `20` | 0-20 | Long polling wait time |
| `MaxMessageSize` | Optional | `262144` | 1024-262144 | Maximum message size in bytes (256KB default) |

### Dead Letter Queue Settings

| Parameter | Required | Default Value | Description |
|-----------|----------|---------------|-------------|
| `EnableDeadLetterQueue` | Optional | `true` | Enable dead letter queue for failed messages |
| `DeadLetterQueueMessageRetentionPeriod` | Optional | `1209600` | Message retention for DLQ (14 days) |

### Encryption Settings

| Parameter | Required | Default Value | Description |
|-----------|----------|---------------|-------------|
| `EnableServerSideEncryption` | Optional | `true` | Enable server-side encryption |
| `KmsMasterKeyId` | Optional | `alias/aws/sqs` | KMS key for encryption (AWS managed default) |

## 🔧 Common Queue Configurations

### High-Throughput Processing Queue
```json
[
  {
    "ParameterKey": "QueueName",
    "ParameterValue": "high-throughput"
  },
  {
    "ParameterKey": "VisibilityTimeoutSeconds",
    "ParameterValue": "60"
  },
  {
    "ParameterKey": "ReceiveMessageWaitTimeSeconds",
    "ParameterValue": "20"
  },
  {
    "ParameterKey": "MaxReceiveCount",
    "ParameterValue": "3"
  }
]
```

### Batch Processing Queue
```json
[
  {
    "ParameterKey": "QueueName",
    "ParameterValue": "batch-processing"
  },
  {
    "ParameterKey": "VisibilityTimeoutSeconds",
    "ParameterValue": "900"
  },
  {
    "ParameterKey": "DelaySeconds",
    "ParameterValue": "300"
  },
  {
    "ParameterKey": "MaxReceiveCount",
    "ParameterValue": "10"
  }
]
```

### Notification Queue
```json
[
  {
    "ParameterKey": "QueueName",
    "ParameterValue": "notifications"
  },
  {
    "ParameterKey": "VisibilityTimeoutSeconds",
    "ParameterValue": "120"
  },
  {
    "ParameterKey": "MessageRetentionPeriod",
    "ParameterValue": "86400"
  },
  {
    "ParameterKey": "MaxReceiveCount",
    "ParameterValue": "3"
  }
]
```

## 🚀 Deployment

### Single Queue Deployment

```bash
# Deploy a processing queue
aws cloudformation create-stack \
  --stack-name myapp-nprd-sqs-processing \
  --template-body file://cf-sqs.yaml \
  --parameters file://parameters-sqs.json
```

### Multiple Queues Deployment via Pipeline

Create separate parameter files for different queue types:

#### parameters-sqs-processing.json
```json
[
  {
    "ParameterKey": "QueueName",
    "ParameterValue": "processing"
  },
  {
    "ParameterKey": "QueueDescription",
    "ParameterValue": "Main processing queue for application events"
  },
  {
    "ParameterKey": "VisibilityTimeoutSeconds",
    "ParameterValue": "300"
  }
]
```

#### parameters-sqs-notifications.json
```json
[
  {
    "ParameterKey": "QueueName",
    "ParameterValue": "notifications"
  },
  {
    "ParameterKey": "QueueDescription",
    "ParameterValue": "Queue for sending email and SMS notifications"
  },
  {
    "ParameterKey": "VisibilityTimeoutSeconds",
    "ParameterValue": "120"
  }
]
```

#### parameters-sqs-dlq-analysis.json
```json
[
  {
    "ParameterKey": "QueueName",
    "ParameterValue": "dlq-analysis"
  },
  {
    "ParameterKey": "QueueDescription",
    "ParameterValue": "Queue for analyzing failed messages"
  },
  {
    "ParameterKey": "EnableDeadLetterQueue",
    "ParameterValue": "false"
  }
]
```

### Azure Pipeline Integration

```yaml
# Example pipeline structure
stages:
  - stage: DeployQueues
    jobs:
      - job: DeployProcessingQueue
        steps:
          - task: AWSCloudFormation
            inputs:
              templateParametersFile: 'parameters-sqs-processing.json'
      
      - job: DeployNotificationQueue
        steps:
          - task: AWSCloudFormation
            inputs:
              templateParametersFile: 'parameters-sqs-notifications.json'
      
      - job: DeployDLQAnalysisQueue
        steps:
          - task: AWSCloudFormation
            inputs:
              templateParametersFile: 'parameters-sqs-dlq-analysis.json'
```

## 🔐 Security Configuration

### Development Environment
```json
[
  {
    "ParameterKey": "EnableServerSideEncryption",
    "ParameterValue": "true"
  },
  {
    "ParameterKey": "KmsMasterKeyId",
    "ParameterValue": "alias/aws/sqs"
  }
]
```

### Production Environment with Custom KMS
```json
[
  {
    "ParameterKey": "EnableServerSideEncryption",
    "ParameterValue": "true"
  },
  {
    "ParameterKey": "KmsMasterKeyId",
    "ParameterValue": "arn:aws:kms:ap-southeast-1:123456789012:key/12345678-1234-1234-1234-123456789012"
  }
]
```

## 📊 Queue Performance Tuning

### High-Throughput Configuration
- **VisibilityTimeout**: 60-120 seconds for fast processing
- **ReceiveMessageWaitTime**: 20 seconds (maximum long polling)
- **MaxReceiveCount**: 3-5 attempts before DLQ

### Long-Running Tasks Configuration
- **VisibilityTimeout**: 900 seconds (15 minutes)
- **DelaySeconds**: 0-300 seconds based on processing needs
- **MaxReceiveCount**: 10+ attempts for retry tolerance

### Cost-Optimized Configuration
- **ReceiveMessageWaitTime**: 20 seconds (reduce empty polls)
- **MessageRetention**: Shorter periods for temporary data
- **Encryption**: AWS managed keys for cost efficiency

## 🔗 Integration with Other Services

### Lambda Function Integration

Use queue outputs in Lambda function parameters:

```json
{
  "ParameterKey": "SqsQueueArn",
  "ParameterValue": "arn:aws:sqs:ap-southeast-1:123456789012:myapp-nprd-sqs-processing"
},
{
  "ParameterKey": "DeadLetterQueueArn", 
  "ParameterValue": "arn:aws:sqs:ap-southeast-1:123456789012:myapp-nprd-sqs-processing-dlq"
}
```

### Application Configuration

Reference queue URLs in application environment variables:

```json
{
  "ParameterKey": "SqsQueueUrl",
  "ParameterValue": "https://sqs.ap-southeast-1.amazonaws.com/123456789012/myapp-nprd-sqs-processing"
}
```

## 🗂️ Naming Conventions

### Stack Names
- **Pattern**: `{AppShortName}-{EnvName}-sqs-{QueueName}`
- **Examples**:
  - `ecommerce-prod-sqs-orders`
  - `webapp-nprd-sqs-notifications`
  - `api-gateway-prod-sqs-events`

### Queue Names
- **Main Queue**: `{AppShortName}-{EnvName}-sqs-{QueueName}`
- **Dead Letter Queue**: `{AppShortName}-{EnvName}-sqs-{QueueName}-dlq`
- **Examples**:
  - `myapp-prod-sqs-processing`
  - `myapp-prod-sqs-processing-dlq`

## 🔍 Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Messages not visible | Visibility timeout too long | Reduce VisibilityTimeoutSeconds |
| Too many messages in DLQ | MaxReceiveCount too low | Increase MaxReceiveCount |
| High costs | Too many empty polls | Enable long polling (ReceiveMessageWaitTimeSeconds=20) |
| Encryption errors | Invalid KMS key | Verify KmsMasterKeyId exists and has permissions |
| Stack creation failed | Parameter out of range | Check parameter values against min/max limits |

### Performance Issues

| Symptom | Likely Cause | Recommended Action |
|---------|--------------|-------------------|
| Slow message processing | Short visibility timeout | Increase VisibilityTimeoutSeconds |
| Messages processed multiple times | Visibility timeout too short | Match timeout to processing time |
| High polling costs | Short polling | Set ReceiveMessageWaitTimeSeconds to 20 |
| Messages lost | No dead letter queue | Enable DLQ with appropriate MaxReceiveCount |

## 📊 Best Practices

### 1. **Queue Configuration**
- Use long polling (20 seconds) to reduce costs
- Set visibility timeout to match processing time
- Enable dead letter queues for error handling

### 2. **Security**
- Always enable server-side encryption
- Use custom KMS keys for sensitive data
- Implement least-privilege IAM policies

### 3. **Monitoring**
- Monitor queue depth and processing rates
- Set up CloudWatch alarms for DLQ messages
- Track age of oldest message

### 4. **Cost Optimization**
- Use appropriate message retention periods
- Minimize empty polls with long polling
- Right-size queue parameters for workload

### 5. **Environment Separation**
- Deploy separate queues for each environment
- Use environment-specific encryption keys
- Maintain consistent naming conventions

### 6. **Pipeline Integration**
- Create separate parameter files for different queue types
- Use Azure DevOps for consistent deployments
- Implement proper dependency management between queues

This template provides a robust foundation for message queue infrastructure across any AWS project with built-in reliability, security, and performance optimization features.