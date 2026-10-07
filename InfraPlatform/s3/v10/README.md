# Amazon S3 Infrastructure Templates

## Version 10

**IaC Version Tag:** `InfraPlatform-s3-v10`

Version 10 adds an optional Glacier lifecycle transition to all four S3
templates. It is disabled by default, so v10 behaves like v9 unless
`EnableGlacierTransition` is set to `true`. The optional S3 Object Lock from v9
in `cf-s3bucket-app.yaml` and `cf-s3buckets-batchjob.yaml` is unchanged.

## Template Selection

| Template | Parameter guide | Use case |
| --- | --- | --- |
| `cf-s3bucket.yaml` | `env/parameters-s3bucket.yaml` | One or more general-purpose buckets with optional Glacier transition |
| `cf-s3bucket-app.yaml` | `env/parameters-s3bucket-app.yaml` | Application or log bucket with optional CORS, EventBridge, lifecycle, versioning, Glacier transition, and Object Lock |
| `cf-s3buckets-batchjob.yaml` | `env/parameters-s3-batchjob.yaml` | Dataload and data-extraction buckets with optional shared Object Lock or Glacier settings |
| `cf-s3-buckets-infra.yaml` | `env/parameters-s3buckets-infra.yaml` | EC2 file repository (optional Glacier transition) and Inspector findings export resources |

For a project-owned log bucket requiring WORM retention, use
`cf-s3bucket-app.yaml` with `EnableObjectLock: "true"` only after confirming
that the producer supports Object Lock and `BucketOwnerEnforced`.

## What's New in v10

- Adds an optional Glacier lifecycle transition to all four templates, using
  the same parameters in each.
- Keeps Glacier transition disabled by default. With default parameters every
  template produces the same lifecycle rules as v9.
- Supports up to 3 Glacier settings per stack. Each setting has its own list of
  up to 5 object key prefixes, transition days and storage class, so prefixes
  that need the same aging are grouped in one setting.
- `cf-s3bucket.yaml` keeps a single whole-bucket `BucketLifecycle` rule when no
  prefixes are set. `AWS::LanguageExtensions` turns a `NoValue` list item into
  null, so rules cannot be toggled individually: when any prefix is set, the
  template switches to one rule per prefix slot and keeps unused slots as
  `Disabled` rules.
- `cf-s3-buckets-infra.yaml` and `cf-s3buckets-batchjob.yaml` keep their v9
  rules unchanged and add one Glacier rule per prefix in use.
- `cf-s3bucket-app.yaml` adds one Glacier rule per prefix in use and leaves its
  v9 `ExpirationRule` unchanged.
- The app and Batch Job templates reject `EnableGlacierTransition: "true"` when
  `EnableLifecycle` is `false`. Glacier transition therefore cannot be combined
  with Object Lock in those templates.

## Optional Glacier Transition Parameters

`EnableGlacierTransition` (default `false`) turns on all Glacier settings.

| Setting | Prefixes | Days (default `90`) | Storage class (default `GLACIER`) | Old versions (default `0` = off) |
| --- | --- | --- | --- | --- |
| 1 | `GlacierTransitionPrefix` (empty = whole bucket) | `GlacierTransitionDays` | `GlacierStorageClass` | `GlacierNoncurrentTransitionDays` |
| 2 | `Glacier2TransitionPrefix` (empty = not used) | `Glacier2TransitionDays` | `Glacier2StorageClass` | `Glacier2NoncurrentTransitionDays` |
| 3 | `Glacier3TransitionPrefix` (empty = not used) | `Glacier3TransitionDays` | `Glacier3StorageClass` | `Glacier3NoncurrentTransitionDays` |

- Prefix lists are comma-separated, up to 5 prefixes, no spaces, for example
  `archive/,backup/`. CloudFormation rejects other formats.
- Storage classes: `GLACIER_IR` (Instant Retrieval), `GLACIER` (Flexible
  Retrieval) or `DEEP_ARCHIVE`.
- Old-version transitions require versioning.
- A prefix list for setting 2 or 3 is rejected unless
  `EnableGlacierTransition` is `true`.

Example: move `archive/` and `backup/` to `GLACIER` after 30 days, and `logs/`
to `DEEP_ARCHIVE` after 90 days:

```yaml
EnableGlacierTransition: "true"
GlacierTransitionPrefix: "archive/,backup/"
GlacierTransitionDays: "30"
GlacierStorageClass: "GLACIER"
Glacier2TransitionPrefix: "logs/"
Glacier2TransitionDays: "90"
Glacier2StorageClass: "DEEP_ARCHIVE"
```

Where the Glacier transition applies:

| Template | Scope | Extra requirement |
| --- | --- | --- |
| `cf-s3bucket.yaml` | Every bucket in `BucketNames` | None |
| `cf-s3bucket-app.yaml` | The app bucket; Glacier prefixes are separate from `LifecyclePrefix` | `EnableLifecycle: "true"` |
| `cf-s3buckets-batchjob.yaml` | Dataload and data-extraction buckets (same settings for both) | `EnableLifecycle: "true"` |
| `cf-s3-buckets-infra.yaml` | EC2 file repository bucket only | None; the Inspector bucket lifecycle stays fixed |

Expiration rules keep their existing scope (whole bucket, or `LifecyclePrefix`
in the app template).

Things to know before enabling it:

- Keep transition days lower than the expiration days that apply to the same
  objects. Within one rule S3 rejects the configuration; across rules the
  objects are deleted before they move.
- Prefix matching is case-sensitive; include the trailing slash for a folder
  (`archive/`, not `archive`, which would also match `archive-old/`).
- Use separate prefixes in each setting. Overlapping prefixes, including an
  empty setting 1 (whole bucket) next to settings 2 or 3, make S3 apply more
  than one rule to the same objects.
- In the app template, if the `STANDARD_IA` noncurrent transition is also
  enabled for the same objects, set the Glacier old-version days at least 30
  days after `NoncurrentVersionTransitionDays`.
- In `cf-s3bucket.yaml`, when any prefix is set, `get-bucket-lifecycle-configuration`
  shows all 15 prefix slots; unused ones have `Status: Disabled` and do nothing.
- S3 runs lifecycle rules about once a day (midnight UTC), so objects
  transition 24 to 48 hours after they become eligible.
- By default S3 does not transition objects smaller than 128 KB.
- `GLACIER_IR` and `GLACIER` are billed for at least 90 days, `DEEP_ARCHIVE`
  for at least 180 days, even if an object is deleted sooner.
- `GLACIER` and `DEEP_ARCHIVE` objects must be restored with `restore-object`
  before they can be read. `GLACIER_IR` objects are readable immediately.

## What Was New in v9

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
cfn-lint InfraPlatform/s3/v10/*.yaml
git diff --check -- InfraPlatform/s3/v10 InfraPlatform/s3/release-notes.md
```
