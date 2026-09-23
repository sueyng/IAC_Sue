# AWS Resources Naming Convention - Data Loading Template Version 3

This document outlines the standardized naming conventions for AWS resources deployed via the Data Loading CloudFormation template Version 3.

**Version 3 Changes:**
- Removed InputPrefix parameter and related environment variable
- Added IaCVersion tag to all resources for version tracking
- Simplified S3 event monitoring (entire bucket instead of prefix-based)

## Resource Naming Patterns

## Variable Definitions
- `${AppShortName}`: Application short name (lowercase)
- `${EnvName}`: Environment name (e.g., prod, nprd, nprd-dev, etc.)
- `${BatchJobName}`: Unique identifier for batch job (e.g., learner-master-data)
  - Allowed pattern: `[a-zA-Z0-9-]+`
  - Only letters, numbers, and hyphens allowed
  - Must be unique within AWS account
- `${SNSTopicName}`: Name of the SNS topic for notifications (without the ARN)

## Environment Values
Allowed environment values:
- Non-Production Environments:
  - `nprd`: Non-production default
  - `nprd-dev`: Development environment
  - `nprd-sit1`: System Integration Testing 1
  - `nprd-sit2`: System Integration Testing 2
  - `nprd-sit`: System Integration Testing default
  - `nprd-sit-a`: System Integration Testing A
  - `nprd-sit-b`: System Integration Testing B
  - `nprd-uat`: User Acceptance Testing
  - `nprd-uat-a`: User Acceptance Testing A
  - `nprd-uat-b`: User Acceptance Testing B
  - `nprd-pt`: Performance Testing
  - `nprd-pp`: Pre-production
  - `nprd-pp-a`: Pre-production A
  - `nprd-pp-b`: Pre-production B
- Production Environments:
  - `prod`: Production default
  - `prod-a`: Production A
  - `prod-b`: Production B

## Resource Deletion Behavior
For production environments (prod, prod-a, prod-b):
- DeletionPolicy: Retain
- UpdateReplacePolicy: Retain

For non-production environments:
- DeletionPolicy: Delete
- UpdateReplacePolicy: Delete

## Resource Tags
All resources are tagged with:
- **Name**: Follows the respective resource naming pattern
- **IaCVersion**: `AppSubsystem-BatchJob-v3` (identifies resources created by this template version)

### Standard Tags Applied to All Resources
| Tag Key | Tag Value | Purpose |
|---------|-----------|---------|
| Name | Resource-specific naming pattern | Resource identification |
| IaCVersion | AppSubsystem-BatchJob-v3 | Version tracking and governance |

**Tagged Resources Include:**
- CloudWatch Log Groups
- Security Groups  
- IAM Roles and Policies
- Batch Compute Environments, Job Queues, and Job Definitions
- EventBridge Schedules
- All other taggable AWS resources created by this template

### Storage Resources
| Resource Type | Resource Name Pattern | Notes |
|--------------|----------------------|--------|
| S3 Bucket | User-defined | Existing bucket name provided via ExistingBucketName parameter when UseExistingS3 is true |

### Batch Resources
| Resource Type | Resource Name Pattern | Notes |
|--------------|----------------------|--------|
| Compute Environment | `${AppShortName}-${EnvName}-${BatchJobName}` | FARGATE type compute environment |
| Job Queue | `${AppShortName}-${EnvName}-${BatchJobName}-queue` | Priority 1 queue |
| Job Definition | `${AppShortName}-${EnvName}-${BatchJobName}-job` | FARGATE platform job definition |

### Network Resources
| Resource Type | Resource Name Pattern | Notes |
|--------------|----------------------|--------|
| Security Group | `${AppShortName}-${EnvName}-sg-${BatchJobName}` | Outbound HTTPS (443) only |

### IAM Resources
| Resource Type | Resource Name Pattern | Notes |
|--------------|----------------------|--------|
| Batch Job Role | `${AppShortName}-${EnvName}-${BatchJobName}-role` | Task role for container |
| Batch Job Policy | `${AppShortName}-${EnvName}-${BatchJobName}-policy` | S3, Secrets Manager, SNS permissions |
| Batch Execution Role | `${AppShortName}-${EnvName}-${BatchJobName}-execution-role` | Fargate execution role |
| Batch Execution Policy | `${AppShortName}-${EnvName}-${BatchJobName}-execution-policy` | ECR and CloudWatch permissions |
| EventBridge Role | `${AppShortName}-${EnvName}-${BatchJobName}-events-role` | Event trigger role |
| EventBridge Policy | `${AppShortName}-${EnvName}-${BatchJobName}-events-policy` | Batch job submission permissions |

### Notification Resources
| Resource Type | Resource Name Pattern | Notes |
|--------------|----------------------|--------|
| SNS Topic | User-defined | Existing SNS topic name provided via SNSTopicName parameter |

### Monitoring Resources
| Resource Type | Resource Name Pattern | Notes |
|--------------|----------------------|--------|
| CloudWatch Log Group | `/aws/batch/${AppShortName}-${EnvName}-${BatchJobName}` | Batch job logs |
| EventBridge Scheduler | `${AppShortName}-${EnvName}-${BatchJobName}-schedule` | Schedule-based trigger |
| EventBridge Rule | `${AppShortName}-${EnvName}-${BatchJobName}-s3event` | S3 event trigger rule (monitors entire bucket) |

## Template Parameter Changes in Version 3

### Removed Parameters
- **InputPrefix**: No longer required as S3 events monitor the entire bucket

### Updated S3 Event Behavior
- **Version 2**: S3 events monitored specific prefix within bucket
- **Version 3**: S3 events monitor entire bucket for any file uploads
- **Benefit**: Simplified configuration, broader file monitoring capabilities

## Resource Lifecycle Management

### Environment Variables
| Environment Variable | Value Pattern | Condition |
|--------------|----------------------|--------|
| S3_BUCKET_NAME | `${ExistingBucketName}` | When UseExistingS3 is true |
| ENVIRONMENT | `${EnvName}` | Always set |
| DB_SECRET_NAME | `${DatabaseSecretName}` | When DatabaseSecretName is provided |
| SNS_TOPIC_ARN | `arn:aws:sns:${AWS::Region}:${AWS::AccountId}:${SNSTopicName}` | When SNSTopicName is provided |

**Version 3 Changes:**
- **Removed**: `S3_INPUT_PREFIX` environment variable (no longer needed as S3 events monitor entire bucket)
- **Simplified**: S3 event configuration without prefix filtering

Resources created by this template can be easily identified and managed using the IaCVersion tag:

```bash
# List all resources created by this template version
aws resourcegroupstaggingapi get-resources --tag-filters Key=IaCVersion,Values=AppSubsystem-BatchJob-v3

# Filter resources by both version and environment
aws resourcegroupstaggingapi get-resources --tag-filters Key=IaCVersion,Values=AppSubsystem-BatchJob-v3 Key=Name,Values=*nprd-dev*
```

## Version Migration Considerations

When upgrading from previous versions:

### From Version 2 to Version 3
- **Remove InputPrefix parameter** from parameter files
- **Update application code** to handle files from any location in S3 bucket
- **Review S3 event configuration** as triggers will now fire for any file upload
- **Benefits**: Simplified configuration, broader monitoring, enhanced resource tracking
