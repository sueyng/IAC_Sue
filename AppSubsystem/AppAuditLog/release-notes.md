# Release Notes: AppAuditLog Infrastructure

## Version Comparison: v1 vs v2 vs v3 vs v4 vs v5 vs v6 vs v7

### v7 Updates
- **Glue Iceberg Catalog**:
  - Added optional `GlueCatalogMaxConnections` parameter for the Iceberg HTTP connection pool.
  - The parameter defaults to an empty value, so existing applications receive no additional Glue `--conf` argument.
  - When set to `200`, the Glue job receives `spark.sql.catalog.glue_catalog.http-client.apache.max-connections=200`.
  - This setting is intended for the audit-log application experiencing Iceberg S3 HTTP connection pool exhaustion; other applications can leave it empty.
  - Enabled `GlueS3ChecksumEnabled` by default for compatibility with the Object Lock-enabled AppAuditLog S3 buckets.
  - When both settings are enabled, the Glue job receives both Spark `--conf` values through the single CloudFormation `--conf` map entry.
- **Lambda Dead-Letter Queue Scan Remediation**:
  - Added `AuditlogLambda.DeadLetterConfig` targeting the existing `AuditQueueDLQ`.
  - Added a dedicated managed policy granting `LambdaRole` only `sqs:SendMessage` to `AuditQueueDLQ`.
  - The existing `AuditQueue` `RedrivePolicy` remains responsible for SQS-triggered Lambda processing failures.

### General Updates
- **IaC Version Tag**:
  - Updated from `AppAuditLog-v1` to `AppAuditLog-v2`, `AppAuditLog-v3`, and through to `AppAuditLog-v5` across all templates.

### Core Infrastructure (`cf-app-auditlog.yaml`)
- **v2 Updates**:
  - Added **AWS Glue Crawler** for raw data cataloging.
  - Introduced **Step Functions** for orchestrating Glue jobs.
  - Enhanced **S3 bucket policies** for improved security:
    - Enabled AES-256 encryption.
    - Blocked public access.
  - Added **Dead Letter Queue (DLQ)** for SQS to handle failed messages.

- **v3 Updates**:
  - Enhanced **Glue Job**:
    - Added support for **Iceberg table compaction**.
    - Configurable parameters for `SnapshotExpiryHours`, `CompactionStrategy`, and `MinSnapshotsToKeep`.
  - Improved **Step Functions**:
    - Added error handling and retry logic.
    - Integrated SNS notifications for success and failure events.
  - Updated **Lambda runtime** to `Python 3.13`.
  - Enhanced **IAM roles**:
    - Fine-grained permissions for Glue, S3, and Step Functions.
  - **v3.1 Updates**:
    - Introduced **S3 Object Lock** on all AppAuditLog buckets in `cf_s3buckets.yaml`:
      - `${AppShortName}-${AWSEnvName}-app-artifact`
      - `${AppShortName}-${AWSEnvName}-app-runtime`
      - `${AppShortName}-${AWSEnvName}-data-lake`
    - Default retention is hardcoded to **COMPLIANCE mode, 1 year**.
    - Object Lock parameters are not exposed in `parameters-s3buckets.yaml` / `parameters-s3buckets.json`.
    - Bucket **DeletionPolicy/UpdateReplacePolicy** behavior remains unchanged:
      - `prod`: Retain
      - `nprd`: Delete
    - Added matching documentation updates in `v3.1/README.md`.

- **v4 Updates**:
  - Updated **Lambda Layer** to **V1.1**:
    - urllib3 upgrade from 2.5.0 to 2.6.0.

- **v6 Updates**:
  - **TISO Compliance — Lambda VPC Enforcement**:
    - Added mandatory `VpcConfig` to `AuditlogLambda` — Lambda now runs inside VPC.
    - New `LambdaSecurityGroup` (`AWS::EC2::SecurityGroup`) with least-privilege egress:
      - HTTPS (port 443) to VPC CIDR ranges for Interface VPC Endpoints (CloudWatch Logs, X-Ray).
      - Optional egress to S3 via Gateway Endpoint prefix list (`S3PrefixListId`).
    - New VPC parameters: `VpcId`, `SubnetIds`, `VpcCidr1`–`VpcCidr5`, `S3PrefixListId`.
    - New conditions: `HasVpcCidr2`–`HasVpcCidr5`, `HasS3PrefixListId`.
  - **IAM Role Updates** (`LambdaRole`):
    - Replaced `AWSLambdaBasicExecutionRole` with `AWSLambdaVPCAccessExecutionRole` (includes ENI permissions: `ec2:CreateNetworkInterface`, `ec2:DeleteNetworkInterface`, `ec2:DescribeNetworkInterfaces`).
    - Added `AWSXrayWriteOnlyAccess` managed policy for X-Ray tracing.
  - **X-Ray Tracing**: Added `TracingConfig` with new `EnableXRayTracing` parameter (`'true'`/`'false'`, default `'true'`) — mode switches between `Active` and `PassThrough`. New `EnableTracing` condition.
  - **SQS Encryption at Rest**: Added `SqsManagedSseEnabled: true` to both `AuditQueueDLQ` and `AuditQueue` (dropped in v2, reinstated).
  - **SNS Encryption at Rest**: Added `KmsMasterKeyId: alias/aws/sns` to `DataLoadingSNSTopic`.
  - **Lambda Log Group**: Added `AuditlogLambdaLogGroup` (`AWS::Logs::LogGroup`) with 90-day retention; Lambda uses `DependsOn` to ensure log group is created first.
  - **Inline Policy Removed** (`IAM_NO_INLINE_POLICY_CHECK`): `EventBridgeRole` inline `Policies` extracted to standalone `EventBridgeStartSFPolicy` (`AWS::IAM::Policy`).
  - **Lambda Layer V1.2** — Critical security fix:
    - AWS Inspector flagged `aiohttp 3.12.14` (critical CVE).
    - Full dependency rebuild with `aiohttp>=3.14.0`.
    - Built with `--platform manylinux2014_x86_64 --python-version 313` for Linux compatibility.
    - `lambda_layer_v1.1.zip` retained (archived); new `lambda_layer_v1.2.zip` (63 MB).
  - **Parameters file** migrated from JSON to YAML with inline documentation and VPC section.
  - **cfn-lint fixes**:
    - E1029: Removed `${}` substitution syntax from plain `Description` fields (not valid outside `!Sub`).
    - Fixed `s3::/` typo → `s3://` in parameter Description fields.
  - **Miscellaneous fixes**:
    - `GlueDatalakeJobsRole.Description` moved inside `Properties` block (was at resource level, silently ignored).
    - Garbled comment `# 14 daysAuditLogGlueTable` fixed to `# 14 days` on `AuditQueueDLQ`.

- **v5 Updates**:
  - **Glue Version** upgraded from 4.0 to **5.0**.
  - **Rewritten Glue ETL** with class-based `AuditLogTransformer` architecture.
  - Added separate **`audit_transform.py`** module loaded via `--extra-py-files` for modular transformation logic.
  - Added **MERGE-based deduplication** (upsert on `id`) to prevent duplicate records in Iceberg tables.
  - **Inconsistent parquet schema handling**: reads each file individually and unifies schemas before transformation.
  - Added **`AuditLogGlueTable`** CloudFormation resource for pre-defined Glue table schema (raw audit log data).
  - New parameters: **`JobIdentifier`** and **`StepFunctionFileName`**.
  - Added **DeletionPolicy / UpdateReplacePolicy** conditions on all resources (Retain for production, Delete otherwise).
  - Lambda layer default reverted to **`lambda_layer.zip`**.

### Glue ETL Job (`audit_convert_iceberg.py`)
- **v2 Updates**:
  - Added support for **partitioning by date**.
  - Improved **schema validation** for audit log data.
  - Introduced **job bookmarking** to avoid reprocessing data.

- **v3 Updates**:
  - Added support for **Iceberg table format**.
  - Enhanced **data compaction** for optimized storage.
  - Improved **logging**:
    - Added detailed logs for data transformation and errors.

- **v4 Updates**:
  - **Enhanced compatibility** with Lambda Layer V1.1.

- **v5 Updates**:
  - **Complete rewrite** with class-based `AuditLogTransformer` design.
  - Separated transformation logic into **`audit_transform.py`** module (column normalization, header handling, timestamp conversion, schema enforcement).
  - Added **MERGE INTO** (upsert) for deduplication — updates existing records by `id`, inserts new ones.
  - **Per-file parquet reading** with automatic schema unification to handle inconsistent column sets across files.
  - Table creation now uses **`createOrReplace()`** with full Iceberg table properties.

### Step Functions Workflow (`auditlog_state_machine.json`)
- **v2 Updates**:
  - Added states for starting and monitoring Glue Crawlers.
  - Integrated SNS notifications for job completion.

- **v3 Updates**:
  - Enhanced error handling with detailed failure messages.
  - Added support for **manual input parameters** for CDC ranges.

- **v4 Updates**:
  - **Improved integration** with updated Lambda Layer V1.1.

- **v5 Updates**:
  - No structural changes to the state machine workflow.

### Deployment Flow Updates
- **v2 Updates**:
  - Introduced a deployment order:
    1. Deploy S3 buckets.
    2. Deploy Glue Crawlers.
    3. Deploy Lambda and Step Functions.

- **v3 Updates**:
  - Added support for **customizable parameters**:
    - `CronExpressionRaw` for scheduling.
    - `GlueWorkerType` and `NumberOfWorkers` for Glue jobs.
  - Improved deployment documentation for Iceberg integration.

- **v3.1 Updates**:
  - S3 bucket stack now enforces Object Lock with fixed 1-year COMPLIANCE retention.
  - No additional deployment parameter is required for Object Lock in v3.1.

- **v4 Updates**:
  - **Updated Lambda Layer** deployment to V1.2:
    - New artifact: `lambda_layer_v1.2.zip`.

- **v5 Updates**:
  - Upload **`audit_transform.py`** to `app-runtime` S3 bucket alongside `audit_convert_iceberg.py`.
  - Glue job now references `--extra-py-files` for the transform module.

- **v6 Updates**:
  - **Lambda VPC enforcement** (TISO compliance): `AuditlogLambda` now runs inside VPC via mandatory `VpcConfig` (`SubnetIds`, `SecurityGroupIds`).
  - New **`LambdaSecurityGroup`** resource with least-privilege egress rules (HTTPS 443 only to VPC CIDR ranges for Interface Endpoints; optional S3 Gateway Endpoint prefix list).
  - New VPC parameters added: `VpcId`, `SubnetIds`, `VpcCidr1`–`VpcCidr5`, `S3PrefixListId`.
  - New **VPC ENI inline policy** on `LambdaRole`: `ec2:CreateNetworkInterface`, `ec2:DeleteNetworkInterface`, `ec2:DescribeNetworkInterfaces`.
  - **Lambda Layer upgraded to V1.2**: resolves AWS Inspector critical finding on `aiohttp`.
    - `aiohttp`: 3.12.14 → **3.14.0** (CVE fix)
    - `aiobotocore`: 2.19.0 → 3.7.0
    - `botocore`: 1.36.3 → 1.43.0
    - `s3fs`: 2024.12.0 → 2026.4.0
    - `pyarrow`: 19.0.0 → 20.0.0
    - Full dependency chain upgraded (see `lambda_layer_v1.2.zip`).
  - **Lambda Layer Patch V1.2.1**: critical security fixes.
    - `aiohttp`: 3.13.5 → **3.14.0** (AWS Inspector finding fix)
    - `idna`: 3.14 → **3.15** (CVE-2024-3651 — DNS security improvement)
    - `pyarrow`: 20.0.0 → **23.0.1** (CVE-2026-25087 — High severity fix)
    - All other dependencies remain unchanged from V1.2.1
    - Updated artifact: `lambda_layer_v1.2.1.zip` (65 MB).
  - **Lambda Layer Patch V1.3**: security patch.
    - `aiohttp`: 3.14.0 → **3.14.1** (AWS Inspector finding fix)
    - All other dependencies remain unchanged from V1.2.1
    - Updated artifact: `lambda_layer_v1.3.zip` (62 MB).
  - **Lambda Layer Patch V1.3.1**: security patch.
    - `aiohttp`: 3.14.1 → **3.14.3** (AWS Inspector finding fix)
    - All other dependencies remain unchanged from V1.3.
    - Updated artifact: `lambda_layer_v1.3.1.zip` (62 MB).
  - Parameters file migrated from `.json` to `.yaml` format with inline documentation and Quick Start guide.
  - VPC configuration section added to parameters file with deployment guidance.

### Documentation Updates
- **v2 Updates**:
  - Added detailed descriptions for Glue and Step Functions integration.
  - Updated troubleshooting guide for common issues.

- **v3 Updates**:
  - Enhanced deployment guide with Iceberg configuration.
  - Added examples for configuring Glue job parameters.

- **v3.1 Updates**:
  - Added documentation for mandatory S3 Object Lock behavior and operational implications.

- **v4 Updates**:
  - **Updated documentation** for Lambda Layer V1.2 integration.

- **v5 Updates**:
  - Updated deployment guide for modular Glue ETL architecture.
  - Added documentation for MERGE-based deduplication and schema unification.

## Summary of Key Changes
| Feature/Component         | v1                 | v2                         | v3                           | v4                                    | v5                                              |
|---------------------------|--------------------|----------------------------|------------------------------|---------------------------------------|-------------------------------------------------|
| IaC Version               | AppAuditLog-v1     | AppAuditLog-v2             | AppAuditLog-v3               | AppAuditLog-v4                        | AppAuditLog-v5                                  |
| Lambda Layer              | lambda_layer.zip   | lambda_layer.zip           | lambda_layer_v1.0.zip        | lambda_layer_v1.2.zip (aiohttp 3.14.0) | lambda_layer.zip                                |
| Glue Version              | —                  | —                          | —                            | —                                     | 5.0                                             |
| Glue Crawler              | Not supported      | Supported                  | Supported                    | Supported                             | Supported                                       |
| Step Functions            | Not supported      | Basic orchestration        | Enhanced with error handling | Enhanced with error handling          | Enhanced with error handling                    |
| Glue Job                  | Basic ETL          | Partitioning and bookmarking| Iceberg table compaction    | Iceberg table compaction              | MERGE-based upsert with schema unification      |
| Glue Table (CF resource)  | Not supported      | Not supported              | Not supported                | Not supported                         | Supported (pre-defined raw schema)              |
| Deletion Policy           | Not supported      | Not supported              | Not supported                | Not supported                         | Retain (prod) / Delete (non-prod)               |
| Lambda Runtime            | Python 3.8         | Python 3.8                 | Python 3.13                  | Python 3.13                           | Python 3.13                                     |
| S3 Security               | Basic              | AES-256 encryption         | AES-256 encryption           | AES-256 encryption                    | AES-256 encryption                              |
| Notifications             | Not supported      | SNS for job completion     | SNS for success and failure  | SNS for success and failure           | SNS for success and failure                     |

### v3.1 Patch Summary
- Introduced Object Lock on all AppAuditLog S3 buckets.
- Retention set to COMPLIANCE mode with a fixed 1-year default.
- No Object Lock toggle in S3 parameter files.
- Deletion policy behavior remains `prod: Retain`, `nprd: Delete`.

For detailed changes, refer to the respective `README.md` files in the `v1`, `v2`, `v3`, `v4`, and `v5` directories.