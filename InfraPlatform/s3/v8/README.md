# Amazon S3 Infrastructure Template

## Version 8

**IaC Version Tag:** `InfraPlatform-s3-v8`

This version covers the v8 S3 template set:

- `cf-s3bucket.yaml`
- `cf-s3bucket-app.yaml`
- `cf-s3buckets-batchjob.yaml`
- `cf-s3-buckets-infra.yaml`

## What's New in v8

- Updates all v8 S3 buckets to use `BucketOwnerEnforced` object ownership so S3 ACLs are disabled.
- Adds optional native Amazon Inspector findings report export scheduler in `cf-s3-buckets-infra.yaml`.
- Uses EventBridge Scheduler native AWS SDK target integration for Inspector export.
- Does not create a Lambda function for Inspector report export.
- Keeps scheduler values fixed for common shared use:
  - Schedule name: `{AppShortName}-{EnvName}-inspector-findings-export`
  - Schedule state: `ENABLED`
  - Schedule expression: `cron(0 20 * * ? *)`
  - Timezone: `Asia/Singapore`
  - Report format: `CSV`
  - Finding status: `ACTIVE`
  - S3 prefix: `inspector2/findings`
- Adds `EnableInspectorFindingsExportScheduler` toggle to create or skip the scheduler.
- Keeps the existing v7 parameter interface for generic, app, and batch job S3 templates.

## Resources Created

- Generic S3 buckets through `cf-s3bucket.yaml`
- App S3 bucket through `cf-s3bucket-app.yaml`
- Dataload and data extraction buckets through `cf-s3buckets-batchjob.yaml`
- EC2 file repository and Inspector report buckets through `cf-s3-buckets-infra.yaml`
- S3 bucket policies with TLS enforcement
- S3 object ownership with ACLs disabled
- KMS key and alias for Inspector report encryption
- Optional EventBridge Scheduler schedule for Inspector findings export
- Optional Scheduler execution IAM role

## Common Parameter Guidance

Use the matching file under `env/` for the template being deployed:

- `parameters-s3bucket.yaml` for `cf-s3bucket.yaml`
- `parameters-s3bucket-app.yaml` for `cf-s3bucket-app.yaml`
- `parameters-s3-batchjob.yaml` for `cf-s3buckets-batchjob.yaml`
- `parameters-s3buckets-infra.yaml` for `cf-s3-buckets-infra.yaml`

## Infra Template Parameters

| Parameter | Required | Default | Description |
| --- | --- | --- | --- |
| `AppShortName` | Yes | - | Application short name used for resource naming |
| `EnvName` | Yes | - | Environment name |
| `KMSKeyRotationPeriod` | No | `365` | Number of days for KMS key rotation |
| `EnableS3Versioning` | No | `true` | Enable versioning for the EC2 file repo bucket |
| `S3CurrentVersionExpirationDays` | No | `365` | Current object expiration for EC2 file repo bucket. Set `0` to disable |
| `S3NoncurrentVersionExpirationDays` | No | `30` | Noncurrent version expiration for EC2 file repo bucket. Set `0` to disable |
| `EnableInspectorFindingsExportScheduler` | No | `false` | Create native EventBridge Scheduler for Inspector findings export. Applies to `cf-s3-buckets-infra.yaml` only |

## Inspector Scheduler Behavior

When `EnableInspectorFindingsExportScheduler` is `true`, the template creates:

- EventBridge Scheduler schedule: `{AppShortName}-{EnvName}-inspector-findings-export`
- Scheduler IAM role: `{AppShortName}-{EnvName}-inspector-findings-export-role`

The scheduler calls:

```text
arn:aws:scheduler:::aws-sdk:inspector2:createFindingsReport
```

The report is exported to:

```text
s3://{AppShortName}-{EnvName}-s3-inspector/inspector2/findings/
```

## Prerequisites

Before enabling the scheduler:

1. Amazon Inspector v2 must be enabled in the account and Region.
2. The deployment role must be allowed to create EventBridge Scheduler schedules and IAM roles.
3. No other Inspector findings report export should be running at the same time.

## Notes

- The Inspector report bucket lifecycle remains fixed at 365 days.
- The Inspector report bucket versioning remains always enabled.
- The EC2 file repo bucket lifecycle and versioning remain configurable.
- The scheduler is skipped when `EnableInspectorFindingsExportScheduler` is `false`.
- Because ACLs are disabled, workloads must not upload objects with ACL headers such as `x-amz-acl`.
