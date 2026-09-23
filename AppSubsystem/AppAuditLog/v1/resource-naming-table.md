# AWS Resources Naming Convention - Audit Log Template

This document outlines the standardized naming conventions for AWS resources deployed via the Audit Log CloudFormation template.

## Resource Naming Patterns

### Storage Resources
| Resource Type | Resource Name Pattern |
|--------------|----------------------|
| S3 Bucket | `${AppShortName}-${EnvName}-${AuditType}-${AuditLogBucketName}` |

### Messaging Resources
| Resource Type | Resource Name Pattern |
|--------------|----------------------|
| SNS Topic | `${AppShortName}-${EnvName}-sns-${AuditType}` |
| SQS Queue (Main) | `${AppShortName}-${EnvName}-sqs-${AuditType}` |
| SQS Queue (DLQ) | `${AppShortName}-${EnvName}-sqs-${AuditType}-dlq` |

### Network Resources
| Resource Type | Resource Name Pattern |
|--------------|----------------------|
| Security Group | `${AppShortName}-${EnvName}-sg-sqs-${AuditType}-lambda` |

### IAM Resources
| Resource Type | Resource Name Pattern |
|--------------|----------------------|
| IAM Policy (Network) | `${AppShortName}-${EnvName}-${AuditType}-network-interface-policy` |
| IAM Policy (SQS) | `${AppShortName}-${EnvName}-${AuditType}-sqs-access-policy` |
| IAM Role (Lambda) | `${AppShortName}-${EnvName}-save-sqs-${AuditType}-lambda-role` |
| IAM Policy (Secrets) | `${AppShortName}-${EnvName}-${AuditType}-secrets-access-policy` |
| IAM Policy (S3) | `${AppShortName}-${EnvName}-${AuditType}-s3-access-policy` |

### Serverless Resources
| Resource Type | Resource Name Pattern |
|--------------|----------------------|
| CloudWatch Log Group | `/aws/lambda/${AppShortName}-${EnvName}-save-sqs-${AuditType}-lambda-func` |
| Lambda Function | `${AppShortName}-${EnvName}-save-sqs-${AuditType}-lambda-func` |

## Variable Definitions
- `${AppShortName}`: Application short name (lowercase)
- `${EnvName}`: Environment name (e.g., prod, nprd, nprd-dev, etc.)
- `${AuditType}`: Type of audit (e.g., audit-log, security-log, api-log)
- `${AuditLogBucketName}`: Name parameter for audit log bucket

## Notes
1. All resource names follow a consistent pattern using hyphen (-) as the delimiter
2. Security Group names use the format `<app>-<env>-sg-<purpose>`
3. CloudWatch Log Group names use forward slash (/) as path delimiter
4. Environment names are standardized according to allowed values in template
5. All components of the name should be lowercase unless specifically required otherwise

## Environment Values
Allowed environment values:
- nprd
- nprd-dev
- nprd-sit1
- nprd-sit2
- nprd-sit
- nprd-sit-a
- nprd-sit-b
- nprd-uat
- nprd-uat-a
- nprd-uat-b
- nprd-pt
- nprd-pp
- nprd-pp-a
- nprd-pp-b
- prod
- prod-a
- prod-b
