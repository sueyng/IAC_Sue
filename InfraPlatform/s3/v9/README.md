# Amazon S3 Infrastructure Templates

## Version 9

**IaC Version Tag:** `InfraPlatform-s3-v9`

Version 9 provides optional S3 Object Lock in `cf-s3bucket-app.yaml` and
`cf-s3buckets-batchjob.yaml`. Object Lock remains disabled by default for
backward compatibility.

## Template Selection

| Template | Parameter guide | Use case |
| --- | --- | --- |
| `cf-s3bucket.yaml` | `env/parameters-s3bucket.yaml` | One or more general-purpose buckets |
| `cf-s3bucket-app.yaml` | `env/parameters-s3bucket-app.yaml` | Application or log bucket with optional CORS, EventBridge, lifecycle, versioning, and Object Lock |
| `cf-s3buckets-batchjob.yaml` | `env/parameters-s3-batchjob.yaml` | Dataload and data-extraction buckets with optional shared Object Lock settings |
| `cf-s3-buckets-infra.yaml` | `env/parameters-s3buckets-infra.yaml` | EC2 file repository and Inspector findings export resources |

For a project-owned log bucket requiring WORM retention, use
`cf-s3bucket-app.yaml` with `EnableObjectLock: "true"` only after confirming
that the producer supports Object Lock and `BucketOwnerEnforced`.

## What's New in v9

- Adds optional Object Lock to `cf-s3bucket-app.yaml`.
- Adds the same optional Object Lock baseline to both buckets created by
  `cf-s3buckets-batchjob.yaml`.
- Keeps Object Lock disabled by default.
- Fixes the default retention mode to `COMPLIANCE`.
- Adds a configurable retention period from 1 to 100 years, defaulting to one
  year.
- Automatically enables versioning when Object Lock is selected, regardless of
  the applicable versioning parameter.
- Retains Object-Lock-enabled buckets and their bucket policies during deletion
  or replacement, including in non-production environments.
- Keeps the generic and infra templates functionally aligned with the previous
  version, apart from v9 descriptions and `IaCVersion` tags.

## Optional Object Lock Parameters

| Parameter | Default | Description |
| --- | --- | --- |
| `EnableObjectLock` | `false` | Enables S3 Object Lock as a permanent bucket-level setting; applies to both buckets in the Batch Job template |
| `ObjectLockRetentionYears` | `1` | Default COMPLIANCE retention for each new object version; allowed range is 1 to 100 years |
| App: `EnableVersioning` | `false` | Existing app-bucket versioning toggle; effectively forced to `true` when Object Lock is enabled |
| Batch Job: `EnableS3Versioning` | `true` | Existing shared versioning toggle; effectively forced to `true` when Object Lock is enabled |
| App: `EnableLifecycle` | `false` | Existing app lifecycle toggle; must remain `false` when Object Lock is enabled |
| Batch Job: `EnableLifecycle` | `true` | Shared lifecycle toggle added for v8 compatibility; set to `false` when Object Lock is enabled |

Both supported templates continue to configure AES256 server-side encryption,
block public access, disable ACLs with `BucketOwnerEnforced`, and enforce HTTPS
with TLS 1.2 or higher.

## Enabling Object Lock

1. Use the parameter guide matching the selected template:
   `env/parameters-s3bucket-app.yaml` or `env/parameters-s3-batchjob.yaml`.
2. Confirm that the bucket is project-owned. HCC platform-owned log buckets are
   remediated by the HCC platform team.
3. Confirm the retention period and permanent change with the application and
   security owners.
4. Set `EnableObjectLock: "true"`.
5. Set `ObjectLockRetentionYears` to at least `1`.
6. Disable lifecycle expiration:
   - App template: keep `EnableLifecycle: "false"`.
   - Batch Job template: set `EnableLifecycle: "false"`; the configured
     expiration-day values are then ignored.
   CloudFormation rejects Object Lock when the corresponding lifecycle
   configuration remains enabled.
7. Deploy the stack and validate producer delivery.
8. Verify a delivered object version has `COMPLIANCE` mode and the expected
   retain-until date.
9. Record the bucket name, retention, owner, producer, and validation evidence
   in the runbook or handover record.

## Permanent One-Way Change

When `EnableObjectLock` is set to `true`:

- Object Lock cannot later be disabled for the bucket.
- Bucket versioning cannot be suspended.
- Changing `EnableObjectLock` back to `false` is not a rollback mechanism and
  must not be attempted.
- COMPLIANCE-protected object versions cannot be deleted or have their
  retention shortened before expiry, including by the AWS account root user.
- The bucket and its bucket policy use `Retain` during stack deletion or
  replacement.

The default retention rule applies to new object versions written after the
configuration becomes active. It does not retroactively protect historical
versions. Changing the default retention later affects new versions and does
not shorten retention already applied to existing protected versions.

## Lifecycle Interaction

Existing lifecycle options remain available when Object Lock is disabled. When
`EnableObjectLock` is `true`, both the app and Batch Job templates require
`EnableLifecycle` to remain `false`:

- Current-version expiration can add a delete marker while the protected object
  version remains retained, making the object unavailable through normal reads.
- Protected noncurrent versions cannot be permanently deleted before their
  retention expires.
- Retention and lifecycle settings should be approved together to avoid
  unexpected visibility, storage, and cost behavior.

Design and test post-retention cleanup separately before adding it to a future
template version.

## Delivery and Service Compatibility

The app template creates the protected bucket baseline but does not grant broad
write access to every logging service. Add only the producer-specific,
least-privilege permissions required for CloudFront logging v2, CloudTrail,
VPC Flow Logs, ALB/NLB, Firehose, or the application.

Important limitations:

- An Object-Lock-enabled bucket cannot be an Amazon S3 server access logging
  destination.
- CloudFront legacy standard logging is not compatible with
  `BucketOwnerEnforced`; use CloudFront standard logging v2.
- If a console workflow changes the CloudFormation-managed bucket policy,
  capture the final policy in IaC to prevent later stack updates from
  overwriting it.

## Existing Buckets

CloudFormation can enable Object Lock on a supported existing general-purpose
bucket without replacing it. Treat this as a permanent migration:

1. Confirm versioning, lifecycle, producer compatibility, and permissions.
2. Obtain approval for the one-way change.
3. Update the stack with `EnableObjectLock: "true"`.
4. Validate new object retention.
5. Decide separately whether historical versions require remediation.

## Existing Infra Template Behavior

`cf-s3-buckets-infra.yaml` retains the existing Inspector export design,
including the optional native EventBridge Scheduler. Its Inspector bucket is
versioned and has a fixed 365-day lifecycle, but it does not use Object Lock.
If it falls under the log-storage control, assess migration to
`cf-s3bucket-app.yaml` with Object Lock enabled.

## Validation

Run focused validation from the `IaC-Templates` repository root:

```bash
cfn-lint InfraPlatform/s3/v9/*.yaml
git diff --check -- InfraPlatform/s3/v9 InfraPlatform/s3/release-notes.md
```
