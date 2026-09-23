# AMAZON S3

**Amazon S3** is an object storage service offering industry-leading scalability, data availability, security, and performance. This repository contains CloudFormation templates for provisioning S3 resources:

1. `cf-s3bucket.yaml`: Multiple S3 bucket creation with basic configuration
2. `cf-s3bucket-app.yaml`: Dynamic S3 bucket creation with advanced features
3. `cf-s3buckets-batchjob.yaml`: S3 buckets for batch processing workflows
4. `cf-s3buckets-infra.yaml`: S3 buckets and resources for infrastructure

## Templates Overview

### 1. cf-s3bucket.yaml

This template provides multiple S3 bucket creation using ForEach loops for basic bucket provisioning.

Resources provisioned:
* Multiple S3 Buckets with standard configuration
* S3 Bucket Policies with security controls

### 2. cf-s3bucket-app.yaml

This template provides dynamic S3 bucket creation with advanced features like CORS, EventBridge notifications, lifecycle management, and versioning.

Resources provisioned:
* S3 Bucket with configurable features:
  - CORS Configuration
  - EventBridge Notifications
  - Lifecycle Rules
  - **Versioning Support (NEW)**
  - **Non-current Version Management (NEW)**
* S3 Bucket Policy with security controls

### 3. cf-s3buckets-batchjob.yaml

This template creates S3 buckets specifically for batch processing workflows.

Resources provisioned:
* Dataload S3 Bucket
* Data Extraction S3 Bucket
* S3 Bucket Policies with security controls

### 4. cf-s3buckets-infra.yaml

This template creates S3 buckets and resources for infrastructure purposes.

Resources provisioned:
* EC2 File Repository S3 Bucket
* Inspector S3 Bucket
* KMS Key for Inspector (with automatic key rotation)
* KMS Key Alias
* S3 Bucket Policies

## Parameters and their valid values

### 1. cf-s3bucket.yaml (parameters-s3bucket.json)

| ParameterKey | ValueType | Allowed Values | Example | Default | Mandatory |
|--------------|-----------|----------------|---------|---------|-----------|
| AppShortName | String | e.g., my-application | "xxx" | - | Yes |
| EnvName | String | nprd, nprd-dev, nprd-sit1, nprd-sit2, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b, prod, prod-a, prod-b | "nprd-sit1" | - | Yes |
| BucketNames | CommaDelimitedList | e.g., "dataloading,extraction" | "dataloading,extraction" | - | Yes |

### 2. cf-s3bucket-app.yaml (parameters-s3bucket-app.json)

| ParameterKey | ValueType | Allowed Values | Example | Default | Mandatory |
|--------------|-----------|----------------|---------|---------|-----------|
| AppShortName | String | e.g., my-application | "xxx" | - | Yes |
| EnvName | String | nprd, nprd-dev, nprd-sit1, nprd-sit2, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b, prod, prod-a, prod-b | "nprd-sit1" | - | Yes |
| BucketName | String | e.g., mybucket | "mybucket" | - | Yes |
| DomainBucketName | String | e.g., mybucket.synapxe.sg | "mybucket.synapxe.sg" | "" | No |
| EnableCorsConfiguration | String | "true", "false" | "false" | "false" | No |
| AllowedOrigins | String | Comma-separated URLs or "*" | "*" | "*" | No |
| EnableEventBridgeForS3Bucket | String | "true", "false" | "false" | "false" | No |
| EnableLifecycle | String | "true", "false" | "false" | "false" | No |
| LifecycleExpirationDays | Number | Any number >= 1 | 90 | 90 | No |
| LifecyclePrefix | String | e.g., "temp/" | "temp/" | "" | No |
| **EnableVersioning** | **String** | **"true", "false"** | **"false"** | **"false"** | **No** |
| **EnableNoncurrentVersionExpiration** | **String** | **"true", "false"** | **"false"** | **"false"** | **No** |
| **NoncurrentVersionExpirationDays** | **Number** | **Any number >= 1** | **30** | **30** | **No** |
| **NoncurrentVersionTransitionDays** | **Number** | **Any number >= 1** | **7** | **7** | **No** |

### 3. cf-s3buckets-batchjob.yaml (parameters-s3-batchjob.json)

| ParameterKey | ValueType | Allowed Values | Example | Default | Mandatory |
|--------------|-----------|----------------|---------|---------|-----------|
| AppShortName | String | e.g., my-application | "xxx" | - | Yes |
| EnvName | String | nprd, nprd-dev, nprd-sit1, nprd-sit2, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b, prod, prod-a, prod-b | "prod" | - | Yes |

### 4. cf-s3buckets-infra.yaml (parameters-s3buckets-infra.json)

| ParameterKey | ValueType | Allowed Values | Example | Default | Mandatory |
|--------------|-----------|----------------|---------|---------|-----------|
| AppShortName | String | e.g., my-application | "xxx" | - | Yes |
| EnvName | String | nprd, nprd-dev, nprd-sit1, nprd-sit2, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b, prod, prod-a, prod-b | "prod" | - | Yes |
| KMSKeyRotationPeriod | Number | 1-3650 | 365 | 365 | No |

## **NEW: Versioning Features**

### Versioning Configuration

The `cf-s3bucket-app.yaml` template now supports advanced versioning capabilities:

- **EnableVersioning**: Controls whether S3 bucket versioning is enabled
- **EnableNoncurrentVersionExpiration**: Manages automatic cleanup of non-current versions
- **NoncurrentVersionExpirationDays**: Specifies retention period for non-current versions
- **NoncurrentVersionTransitionDays**: Controls transition to IA storage class for cost optimization

### Versioning Use Cases

#### Development Environment - Basic Versioning
```json
{
  "EnableVersioning": "true",
  "EnableNoncurrentVersionExpiration": "false"
}
```

#### Production Environment - Full Version Management
```json
{
  "EnableVersioning": "true",
  "EnableNoncurrentVersionExpiration": "true",
  "NoncurrentVersionExpirationDays": "90",
  "NoncurrentVersionTransitionDays": "30"
}
```

#### Cost-Optimized Versioning
```json
{
  "EnableVersioning": "true",
  "EnableNoncurrentVersionExpiration": "true",
  "NoncurrentVersionExpirationDays": "7",
  "NoncurrentVersionTransitionDays": "1"
}
```

## Security Features

### KMS Key Rotation

Templates that utilize KMS keys now support automatic key rotation with a configurable rotation period. This security enhancement ensures encryption keys are regularly rotated according to best practices.

KMS key rotation features include:
* Automatic rotation of KMS keys enabled by default
* Configurable rotation period with default of 365 days
* User ability to override rotation period through template parameters
* Resource seamless transition during key rotation

The `KMSKeyRotationPeriod` parameter controls the rotation schedule in days. If not specified, a default value of 365 days (annual rotation) is used.

## S3 Bucket Naming Convention

All S3 buckets created by these templates follow a specific naming convention using the AppShortName and EnvName as prefixes.

The general format for bucket names is:
`<AppShortName>-<EnvName>-<BucketPurpose>`

Where:
- `<AppShortName>` is the short name or acronym for your application
- `<EnvName>` is the environment name (e.g., prod, nprd-sit1)
- `<BucketPurpose>` is a descriptor for the bucket's specific use

Examples:
1. For the application S3 bucket (cf-s3bucket-app.yaml):
   If AppShortName = "xxx", EnvName = "nprd-sit1", and BucketName = "mybucket"
   The resulting bucket name would be:
   - xxx-nprd-sit1-mybucket

2. For multiple buckets (cf-s3bucket.yaml):
   If AppShortName = "xxx", EnvName = "nprd-sit1", and BucketNames = "dataloading,extraction"
   The resulting bucket names would be:
   - xxx-nprd-sit1-dataloading
   - xxx-nprd-sit1-extraction

3. For batch job buckets (cf-s3buckets-batchjob.yaml):
   If AppShortName = "xxx" and EnvName = "prod"
   The resulting bucket names would be:
   - xxx-prod-dataload
   - xxx-prod-data-extraction

4. For infrastructure buckets (cf-s3buckets-infra.yaml):
   If AppShortName = "xxx" and EnvName = "prod"
   The resulting bucket names would be:
   - xxx-prod-s3-ec2-file-repo
   - xxx-prod-s3-inspector

## How to use these templates

1. Choose the appropriate template based on your requirements:
   - Use `cf-s3bucket.yaml` for multiple basic buckets
   - Use `cf-s3bucket-app.yaml` for single bucket with advanced features
   - Use `cf-s3buckets-batchjob.yaml` for batch processing workflows
   - Use `cf-s3buckets-infra.yaml` for infrastructure requirements

2. Locate the corresponding parameters JSON file for the chosen template:
   - For `cf-s3bucket.yaml`, use `parameters-s3bucket.json`
   - For `cf-s3bucket-app.yaml`, use `parameters-s3bucket-app.json`
   - For `cf-s3buckets-batchjob.yaml`, use `parameters-s3-batchjob.json`
   - For `cf-s3buckets-infra.yaml`, use `parameters-s3buckets-infra.json`

3. Update the parameters in the JSON file based on the available parameters for the specific template.

4. Ensure all mandatory parameters are filled with appropriate values.

5. For templates with KMS keys, you can optionally specify the `KMSKeyRotationPeriod` to customize the key rotation schedule.

6. **For versioning features**, configure the versioning parameters in `cf-s3bucket-app.yaml` based on your data protection and cost optimization requirements.

## Common Features Across Templates

- All templates use conditions to determine if the environment is production.
- Production environments have different deletion and update replace policies (Retain instead of Delete).
- All S3 buckets are created with:
  - AES256 encryption
  - Private access control
  - Public access blocking
- All S3 bucket policies enforce:
  - TLS 1.2 or higher
  - SSL-only requests
- All KMS keys have automatic key rotation enabled with configurable rotation periods.

## Notes

- The `cf-s3bucket.yaml` template uses AWS CloudFormation ForEach loops for efficient multiple bucket creation.
- The `cf-s3bucket-app.yaml` template includes optional features like CORS configuration, EventBridge notifications, lifecycle rules, and **versioning support** that can be enabled or disabled through parameters.
- The `cf-s3buckets-batchjob.yaml` template creates fixed buckets for data loading and extraction workflows with automatic 1-year lifecycle expiration.
- The `cf-s3buckets-infra.yaml` template includes additional resources like KMS keys for the Inspector service with automatic key rotation enabled by default.
- **Versioning is only available** in the `cf-s3bucket-app.yaml` template and provides comprehensive version management capabilities including cost optimization through lifecycle transitions.