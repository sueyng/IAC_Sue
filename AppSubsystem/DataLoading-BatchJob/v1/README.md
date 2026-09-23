# Data Loading with Optional Schedule or S3 Event Trigger and AWS Batch

This CloudFormation template deploys a serverless data loading infrastructure using AWS Batch, S3, and EventBridge Scheduler/Rules. The template supports both schedule-based and S3 event-based triggers, along with options for using existing S3 buckets for data ingestion, processed using AWS Batch jobs with Fargate compute resources.

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
                           +----------------------|------------------------+---------------+
                           |                      |                        |               |
                           v                      v                        v               v
                +----------------+    +------------------+    +--------------+       +--------------+
                |   Secrets      |    |    Container     |    |  CloudWatch  |       |  Amazon SES  |
                |   Manager      |    |    Registry      |    |    Logs      |       |  (Email)     |
                |                |    |     (ECR)        |    |              |       |              |
                +----------------+    +------------------+    +--------------+       +--------------+

```

### Flow Options:

1. Schedule-based Trigger (using EventBridge Scheduler):
   - EventBridge scheduler triggers batch job at specified times
   - Batch job processes data according to schedule
   - Supports both cron and rate expressions

2. S3 Event-based Trigger:
   - S3 -> EventBridge: File upload triggers event
   - EventBridge -> Batch: Start loading job
   - Monitors specific prefix for new files

Common Processing Flow:
1. Batch -> ECR: Pull container image
2. Batch -> Secrets: Get database credentials (if configured)
3. Batch -> S3: Load data files
4. Batch -> RDS: Store loaded data in database
5. Batch -> SES: Send email notifications
6. Batch -> CloudWatch: Log loading output

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

### 3. Database Secret (Optional)
- Existing AWS Secrets Manager secret for RDS database credentials
- Secret name or ARN needed for template deployment

### 4. Additional Secrets (Optional - Up to 4)
- Support for up to 4 additional secrets from AWS Secrets Manager
- Each secret can be mapped to a custom environment variable name
- Useful for API keys, external service credentials, or other sensitive configuration

### 5. S3 Bucket Configuration
- Existing S3 bucket required for S3Event trigger or when UseExistingS3 is true
- Proper bucket permissions and notifications configured

### 6. Amazon SES Configuration
- Verified email addresses or domains in Amazon SES
- If in sandbox mode, verified recipient email addresses
- Proper SES configuration in the deployment region
- Email templates for job status notifications

## Environment Variables and Configuration

### Container Environment Variables
The following environment variables are automatically passed to your container:
- `S3_BUCKET_NAME`: Name of the S3 bucket (when UseExistingS3 is true)
- `S3_INPUT_PREFIX`: The input prefix path for monitoring (e.g., "input/")
- `ENVIRONMENT`: The deployment environment name (e.g., "nprd-dev", "prod")
- `DB_SECRET_NAME`: Name of the Secrets Manager secret containing database credentials (if configured)
- **Custom Secret Variables**: Additional secrets can be mapped to custom environment variable names (e.g., `API_KEY_SECRET`, `EXTERNAL_API_SECRET`, etc.)

## Security and Networking Requirements

### VPC Endpoints
The following VPC endpoints are **required** for Fargate tasks running in private subnets:
- `com.amazonaws.region.ecr.api`: ECR API endpoint
- `com.amazonaws.region.ecr.dkr`: ECR Docker endpoint
- `com.amazonaws.region.s3`: S3 endpoint
- `com.amazonaws.region.secretsmanager`: Secrets Manager endpoint
- `com.amazonaws.region.logs`: CloudWatch Logs endpoint
- `com.amazonaws.region.email-smtp`: SES SMTP endpoint (for email notifications)

Without these endpoints, Fargate tasks will fail to:
- Pull container images
- Access S3 buckets
- Retrieve secrets
- Send logs to CloudWatch
- Send email notifications

### Security Group Configuration
The template configures a security group with:
- Outbound: All traffic allowed (default AWS behavior)
  - Allows access to AWS services (S3, Secrets Manager, CloudWatch, SES)
  - Allows external API calls if needed by your application
- Inbound: None
  - No inbound rules as Batch jobs don't accept incoming connections

## Event Patterns and Triggers

The template supports two types of triggers:

### 1. Schedule-based Pattern
When TriggerType is set to 'Schedule', the template uses AWS::Scheduler::Schedule resource:
```yaml
ScheduleExpression: cron(0 12 * * ? *)  # Example: Run daily at 12 PM UTC
```

Schedule expressions can be specified in two formats:
- Cron expressions: `cron(0 12 * * ? *)`
- Rate expressions: `rate(1 day)`

### 2. S3 Event Pattern
When TriggerType is set to 'S3Event', the template uses AWS::Events::Rule with an event pattern that watches for object creation events:
```json
{
  "detail-type": ["Object Created"],
  "source": ["aws.s3"],
  "detail": {
    "bucket": {
      "name": ["<your-bucket-name>"]
    },
    "object": {
      "key": [{"prefix": "<your-input-prefix>"}]
    }
  }
}
```

This pattern ensures:
- Only object creation events trigger jobs
- Only objects in the specified input prefix trigger jobs
- Events from the correct bucket are processed

## Template Parameters

### Environment Configuration
| Parameter | Type | Required | Sample Value | Description |
|-----------|------|----------|--------------|-------------|
| AppShortName | String | Yes | myapp | Application identifier for resource naming |
| BatchJobName | String | Yes | learner-master-data | Unique identifier for this batch job |
| EnvName | String | Yes | nprd-dev | Environment name (multiple options including prod, nprd variants) |
| TriggerType | String | Yes | Schedule/S3Event | Choose whether to trigger batch job by schedule or S3 event |
| ScheduleExpression | String | No* | cron(0 12 * * ? *) | Schedule expression (*Required if TriggerType is Schedule) |
| DatabaseSecretName | String | No | myapp-dev-postgresql | Name or ARN of existing RDS secret |
| VpcId | String | Yes | vpc-0abc123def456789 | VPC for Batch compute environment |
| AppSubnetIds | List | Yes | subnet-0abc123def456789,subnet-0xyz987wvu654321 | Private subnet IDs for Batch jobs |
| InputPrefix | String | No | input/ | S3 prefix path for input files |

### Additional Secrets Configuration (Optional)
| Parameter | Type | Required | Sample Value | Description |
|-----------|------|----------|--------------|-------------|
| AdditionalSecret2Name | String | No | myapp-dev-api-key | Name of the second secret in Secrets Manager |
| AdditionalSecret2EnvVarName | String | No | API_KEY_SECRET | Environment variable name for Additional Secret 2 |
| AdditionalSecret3Name | String | No | myapp-dev-external-api | Name of the third secret in Secrets Manager |
| AdditionalSecret3EnvVarName | String | No | EXTERNAL_API_SECRET | Environment variable name for Additional Secret 3 |
| AdditionalSecret4Name | String | No | myapp-dev-storage | Name of the fourth secret in Secrets Manager |
| AdditionalSecret4EnvVarName | String | No | STORAGE_SECRET | Environment variable name for Additional Secret 4 |
| AdditionalSecret5Name | String | No | myapp-dev-auth-token | Name of the fifth secret in Secrets Manager |
| AdditionalSecret5EnvVarName | String | No | AUTH_TOKEN_SECRET | Environment variable name for Additional Secret 5 |

**Note**: For additional secrets, you only need to provide the secret name if you want to use it. If the secret name is empty, the corresponding environment variable will not be created, and the EnvVarName parameter will be ignored.

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
| LogRetention | Number | No | 365 | Days to retain logs (default: 365) |

### Network Configuration (Optional)
| Parameter | Type | Required | Sample Value | Description |
|-----------|------|----------|--------------|-------------|
| VpcCidr1 | String | No | 10.0.0.0/16 | Primary VPC CIDR range |
| VpcCidr2 | String | No | 172.16.0.0/16 | Secondary VPC CIDR range (optional) |
| VpcCidr3 | String | No | 192.168.0.0/16 | Tertiary VPC CIDR range (optional) |
| VPCSubnetCidrDBAZ1 | String | No | 10.0.1.0/24 | AZ1 Database subnet CIDR |
| VPCSubnetCidrDBAZ2 | String | No | 10.0.2.0/24 | AZ2 Database subnet CIDR |
| VPCSubnetCidrDBAZ3 | String | No | 10.0.3.0/24 | AZ3 Database subnet CIDR (optional) |
| ProdDBPort | String | No | 53341 | Production database port |
| NProdDBPort | String | No | 53331 | Non-production database port |
| S3PrefixListId | String | No | pl-123abc | S3 prefix list ID (optional) |
| HCCVpceCidr | String | No | 10.0.0.0/24 | HCC VPC Endpoint CIDR range (optional) |

## Deployed Resources

### EventBridge Resources
Based on TriggerType, one of the following will be created:

1. Schedule-based Resource (TriggerType = Schedule):
   - Type: AWS::Scheduler::Schedule
   - Name: `${AppShortName}-${EnvName}-${BatchJobName}-schedule`
   - Triggers based on provided schedule expression
   - Configurable timezone (UTC by default)
   - Flexible time window set to "OFF"

2. S3 Event-based Rule (TriggerType = S3Event):
   - Type: AWS::Events::Rule
   - Name: `${AppShortName}-${EnvName}-${BatchJobName}-s3event`
   - Triggers on S3 object creation in specified prefix
   - Monitors configured S3 bucket

### AWS Batch Resources
1. Compute Environment
   - Name: `${AppShortName}-${EnvName}-${BatchJobName}`
   - Type: FARGATE
   - MaxvCpus: 4
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
   - Read-only root filesystem (enabled)
   - Fargate Platform Version: 1.4.0

### IAM Resources
1. Batch Job Role
   - Name: `${AppShortName}-${EnvName}-${BatchJobName}-role`
   - S3 operations for configured bucket
   - SFTP bucket access (sftp* & application-specific buckets)
   - SES permissions for email notifications
   - Secrets Manager access for database credentials (if configured)
   - **Secrets Manager access for additional secrets (if configured)**

2. Batch Execution Role
   - Name: `${AppShortName}-${EnvName}-${BatchJobName}-execution-role`
   - ECR image pull permissions
   - CloudWatch Logs access
   - S3 access (configured bucket, SFTP & application-specific buckets)
   - SES permissions for email notifications
   - Secrets Manager access (if configured)
   - **Secrets Manager access for additional secrets (if configured)**

3. EventBridge Role
   - Name: `${AppShortName}-${EnvName}-${BatchJobName}-events-role`
   - Permissions for batch:SubmitJob and related operations
   - Scheduler permissions for creating and managing schedules

### Security Group
- Name: `${AppShortName}-${EnvName}-sg-${BatchJobName}`
- Default outbound access (all traffic allowed)
- No inbound rules required

### Bucket Policy (When UseExistingS3 is true)
- Allows Batch Job role to access the bucket
- Enforces TLS v1.2 or higher 
- Requires SSL for all S3 requests

## Production Considerations

### Resource Retention
For production environments (prod, prod-a, prod-b):
- Resources retained on stack deletion (DeletionPolicy: Retain)
- UpdateReplacePolicy set to Retain
- Applies to all major resources (IAM, CloudWatch, Batch, Security Groups)

## Important Notes for Developers

1. Container Requirements
   - Must run in Fargate environment
   - Should handle S3 file loading using environment variables
   - Must use database credentials from Secrets Manager (if configured)
   - Should implement proper error handling and logging
   - Should implement email notifications using SES
   - Root filesystem is read-only by default

2. Database Credentials (Optional)
   - When specified, uses existing secret from Secrets Manager
   - Secret name provided as parameter during deployment (DatabaseSecretName)
   - Accessed by Batch jobs via environment variable (DB_SECRET_NAME)
   - Ensure secret permissions are properly configured
   - Production secrets should be managed separately from stack lifecycle

3. **Additional Secrets Support (Optional - Up to 4)**
   - Template supports up to 4 additional secrets beyond the database secret
   - Each secret can be configured independently:
     - Provide the secret name (e.g., `myapp-dev-api-key`)
     - Specify custom environment variable name (e.g., `API_KEY_SECRET`)
   - **If you don't need a secret, leave the secret name empty (`""`)**
   - When a secret name is empty, the environment variable will NOT be created
   - Secrets are accessed in your container via the custom environment variable names
   - IAM permissions are automatically granted only for configured secrets
   - Use cases include:
     - API keys for external services
     - Authentication tokens
     - Storage credentials
     - Third-party service secrets
   - Example configuration:
     ```json
     {
       "ParameterKey": "AdditionalSecret2Name",
       "ParameterValue": "myapp-dev-api-key"
     },
     {
       "ParameterKey": "AdditionalSecret2EnvVarName",
       "ParameterValue": "API_KEY_SECRET"
     }
     ```

4. S3 Bucket Configuration
   - Template supports using an existing S3 bucket (UseExistingS3 parameter)
   - Bucket name provided through ExistingBucketName parameter
   - Bucket policy enforces:
     - s3:GetObject, s3:ListBucket, and s3:PutObject permissions
     - TLS 1.2 or higher enforcement
     - SSL/TLS for all requests
   - Input prefix configuration via InputPrefix parameter
   - S3 event notifications required if using S3Event trigger

5. EventBridge Configuration
   Two trigger options available:
   
   a. Schedule Trigger (Using EventBridge Scheduler):
      - Set TriggerType to 'Schedule'
      - Provide valid schedule expression in ScheduleExpression parameter
      - Supports cron and rate expressions
      - UTC timezone by default
      - FlexibleTimeWindow mode is OFF

   b. S3 Event Trigger:
      - Set TriggerType to 'S3Event'
      - UseExistingS3 must be true
      - Configure proper InputPrefix for monitoring
      - Monitors only Object Created events
      - Retry attempts configured to 3

6. SFTP Bucket Access
   - Template includes permissions for accessing sftp* & application-specific buckets
   - Allows s3:GetObject, s3:ListBucket, and s3:PutObject operations
   - These permissions apply to any bucket with a name pattern matching:
     - arn:aws:s3:::sftp*
     - arn:aws:s3:::sftp*/*
     - arn:aws:s3:::${AppShortName}-${EnvName}-*
     - arn:aws:s3:::${AppShortName}-${EnvName}-*/*

7. Email Notification Support
   - Template includes SES permissions for email notifications
   - Container should implement email sending functionality
   - SES permissions configured in both BatchJobPolicy and BatchExecutionPolicy

8. Environment Variables
   The following environment variables are automatically passed to your container:
   - S3_BUCKET_NAME: Name of the existing S3 bucket (when UseExistingS3 is true)
   - S3_INPUT_PREFIX: The input prefix path for monitoring
   - ENVIRONMENT: The deployment environment name (e.g., "nprd-dev", "prod")
   - DB_SECRET_NAME: Name of the Secrets Manager secret (when DatabaseSecretName is provided)
   - **Custom Secret Variables**: Any additional secrets configured will be available with their custom environment variable names

9. Resource Naming Convention
   All resources follow the pattern: ${AppShortName}-${EnvName}-${BatchJobName}[-resource-type]
   Examples:
   - Batch Compute Environment: ${AppShortName}-${EnvName}-${BatchJobName}
   - Job Queue: ${AppShortName}-${EnvName}-${BatchJobName}-queue
   - Job Definition: ${AppShortName}-${EnvName}-${BatchJobName}-job
   - Schedule: ${AppShortName}-${EnvName}-${BatchJobName}-schedule
   - S3 Event Rule: ${AppShortName}-${EnvName}-${BatchJobName}-s3event
   - Security Group: ${AppShortName}-${EnvName}-sg-${BatchJobName}

10. Production vs. Non-Production Environments
   - Different behavior for production environments (prod, prod-a, prod-b)
   - Resources retained on stack deletion in production
   - Database port differences between production (ProdDBPort) and non-production (NProdDBPort)

## Core Configuration Patterns

### 1. Schedule-based Processing with Existing S3 Bucket
**Use Case**: Process files from an existing S3 bucket on a schedule, regardless of when files arrive
**Configuration**:
- Set `TriggerType: Schedule`
- Set `UseExistingS3: true`
- Set `ExistingBucketName: my-data-bucket`
- Set `InputPrefix: input/`
- Set `ScheduleExpression: cron(0 0 * * ? *)`  # Customize schedule as needed

### 2. Event-driven Processing with Existing S3 Bucket
**Use Case**: Process files immediately when they arrive in an existing S3 bucket
**Configuration**:
- Set `TriggerType: S3Event`
- Set `UseExistingS3: true`  # Required for S3Event
- Set `ExistingBucketName: my-data-bucket`
- Set `InputPrefix: input/`

### 3. Schedule-based Processing without S3 Bucket
**Use Case**: Schedule-based processing without requiring S3 bucket access
**Configuration**:
- Set `TriggerType: Schedule`
- Set `UseExistingS3: false`
- Set `ScheduleExpression: cron(0 0 * * ? *)`  # Customize schedule as needed

### 4. Processing with Multiple Secrets
**Use Case**: Batch job requires database credentials plus API keys for external services
**Configuration**:
- Set `DatabaseSecretName: myapp-dev-postgresql`
- Set `AdditionalSecret2Name: myapp-dev-api-key`
- Set `AdditionalSecret2EnvVarName: API_KEY_SECRET`
- Set `AdditionalSecret3Name: myapp-dev-external-api`
- Set `AdditionalSecret3EnvVarName: EXTERNAL_API_SECRET`
- Leave other secret parameters empty if not needed

## Troubleshooting
Common issues and solutions:

1. Deployment Failures
   - Verify ECR repository exists and image URI is correct
   - Check VPC and subnet configurations
   - Ensure required VPC endpoints are in place
   - Validate IAM role permissions
   - Verify database secret exists and is accessible (if configured)
   - **Verify additional secrets exist in Secrets Manager (if configured)**
   - Confirm SFTP bucket exists and is accessible (if using SFTP-managed bucket)
   - Verify SES configuration and email verification status

2. Job Failures
   - Check CloudWatch logs for container errors
   - Verify database secret access permissions
   - **Verify additional secrets access permissions**
   - Ensure container can access required AWS services
   - Validate S3 bucket permissions
   - Check EventBridge rule configuration
   - Verify SES sending limits and permissions

3. Email Notification Issues
   - Verify email addresses are verified in SES
   - Check SES sending limits
   - Confirm proper SES permissions
   - Review CloudWatch logs for email sending errors

4. **Secret Access Issues**
   - Verify secret names are correct in Secrets Manager
   - Ensure secrets exist in the same region as the stack
   - Check IAM permissions for Secrets Manager access
   - Verify the secret ARN format is correct
   - Confirm the container is reading secrets using the correct environment variable names

## Monitoring and Logging

1. CloudWatch Logs
   - Log group name: `/aws/batch/${AppShortName}-${EnvName}-${BatchJobName}`
   - Configurable retention period (default: 365 days)
   - Contains batch job execution logs
   - Container application logs available
   - Email notification logs (if implemented)

2. AWS Batch Dashboard
   - Job queue metrics
   - Job success/failure rates
   - Resource utilization
   - Trigger event monitoring (Schedule or S3)