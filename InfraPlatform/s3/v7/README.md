# AMAZON S3

**Amazon S3** is an object storage service offering industry-leading scalability, data availability, security, and performance. This repository contains CloudFormation templates for provisioning S3 resources:

1. `cf-s3bucket.yaml`: Multiple S3 bucket creation with basic configuration
2. `cf-s3bucket-app.yaml`: Dynamic S3 bucket creation with advanced features
3. `cf-s3buckets-batchjob.yaml`: S3 buckets for batch processing workflows
4. `cf-s3buckets-infra.yaml`: S3 buckets and resources for infrastructure

## Version 7

**IaC Version Tag:** `InfraPlatform-s3-v7`

### Changes from v6
- **S3 Bucket Versioning**: Added `EnableS3Versioning` toggle (default: true) — applies to `cf-s3bucket.yaml`, `cf-s3buckets-batchjob.yaml`, and `cf-s3-buckets-infra.yaml` (ec2FileRepo bucket)
- **Standardized Lifecycle Parameters** — applies to the same 3 templates:
  - `S3CurrentVersionExpirationDays` (NEW) — configurable auto-delete of current/live objects. Replaces hardcoded 365-day rules. Defaults preserve v6 behavior:
    - `cf-s3bucket.yaml`: `0` (disabled — was no rule)
    - `cf-s3-buckets-infra.yaml`: `365` (was hardcoded 365)
    - `cf-s3buckets-batchjob.yaml`: `365` (was hardcoded 365)
  - `S3NoncurrentVersionExpirationDays` — auto-delete old object versions after configurable days
- **InspectorS3Bucket** lifecycle remains hardcoded at 365 days by design (compliance/audit bucket)
- `cf-s3bucket-app.yaml` left unchanged — already has its own (more granular) lifecycle parameter set
- Addresses CxOne finding: "S3 Bucket Without Versioning"

## Templates Overview

### 1. cf-s3bucket.yaml

This template provides multiple S3 bucket creation using ForEach loops for basic bucket provisioning.

Resources provisioned:
* Multiple S3 Buckets with standard configuration
* S3 Bucket Policies with security controls
* Versioning (configurable, default enabled)
* Noncurrent version lifecycle rule (configurable)
* Current version lifecycle rule (configurable)

### 2. cf-s3bucket-app.yaml

This template provides dynamic S3 bucket creation with advanced features like CORS, EventBridge notifications, lifecycle management, and versioning.

Resources provisioned:
* S3 Bucket with configurable features:
  - CORS Configuration
  - EventBridge Notifications
  - Lifecycle Rules
  - Versioning Support
  - Non-current Version Management (with transition to IA storage)
* S3 Bucket Policy with security controls

### 3. cf-s3buckets-batchjob.yaml

This template creates S3 buckets specifically for batch processing workflows.

Resources provisioned:
* Dataload S3 Bucket
* Data Extraction S3 Bucket
* S3 Bucket Policies with security controls
* Versioning (configurable, default enabled)
* Current version lifecycle rule (configurable, default 365 days)
* Noncurrent version lifecycle rule (configurable, default 14 days)

### 4. cf-s3buckets-infra.yaml

This template creates S3 buckets and resources for infrastructure purposes.

Resources provisioned:
* EC2 File Repository S3 Bucket (with configurable versioning + lifecycle)
* Inspector Report S3 Bucket (versioning always enabled, 365-day fixed lifecycle)
* S3 Bucket Policies with security controls
* KMS Key for Inspector with automatic key rotation
* KMS Key Alias

## Parameters and Valid Values

### 1. cf-s3bucket.yaml (parameters-s3bucket)

| Parameter | Type | Allowed Values | Example | Default | Required |
|-----------|------|----------------|---------|---------|----------|
| AppShortName | String | Application identifier | "xxx" | - | Yes |
| EnvName | String | nprd, nprd-dev, nprd-dev1, nprd-dev2, nprd-sit, nprd-sit1, nprd-sit2, nprd-sit3, nprd-sit-a, nprd-sit-b, nprd-sit-c, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-uat-c, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b, nprd-pp-c, prod, prod-a, prod-b, prod-c | "nprd-sit1" | - | Yes |
| BucketNames | CommaDelimitedList | Comma-separated bucket suffixes (**ALPHANUMERIC ONLY**) | "dataloading,extraction" | - | Yes |
| EnableS3Versioning | String | "true", "false" | "true" | "true" | No |
| S3CurrentVersionExpirationDays | Number | 0-3650 | 0 | 0 | No |
| S3NoncurrentVersionExpirationDays | Number | 0-365 | 30 | 30 | No |

**IMPORTANT — `BucketNames` ALPHANUMERIC ONLY:**
Each name MUST contain only letters and digits — NO hyphens, underscores, or dots. The template uses `Fn::ForEach` to generate resource logical IDs (e.g. `S3Bucket{name}`), and CloudFormation requires logical IDs to be alphanumeric. Stack creation will fail with `OutputKey '...' should be alphanumeric` if any name contains non-alphanumeric characters.

- ✓ Correct: `"dataloading,extraction,archive"`
- ✗ Wrong: `"data-loading,extraction"` (hyphens not allowed)

Note: the resulting full bucket name (e.g. `myapp-prod-s3-dataloading`) can still contain hyphens — the restriction only applies to the suffix you provide.

### 2. cf-s3bucket-app.yaml (parameters-s3bucket-app)

| Parameter | Type | Allowed Values | Example | Default | Required |
|-----------|------|----------------|---------|---------|----------|
| AppShortName | String | Application identifier | "xxx" | - | Yes |
| EnvName | String | (same as above) | "nprd-sit1" | - | Yes |
| BucketName | String | Bucket name suffix | "mybucket" | "" | No |
| DomainBucketName | String | Fully qualified domain name | "mybucket.synapxe.sg" | "" | No |
| EnableCorsConfiguration | String | "true", "false" | "false" | "false" | No |
| AllowedOrigins | String | Comma-separated URLs or "*" | "*" | "*" | No |
| EnableEventBridgeForS3Bucket | String | "true", "false" | "false" | "false" | No |
| EnableLifecycle | String | "true", "false" | "false" | "false" | No |
| LifecycleExpirationDays | Number | >= 1 | 90 | 90 | No |
| LifecyclePrefix | String | Object prefix filter | "temp/" | "" | No |
| EnableVersioning | String | "true", "false" | "false" | "false" | No |
| EnableNoncurrentVersionExpiration | String | "true", "false" | "false" | "false" | No |
| NoncurrentVersionExpirationDays | Number | >= 1 | 30 | 30 | No |
| NoncurrentVersionTransitionDays | Number | >= 1 | 7 | 7 | No |

### 3. cf-s3buckets-batchjob.yaml (parameters-s3-batchjob)

| Parameter | Type | Allowed Values | Example | Default | Required |
|-----------|------|----------------|---------|---------|----------|
| AppShortName | String | Application identifier | "xxx" | - | Yes |
| EnvName | String | (same as above) | "prod" | - | Yes |
| EnableS3Versioning | String | "true", "false" | "true" | "true" | No |
| S3CurrentVersionExpirationDays | Number | 0-3650 | 365 | 365 | No |
| S3NoncurrentVersionExpirationDays | Number | 0-365 | 14 | 14 | No |

### 4. cf-s3buckets-infra.yaml (parameters-s3buckets-infra)

| Parameter | Type | Allowed Values | Example | Default | Required |
|-----------|------|----------------|---------|---------|----------|
| AppShortName | String | Application identifier | "xxx" | - | Yes |
| EnvName | String | (same as above) | "prod" | - | Yes |
| KMSKeyRotationPeriod | Number | 90-2560 days | 365 | 365 | No |
| EnableS3Versioning | String | "true", "false" | "true" | "true" | No |
| S3CurrentVersionExpirationDays | Number | 0-3650 | 365 | 365 | No |
| S3NoncurrentVersionExpirationDays | Number | 0-365 | 30 | 30 | No |

Note: `S3CurrentVersionExpirationDays` and `S3NoncurrentVersionExpirationDays` apply to `ec2FileRepo` bucket only. Inspector bucket has fixed 365-day lifecycle and always-on versioning (compliance/audit requirement).

## Versioning & Lifecycle Parameters (v7 — standardized across 3 templates)

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `EnableS3Versioning` | String | `true` | Enable/disable versioning for all buckets |
| `S3CurrentVersionExpirationDays` | Number | 0 (generic), 365 (infra ec2FileRepo), 365 (batchjob) | Days before CURRENT (live) objects deleted. `0` to disable. |
| `S3NoncurrentVersionExpirationDays` | Number | 30 (generic, infra), 14 (batchjob) | Days to keep OLD versions before auto-delete. `0` to disable. |

**InspectorS3Bucket** in `cf-s3-buckets-infra.yaml` keeps its hardcoded 365-day rule (compliance bucket — not parameterized).

### Recommended Retention by Use Case

| Bucket Type | Current Version | Noncurrent Version | Rationale |
|-------------|----------------|---------------------|-----------|
| General purpose (app-artifact, app-runtime) | 0 (disabled) | 30 days | Data lifetime varies; team decides. Versions cleaned after 30 days. |
| Batch job data (dataload, data-extraction) | 365 days | 14 days | Transient data, reprocessable from source |
| DB backups | 365 days | 90 days | Match RDS backup retention window |
| Audit/compliance data | 365+ days | 365 days | Regulatory requirement |
| Temporary/transient | 30 days | 7 days | Minimal retention needed |

## Advanced Versioning Features (cf-s3bucket-app.yaml)

The `cf-s3bucket-app.yaml` template provides comprehensive versioning capabilities with cost optimization features:

**Core Versioning Parameters:**
- **EnableVersioning**: Controls S3 bucket versioning (true/false)
- **EnableNoncurrentVersionExpiration**: Manages automatic cleanup of non-current versions
- **NoncurrentVersionExpirationDays**: Retention period for non-current versions
- **NoncurrentVersionTransitionDays**: Transition timing to IA storage class

### Versioning Use Cases and Configurations

#### 1. Development Environment - Basic Versioning
```yaml
EnableVersioning: "true"
EnableNoncurrentVersionExpiration: "false"
```
*Use case: Simple version tracking without automatic cleanup*

#### 2. Production Environment - Full Version Management
```yaml
EnableVersioning: "true"
EnableNoncurrentVersionExpiration: "true"
NoncurrentVersionExpirationDays: "90"
NoncurrentVersionTransitionDays: "30"
```
*Use case: Complete data protection with cost-optimized storage transitions*

#### 3. Cost-Optimized Versioning
```yaml
EnableVersioning: "true"
EnableNoncurrentVersionExpiration: "true"
NoncurrentVersionExpirationDays: "7"
NoncurrentVersionTransitionDays: "1"
```
*Use case: Minimal version retention for cost-sensitive environments*

#### 4. Compliance-Ready Configuration
```yaml
EnableVersioning: "true"
EnableNoncurrentVersionExpiration: "true"
NoncurrentVersionExpirationDays: "2555"
NoncurrentVersionTransitionDays: "90"
```
*Use case: 7-year retention for regulatory compliance*

## Security Features

### Enhanced Security Controls

All templates include comprehensive security measures:

**Encryption:**
* AES256 server-side encryption by default
* KMS encryption available for infrastructure buckets (Inspector)

**Access Controls:**
* Complete public access blocking (all 4 settings)
* TLS 1.2+ enforcement for all requests
* SSL-only request policies
* Service-specific IAM permissions (Inspector template)

**KMS Key Management (cf-s3buckets-infra.yaml):**
* Automatic key rotation enabled by default
* Configurable rotation period (90-2560 days, default 365)
* Service-specific key policies for AWS Inspector
* Key alias: `alias/{AppShortName}-{EnvName}-kms-inspector`

### Production Environment Protection

Templates automatically detect production environments and apply enhanced protection:
* **Deletion Policy**: `Retain` for production, `Delete` for non-production
* **Update Replace Policy**: `Retain` for production, `Delete` for non-production

Production environments: `prod`, `prod-a`, `prod-b`, `prod-c`

## S3 Bucket Naming Convention

All S3 buckets follow the naming convention:
```
{AppShortName}-{EnvName}-s3-{BucketPurpose}
```

Examples:

1. **cf-s3bucket.yaml** (generic multiple buckets):
   AppShortName = "xxx", EnvName = "nprd-sit1", BucketNames = "dataloading,extraction"
   - `xxx-nprd-sit1-s3-dataloading`
   - `xxx-nprd-sit1-s3-extraction`

2. **cf-s3bucket-app.yaml** (single app bucket):
   AppShortName = "xxx", EnvName = "nprd-sit1", BucketName = "mybucket"
   - `xxx-nprd-sit1-s3-mybucket`

3. **cf-s3buckets-batchjob.yaml** (fixed batch buckets):
   AppShortName = "xxx", EnvName = "prod"
   - `xxx-prod-s3-dataload`
   - `xxx-prod-s3-data-extraction`

4. **cf-s3buckets-infra.yaml** (infrastructure buckets):
   AppShortName = "xxx", EnvName = "prod"
   - `xxx-prod-s3-ec2-file-repo`
   - `xxx-prod-s3-inspector`

## Template Selection Guide

| Template | Use Case | Key Features |
|----------|----------|--------------|
| `cf-s3bucket.yaml` | Multiple basic buckets | ForEach loops, simple configuration, versioning toggle |
| `cf-s3bucket-app.yaml` | Single advanced bucket | Versioning, CORS, EventBridge, lifecycle, IA transitions |
| `cf-s3buckets-batchjob.yaml` | Data processing workflows | Fixed buckets, configurable lifecycle + versioning |
| `cf-s3buckets-infra.yaml` | Infrastructure storage | KMS encryption, Inspector integration, configurable lifecycle + versioning |

## Migration from v6 to v7

### Is it safe to upgrade?

**Yes.** All changes are non-disruptive in-place updates:
- `VersioningConfiguration` — in-place update, no bucket replacement
- `LifecycleConfiguration` — in-place update, no disruption
- `BucketName` — unchanged, no replacement triggered
- No mandatory parameters added — all new params have defaults

### Behavioral change on upgrade

- **Versioning will be turned ON by default** (one-way operation — S3 can only Suspend afterwards, not return to Unversioned). To opt out, set `EnableS3Versioning: "false"` BEFORE first v7 deploy.
- **Noncurrent version lifecycle rule** will be created (auto-cleanup of old versions after default 30/14 days).
- **Current version lifecycle** unchanged for `cf-s3bucket.yaml` (default 0 = no expiration). For `cf-s3-buckets-infra.yaml` and `cf-s3buckets-batchjob.yaml`, the existing 365-day rule is preserved (now parameterized instead of hardcoded).

### What happens after upgrade

- **Existing objects**: Unaffected. Versioning applies only to new writes after enabling.
- **New writes**: Every overwrite/delete keeps the previous version automatically.
- **Old versions**: Auto-deleted after `S3NoncurrentVersionExpirationDays` (default 30 / 14).
- **Storage cost**: Will gradually increase as versions accumulate, then stabilize once the noncurrent lifecycle rule cleans up.

### To opt out of versioning

Set in your parameter file BEFORE first v7 deploy:
```yaml
EnableS3Versioning: "false"
```

### To adjust current-version retention

```yaml
S3CurrentVersionExpirationDays: "90"  # 0 to disable, max 3650
```

### To adjust noncurrent-version retention

```yaml
S3NoncurrentVersionExpirationDays: "90"  # 0 to disable, max 365
```

## Common Features Across All Templates

- All templates use conditions to determine if the environment is production.
- Production environments have different deletion and update replace policies (Retain instead of Delete).
- All S3 buckets are created with:
  - AES256 encryption
  - Private access control
  - Public access blocking (all 4 settings)
- All S3 bucket policies enforce:
  - TLS 1.2 or higher
  - SSL-only requests
- S3 Versioning is configurable across all templates (default: enabled in v7).
- KMS keys (infra template) have automatic key rotation enabled with configurable rotation periods.

## Supported Environment Names

- Non-Production: nprd, nprd-dev, nprd-dev1, nprd-dev2, nprd-sit, nprd-sit1, nprd-sit2, nprd-sit3, nprd-sit-a, nprd-sit-b, nprd-sit-c, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-uat-c, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b, nprd-pp-c
- Production: prod, prod-a, prod-b, prod-c
