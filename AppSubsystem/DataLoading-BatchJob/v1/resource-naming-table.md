# AWS Resources Naming Convention - Data Loading Template

This document outlines the standardized naming conventions for AWS resources deployed via the Data Loading CloudFormation template.

## Resource Naming Patterns

### Variable Definitions
- `${AppShortName}`: Application short name (lowercase)
- `${EnvName}`: Environment name (e.g., prod, nprd, nprd-dev, etc.)
- `${BatchJobName}`: Unique identifier for batch job (e.g., learner-master-data)
  - Allowed pattern: `[a-zA-Z0-9-]+`
  - Only letters, numbers, and hyphens allowed
  - Must be unique within AWS account

### Environment Values
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

### Resource Deletion Behavior
For production environments (prod, prod-a, prod-b):
- DeletionPolicy: Retain
- UpdateReplacePolicy: Retain

For non-production environments:
- DeletionPolicy: Delete
- UpdateReplacePolicy: Delete

### Resource Tags
All resources are tagged with:
- Key: Name
- Value: Follows the respective resource naming pattern

## AWS Resources

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
| Security Group | `${AppShortName}-${EnvName}-sg-${BatchJobName}` | Security group for Batch Compute Environment |

### IAM Resources
| Resource Type | Resource Name Pattern | Notes |
|--------------|----------------------|--------|
| Batch Job Role | `${AppShortName}-${EnvName}-${BatchJobName}-role` | Task role for container |
| Batch Job Policy | `${AppShortName}-${EnvName}-${BatchJobName}-policy` | S3 and Secrets Manager permissions |
| Batch Execution Role | `${AppShortName}-${EnvName}-${BatchJobName}-execution-role` | Fargate execution role |
| Batch Execution Policy | `${AppShortName}-${EnvName}-${BatchJobName}-execution-policy` | ECR and CloudWatch permissions |
| EventBridge Role | `${AppShortName}-${EnvName}-${BatchJobName}-events-role` | Event trigger role |
| EventBridge Policy | `${AppShortName}-${EnvName}-${BatchJobName}-events-policy` | Batch job submission permissions |

### Monitoring Resources
| Resource Type | Resource Name Pattern | Notes |
|--------------|----------------------|--------|
| CloudWatch Log Group | `/aws/batch/${AppShortName}-${EnvName}-${BatchJobName}` | Batch job logs with configurable retention |
| EventBridge Scheduler | `${AppShortName}-${EnvName}-${BatchJobName}-schedule` | Schedule-based trigger (when TriggerType is Schedule) |
| EventBridge Rule | `${AppShortName}-${EnvName}-${BatchJobName}-s3event` | S3 event trigger rule (when TriggerType is S3Event) |