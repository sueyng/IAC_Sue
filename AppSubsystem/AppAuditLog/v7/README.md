# AWS Audit Log Infrastructure with SQS, Lambda, and Iceberg

This repository contains CloudFormation templates and associated artifacts for deploying a serverless audit log processing system using AWS Lambda, SQS, Glue, and Apache Iceberg. 
The system captures audit logs through SQS, processes them with Lambda, stores them in S3, and transforms them using AWS Glue for analytics purposes.

## What's New in v7

| Area | Change |
|---|---|
| **Glue Iceberg Catalog** | Added `GlueS3ChecksumEnabled` with a default of `true` for Object Lock compatibility, while `GlueCatalogMaxConnections` remains optional |
| **Lambda Dead-Letter Queue** | Configured `AuditlogLambda.DeadLetterConfig` to use the existing `AuditQueueDLQ`; failed SQS-triggered messages continue to use `AuditQueue`'s `RedrivePolicy` |

## v6 Baseline

| Area | Change |
|---|---|
| **TISO Compliance** | Lambda runs inside VPC — `VpcConfig`, `LambdaSecurityGroup`, and VPC parameters added |
| **IAM** | `AWSLambdaVPCAccessExecutionRole` replaces `AWSLambdaBasicExecutionRole`; `AWSXrayWriteOnlyAccess` added |
| **X-Ray Tracing** | `EnableXRayTracing` parameter (`'true'`/`'false'`, default `'true'`) — `TracingConfig` mode switches `Active`/`PassThrough` |
| **SQS Encryption** | `SqsManagedSseEnabled: true` re-added to `AuditQueueDLQ` and `AuditQueue` (dropped since v2) |
| **SNS Encryption** | `KmsMasterKeyId: alias/aws/sns` added to `DataLoadingSNSTopic` |
| **Lambda Log Group** | `AuditlogLambdaLogGroup` resource with 90-day retention; `DependsOn` ensures creation order |
| **Inline Policy** | `EventBridgeRole` inline policy extracted to standalone `EventBridgeStartSFPolicy` (`IAM_NO_INLINE_POLICY_CHECK`) |
| **Lambda Layer V1.2** | Critical CVE fix — `aiohttp` upgraded 3.12.14 → 3.13.5 (AWS Inspector finding) |
| **Lambda Layer V1.2.1** | Security patch — `aiohttp` upgraded 3.13.5 → 3.14.0 and `idna` upgraded 3.14 → 3.15 |
| **Lambda Layer V1.3** | Security patch — `aiohttp` upgraded 3.14.0 → 3.14.1 (AWS Inspector finding) |
| **Lambda Layer V1.3.1** | Security patch — `aiohttp` upgraded 3.14.1 → 3.14.3 (AWS Inspector finding) |
| **Parameters file** | Migrated from JSON to YAML with VPC section and inline documentation |
| **cfn-lint E1029** | Removed `${}` substitution syntax from plain `Description` fields |

## Repository Structure
```
AppAuditLog/
├── v7/
│   ├── README.md                            # This documentation
│   ├── cf_s3buckets.yaml                    # S3 infrastructure template
│   ├── cf-app-auditlog.yaml                 # Main infrastructure template
│   ├── artifacts/
│   │   ├── glue/
│   │   │   ├── audit_convert_iceberg.py     # Glue ETL script
│   │   │   └── audit_transform.py           # Transformation module
│   │   ├── lambda/
│   │   │   ├── lambda_function.zip          # Lambda implementation
│   │   │   ├── lambda_layer_v1.1.zip        # Pyarrow dependency layer V1.1 (archived)
│   │   │   ├── lambda_layer_v1.2.zip        # Pyarrow dependency layer V1.2 (aiohttp CVE fix)
│   │   │   ├── lambda_layer_v1.2.1.zip      # Pyarrow dependency layer V1.2.1 (idna security patch)
│   │   │   ├── lambda_layer_v1.3.zip        # Pyarrow dependency layer V1.3 (aiohttp 3.14.1 patch)
│   │   │   └── lambda_layer_v1.3.1.zip      # Pyarrow dependency layer V1.3.1 (aiohttp 3.14.3 patch)
│   │   └── stepfunction/
│   │       └── auditlog_state_machine.json  # Step Function workflow
│   └── env/
│       └── parameters-app-auditlog.yaml     # Main stack parameters
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

## Component Details

### 1. Lambda Function
- Purpose: Process audit log messages from SQS
- Key features:
  - SQS batch processing
  - Pyarrow for data serialization
  - S3 raw data storage
  - SQS processing failures are retried by `AuditQueue` and sent to `AuditQueueDLQ` after three receives
  - Lambda asynchronous invocation failures are configured to use `AuditQueueDLQ`
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
  - Optional connection-pool configuration:
    - Set `GlueCatalogMaxConnections` to `200` for deployments that need a larger Iceberg S3 HTTP connection pool.
    - `GlueS3ChecksumEnabled` defaults to `true` because the v7 application buckets have Object Lock enabled.
    - Leave `GlueCatalogMaxConnections` empty unless the deployment needs the larger S3 HTTP connection pool.

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

### Audit Log Infrastructure Parameters (parameters-app-auditlog.yaml)
| Parameter | Type | Default Value | Description |
|-----------|------|--------------|-------------|
| AppShortName | String | *(required)* | Short name of the application |
| AppEnvName | String | *(required)* | Environment name of the application |
| AWSEnvName | String | *(required)* | AWS environment name (nprd/prod) |
| VpcId | String | *(required)* | VPC ID for Lambda ENIs and Security Group |
| SubnetIds | String | *(required)* | Comma-separated private subnet IDs (min 2) |
| VpcCidr1 | String | *(required)* | Primary VPC CIDR for Lambda SG egress rules |
| VpcCidr2–5 | String | *(optional)* | Additional VPC CIDR blocks |
| S3PrefixListId | String | *(optional)* | S3 Gateway Endpoint prefix list ID |
| LambdaPackageName | String | lambda_function.zip | Lambda function ZIP file name |
| LambdaLayerZipfileKey | String | lambda_layer_v1.3.1.zip | Lambda layer ZIP file name (V1.3.1 — aiohttp 3.14.3 patch) |
| GluePackageName | String | audit_convert_iceberg.py | Glue ETL script file name |
| StepFunctionFileName | String | auditlog_state_machine.json | Step Functions state machine definition |
| SQSBatchWindowSize | Number | 1000 | Maximum number of messages in SQS batch |
| SQSBatchWindowInterval | Number | 300 | Maximum batch window in seconds |
| NumberOfWorkers | String | 2 | Number of workers for Glue job |
| GlueWorkerType | String | G.1X | Type of worker for Glue job |
| MaxConcurrentRuns | String | 1 | Maximum number of concurrent job runs |
| MaxRetries | String | 0 | Maximum number of retry attempts |
| SnapshotExpiryHours | String | 168 | Hours before snapshot expiry (7 days) |
| MinSnapshotsToKeep | String | 2 | Minimum number of snapshots to retain |
| CompactionStrategy | String | copy-on-write | Strategy for table compaction |
| GlueCatalogMaxConnections | String | *(empty)* | Optional Iceberg HTTP connection pool size; when set, configures `spark.sql.catalog.glue_catalog.http-client.apache.max-connections` |
| GlueS3ChecksumEnabled | String | true | S3 checksum support for Iceberg writes to Object Lock-enabled buckets |
| CronExpressionRaw | String | cron(0 17 * * ? *) | Schedule expression for ETL job (1AM SGT) |
| JobIdentifier | String | auditlog | Job identifier used in resource naming |

## Security Features

### S3 Bucket Security
- Versioning enabled
- AES-256 encryption
- Public access blocked
- TLS 1.2 or higher enforced
- SSL/TLS connections required

### IAM Roles and Policies
- **Lambda execution role** (`LambdaRole`): `AWSLambdaVPCAccessExecutionRole` (VPC ENI permissions), `AWSXrayWriteOnlyAccess`, SQS/S3/CloudWatch access
- **Glue job execution role** (`GlueDatalakeJobsRole`): S3, Glue, and Lake Formation permissions
- **Step Functions execution role** (`StepFunctionsRole`): Glue, SNS, CloudWatch permissions
- **EventBridge execution role** (`EventBridgeRole`): Step Functions `StartExecution` via standalone `EventBridgeStartSFPolicy`

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
