# Data Loading with Optional Schedule or S3 Event Trigger and AWS Batch - Version 4

This CloudFormation template deploys a serverless data loading infrastructure using AWS Batch, S3, and EventBridge Scheduler/Rules. The template supports both schedule-based and S3 event-based triggers, along with options for using existing S3 buckets for data ingestion, processed using AWS Batch jobs with Fargate compute resources.

**Version 4 Changes:**
- **Enhanced Secrets Management**: Now supports up to 5 additional secrets beyond the primary database secret (6 secrets total)
  - Added `AdditionalSecret2Name` through `AdditionalSecret5Name` parameters for flexible secret injection
  - Added customizable environment variable names for each additional secret
  - Improved IAM policies to support granular access control for multiple secrets
  - Enhanced BatchJobDefinition with conditional secret injection based on provided parameters
- **Customizable Environment Variables**: Added support for custom environment variable parameters matching ECS service pattern
  - Added `EnvVarConnectionStringSecretName` for database connection string secret
  - Added EnvVar1Name/EnvVar1Value, EnvVar2Name/EnvVar2Value, EnvVar3Name/EnvVar3Value for custom environment variables
  - Enhanced environment variable configuration with conditional inclusion
  - Improved consistency with ECS service environment variable handling
- **Backward Compatibility**: Maintained full backward compatibility with existing v3 deployments

**Version 3 Changes:**
- Added InputPrefix parameter for flexible S3 prefix filtering
- S3 event triggers can now monitor specific prefixes or entire bucket
- Enhanced conditional logic for InputPrefix - only applies prefix filter when value is provided
- When InputPrefix is empty, S3 events trigger on any file in the bucket
- Added S3_INPUT_PREFIX environment variable passed to container when InputPrefix is configured
- Streamlined template with consistent resource tagging
- Improved EventBridge policy permissions with better resource scope
- Added IaCVersion tags to core resources for better resource tracking

## Architecture Flow
```
                     +----------------+
Schedule--------+--->|  EventBridge   |
                |    | Scheduler/Rules|     +------------------+     +-------------+
+-----------+   |    |                |     |   AWS Batch      |     | RDS         |
|    S3     |---+--->|  (Schedule or  |---->|  Job (Fargate)   |---->| Database    |
|  Bucket   |        |   S3 Event)    |     |                  |     |             |
+-----------+        +----------------+     +------------------+     +-------------+
                                                  |
                                                  |
                           +----------------------|------------------------+---------------+--------------------+
                           |                      |                        |               |                    |
                           v                      v                        v               v                    v
                +----------------+    +------------------+    +--------------+    +--------------+    +--------------+
                |   Secrets      |    |    Container     |    |  CloudWatch  |    |  Amazon SES  |    |  Amazon SNS  |
                |   Manager      |    |     Registry     |    |    Logs      |    |  (Email)     |    | (Notifications)|
                | (Up to 6       |    |     (ECR)        |    |              |    |              |    |              |
                |  Secrets)      |    |                  |    |              |    |              |    |              |
                +----------------+    +------------------+    +--------------+    +--------------+    +--------------+

```

### Flow Options:

1. Schedule-based Trigger (using EventBridge Scheduler):
   - EventBridge scheduler triggers batch job at specified times
   - Batch job processes data according to schedule
   - Supports both cron and rate expressions

2. S3 Event-based Trigger:
   - S3 -> EventBridge: File upload triggers event
   - EventBridge -> Batch: Start loading job
   - Supports flexible prefix filtering - can monitor specific paths or entire bucket
   - When InputPrefix is provided: monitors only files with matching prefix
   - When InputPrefix is empty: monitors all files in the bucket

Common Processing Flow:
1. Batch -> ECR: Pull container image
2. Batch -> Secrets: Get database credentials and additional secrets (up to 6 total)
3. Batch -> S3: Load data files
4. Batch -> RDS: Store loaded data in database
5. Batch -> SES: Send email notifications
6. Batch -> SNS: Send event notifications
7. Batch -> CloudWatch: Log loading output

## Prerequisites

Before deploying this template, you must have:

### 1. Container Image
- Docker container image built and pushed to ECR
- Image contains data loading logic
- Image compatible with AWS Batch Fargate platform

### 2. VPC Infrastructure
- VPC with private subnets
- Required VPC endpoints:
  - AWS ECR VPC Endpoint
  - AWS S3 VPC Endpoint
  - AWS Secrets Manager VPC Endpoint
  - AWS CloudWatch Logs VPC Endpoint
  - AWS SES VPC Endpoint (for email notifications)
  - AWS SNS VPC Endpoint (for event notifications)

### 3. Secrets Configuration
- Primary database secret in AWS Secrets Manager (optional)
- Up to 5 additional secrets in AWS Secrets Manager (optional)
- Secret names or ARNs needed for template deployment
- All secrets must be accessible from the deployment region

### 4. S3 Bucket Configuration
- Existing S3 bucket required
- Proper bucket permissions and notifications configured

### 5. Amazon SES Configuration
- Verified email addresses or domains in Amazon SES
- If in sandbox mode, verified recipient email addresses
- Proper SES configuration in the deployment region
- Email templates for job status notifications

### 6. Amazon SNS Configuration
- Existing SNS topic for notifications
- Proper SNS topic policies
- SNS topic name for template deployment

## Secrets Management

### Overview
The template supports up to **6 secrets** that can be injected into your batch job containers:
1. **Primary Database Secret** (`DatabaseSecretName`) - Typically used for RDS database credentials
2. **Additional Secret 2-5** (`AdditionalSecret2Name` through `AdditionalSecret5Name`) - For API keys, OAuth tokens, external service credentials, etc.

### How Secrets Work
All secrets are retrieved from AWS Secrets Manager and injected as **environment variables** into your container at runtime. This means:
- Secret values are not visible in CloudFormation templates or AWS Console
- Secrets are securely fetched at container startup
- Your application code accesses them as standard environment variables

### Secret Configuration

#### Primary Database Secret
```yaml
Parameters:
  DatabaseSecretName: "my-rds-database-secret"
```
Injected as environment variable: `DB_SECRET_NAME`

#### Additional Secrets
```yaml
Parameters:
  # Secret 2 - API Key
  AdditionalSecret2Name: "my-api-key-secret"
  AdditionalSecret2EnvVarName: "API_KEY"
  
  # Secret 3 - OAuth Token
  AdditionalSecret3Name: "my-oauth-token"
  AdditionalSecret3EnvVarName: "OAUTH_TOKEN"
  
  # Secret 4 - External Service
  AdditionalSecret4Name: "my-external-service-creds"
  AdditionalSecret4EnvVarName: "EXTERNAL_SERVICE_SECRET"
  
  # Secret 5 - Storage Access
  AdditionalSecret5Name: "my-storage-access-key"
  AdditionalSecret5EnvVarName: "STORAGE_ACCESS_KEY"
```

### Accessing Secrets in Your Application

**Python Example:**
```python
import os
import json

# Access database secret
db_secret = os.getenv('DB_SECRET_NAME')

# Access additional secrets
api_key = os.getenv('API_KEY')
oauth_token = os.getenv('OAUTH_TOKEN')
external_service_secret = os.getenv('EXTERNAL_SERVICE_SECRET')
storage_key = os.getenv('STORAGE_ACCESS_KEY')

# If secret contains JSON, parse it
if db_secret:
    db_credentials = json.loads(db_secret)
    username = db_credentials['username']
    password = db_credentials['password']
```

### Secret Naming Best Practices
1. Use descriptive environment variable names that clearly indicate the secret's purpose
2. Follow your organization's naming conventions (e.g., `DB_PASSWORD`, `API_KEY`, `OAUTH_TOKEN`)
3. Keep environment variable names uppercase with underscores for consistency
4. Document which secrets are required vs. optional for your batch job

### IAM Permissions
The template automatically configures IAM permissions for:
- **BatchJobRole** - Runtime access to retrieve secret values
- **BatchExecutionRole** - Startup access to inject secrets into containers

All secrets are conditionally included - only configured secrets receive IAM permissions.

## Environment Variables and Configuration

### Container Environment Variables
The following environment variables are automatically passed to your container:

**Standard Environment Variables:**
- `S3_BUCKET_NAME`: Name of the S3 bucket (when UseExistingS3 is true)
- `S3_INPUT_PREFIX`: S3 prefix path for input files (when InputPrefix is provided)
- `ENVIRONMENT`: The deployment environment name (e.g., "nprd-dev", "prod")
- `SNS_TOPIC_ARN`: ARN of the SNS topic for notifications (if configured)

**Secret Environment Variables (from AWS Secrets Manager):**
- `DB_SECRET_NAME`: Primary database secret (when DatabaseSecretName is provided)
- Custom secret variables: Up to 5 additional secrets with customizable environment variable names:
  - `AdditionalSecret2EnvVarName` (default: ADDITIONAL_SECRET_2)
  - `AdditionalSecret3EnvVarName` (default: ADDITIONAL_SECRET_3)
  - `AdditionalSecret4EnvVarName` (default: ADDITIONAL_SECRET_4)
  - `AdditionalSecret5EnvVarName` (default: ADDITIONAL_SECRET_5)

**Customizable Plain-Text Environment Variables:**
- `AwsSecretPrefix`: Database connection string secret name (when EnvVarConnectionStringSecretName is provided)
- Custom variables: Up to 3 additional environment variables can be configured using:
  - `EnvVar1Name` and `EnvVar1Value` parameters
  - `EnvVar2Name` and `EnvVar2Value` parameters  
  - `EnvVar3Name` and `EnvVar3Value` parameters

These customizable environment variables allow you to pass application-specific configuration to your batch jobs, maintaining consistency with ECS service patterns.

## Security and Networking Requirements

### VPC Endpoints
The following VPC endpoints are **required** for Fargate tasks running in private subnets:
- `com.amazonaws.region.ecr.api`: ECR API endpoint
- `com.amazonaws.region.ecr.dkr`: ECR Docker endpoint
- `com.amazonaws.region.s3`: S3 endpoint
- `com.amazonaws.region.secretsmanager`: Secrets Manager endpoint
- `com.amazonaws.region.logs`: CloudWatch Logs endpoint
- `com.amazonaws.region.email-smtp`: SES SMTP endpoint (for email notifications)
- `com.amazonaws.region.sns`: SNS endpoint (for event notifications)

Without these endpoints, Fargate tasks will fail to:
- Pull container images
- Access S3 buckets
- Retrieve secrets
- Send logs to CloudWatch
- Send email notifications
- Send SNS notifications

### Security Group Configuration
The template configures a security group with:
- Outbound: Tightly controlled egress rules:
  - HTTPS (443) to VPC CIDR ranges
  - Database port access to DB subnet CIDRs
  - HTTPS to S3 endpoints via prefix list (if configured)
  - HTTPS to HCC VPC endpoint (if configured)
- Inbound: None (No inbound rules as Batch jobs don't accept incoming connections)

This configuration follows security best practices by allowing only the minimum required outbound traffic rather than allowing all outbound traffic.

### Database Port Configuration
The template includes parameters for database ports:
- ProdDBPort: Port for production environments (default: 53341)
- NProdDBPort: Port for non-production environments (default: 53331)

The appropriate port is automatically selected based on the environment (prod vs. non-prod) and applied to the security group rules for database access.

## Event Patterns and Triggers

The template supports two types of triggers:

### 1. Schedule-based Pattern
When TriggerType is set to 'Schedule', the EventBridge rule uses the provided schedule expression:
```yaml
ScheduleExpression: cron(0 12 * * ? *)  # Example: Run daily at 12 PM UTC
```

Schedule expressions can be specified in two formats:
- Cron expressions: `cron(0 12 * * ? *)`
- Rate expressions: `rate(1 day)`

### 2. S3 Event Pattern
When TriggerType is set to 'S3Event', the EventBridge rule uses the following pattern:

**With InputPrefix (monitors specific prefix):**
```json
{
  "detail-type": ["Object Created"],
  "source": ["aws.s3"],
  "detail": {
    "bucket": {
      "name": ["<your-bucket-name>"]
    },
    "object": {
      "key": [
        {"prefix": "<your-input-prefix>"}
      ]
    }
  }
}
```

**Without InputPrefix (monitors entire bucket):**
```json
{
  "detail-type": ["Object Created"],
  "source": ["aws.s3"],
  "detail": {
    "bucket": {
      "name": ["<your-bucket-name>"]
    }
  }
}
```

This pattern ensures:
- Only object creation events trigger jobs
- Flexible prefix filtering based on InputPrefix parameter
- Events from the correct bucket are processed

## Template Parameters

### Environment Configuration
| Parameter | Type | Required | Sample Value | Description |
|-----------|------|----------|--------------|-------------|
| AppShortName | String | Yes | myapp | Application identifier for resource naming |
| BatchJobName | String | Yes | learner-master-data | Unique identifier for this batch job |
| EnvName | String | Yes | nprd-dev | Environment name (e.g., nprd-dev, prod) |
| TriggerType | String | Yes | Schedule/S3Event | Choose whether to trigger batch job by schedule or S3 event |
| ScheduleExpression | String | No* | cron(0 12 * * ? *) | Schedule expression (*Required if TriggerType is Schedule) |
| SNSTopicName | String | No | myapp-notifications | Name of the SNS topic for notifications |
| VpcId | String | Yes | vpc-0abc123def456789 | VPC for Batch compute environment |
| AppSubnetIds | List | Yes | subnet-0abc123def456789,subnet-0xyz987wvu654321 | Private subnet IDs for Batch jobs |

### Secrets Configuration
| Parameter | Type | Required | Sample Value | Description |
|-----------|------|----------|--------------|-------------|
| DatabaseSecretName | String | No | myapp-dev-postgresql | Name or ARN of primary database secret |
| AdditionalSecret2Name | String | No | myapp-api-key | Name of second secret (optional) |
| AdditionalSecret2EnvVarName | String | No | API_KEY | Environment variable name for Secret 2 |
| AdditionalSecret3Name | String | No | myapp-oauth-token | Name of third secret (optional) |
| AdditionalSecret3EnvVarName | String | No | OAUTH_TOKEN | Environment variable name for Secret 3 |
| AdditionalSecret4Name | String | No | myapp-storage-key | Name of fourth secret (optional) |
| AdditionalSecret4EnvVarName | String | No | STORAGE_KEY | Environment variable name for Secret 4 |
| AdditionalSecret5Name | String | No | myapp-auth-token | Name of fifth secret (optional) |
| AdditionalSecret5EnvVarName | String | No | AUTH_TOKEN | Environment variable name for Secret 5 |

### Container Configuration
| Parameter | Type | Required | Sample Value | Description |
|-----------|------|----------|--------------|-------------|
| ECRImageUri | String | Yes | 123456789012.dkr.ecr.us-east-1.amazonaws.com/myapp-loader:latest | Full URI of the ECR image |
| BatchJobVCPU | Number | No | 2 | Number of vCPUs for Batch job (0.25-16) |
| BatchJobMemory | Number | No | 4096 | Memory (MB) for Batch job (512-120000) |

### S3 Configuration
| Parameter | Type | Required | Sample Value | Description |
|-----------|------|----------|--------------|-------------|
| UseExistingS3 | String | Yes | true | Set to true if using existing S3 bucket |
| ExistingBucketName | String | No* | my-bucket | Name of the existing S3 bucket (*Required if UseExistingS3 is true) |
| InputPrefix | String | No | input/ | S3 prefix path for input files (e.g., input/, data/incoming/) - Leave empty to monitor entire bucket |
| LogRetention | Number | No | 365 | Days to retain logs (default: 365) |
| EnableInputTransformation | String | No | false | Enable input transformation for S3 events to pass bucket/key as env vars |

### Network Configuration
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| VpcCidr1 | String | Yes | "" | Primary VPC CIDR IP Range |
| VpcCidr2 | String | No | "" | Secondary VPC CIDR IP Range (optional) |
| VpcCidr3 | String | No | "" | Tertiary VPC CIDR IP Range (optional) |
| VpcCidr4 | String | No | "" | Quaternary VPC CIDR IP Range (optional) |
| VpcCidr5 | String | No | "" | Quinary VPC CIDR IP Range (optional) |
| VPCSubnetCidrDBAZ1 | String | Yes | "" | Database subnet CIDR for AZ1 |
| VPCSubnetCidrDBAZ2 | String | Yes | "" | Database subnet CIDR for AZ2 |
| VPCSubnetCidrDBAZ3 | String | No | "" | Database subnet CIDR for AZ3 (optional) |
| ProdDBPort | String | No | 53341 | Database port for production environments |
| NProdDBPort | String | No | 53331 | Database port for non-production environments |
| S3PrefixListId | String | No | "" | S3 prefix list ID for VPC endpoint access |
| HCCVpceCidr | String | No | "" | HCC VPC endpoint subnet CIDR range |

### Environment Variable Configuration
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| EnvVarConnectionStringSecretName | String | No | "" | Environment variable for ECS connection string secret name |
| EnvVar1Name | String | No | "" | Name for first custom environment variable |
| EnvVar1Value | String | No | "" | Value for first custom environment variable |
| EnvVar2Name | String | No | "" | Name for second custom environment variable |
| EnvVar2Value | String | No | "" | Value for second custom environment variable |
| EnvVar3Name | String | No | "" | Name for third custom environment variable |
| EnvVar3Value | String | No | "" | Value for third custom environment variable |

## Template Conditions

The template uses the following conditions to control resource creation and configuration:

| Condition | Description |
|-----------|-------------|
| IsProduction | True for prod, prod-a, prod-b, and prod-c environments |
| HasDatabaseSecret | True when DatabaseSecretName is provided |
| HasAdditionalSecret2 | True when AdditionalSecret2Name is provided |
| HasAdditionalSecret3 | True when AdditionalSecret3Name is provided |
| HasAdditionalSecret4 | True when AdditionalSecret4Name is provided |
| HasAdditionalSecret5 | True when AdditionalSecret5Name is provided |
| HasAnySecret | True when any secret (database or additional) is provided |
| HasSNSTopic | True when SNSTopicName is provided |
| HasInputPrefix | True when InputPrefix is provided and not empty |
| UseS3 | True when UseExistingS3 is set to 'true' |
| IsScheduleTrigger | True when TriggerType is 'Schedule' |
| IsS3EventTrigger | True when TriggerType is 'S3Event' AND UseExistingS3 is 'true' |
| IsInputTransformationEnabled | True when EnableInputTransformation is 'true' |
| HasVPCSubnetCidrDBAZ3 | True when VPCSubnetCidrDBAZ3 is provided |
| HasHCCVpceCidr | True when HCCVpceCidr is provided |
| HasS3PrefixListId | True when S3PrefixListId is provided |
| HasVpcCidr5 | True when VpcCidr5 is provided |
| HasVpcCidr4 | True when VpcCidr4 is provided |
| HasVpcCidr3 | True when VpcCidr3 is provided |
| HasVpcCidr2 | True when VpcCidr2 is provided |
| HasEnvVar1Name | True when EnvVar1Name is provided and not empty |
| HasEnvVar2Name | True when EnvVar2Name is provided and not empty |
| HasEnvVar3Name | True when EnvVar3Name is provided and not empty |
| HasEnvVarConnectionStringSecretName | True when EnvVarConnectionStringSecretName is provided and not empty |

These conditions determine which resources are created and how they are configured based on the input parameters.

## Deployed Resources

### EventBridge Resources
Based on TriggerType, one of the following will be created:

1. Schedule-based Resource (TriggerType = Schedule):
   - Type: AWS::Scheduler::Schedule
   - Name: `${AppShortName}-${EnvName}-${BatchJobName}-schedule`
   - Triggers based on provided schedule expression
   - Supports cron and rate expressions
   - Configurable timezone and flexible time window

2. S3 Event-based Rule (TriggerType = S3Event):
   - Type: AWS::Events::Rule
   - Name: `${AppShortName}-${EnvName}-${BatchJobName}-s3event`
   - Triggers on S3 object creation events
   - Monitors configured S3 bucket
   - Conditional prefix filtering based on InputPrefix parameter
   - When InputPrefix provided: monitors only files with matching prefix
   - When InputPrefix empty: monitors all files in bucket
   - Optional input transformation to pass bucket name and object key as environment variables

### AWS Batch Resources
1. Compute Environment
   - Name: `${AppShortName}-${EnvName}-${BatchJobName}`
   - Type: FARGATE
   - Max vCPUs: 4
   - VPC configuration with security group

2. Job Queue
   - Name: `${AppShortName}-${EnvName}-${BatchJobName}-queue`
   - Priority: 1
   - Connected to compute environment

3. Job Definition
   - Name: `${AppShortName}-${EnvName}-${BatchJobName}-job`
   - Platform: FARGATE
   - CPU: Configurable (default: 2 vCPU)
   - Memory: Configurable (default: 4096 MB)
   - Container image from ECR
   - Read-only root filesystem
   - Support for up to 6 secrets injection

### IAM Resources
1. Batch Job Role
   - Name: `${AppShortName}-${EnvName}-${BatchJobName}-role`
   - S3 operations for configured bucket
   - Secrets Manager access for all configured secrets (database + additional secrets)
   - SES permissions for email notifications
   - SNS permissions for publishing notifications

2. Batch Execution Role
   - Name: `${AppShortName}-${EnvName}-${BatchJobName}-execution-role`
   - ECR image pull permissions
   - CloudWatch Logs access
   - Secrets Manager access for all configured secrets
   - Basic execution permissions

3. EventBridge Role
   - Name: `${AppShortName}-${EnvName}-${BatchJobName}-events-role`
   - Permission to submit Batch jobs

### Security Group
- Name: `${AppShortName}-${EnvName}-sg-${BatchJobName}`
- Controlled outbound access based on VPC CIDR and database subnet CIDRs
- No inbound rules required

## SFTP Bucket Access
In addition to the configured S3 bucket, the template automatically includes permissions for accessing any S3 bucket with a name starting with "sftp" & application-specific:

- Both BatchJobPolicy and BatchExecutionPolicy include permissions for:
  - s3:GetObject
  - s3:ListBucket
  - s3:PutObject
  - s3:DeleteObject
- These permissions apply to:
  - arn:aws:s3:::sftp*
  - arn:aws:s3:::sftp*/*
  - arn:aws:s3:::${AppShortName}-${EnvName}-*
  - arn:aws:s3:::${AppShortName}-${EnvName}-*/*
- This allows batch jobs to read from and write to application-specific and SFTP-managed buckets without additional configuration

## Resource Retention and Deletion Policies
For production environments (prod, prod-a, prod-b, prod-c):
- Resources have DeletionPolicy set to Retain
- UpdateReplacePolicy set to Retain
- Applies to all major resources (IAM, CloudWatch, Batch, Security Groups)

For non-production environments:
- Resources have DeletionPolicy set to Delete
- UpdateReplacePolicy set to Delete
- Resources will be removed when the stack is deleted

This provides appropriate lifecycle management based on environment type.

## Important Notes for Developers

1. Container Requirements
   - Must run in Fargate environment
   - Should handle S3 file loading using environment variables
   - Must use database credentials and other secrets from Secrets Manager
   - Should implement proper error handling and logging
   - Should implement email notifications using SES
   - Should implement event notifications using SNS
   - Root filesystem is read-only by default

2. Secrets Management
   - Up to 6 secrets supported (1 primary database + 5 additional)
   - All secrets retrieved from AWS Secrets Manager
   - Secrets injected as environment variables at container startup
   - Secret values never exposed in CloudFormation or Console
   - IAM permissions automatically configured for all provided secrets
   - Each additional secret has a customizable environment variable name
   - Production secrets should be managed separately from stack lifecycle

3. S3 Bucket Configuration
   - Template requires an existing S3 bucket (UseExistingS3 must be true)
   - Bucket name provided through ExistingBucketName parameter
   - InputPrefix parameter controls which files trigger processing:
     - When InputPrefix provided: only files with matching prefix trigger jobs
     - When InputPrefix empty: any file upload triggers jobs
   - Ensure proper bucket permissions are configured:
     - s3:GetObject, s3:ListBucket, s3:PutObject, s3:DeleteObject permissions
     - TLS 1.2 or higher enforcement
     - SSL/TLS for all requests
   - EventBridge notifications must be configured if using S3Event trigger

4. EventBridge Configuration
   Two trigger options available:
   
   a. Schedule Trigger (Using EventBridge Scheduler):
      - Set TriggerType to 'Schedule'
      - Provide valid schedule expression in ScheduleExpression parameter
      - Supports cron and rate expressions
      - UTC timezone by default
      - FlexibleTimeWindow mode is OFF by default
      - Retry attempts configured to 3

   b. S3 Event Trigger:
      - Set TriggerType to 'S3Event'
      - UseExistingS3 must be true
      - InputPrefix parameter controls event scope:
        - Provide InputPrefix to monitor specific prefix only
        - Leave InputPrefix empty to monitor entire bucket
      - Ensures bucket notifications are properly set up
      - Monitors only Object Created events
      - Retry attempts configured to 3
      - Optional input transformation to pass bucket/key dynamically

5. Email Notification Configuration
   - Container must include SMTP configuration for Amazon SES
   - Required configurations to be bundled in container code:
     - SMTP server details
     - SMTP port
     - From email address
     - Recipient list
     - Email subject template
   - SES permissions configured through BatchJobPolicy
   - Ensure proper SES sending limits and domain verification
   - Consider implementing email templates for different job statuses
   - Handle email sending errors appropriately

6. SNS Notification Configuration
   - Container must include code to publish to SNS
   - SNS topic ARN provided as environment variable
   - SNS permissions configured through BatchJobPolicy
   - Consider structured JSON messages for event notifications
   - Implement proper error handling for notification failures
   - Use attributes for message filtering by subscribers

7. Environment Variables
   The following environment variables are automatically passed to your container:
   
   **Standard Variables:**
   - S3_BUCKET_NAME: Name of the existing S3 bucket (when UseExistingS3 is true)
   - S3_INPUT_PREFIX: S3 prefix path (when InputPrefix is provided)
   - ENVIRONMENT: The deployment environment name (e.g., "nprd-dev", "prod")
   - SNS_TOPIC_ARN: ARN of the SNS topic for notifications (when SNSTopicName is provided)
   
   **Secret Variables (from Secrets Manager):**
   - DB_SECRET_NAME: Primary database secret (when DatabaseSecretName is provided)
   - Up to 5 additional secret variables with custom names (when AdditionalSecretXName is provided)
   
   **Custom Plain-Text Variables:**
   - AwsSecretPrefix: Connection string secret name (when EnvVarConnectionStringSecretName is provided)
   - Up to 3 additional custom variables (when EnvVarXName is provided)

8. Resource Naming Convention
   All resources follow the pattern: ${AppShortName}-${EnvName}-${BatchJobName}[-resource-type]
   Examples:
   - Batch Compute Environment: ${AppShortName}-${EnvName}-${BatchJobName}
   - Job Queue: ${AppShortName}-${EnvName}-${BatchJobName}-queue
   - Job Definition: ${AppShortName}-${EnvName}-${BatchJobName}-job
   - Schedule: ${AppShortName}-${EnvName}-${BatchJobName}-schedule
   - S3 Event Rule: ${AppShortName}-${EnvName}-${BatchJobName}-s3event

9. VPC CIDR Configuration
   The template supports multiple VPC CIDR ranges for security group configuration:
   - VpcCidr1: Primary VPC CIDR range (required)
   - VpcCidr2: Secondary VPC CIDR range (optional)
   - VpcCidr3: Tertiary VPC CIDR range (optional)
   - VpcCidr4: Quaternary VPC CIDR range (optional)
   - VpcCidr5: Quinary VPC CIDR range (optional)
   - VPCSubnetCidrDBAZ1: AZ1 Database subnet CIDR (required)
   - VPCSubnetCidrDBAZ2: AZ2 Database subnet CIDR (required)
   - VPCSubnetCidrDBAZ3: AZ3 Database subnet CIDR (optional)
   - HCCVpceCidr: CIDR for HCC VPC endpoint (optional)
   - S3PrefixListId: S3 prefix list ID for endpoint access (optional)

   These parameters provide fine-grained control over network security and access paths.

## Core Configuration Patterns

### 1. Schedule-based Processing with Multiple Secrets
**Use Case**: Process files on a schedule with access to multiple external services requiring separate credentials
**Configuration**:
- Set `TriggerType: Schedule`
- Set `UseExistingS3: true`
- Set `ExistingBucketName: my-data-bucket`
- Set `ScheduleExpression: cron(0 0 * * ? *)`
- Configure secrets:
  - `DatabaseSecretName: my-db-secret`
  - `AdditionalSecret2Name: my-api-key-secret`
  - `AdditionalSecret2EnvVarName: API_KEY`
  - `AdditionalSecret3Name: my-oauth-token`
  - `AdditionalSecret3EnvVarName: OAUTH_TOKEN`

### 2. Event-driven Processing with Existing S3 Bucket
**Use Case**: Process files immediately when they arrive anywhere in an existing S3 bucket
**Configuration**:
- Set `TriggerType: S3Event`
- Set `UseExistingS3: true`
- Set `ExistingBucketName: my-data-bucket`
- Configure secrets as needed

### 3. Event-driven Processing with Prefix Filtering and Multiple Secrets
**Use Case**: Process only specific files (with prefix) and use multiple credentials
**Configuration**:
- Set `TriggerType: S3Event`
- Set `UseExistingS3: true`
- Set `ExistingBucketName: my-data-bucket`
- Set `InputPrefix: incoming/data/`
- Configure multiple secrets:
  - `DatabaseSecretName: my-db-secret`
  - `AdditionalSecret2Name: my-storage-key`
  - `AdditionalSecret2EnvVarName: STORAGE_ACCESS_KEY`

### 4. Schedule-based Processing without S3 Bucket
**Use Case**: Schedule-based processing without requiring S3 bucket access
**Configuration**:
- Set `TriggerType: Schedule`
- Set `UseExistingS3: false`
- Set `ScheduleExpression: cron(0 0 * * ? *)`
- Configure secrets as needed for external API access

## Troubleshooting
Common issues and solutions:

1. Deployment Failures
   - Verify ECR repository exists
   - Check VPC and subnet configurations
   - Ensure required VPC endpoints are in place
   - Validate IAM role permissions
   - Verify all configured secrets exist and are accessible
   - Confirm SFTP bucket exists and is accessible (if using SFTP-managed bucket)
   - Verify SES configuration and email verification status
   - Verify SNS topic exists and is accessible

2. Job Failures
   - Check CloudWatch logs for container errors
   - Verify all secret access permissions
   - Ensure container can access required AWS services
   - Validate S3 bucket permissions
   - Check EventBridge rule configuration
   - Verify SES sending limits and permissions
   - Verify SNS publishing permissions
   - Confirm all required secrets are configured and accessible

3. Secret Access Issues
   - Verify secret names match exactly (case-sensitive)
   - Ensure secrets exist in the same region
   - Check IAM policies for Secrets Manager permissions
   - Verify secret ARN format is correct
   - Review CloudWatch logs for specific secret retrieval errors
   - Confirm container code is reading the correct environment variable names

4. Email Notification Issues
   - Verify email addresses are verified in SES
   - Check SES sending limits
   - Confirm proper SES permissions
   - Review CloudWatch logs for email sending errors

5. SNS Notification Issues
   - Verify SNS topic exists
   - Check SNS publishing permissions
   - Confirm proper topic policy configuration
   - Review CloudWatch logs for SNS publishing errors

6. S3 Event Processing Issues
   - Verify EventBridge notifications are enabled on the S3 bucket
   - Check InputPrefix configuration matches your file paths
   - Confirm S3 event pattern in EventBridge rule is correct
   - Review EventBridge metrics for rule invocation counts
   - Check if EnableInputTransformation is set correctly for your use case

## Monitoring and Logging

1. CloudWatch Logs
   - Log group name: `/aws/batch/${AppShortName}-${EnvName}-${BatchJobName}`
   - Configurable retention period
   - Batch job execution logs
   - Container application logs
   - Email notification logs
   - SNS notification logs
   - Secret retrieval logs (errors only)

2. AWS Batch Dashboard
   - Job queue metrics
   - Job success/failure rates
   - Resource utilization
   - Trigger event monitoring (Schedule or S3)

3. Secrets Manager Monitoring
   - Monitor secret retrieval via CloudTrail
   - Track secret rotation events
   - Review access patterns for security auditing

4. EventBridge Metrics
   - Rule invocation counts
   - Failed invocations
   - Throttled requests

## Security Best Practices

1. **Secrets Management**
   - Rotate secrets regularly using Secrets Manager rotation
   - Use separate secrets for different environments
   - Never hardcode credentials in container images
   - Implement least-privilege access for secret retrieval
   - Monitor secret access via CloudTrail

2. **IAM Permissions**
   - Follow principle of least privilege
   - Use separate roles for job execution and runtime
   - Regularly audit IAM policies
   - Remove unused permissions

3. **Network Security**
   - Deploy in private subnets only
   - Use VPC endpoints for AWS service access
   - Implement security group rules with minimal access
   - Enable VPC flow logs for network monitoring

4. **Container Security**
   - Use read-only root filesystem
   - Scan container images for vulnerabilities
   - Keep base images updated
   - Use minimal base images

## Resource Tagging

All resources in this template are tagged with:
- **IaCVersion**: `AppSubsystem-BatchJob-v3` - Identifies resources created by this specific version of the template

This tagging strategy helps with:
- Resource identification and tracking
- Cost allocation and management
- Governance and compliance
- Version-specific resource management

Tagged resources include:
- CloudWatch Log Groups
- Security Groups
- IAM Roles and Policies
- Batch Compute Environments, Job Queues, and Job Definitions
- EventBridge Schedules and Rules
- All other taggable AWS resources created by this template
