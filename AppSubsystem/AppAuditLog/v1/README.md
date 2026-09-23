# Audit Log SQS Lambda Infrastructure

This CloudFormation template deploys an audit logging infrastructure using Amazon SQS queues and AWS Lambda. The system processes audit logs through a primary queue with dead-letter queue support, using a Lambda function for message processing.

## Architecture Flow

```
+------------+     +----------------+     +----------------+     +------------------+     +--------------+
|    ECS     |     |   Audit Log    |     |   Audit Log    |     |     Lambda       |     |      S3      |
|Application |---->|      SNS       |---->|      SQS       |---->|    Function      |---->|    Bucket    |
|            |     |                |     |                |     |                  |     |              |
+------------+     +----------------+     +----------------+     +------------------+     +--------------+
                                                |                       |
                                                |                       |
                                                v                       |
                                         +----------------+             |
                                         |   Audit Log    |<------------+
                                         |     DLQ        | (after 3 retries)
                                         |                |
                                         +----------------+

----------------------------------------------------------------
Flow:
1. ECS App -> SNS        : Publish audit log messages
2. SNS -> SQS           : Fan-out message delivery
3. SQS -> Lambda        : Poll and process messages
4. Lambda -> S3         : Store processed logs
5. Lambda -> SQS -> DLQ : Failed messages after 3 retries
```

1. Message Generation:
   - ECS applications generate audit log messages
   - Messages are sent to the main SQS queue ( {AppShortName}-{EnvName}-sqs-audit-log )
   - SNS delivers messages to subscribed SQS queue

2. Message Processing:
   - Lambda function polls the main queue
   - Processes messages in batches (configurable via SQSAuditBatchSize)
   - Stores processed messages in S3 bucket

3. Error Handling:
   - Failed message processing (after 3 attempts) -> messages moved to DLQ
   - DLQ retention period: configurable (1-14 days, default 14 days)
   - Main queue retention period: configurable (1-14 days, default 4 days)

4. Security:
   - All components run within VPC
   - Communication via VPC endpoints
   - Encrypted data at rest (S3 SSE, SQS encryption)
   - TLS 1.2+ enforced for S3

## Prerequisites

Before deploying this template, you must have the following components in place:

### 1. Lambda Function Package
The Lambda function deployment package must be:
- Built for supported runtime (specified in AuditLambdaRuntime parameter)
- Uploaded to an S3 bucket
- Accessible via the specified bucket and path parameters

### 2. AWS Secret for Environment Variables
A secret must be created in AWS Secrets Manager before deployment:
- Contains all environment variables needed by the Lambda function
- Format should be JSON key-value pairs, for example:
```json
{
    "AUDIT_CONNECTION": "connection-string-value",
    "OTHER_VARIABLE": "other-value"
}
```

### 3. VPC Endpoints
The following VPC endpoints are required for this architecture:
- AWS SNS VPC Endpoint
- AWS SQS VPC Endpoint
- AWS S3 VPC Endpoint
- AWS Secrets Manager VPC Endpoint
These endpoints should be provisioned separately before deploying this template.

### 4. ECS Application Integration
This infrastructure is designed to work with ECS applications that need to send audit logs:
- ECS applications should be configured to send messages to the main SQS queue
- Message flow: ECS Application -> Audit Log SQS -> Lambda -> S3 bucket
- Failed messages flow: Audit Log SQS -> Audit Log DLQ

## Template Parameters

### Environment Configuration
| Parameter | Type | Required | Sample Value | Description |
|-----------|------|----------|--------------|-------------|
| AuditType | String | Yes | audit-log | Type of audit (e.g., audit-log, security-log, api-log) |
| AppShortName | String | Yes | hxis | Application identifier used in resource naming |
| EnvName | String | Yes | nprd-dev | Environment name (e.g., nprd-dev, prod) |
| VpcId | String | Yes | vpc-12345678 | VPC for Lambda deployment |
| AppSubnetIds | List | Yes | subnet-12345678,subnet-87654321 | Private subnet IDs for Lambda function |

### SQS Configuration
| Parameter | Type | Default | Sample Value | Description |
|-----------|------|---------|--------------|-------------|
| SQSAuditBatchSize | Number | 100 | 100 | Number of messages to process per batch (10-10000) |
| SQSAuditMaximumBatchWindowInSeconds | Number | 30 | 30 | Maximum wait time for batch processing |
| MainQueueRetentionPeriodInDays | Number | 4 | 4 | Message retention period for main queue (1-14 days) |
| DLQRetentionPeriodInDays | Number | 14 | 14 | Message retention period for DLQ (1-14 days) |

### Lambda Configuration
| Parameter | Type | Required | Sample Value | Description |
|-----------|------|----------|--------------|-------------|
| LambdaArtifactBucket | String | Yes | hxis-nprd-dev-lambda-artifacts | S3 bucket containing Lambda package |
| LambdaArtifactKey | String | Yes | functions/audit-processor/audit-processor.zip | S3 key (path) to Lambda package |
| LambdaHandler | String | Yes | Ihis.PopHealth.Lambda.SaveSQSAuditRecord::Ihis.PopHealth.Lambda.SaveSQSAuditRecord.Function::FunctionHandler | Lambda function handler |
| AuditLambdaLogRetentionInDays | Number | No | 90 | CloudWatch log retention period |
| AuditLambdaMemorySize | Number | No | 256 | Lambda function memory allocation |
| AuditLambdaRuntime | String | No | dotnet8 | Lambda runtime |

### S3 Configuration
| Parameter | Type | Default | Sample Value | Description |
|-----------|------|---------|--------------|-------------|
| AuditLogBucketName | String | Required | audit-logs | Name of S3 bucket for audit logs |
| LogRetention | Number | 365 | 365 | Number of days to retain logs in S3 |

### Secret Configuration
| Parameter | Type | Required | Sample Value | Description |
|-----------|------|----------|--------------|-------------|
| SecretName | String | Yes | hxis-nprd-app-LambdaAuditConfig | Name of secret containing environment variables |

## Deployed Resources

### S3 Bucket
- Name: `${AppShortName}-${EnvName}-${AuditType}-${AuditLogBucketName}`
- Versioning enabled
- Server-side encryption (AES-256)
- Lifecycle rules for log retention
- Public access blocked
- Enforced TLS 1.2 or higher
- SSL/TLS connections required

### SNS Topic
- Name: `${AppShortName}-${EnvName}-sns-${AuditType}`
- KMS encryption enabled
- Topic policy allowing publish from account
- Subscription to SQS queue

### SQS Queues
1. Main Queue
   - Name: `${AppShortName}-${EnvName}-sqs-${AuditType}`
   - Message Retention: Configurable 1-14 days (default 4)
   - Maximum Message Size: 256 KB
   - Server-side encryption enabled
   - Subscribed to SNS topic

2. Dead Letter Queue (DLQ)
   - Name: `${AppShortName}-${EnvName}-sqs-${AuditType}-dlq`
   - Message Retention: Configurable 1-14 days (default 14)
   - Maximum Message Size: 256 KB
   - Server-side encryption enabled

### Lambda Function
- Name: `${AppShortName}-${EnvName}-save-sqs-${AuditType}-lambda-func`
- VPC-deployed with dedicated security group
- Reserved concurrency: 5 concurrent executions
- Environment variables from Secrets Manager
- CloudWatch log group with configurable retention

### IAM Resources
1. Lambda Execution Role
   - Basic Lambda execution permissions
   - Network interface management
   - SQS operations
   - S3 operations for audit log bucket
   - Inline policy for Secrets Manager access

2. SQS Queue Policy
   - Allows necessary SQS operations
   - Allows SNS to send messages
   - Scoped to account resources

3. SNS Topic Policy
   - Allows publish operations from account
   - Scoped to specific topic

### Security Group
- Name: `sg_${AppShortName}-${EnvName}-save-sqs-${AuditType}-lambda`
- Outbound HTTPS (443) access for AWS service communication
- No inbound rules required

## Production Considerations

### Resource Retention
The template includes retention policies for production environments:
- Production resources (identified by EnvName: prod, prod-a, prod-b) are retained on deletion
- Non-production resources are deleted when the stack is deleted
This applies to:
- S3 bucket and bucket policy
- SQS queues and policies
- Lambda function and role
- CloudWatch log groups
- Security groups

## Important Notes for Developers
1. SNS Message Publishing
   - Applications should publish to SNS topic using AWS SDK
   - Use appropriate error handling and retry logic

2. Environment Variables
   - All environment variables should be stored in AWS Secrets Manager
   - Create a secret with JSON format containing all required key-value pairs
   - The Lambda function will retrieve variables from the secret at runtime
   - Update the secret when environment variables need to be changed (no Lambda redeployment needed)

## Troubleshooting

Common issues and solutions:

1. Deployment Failures
   - Verify Lambda package exists in S3
   - Check secret exists in Secrets Manager
   - Validate VPC and subnet configurations
   - Ensure required VPC endpoints are in place

2. Message Publishing Issues
   - Verify SNS topic exists and is accessible
   - Check IAM permissions for publishing
   - Validate SNS subscription to SQS
   - Ensure message format is correct

3. Runtime Issues
   - Check CloudWatch logs for secret access errors
   - Verify secret format and values
   - Ensure Lambda has proper VPC connectivity
   - Verify SQS queue permissions

4. Environment Variable Issues
   - Verify secret exists and is accessible
   - Check secret JSON format is valid
   - Confirm all required variables are present in the secret

## Monitoring and Logging

1. CloudWatch Logs
   - Automatic log group creation
   - Configurable retention period
   - Lambda execution logs
