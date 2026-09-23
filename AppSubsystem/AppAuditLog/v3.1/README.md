# AWS Audit Log Infrastructure with SQS, Lambda, and Iceberg

This repository contains CloudFormation templates and associated artifacts for deploying a serverless audit log processing system using AWS Lambda, SQS, Glue, and Apache Iceberg. 
The system captures audit logs through SQS, processes them with Lambda, stores them in S3, and transforms them using AWS Glue for analytics purposes.

## v3.1 Update Highlights
- Introduced S3 Object Lock for all AppAuditLog buckets in `cf_s3buckets.yaml`.
- Object Lock retention is fixed to COMPLIANCE mode with 1-year default retention.
- Object Lock is configured in template code (no Object Lock parameter in S3 parameter files).
- Existing deletion policy behavior remains environment-based (`prod`: Retain, `nprd`: Delete).

## Repository Structure
```
AppAuditLog/
├── archived/           # Archive of previous versions
├── v2/
│   ├── README.md                       # This documentation
│   ├── cf_s3buckets.yaml              # S3 infrastructure template 
│   ├── cf-app-auditlog.yaml           # Main infrastructure template
│   ├── artifacts/
│   │   ├── glue/
│   │   │   ├── audit_convert_iceberg-v2.py  # Updated version
│   │   │   └── audit_convert_iceberg.py     # Original version
│   │   ├── lambda/
│   │   │   ├── lambda_function.zip          # Lambda implementation
│   │   │   └── lambda_layer.zip             # Pyarrow dependency layer
│   │   └── stepfunction/
│   │       └── auditlog_state_machine.json  # Step Function workflow
│   └── env/
│       ├── parameters-s3buckets.json       # S3 stack parameters
│       └── parameters-app-auditlog.json    # Main stack parameters
```

## Architecture and Flow

### Main Flow Sequence Diagram
```
Application (ECS/EKS)  SQS+DLQ    Lambda     S3 Raw    Glue Crawler    Glue ETL    Step Functions    SNS
       |                |           |           |            |             |              |             |
       |                |           |           |            |             |              |             |
       |---audit event->|           |           |            |             |              |             |
       |                |           |           |            |             |              |             |
       |                |--batch--->|           |            |             |              |             |
       |                |(300s      |           |            |             |              |             |
       |                | window)   |           |            |             |              |             |
       |                |           |--store--->|            |             |              |             |
       |                |           |raw data   |            |             |              |             |
       |                |           |           |            |             |              |             |
       |                |<--delete--|           |            |             |              |             |
       |                |messages   |           |            |             |              |             |
       |                |           |           |            |             |              |             |
       |                |           |           |<--catalog--|             |              |             |
       |                |           |           |raw data    |             |              |             |
       |                |           |           |            |             |              |             |
       |                |           |           |            |--transform->|              |             |
       |                |           |           |            |to iceberg   |              |             |
       |                |           |           |            |             |              |             |
       |                |           |           |            |             |--complete--->|             |
       |                |           |           |            |             |              |             |
       |                |           |           |            |             |              |--notify---->|
       |                |           |           |            |             |              |completion   |
```

### Error Handling Flow Sequence Diagram
```
Application (ECS/EKS)  SQS+DLQ    Lambda     S3 Raw    Glue Crawler    Glue ETL    Step Functions    SNS
       |                |           |           |            |             |              |             |
       |                |           |           |            |             |              |             |
       |                |<--fail----| (retry)   |            |             |              |             |
       |                |           |           |            |             |              |             |
       |                |--DLQ----->|           |            |             |              |             |
       |                |after 3    |           |            |             |              |             |
       |                |retries    |           |            |             |              |             |
       |                |           |           |            |             |              |             |
       |                |           |           |            |             |--fail------->|             |
       |                |           |           |            |             |              |             |
       |                |           |           |            |             |              |--alert----->|
       |                |           |           |            |             |              |failure      |
```

## Prerequisites

### S3 Infrastructure (Separate Pipeline)
The S3 buckets are managed through a separate infrastructure pipeline using `cf_s3buckets.yaml` and its parameters. This is a prerequisite that must be handled by the infrastructure team before deploying the audit log system.

Required S3 Buckets:
- Application Artifact Bucket: `${AppShortName}-${AWSEnvName}-app-artifact`
- Application Runtime Bucket: `${AppShortName}-${AWSEnvName}-app-runtime`
- Data Lake Bucket: `${AppShortName}-${AWSEnvName}-data-lake`

S3 Infrastructure Parameters (parameters-s3buckets.json):
| Parameter | Type | Default Value | Description |
|-----------|------|--------------|-------------|
| AppShortName | String | mimo | Short name of the application |
| AWSEnvName | String | nprd | AWS environment name (nprd/prod) |

Object Lock behavior in v3.1 S3 template:
- Enabled by default and mandatory for all three buckets.
- Retention mode is COMPLIANCE with fixed default retention of 1 year.
- This is a one-way setting. After enablement, Object Lock cannot be disabled and versioning cannot be suspended.

## Component Details

### 1. Lambda Function
- Purpose: Process audit log messages from SQS
- Key features:
  - SQS batch processing
  - Pyarrow for data serialization
  - S3 raw data storage
  - Error handling with DLQ
- Environment variables:
  - BUCKET_NAME: Data lake bucket
  - S3_PREFIX: Audit log prefix path

### 2. Glue ETL Job
- Purpose: Transform raw audit logs to Iceberg format
- Key features:
  - Apache Iceberg table creation
  - Data type conversion and validation
  - Table partitioning
  - Snapshot management
- Parameters:
  - RAW_DATALAKE: Source database
  - TRANS_DATALAKE: Target database
  - COMPACTION_STRATEGY: Table optimization

### 3. Step Function Workflow
- Purpose: Orchestrate ETL process
- Key components:
  - Crawler execution
  - Glue job triggering
  - Error handling
  - SNS notifications
- Integration:
  - EventBridge scheduling
  - Job status monitoring
  - Error notifications

## CloudFormation Parameters

### Audit Log Infrastructure Parameters (parameters-app-auditlog.json)
| Parameter | Type | Default Value | Description |
|-----------|------|--------------|-------------|
| AppShortName | String | mimo | Short name of the application |
| AppEnvName | String | dev | Environment name of the application |
| AWSEnvName | String | nprd | AWS environment name (nprd/prod) |
| LambdaPackageName | String | lambda_function.zip | Lambda function ZIP file name |
| LambdaLayerZipfileKey | String | lambda_layer.zip | Lambda layer ZIP file name |
| GluePackageName | String | audit_convert_iceberg.py | Glue ETL script file name |
| SQSBatchWindowSize | Number | 1000 | Maximum number of messages in SQS batch |
| SQSBatchWindowInterval | Number | 300 | Maximum batch window in seconds |
| NumberOfWorkers | String | 2 | Number of workers for Glue job |
| WorkerType | String | G.1X | Type of worker for Glue job |
| MaxConcurrentRuns | String | 1 | Maximum number of concurrent job runs |
| MaxRetries | String | 0 | Maximum number of retry attempts |
| SnapshotExpiryHours | String | 168 | Hours before snapshot expiry (7 days) |
| MinSnapshotsToKeep | String | 2 | Minimum number of snapshots to retain |
| CompactionStrategy | String | copy-on-write | Strategy for table compaction |
| CronExpressionRaw | String | cron(0 17 * * ? *) | Schedule expression for ETL job (1AM SGT) |

## Security Features

### S3 Bucket Security
- Versioning enabled
- AES-256 encryption
- Public access blocked
- TLS 1.2 or higher enforced
- SSL/TLS connections required
- Object Lock enabled with COMPLIANCE mode and 1-year default retention

### Object Lock Operational Notes (v3.1)
- Buckets created by this template use Object Lock with default COMPLIANCE retention of 1 year.
- Deletion and overwrite operations on protected object versions are blocked until retention expiry.
- For non-production environments, stack deletion can fail if locked object versions still exist in buckets at delete time.
- Plan cleanup and retention windows before deleting or replacing stacks.

### IAM Roles and Policies
- Lambda execution role
- Glue job execution role
- Step Functions execution role
- EventBridge execution role

## Monitoring and Troubleshooting

### CloudWatch Log Groups
- Lambda: `/aws/lambda/${AppShortName}-${AppEnvName}-auditlog-lambda`
- Step Functions: `/aws/vendedlogs/states/${AppShortName}-${AppEnvName}-auditlog-stepfunction`
- Glue: AWS Glue job logs

### Common Issues and Solutions

1. SQS Message Processing Issues
   - Check CloudWatch logs for Lambda function errors
   - Monitor DLQ for failed messages
   - Verify Lambda concurrency limits
   - Check Lambda timeout settings

2. Glue Job Failures
   - Check Glue job logs in CloudWatch
   - Verify S3 permissions
   - Check Iceberg table configurations
   - Monitor job metrics in CloudWatch

3. Step Functions Issues
   - Check execution history
   - Verify state machine definition
   - Check SNS permissions
   - Monitor execution metrics

## Best Practices

### 1. Version Control
- Use semantic versioning for artifacts

### 2. Testing
- Test artifacts in development environment
- Validate dependencies
- Check resource permissions
- Verify end-to-end workflow
