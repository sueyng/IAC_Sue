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

## Parameters and Valid Values

### 1. cf-s3bucket.yaml (parameters-s3bucket.json)

| Parameter | Type | Allowed Values | Example | Default | Required |
|-----------|------|----------------|---------|---------|----------|
| AppShortName | String | Application identifier | "xxx" | - | Yes |
| EnvName | String | nprd, nprd-dev, nprd-sit1, nprd-sit2, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b, prod, prod-a, prod-b | "nprd-sit1" | - | Yes |
| BucketNames | CommaDelimitedList | Comma-separated bucket suffixes | "dataloading,extraction" | - | Yes |

### 2. cf-s3bucket-app.yaml (parameters-s3bucket-app.json)

| Parameter | Type | Allowed Values | Example | Default | Required |
|-----------|------|----------------|---------|---------|----------|
| AppShortName | String | Application identifier | "xxx" | - | Yes |
| EnvName | String | nprd, nprd-dev, nprd-sit1, nprd-sit2, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b, prod, prod-a, prod-b | "nprd-sit1" | - | Yes |
| BucketName | String | Bucket name suffix | "mybucket" | "" | No |
| DomainBucketName | String | Fully qualified domain name | "mybucket.synapxe.sg" | "" | No |
| EnableCorsConfiguration | String | "true", "false" | "false" | "false" | No |
| AllowedOrigins | String | Comma-separated URLs or "*" | "*" | "*" | No |
| EnableEventBridgeForS3Bucket | String | "true", "false" | "false" | "false" | No |
| EnableLifecycle | String | "true", "false" | "false" | "false" | No |
| LifecycleExpirationDays | Number | >= 1 | 90 | 90 | No |
| LifecyclePrefix | String | Object prefix filter | "temp/" | "" | No |
| **EnableVersioning** | **String** | **"true", "false"** | **"false"** | **"false"** | **No** |
| **EnableNoncurrentVersionExpiration** | **String** | **"true", "false"** | **"false"** | **"false"** | **No** |
| **NoncurrentVersionExpirationDays** | **Number** | **>= 1** | **30** | **30** | **No** |
| **NoncurrentVersionTransitionDays** | **Number** | **>= 1** | **7** | **7** | **No** |

### 3. cf-s3buckets-batchjob.yaml (parameters-s3-batchjob.json)

| Parameter | Type | Allowed Values | Example | Default | Required |
|-----------|------|----------------|---------|---------|----------|
| AppShortName | String | Application identifier | "xxx" | - | Yes |
| EnvName | String | nprd, nprd-dev, nprd-sit1, nprd-sit2, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b, prod, prod-a, prod-b | "prod" | - | Yes |

### 4. cf-s3buckets-infra.yaml (parameters-s3buckets-infra.json)

| Parameter | Type | Allowed Values | Example | Default | Required |
|-----------|------|----------------|---------|---------|----------|
| AppShortName | String | Application identifier | "xxx" | - | Yes |
| EnvName | String | nprd, nprd-dev, nprd-sit1, nprd-sit2, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b, prod, prod-a, prod-b | "prod" | - | Yes |
| KMSKeyRotationPeriod | Number | 1-3650 days | 365 | 365 | No |

## Advanced Versioning Features (cf-s3bucket-app.yaml)

### Versioning Configuration Options

The `cf-s3bucket-app.yaml` template now provides comprehensive versioning capabilities with cost optimization features:

**Core Versioning Parameters:**
- **EnableVersioning**: Controls S3 bucket versioning (true/false)
- **EnableNoncurrentVersionExpiration**: Manages automatic cleanup of non-current versions
- **NoncurrentVersionExpirationDays**: Retention period for non-current versions
- **NoncurrentVersionTransitionDays**: Transition timing to IA storage class

### Versioning Use Cases and Configurations

#### 1. Development Environment - Basic Versioning
```json
{
  "EnableVersioning": "true",
  "EnableNoncurrentVersionExpiration": "false"
}
```
*Use case: Simple version tracking without automatic cleanup*

#### 2. Production Environment - Full Version Management
```json
{
  "EnableVersioning": "true",
  "EnableNoncurrentVersionExpiration": "true",
  "NoncurrentVersionExpirationDays": "90",
  "NoncurrentVersionTransitionDays": "30"
}
```
*Use case: Complete data protection with cost-optimized storage transitions*

#### 3. Cost-Optimized Versioning
```json
{
  "EnableVersioning": "true",
  "EnableNoncurrentVersionExpiration": "true",
  "NoncurrentVersionExpirationDays": "7",
  "NoncurrentVersionTransitionDays": "1"
}
```
*Use case: Minimal version retention for cost-sensitive environments*

#### 4. Compliance-Ready Configuration
```json
{
  "EnableVersioning": "true",
  "EnableNoncurrentVersionExpiration": "true",
  "NoncurrentVersionExpirationDays": "2555",
  "NoncurrentVersionTransitionDays": "90"
}
```
*Use case: 7-year retention for regulatory compliance*

## Security Features

### Enhanced Security Controls

All templates include comprehensive security measures:

**Encryption:**
* AES256 server-side encryption by default
* KMS encryption available for infrastructure buckets

**Access Controls:**
* Complete public access blocking
* TLS 1.2+ enforcement for all requests
* SSL-only request policies
* Service-specific IAM permissions (Inspector template)

**KMS Key Management (cf-s3buckets-infra.yaml):**
* Automatic key rotation enabled by default
* Configurable rotation period (1-3650 days)
* Service-specific key policies for AWS Inspector
* Proper key alias management

### Production Environment Protection

Templates automatically detect production environments and apply enhanced protection:
* **Deletion Policy**: `Retain` for production, `Delete` for non-production
* **Update Replace Policy**: `Retain` for production, `Delete` for non-production

Production environments: `prod`, `prod-a`, `prod-b`

## S3 Bucket Naming Convention

All S3 buckets created by these templates follow a specific naming convention using the AppShortName and EnvName as prefixes.

The general format for bucket names is:
`<AppShortName>-<EnvName>-s3-<BucketPurpose>`

Where:
- `<AppShortName>` is the short name or acronym for your application
- `<EnvName>` is the environment name (e.g., prod, nprd-sit1)
- `<BucketPurpose>` is a descriptor for the bucket's specific use

Examples:
1. For the application S3 bucket (cf-s3bucket-app.yaml):
   If AppShortName = "xxx", EnvName = "nprd-sit1", and BucketName = "mybucket"
   The resulting bucket name would be:
   - xxx-nprd-sit1-s3-mybucket

2. For multiple buckets (cf-s3bucket.yaml):
   If AppShortName = "xxx", EnvName = "nprd-sit1", and BucketNames = "dataloading,extraction"
   The resulting bucket names would be:
   - xxx-nprd-sit1-s3-dataloading
   - xxx-nprd-sit1-s3-extraction

3. For batch job buckets (cf-s3buckets-batchjob.yaml):
   If AppShortName = "xxx" and EnvName = "prod"
   The resulting bucket names would be:
   - xxx-prod-s3-dataload
   - xxx-prod-s3-data-extraction

4. For infrastructure buckets (cf-s3buckets-infra.yaml):
   If AppShortName = "xxx" and EnvName = "prod"
   The resulting bucket names would be:
   - xxx-prod-s3-ec2-file-repo
   - xxx-prod-s3-inspector

## Template Usage Guide

### 1. Template Selection

Choose the appropriate template based on your requirements:

| Template | Use Case | Key Features |
|----------|----------|--------------|
| `cf-s3bucket.yaml` | Multiple basic buckets | ForEach loops, simple configuration |
| `cf-s3bucket-app.yaml` | Single advanced bucket | Versioning, CORS, EventBridge, lifecycle |
| `cf-s3buckets-batchjob.yaml` | Data processing workflows | Fixed buckets, automatic expiration |
| `cf-s3buckets-infra.yaml` | Infrastructure storage | KMS encryption, Inspector integration |

### 2. Parameter Configuration

1. Locate the corresponding parameter file for your chosen template
2. Update parameter values according to your requirements
3. Ensure all mandatory parameters are populated
4. Configure optional features as needed

### 3. Deployment Steps

1. **Validate Parameters**: Ensure all required parameters are set
2. **Choose Environment**: Select appropriate EnvName for your deployment stage
3. **Configure Features**: Enable optional features (versioning, CORS, etc.) as needed
4. **Deploy Template**: Use CI/CD pipeline
5. **Verify Resources**: Confirm all resources are created successfully


## Common Features Across All Templates

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