# Release Notes: S3 Infrastructure Templates

## Version History

### General Updates
- **IaC Version Tag**:
  - Updated from `InfraPlatform-s3-v1` through `InfraPlatform-s3-v9`.

### Templates Evolution
- **v1**:
  - Basic templates for S3 bucket creation:
    - `cf-s3bucket.yaml`: Simple S3 bucket creation
    - `cf-s3buckets-batchjob.yaml`: S3 buckets for batch job processing

- **v2**:
  - Added `cf-s3buckets-infra.yaml`:
    - EC2 File Repository S3 Bucket
    - Inspector S3 Bucket
    - KMS Key for Inspector with automatic key rotation

- **v3**:
  - Added `cf-s3bucket-app.yaml` for application-specific buckets
  - Enhanced functionality for all templates
  - Added AWS::LanguageExtensions transform with Fn::ForEach for dynamic resource creation
  - Improved documentation with detailed parameter descriptions

- **v4**:
  - Enhanced `cf-s3bucket-app.yaml` with advanced features:
    - CORS Configuration
    - EventBridge Notifications
    - Lifecycle Management
  - Added domain bucket naming support
  - Enforced TLS 1.2 or higher in all bucket policies

- **v5**:
  - Updated bucket naming convention to include "-s3" prefix
  - Enhanced `cf-s3bucket-app.yaml` with versioning support:
    - S3 bucket versioning configuration
    - Non-current version lifecycle management

- **v6**:
  - Enhanced `cf-s3buckets-infra.yaml`:
    - Initially included Lambda function (`InspectorExportLambdaFunction`) and EventBridge rule (`InspectorExportSchedule`) for automated Inspector report export.
    - These were later removed (handled by separate process) — final v6 only retains the `ec2FileRepo` and `Inspector` buckets + KMS key.
  - Enhanced `cf-s3bucket-app.yaml` with comprehensive features: CORS, EventBridge, Lifecycle, Versioning, Domain naming, Outputs.
  - Added `nprd-dev1`, `nprd-dev2` to `EnvName` `AllowedValues`.

- **v7**:
  - **S3 Bucket Versioning** — `EnableS3Versioning` parameter (true/false, default: `true`) added to:
    - `cf-s3bucket.yaml` (all generic ForEach buckets)
    - `cf-s3buckets-batchjob.yaml` (Dataload, DataExtraction)
    - `cf-s3-buckets-infra.yaml` (ec2FileRepo bucket only — Inspector bucket already versioned)
  - **Standardized Lifecycle Parameters** — replaces hardcoded 365-day rules:
    - `S3CurrentVersionExpirationDays` (NEW) — configurable auto-delete of current/live objects. Defaults preserve v6 behavior:
      - `cf-s3bucket.yaml`: `0` (disabled, was no rule)
      - `cf-s3-buckets-infra.yaml`: `365` (was hardcoded)
      - `cf-s3buckets-batchjob.yaml`: `365` (was hardcoded)
    - `S3NoncurrentVersionExpirationDays` — auto-delete old versions after configurable days (default `30` for generic/infra, `14` for batchjob).
  - **Lifecycle Pattern**: Switched from `Status: Suspended` to `!If [EnableVersioning, Status: Enabled, AWS::NoValue]` for cleaner Unversioned bucket state when toggle is off.
  - **InspectorS3Bucket** lifecycle remains hardcoded at 365 days by design (compliance/audit bucket — not parameterized).
  - **`cf-s3bucket-app.yaml` left unchanged** (only IaC tag bump) — already has its own granular lifecycle param set; preserves backward-compatible parameter interface.
  - **Documentation**: added prominent ALPHANUMERIC-ONLY warning for `BucketNames` in `cf-s3bucket.yaml` (Fn::ForEach generates resource logical IDs which CloudFormation requires to be alphanumeric).
  - Addresses CxOne finding: "S3 Bucket Without Versioning"
  - Updated IaCVersion tag to `InfraPlatform-s3-v7`

- **v8**:
  - Added v8 template copies for `cf-s3bucket.yaml`, `cf-s3bucket-app.yaml`, `cf-s3buckets-batchjob.yaml`, and `cf-s3-buckets-infra.yaml`.
  - Replaced legacy `AccessControl: Private` usage with `BucketOwnerEnforced` object ownership for v8-created buckets.
  - S3 ACLs are disabled in v8; workloads must not depend on object ACLs or upload with ACL headers.
  - Added optional native EventBridge Scheduler integration for Amazon Inspector v2 findings report export in `cf-s3-buckets-infra.yaml`.
  - New `EnableInspectorFindingsExportScheduler` toggle controls whether the scheduler and scheduler IAM role are created.
  - Scheduler uses fixed shared defaults: enabled state, daily `20:00` Asia/Singapore schedule, `CSV` format, `ACTIVE` findings, and `inspector2/findings` S3 prefix.
  - Uses native Scheduler AWS SDK target `inspector2:createFindingsReport`; no Lambda function is required.
  - Updated IaCVersion tag to `InfraPlatform-s3-v8`.

- **v9**:
  - Added v9 copies of the four existing S3 templates and their parameter guides.
  - Enhanced `cf-s3bucket-app.yaml` with optional S3 Object Lock, disabled by default for backward compatibility.
  - Enhanced `cf-s3buckets-batchjob.yaml` with the same optional Object Lock baseline, using shared settings for the Dataload and DataExtraction buckets.
  - New `EnableObjectLock` toggle enables fixed `COMPLIANCE` retention as a permanent, one-way bucket-level change.
  - New `ObjectLockRetentionYears` parameter defaults to one year with an allowed range of 1 to 100 years.
  - Enabling Object Lock automatically enables versioning regardless of the applicable app or Batch Job versioning toggle.
  - Object-Lock-enabled app and Batch Job buckets and their bucket policies use `DeletionPolicy: Retain` and `UpdateReplacePolicy: Retain` in every environment.
  - Added CloudFormation rules that reject app or Batch Job lifecycle expiration when Object Lock is selected.
  - Documented that default retention applies to new object versions and does not retroactively protect historical versions.
  - Documented the permanent setting, COMPLIANCE restrictions, lifecycle interaction, and logging-service compatibility requirements.
  - Generic and infra templates retain v8 behavior apart from v9 descriptions and `IaCVersion` tags.
  - Updated IaCVersion tag to `InfraPlatform-s3-v9`.

### Key Features by Template

#### 1. cf-s3bucket.yaml (Basic S3 Bucket)
- **v1-v3 Updates**:
  - Dynamic bucket creation based on BucketNames parameter
  - AES256 encryption and public access blocking
  - SSL-only access via bucket policy

- **v4 Updates**:
  - Enhanced bucket policies with TLS 1.2 enforcement
  - Improved resource tagging with IaCVersion

- **v4 Updates**:
  - Added CORS support with configurable allowed origins
  - Added EventBridge notifications via `EnableEventBridgeForS3Bucket` parameter
  - Added lifecycle rules with configurable expiration days and prefixes
  - Added domain bucket naming support via `DomainBucketName` parameter

- **v5 Updates**:
  - Added versioning support with `EnableVersioning` parameter
  - Added non-current version management with configurable expiration and transition days
  - Updated bucket naming to include "-s3" prefix

- **v6 Updates**:
  - Changed bucket naming to include "-v6" prefix

#### 3. cf-s3buckets-batchjob.yaml (Batch Job S3 Buckets)
- **v1-v4 Consistency**:
  - Consistent set of buckets for batch job processing:
    - AppArtefact S3 Bucket
    - AppRuntime S3 Bucket
    - App S3 Bucket
    - Dataload S3 Bucket
    - DataExtraction S3 Bucket
  - Standard naming convention: `{AppShortName}-{EnvName}-{purpose}`

- **v4 Updates**:
  - Enhanced bucket policies with TLS 1.2 enforcement
  - Improved resource tagging

- **v5 Updates**:
  - Updated bucket naming to include "-s3" prefix: `{AppShortName}-{EnvName}-s3-{purpose}`

- **v6 Updates**:
  - Changed bucket naming to include "-v6" prefix

- **v7 Updates**:
  - Added shared `EnableS3Versioning` configuration for the Dataload and DataExtraction buckets.
  - Replaced hardcoded lifecycle values with configurable current and noncurrent version expiration parameters.

- **v8 Updates**:
  - Disabled S3 ACLs by configuring `BucketOwnerEnforced` object ownership for both Batch Job buckets.

- **v9 Updates**:
  - Added optional shared Object Lock configuration for the Dataload and DataExtraction buckets.
  - Added fixed `COMPLIANCE` mode with configurable 1–100 year retention, defaulting to one year.
  - Automatically enables versioning and retains both buckets and bucket policies when Object Lock is enabled.
  - Added `EnableLifecycle`, defaulting to `true` for v8 compatibility, and requires it to be `false` when Object Lock is enabled.
  - Object Lock remains disabled by default for backward compatibility.

#### 4. cf-s3buckets-infra.yaml (Infrastructure S3 Buckets)
- **v2 Introduction**:
  - EC2 File Repository S3 Bucket
  - Inspector S3 Bucket
  - KMS Key for Inspector with automatic key rotation

- **v4 Updates**:
  - Enhanced KMS key configuration
  - Enforced TLS 1.2 for all connections
  - Improved resource tagging with IaCVersion

- **v5 Updates**:
  - Updated bucket naming to include "-s3" prefix: `{AppShortName}-{EnvName}-s3-{purpose}`

- **v6 Updates**:
  - Changed bucket naming to include "-v6" prefix
  - Lambda Function 
  - EventBridge

### Security Enhancements
- **v1**:
  - Basic security with AES256 encryption
  - Public access blocking
  - SSL-only access enforcement

- **v2**:
  - Added KMS encryption for Inspector bucket
  - Automatic key rotation with configurable periods

- **v3**:
  - Enhanced bucket policies
  - Improved parameter validation

- **v4**:
  - Enforced TLS 1.2 or higher for all connections
  - Enhanced bucket policies with stricter security controls
  - Improved encryption configuration

- **v5**:
  - Enhanced versioning capabilities for data protection
  - Maintained all v4 security features

### Deployment Flow Updates
- **v2 Updates**:
  - Introduced dedicated templates for different use cases

- **v3 Updates**:
  - Added detailed documentation on bucket naming conventions
  - Enhanced parameter descriptions

- **v4 Updates**:
  - Improved deployment guide with examples for advanced features
  - Enhanced parameters with sensible defaults

- **v5 Updates**:
  - Updated documentation for new bucket naming convention
  - Added versioning configuration examples

- **v6 Updates**:
  - Updated new resoruces


### Documentation Updates
- **v2 Updates**:
  - Added basic README with template descriptions

- **v3 Updates**:
  - Added detailed parameter descriptions
  - Enhanced security documentation

- **v4 Updates**:
  - Comprehensive documentation with examples for advanced features
  - Enhanced troubleshooting guide

- **v5 Updates**:
  - Updated bucket naming convention documentation
  - Added versioning configuration examples

- **v6 Updates**:
  - Added new provisoned resources

## Summary of Key Changes

### Legacy Versions (v1 – v4)
| Feature/Component         | v1                       | v2                       | v3                       | v4                       |
|---------------------------|--------------------------|--------------------------|--------------------------|--------------------------|
| IaC Version               | InfraPlatform-s3-v1      | InfraPlatform-s3-v2      | InfraPlatform-s3-v3      | InfraPlatform-s3-v4      |
| Templates                 | Basic bucket, Batch job  | Added Infra bucket       | Added App bucket         | Enhanced App bucket      |
| Security                  | Basic encryption         | KMS encryption           | Enhanced policies        | TLS 1.2+ enforcement     |
| CORS Support              | Not supported            | Not supported            | Not supported            | Configurable (App)       |
| EventBridge Integration   | Not supported            | Not supported            | Not supported            | Supported (App)          |
| Lifecycle Rules           | Not supported            | Not supported            | Not supported            | Configurable (App)       |
| Domain Bucket Naming      | Not supported            | Not supported            | Not supported            | Supported (App)          |
| Bucket Naming Convention  | `{App}-{Env}-{purpose}`  | `{App}-{Env}-{purpose}`  | `{App}-{Env}-{purpose}`  | `{App}-{Env}-{purpose}`  |
| S3 Versioning             | Not supported            | Not supported            | Not supported            | Not supported            |

### Current Versions (v5 – v9)
| Feature/Component                    | v5                            | v6                                              | v7                                                                  | v8 | v9 |
|--------------------------------------|-------------------------------|-------------------------------------------------|---------------------------------------------------------------------|----|----|
| IaC Version                          | InfraPlatform-s3-v5           | InfraPlatform-s3-v6                             | InfraPlatform-s3-v7                                                 | InfraPlatform-s3-v8 | **InfraPlatform-s3-v9** |
| Templates                            | Enhanced naming & versioning  | Enhanced App bucket (+ Infra cleanup)           | Standardized lifecycle params across 3 simple templates             | All S3 templates copied to v8 | Existing four-template set; app and Batch Job templates add optional Object Lock |
| Security                             | Enhanced versioning           | TLS 1.2+ + KMS                                  | TLS 1.2+ + KMS                                                      | TLS 1.2+ + KMS + BucketOwnerEnforced | v8 baseline plus optional Object Lock COMPLIANCE in the app and Batch Job templates |
| CORS Support                         | Configurable (App)            | Configurable (App)                              | Configurable (App, unchanged)                                       | Configurable (App, unchanged) | Same as v8 |
| EventBridge Integration              | Supported (App)               | Supported (App)                                 | Supported (App, unchanged)                                          | App EventBridge unchanged; Inspector Scheduler added for Infra | Same as v8 |
| Lifecycle Rules (App bucket)         | Configurable                  | Configurable                                    | Configurable (unchanged)                                            | Configurable (unchanged) | Configurable when Object Lock is disabled; rejected when enabled |
| Lifecycle — Current Version          | Hardcoded 365d (infra/batchjob) | Hardcoded 365d (infra/batchjob)               | Configurable via `S3CurrentVersionExpirationDays`                   | Same as v7 | Same as v8; app and Batch Job lifecycle expiration rejected when Object Lock is enabled |
| Lifecycle — Noncurrent Version       | App bucket only               | App bucket only                                 | Configurable via `S3NoncurrentVersionExpirationDays` for 3 templates | Same as v7 | Same as v8; app and Batch Job lifecycle expiration rejected when Object Lock is enabled |
| Domain Bucket Naming                 | Supported (App)               | Supported (App)                                 | Supported (App, unchanged)                                          | Supported (App, unchanged) | Same as v8 |
| Bucket Naming Convention             | `{App}-{Env}-s3-{purpose}`    | `{App}-{Env}-s3-{purpose}`                      | `{App}-{Env}-s3-{purpose}`                                          | `{App}-{Env}-s3-{purpose}` | `{App}-{Env}-s3-{purpose}` |
| S3 Versioning                        | Configurable (App bucket only) | Configurable (App bucket only)                 | **Configurable for all 4 templates**                                | Same as v7 | Configurable; automatically enabled when app or Batch Job Object Lock is enabled |
| Object Lock                          | Not present                   | Not present                                     | Not present                                                         | Not present | Optional COMPLIANCE mode in `cf-s3bucket-app.yaml` and `cf-s3buckets-batchjob.yaml`; disabled by default |
| Inspector Lambda Export              | N/A                           | Initially added then removed                    | Not present                                                         | Not present; native Scheduler only | Same as v8 |
| Alphanumeric `BucketNames` Constraint | (undocumented)                | (undocumented)                                  | **Documented warning** in template + param file                     | Same as v7 | Same as v8 |

### Key v7 Highlights
- **`EnableS3Versioning` toggle** — default `true`. Project teams can opt out by setting `false` BEFORE first v7 deploy (versioning is a one-way operation in CloudFormation).
- **`S3CurrentVersionExpirationDays`** — replaces hardcoded 365-day rules with a parameter. Defaults preserve v6 behavior.
- **`S3NoncurrentVersionExpirationDays`** — new noncurrent-cleanup rule (auto-applied when versioning is on).
- **Behavioral change**: existing v6 deployments will have **versioning turned ON** on stack update (default `true`). Storage costs may rise as versions accumulate, then stabilize once the noncurrent-lifecycle rule starts cleanup.
- **`cf-s3bucket-app.yaml` left untouched** in v7 (only IaC tag bump) — preserves its existing rich lifecycle param set for backward compatibility.
- **Alphanumeric-only `BucketNames`** — `Fn::ForEach` requires logical-ID-safe suffixes (no hyphens/underscores/dots in `cf-s3bucket.yaml`). Now documented prominently.
- Addresses CxOne finding: "S3 Bucket Without Versioning"

### Key v8 Highlights
- **Bucket owner enforced object ownership** — all v8 S3 bucket templates disable S3 ACLs with `BucketOwnerEnforced` to align with the platform baseline.
- **No ACL dependency** — project workloads should not send ACL headers such as `x-amz-acl` during object upload.
- **Inspector export scheduler** — `cf-s3-buckets-infra.yaml` can optionally create a native EventBridge Scheduler to export ACTIVE Inspector findings to the Inspector S3 bucket.

### Key v9 Highlights
- **Optional app-bucket Object Lock** — `cf-s3bucket-app.yaml` adds opt-in WORM protection while remaining disabled by default.
- **Optional Batch Job Object Lock** — `cf-s3buckets-batchjob.yaml` adds shared opt-in WORM protection for the Dataload and DataExtraction buckets.
- **One-year COMPLIANCE default** — both supported templates default to one year and allow 1–100 years.
- **Lifecycle safety guard** — Batch Job Object Lock requires `EnableLifecycle: "false"`; expiration-day values remain configured but are ignored.
- **Permanent one-way operation** — after Object Lock is enabled, it cannot be disabled and versioning cannot be suspended.
- **COMPLIANCE retention** — fixed mode with a default/minimum one-year retention and a configurable maximum of 100 years.
- **Automatic versioning and retention** — enabling Object Lock forces versioning and retains the bucket and policy during stack deletion or replacement.
- **Lifecycle guardrail** — CloudFormation rejects app lifecycle expiration when Object Lock is selected.
- **Existing templates remain compatible** — the generic, batch job, and infra templates retain v8 behavior.

For detailed changes, refer to the respective `README.md` files in each version directory.
