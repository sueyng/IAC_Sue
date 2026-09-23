# GuardDuty S3 Malware Protection CloudFormation Template (v2)

> **Version 2** - Latest release with AWS X-Ray tracing support

This CloudFormation template enables AWS GuardDuty S3 malware protection for a source bucket and automates the processing of scanned files. Clean files are automatically moved to a destination bucket, while infected files can optionally be quarantined. The template follows the `AppShortName-EnvName-BucketFunctionName` naming pattern for resources, enabling multiple independent deployments for different S3 buckets within the same environment.

## What's New in v2

- **Multi-Bucket Support**: New `BucketFunctionName` parameter enables deploying malware protection for multiple S3 buckets in the same environment
- **AWS X-Ray Tracing**: Support for distributed tracing to monitor and debug Lambda function execution
- **Selective Scanning**: Choose to scan entire bucket or specific prefixes for cost optimization
- **Advanced Prefix Mapping**: Flexible organization of scanned files with source-to-destination mappings
- **Dual-Copy Capability**: Optional secondary prefix for redundancy and compliance
- **VPC Deployment**: Enhanced security with Lambda deployed inside VPC
- **Multi-VPC Support**: Support for up to 5 VPC CIDR ranges
- **Custom Environment Variables**: Up to 7 custom environment variables for Lambda configuration

See [release notes](../release-notes.md) for complete version history and migration guides.

## Overview

The GuardDuty S3 Malware Protection solution allows you to:

- Enable real-time malware scanning for objects uploaded to S3 buckets
- Choose scan scope: scan all objects or only specific prefixes (folders)
- Automatically process scan results through EventBridge and Lambda
- Move clean files to a designated destination bucket
- Quarantine infected files in a separate bucket (optional)
- Tag scanned objects for tracking and auditing
- Maintain comprehensive CloudWatch logs for all operations
- Delete processed files from the source bucket after handling

The solution consists of:
- GuardDuty Malware Protection Plan for the source S3 bucket
- EventBridge rule to trigger on scan completion
- Lambda function to process scan results and move/quarantine files
- IAM roles and policies for GuardDuty and Lambda execution
- CloudWatch Logs for Lambda function monitoring

## Prerequisites

Before deploying this template, ensure you have:

1. IAM deployment role configured with appropriate permissions
2. AWS GuardDuty enabled in your AWS account and region
3. Source S3 bucket where files will be uploaded for scanning (already created)
4. Destination S3 bucket for clean files (already created)
5. (Optional) Quarantine S3 bucket for infected files
6. VPC and private subnets configured for Lambda deployment
7. S3 VPC Endpoint configured in the VPC (recommended for cost optimization)
8. S3 bucket containing the Lambda deployment package
9. Lambda code zip file (`guardduty-s3malware-handler.zip`) uploaded to the S3 bucket
10. Appropriate S3 bucket policies allowing GuardDuty and Lambda access

## Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| AppShortName | Short name for the application | "myapp" |
| EnvName | Environment name | "nprd-dev", "prod", "nprd-sit", etc. |
| BucketFunctionName | Unique identifier for this bucket's malware protection resources (e.g., bucket-name or purpose). Used to differentiate multiple S3 malware protection deployments in the same environment. | "uploads-bucket", "user-files" |
| UploadBucketName | Name of the source S3 bucket which will be enabled S3 Malware Detection | "myapp-nprd-dev-uploads" |
| ScanScope | Scan scope - ALL for entire bucket or PREFIXES for specific folders | "ALL" or "PREFIXES" |
| ScanScopePrefixList | Comma-separated list of S3 prefixes to scan (only used when ScanScope is PREFIXES) | "uploads/,documents/" or "" |
| CleanBucketName | Name of the destination S3 bucket for clean files | "myapp-nprd-dev-clean" |
| CleanBucketPrefix | Optional prefix mapping for clean bucket files | "scanned/" or "uploads/>scanned/,*>other/" |
| CleanBucketPrefix2 | Optional secondary prefix for clean bucket (dual-copy) | "backup/" or "" |
| MalwareQuarantineBucketName | Optional name of the S3 bucket for quarantining infected files | "myapp-nprd-dev-quarantine" or "" |
| MalwareQuarantineBucketPrefix | Optional prefix mapping for quarantine bucket files | "infected/" or "uploads/>quarantine/uploads/" |
| MalwareQuarantineBucketPrefix2 | Optional secondary prefix for quarantine bucket (dual-copy) | "infected-backup/" or "" |
| LambdaS3bucket | The S3 bucket where Lambda code is stored | "my-lambda-artifacts" |
| CodeZipFileName | Zip file name for lambda function code | "guardduty-s3malware-handler.zip" |
| LambdaRuntime | Runtime for Lambda | "python3.12" |
| LambdaHandler | Handler for Lambda function | "index.lambda_handler" |
| LambdaMemorySize | Memory size (MB) for the Lambda function | 128 |
| LambdaTimeout | Timeout (seconds) for the Lambda function | 30 |
| EnableXRayTracing | Enable AWS X-Ray tracing for Lambda function | 'true' or 'false' (default: 'true') |
| VpcId | VPC ID where Lambda will be deployed | "vpc-0123456789abcdef0" |
| AppSubnetIds | Comma-separated list of 2-4 App subnet IDs for Lambda | "subnet-abc123,subnet-def456" |
| VpcCidr1 | VPC CIDR 1 IP Range | "10.0.0.0/16" |
| VpcCidr2 | VPC CIDR 2 IP Range (optional) | "10.1.0.0/16" or "" |
| VpcCidr3 | Optional VPC CIDR 3 IP Range | "10.2.0.0/16" or "" |
| VpcCidr4 | Optional VPC CIDR 4 IP Range | "10.3.0.0/16" or "" |
| VpcCidr5 | Optional VPC CIDR 5 IP Range | "10.4.0.0/16" or "" |
| S3PrefixListId | S3 VPC Endpoint Prefix List ID for region | "pl-xxxxxx" or "" |
| CustomEnvVar1Name | Name/purpose of custom environment variable 1 (for documentation) | "API_KEY" or "" |
| CustomEnvVar1Value | Value for custom environment variable 1 | "your-api-key" or "" |
| CustomEnvVar2Name | Name/purpose of custom environment variable 2 (for documentation) | "LOG_LEVEL" or "" |
| CustomEnvVar2Value | Value for custom environment variable 2 | "INFO" or "" |
| CustomEnvVar3Name | Name/purpose of custom environment variable 3 (for documentation) | "DATABASE_URL" or "" |
| CustomEnvVar3Value | Value for custom environment variable 3 | "postgres://..." or "" |
| CustomEnvVar4Name | Name/purpose of custom environment variable 4 (for documentation) | "TIMEOUT" or "" |
| CustomEnvVar4Value | Value for custom environment variable 4 | "30" or "" |
| CustomEnvVar5Name | Name/purpose of custom environment variable 5 (for documentation) | "" |
| CustomEnvVar5Value | Value for custom environment variable 5 | "" |
| CustomEnvVar6Name | Name/purpose of custom environment variable 6 (for documentation) | "" |
| CustomEnvVar6Value | Value for custom environment variable 6 | "" |
| CustomEnvVar7Name | Name/purpose of custom environment variable 7 (for documentation) | "" |
| CustomEnvVar7Value | Value for custom environment variable 7 | "" |

### Environment Values

The `EnvName` parameter supports the following values:
- Non-production: nprd, nprd-dev, nprd-dev1, nprd-dev2, nprd-sit1, nprd-sit2, nprd-sit3, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-sit-c, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-uat-c, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b, nprd-pp-c
- Production: prod, prod-a, prod-b, prod-c

### Important Notes on Parameters

#### ScanScope and ScanScopePrefixList
- **ALL**: Scans all objects uploaded to the bucket (default and recommended for comprehensive protection)
- **PREFIXES**: Scans only objects with specific prefixes (useful for cost optimization when only certain folders need scanning)
- When using PREFIXES, specify folders in `ScanScopePrefixList` as comma-separated values: "uploads/,documents/,attachments/"
- Prefixes must end with `/` to represent folders
- If ScanScope is ALL, the ScanScopePrefixList parameter is ignored

#### LambdaRuntime and LambdaHandler
- These parameters allow you to upgrade Python versions or change the handler without modifying the template
- When upgrading from Python 3.12 to a newer version, simply update the `LambdaRuntime` parameter
- Useful for maintaining multiple versions of the template with different runtimes

#### MalwareQuarantineBucketName
- If left empty (""), infected files will be deleted from the source bucket without quarantining
- If specified, infected files will be copied to the quarantine bucket with appropriate tags before deletion from source
- Quarantined files are tagged with `QuarantineReason` and `SourceBucket` for tracking

#### Prefix Mapping Parameters
The prefix mapping parameters allow flexible organization of scanned files in destination and quarantine buckets:

**CleanBucketPrefix / MalwareQuarantineBucketPrefix:**
- **Empty**: Files are copied to the bucket root, preserving their original key
- **Single prefix** (e.g., "scanned/"): All files are copied under this prefix
- **Mapping format** (e.g., "uploads/>scanned/,documents/>reviewed/"): Map source prefixes to destination prefixes
- **Default mapping** (e.g., "*>default/"): Use `*` to specify a default prefix for unmatched sources

Examples:
- `"scanned/"` - All files go to `scanned/` prefix
- `"uploads/>scanned/uploads/,*>other/"` - Files from `uploads/` go to `scanned/uploads/`, others to `other/`
- `"*>processed/"` - All files go to `processed/` prefix

**CleanBucketPrefix2 / MalwareQuarantineBucketPrefix2:**
- Enables dual-copy functionality for redundancy or multi-location archiving
- Files are copied to both primary and secondary prefixes
- Leave empty to disable secondary copy
- Useful for compliance requirements or backup strategies

#### VPC Configuration
The template deploys the Lambda function inside a VPC for enhanced security:

**Required VPC Parameters:**
- `VpcId`: The VPC where Lambda will be deployed
- `AppSubnetIds`: List of 2-4 private app subnets (minimum 2 for high availability)
- `VpcCidr1`: Primary VPC CIDR block

**Optional VPC Parameters:**
- `VpcCidr2-5`: Additional VPC CIDR blocks for multi-VPC scenarios, VPC peering, or hybrid connectivity
- `S3PrefixListId`: S3 VPC Endpoint Prefix List ID for secure S3 access without NAT Gateway

**Security Group:**
- Automatically created security group with ingress rules for all VPC CIDRs
- Egress rules for VPC CIDRs and S3 endpoint access
- Enables secure communication within VPC and to S3

#### AWS X-Ray Tracing
The template includes optional AWS X-Ray distributed tracing for Lambda function monitoring:

**Parameter:**
- `EnableXRayTracing`: Enable or disable X-Ray tracing (default: 'true')

**Benefits:**
- **Performance Insights**: Visualize Lambda execution flow and identify bottlenecks
- **Distributed Tracing**: Track requests across S3, Lambda, and other AWS services
- **Error Analysis**: Quickly identify and debug errors in the malware processing workflow
- **Service Map**: Visual representation of service dependencies and call patterns
- **No Code Changes**: Enabled at deployment time without modifying Lambda code

**IAM Permissions:**
- When enabled, Lambda role includes `AWSXRayDaemonWriteAccess` managed policy
- Lambda TracingConfig set to 'Active' mode
- When disabled, TracingConfig set to 'PassThrough' mode

**Use Cases:**
- Monitoring scan processing latency
- Debugging file copy/quarantine operations
- Analyzing S3 and GuardDuty integration performance
- Troubleshooting VPC endpoint connectivity

#### Custom Environment Variables
The template supports up to 7 custom environment variables for the Lambda function:

**Parameter Pairs (Name + Value):**
- `CustomEnvVar1Name` / `CustomEnvVar1Value` through `CustomEnvVar7Name` / `CustomEnvVar7Value`
- Name parameters are for documentation purposes (e.g., "API_KEY", "DATABASE_URL", "LOG_LEVEL")
- Value parameters contain the actual values used by the Lambda function
- All custom variables are optional

**Lambda Environment Variables:**
- Variables are exposed to Lambda as `CUSTOM_ENV_VAR_1` through `CUSTOM_ENV_VAR_7`
- Only included if values are provided (empty values are excluded)
- CloudFormation limitation: Variable names in Lambda are fixed, cannot be dynamic

**Use Cases:**
- API keys and authentication credentials
- Database connection strings
- Feature flags and configuration settings
- Log levels and timeout values
- External service endpoints
- Environment-specific business logic parameters

**Example in Lambda Code (Python):**
```python
import os

api_key = os.environ.get('CUSTOM_ENV_VAR_1')  # Value from CustomEnvVar1Value
log_level = os.environ.get('CUSTOM_ENV_VAR_2')  # Value from CustomEnvVar2Value
database_url = os.environ.get('CUSTOM_ENV_VAR_3')  # Value from CustomEnvVar3Value
```

**Benefits:**
- No template modifications needed for custom configuration
- Different values per environment (dev, sit, uat, prod)
- Self-documenting with Name parameters
- Lambda code remains portable across environments

#### Bucket Naming
- All bucket names should follow your organization's naming convention
- Ensure buckets exist before deploying this template
- The Lambda function requires read/write permissions on all specified buckets

## Deployment

### Parameter File

The parameter file is maintained in YAML format. Edit the file at `env/parameters-s3malwareprotection.yaml`:

**Example 1: Scan All Objects (Default)**
```yaml
# APPLICATION BASICS
AppShortName: "myapp"
EnvName: "nprd-dev"
BucketFunctionName: "dataloading"

# S3 BUCKET CONFIGURATION
UploadBucketName: "myapp-nprd-dev-uploads"

# SCAN SCOPE CONFIGURATION
ScanScope: "ALL"
ScanScopePrefixList: ""

# DESTINATION BUCKETS
CleanBucketName: "myapp-nprd-dev-clean"
CleanBucketPrefix: ""
CleanBucketPrefix2: ""
MalwareQuarantineBucketName: "myapp-nprd-dev-quarantine"
MalwareQuarantineBucketPrefix: ""
MalwareQuarantineBucketPrefix2: ""

# LAMBDA CODE CONFIGURATION
LambdaS3bucket: "my-lambda-artifacts"
CodeZipFileName: "guardduty-s3malware-handler.zip"
LambdaRuntime: "python3.12"
LambdaHandler: "index.lambda_handler"
LambdaMemorySize: "128"
LambdaTimeout: "30"
EnableXRayTracing: "true"

# VPC CONFIGURATION
VpcId: "vpc-0123456789abcdef0"
AppSubnetIds: "subnet-abc123,subnet-def456"
VpcCidr1: "10.0.0.0/16"
VpcCidr2: ""
VpcCidr3: ""
VpcCidr4: ""
VpcCidr5: ""
S3PrefixListId: "pl-xxxxxx"

# CUSTOM ENVIRONMENT VARIABLES FOR LAMBDA
CustomEnvVar1Name: ""
CustomEnvVar1Value: ""
CustomEnvVar2Name: ""
CustomEnvVar2Value: ""
CustomEnvVar3Name: ""
CustomEnvVar3Value: ""
CustomEnvVar4Name: ""
CustomEnvVar4Value: ""
CustomEnvVar5Name: ""
CustomEnvVar5Value: ""
CustomEnvVar6Name: ""
CustomEnvVar6Value: ""
CustomEnvVar7Name: ""
CustomEnvVar7Value: ""
```

**Example 2: Scan Specific Prefixes with Prefix Mapping**
```yaml
# APPLICATION BASICS
AppShortName: "myapp"
EnvName: "nprd-dev"
BucketFunctionName: "useruploads"

# S3 BUCKET CONFIGURATION
UploadBucketName: "myapp-nprd-dev-uploads"

# SCAN SCOPE CONFIGURATION
ScanScope: "PREFIXES"
ScanScopePrefixList: "uploads/,documents/"

# DESTINATION BUCKETS
CleanBucketName: "myapp-nprd-dev-clean"
CleanBucketPrefix: "uploads/>scanned/,*>other/"
CleanBucketPrefix2: ""
MalwareQuarantineBucketName: "myapp-nprd-dev-quarantine"
MalwareQuarantineBucketPrefix: "infected/"
MalwareQuarantineBucketPrefix2: ""

# LAMBDA CODE CONFIGURATION
LambdaS3bucket: "my-lambda-artifacts"
CodeZipFileName: "guardduty-s3malware-handler.zip"
LambdaRuntime: "python3.12"
LambdaHandler: "index.lambda_handler"
LambdaMemorySize: "128"
LambdaTimeout: "30"
EnableXRayTracing: "true"

# VPC CONFIGURATION
VpcId: "vpc-0123456789abcdef0"
AppSubnetIds: "subnet-abc123,subnet-def456"
VpcCidr1: "10.0.0.0/16"
VpcCidr2: ""
VpcCidr3: ""
VpcCidr4: ""
VpcCidr5: ""
S3PrefixListId: "pl-xxxxxx"

# CUSTOM ENVIRONMENT VARIABLES FOR LAMBDA
CustomEnvVar1Name: ""
CustomEnvVar1Value: ""
CustomEnvVar2Name: ""
CustomEnvVar2Value: ""
CustomEnvVar3Name: ""
CustomEnvVar3Value: ""
CustomEnvVar4Name: ""
CustomEnvVar4Value: ""
CustomEnvVar5Name: ""
CustomEnvVar5Value: ""
CustomEnvVar6Name: ""
CustomEnvVar6Value: ""
CustomEnvVar7Name: ""
CustomEnvVar7Value: ""
```

**Example 3: Using Custom Environment Variables**
```yaml
# APPLICATION BASICS
AppShortName: "myapp"
EnvName: "nprd-dev"

# S3 BUCKET CONFIGURATION
UploadBucketName: "myapp-nprd-dev-uploads"

# SCAN SCOPE CONFIGURATION
ScanScope: "ALL"
ScanScopePrefixList: ""

# DESTINATION BUCKETS
CleanBucketName: "myapp-nprd-dev-clean"
CleanBucketPrefix: "scanned/"
CleanBucketPrefix2: ""
MalwareQuarantineBucketName: "myapp-nprd-dev-quarantine"
MalwareQuarantineBucketPrefix: "infected/"
MalwareQuarantineBucketPrefix2: ""

# LAMBDA CODE CONFIGURATION
LambdaS3bucket: "my-lambda-artifacts"
CodeZipFileName: "guardduty-s3malware-handler.zip"
LambdaRuntime: "python3.12"
LambdaHandler: "index.lambda_handler"
LambdaMemorySize: "128"
LambdaTimeout: "30"
EnableXRayTracing: "true"

# VPC CONFIGURATION
VpcId: "vpc-0123456789abcdef0"
AppSubnetIds: "subnet-abc123,subnet-def456"
VpcCidr1: "10.0.0.0/16"
VpcCidr2: ""
VpcCidr3: ""
VpcCidr4: ""
VpcCidr5: ""
S3PrefixListId: "pl-xxxxxx"

# CUSTOM ENVIRONMENT VARIABLES FOR LAMBDA
CustomEnvVar1Name: "API_KEY"
CustomEnvVar1Value: "your-api-key-here"
CustomEnvVar2Name: "LOG_LEVEL"
CustomEnvVar2Value: "INFO"
CustomEnvVar3Name: "DATABASE_URL"
CustomEnvVar3Value: "postgres://db.example.com:5432/mydb"
CustomEnvVar4Name: "TIMEOUT"
CustomEnvVar4Value: "30"
CustomEnvVar5Name: ""
CustomEnvVar5Value: ""
CustomEnvVar6Name: ""
CustomEnvVar6Value: ""
CustomEnvVar7Name: ""
CustomEnvVar7Value: ""
```

### Deployment Commands

Deploy using AWS CLI:

```bash
# Validate the template
aws cloudformation validate-template \
  --template-body file://cf-s3malwareprotection.yaml

# Create stack using YAML parameters
aws cloudformation create-stack \
  --stack-name myapp-nprd-dev-guardduty-s3 \
  --template-body file://cf-s3malwareprotection.yaml \
  --parameters file://env/parameters-s3malwareprotection.yaml \
  --capabilities CAPABILITY_NAMED_IAM \
  --role-arn arn:aws:iam::YOUR_ACCOUNT_ID:role/YOUR_DEPLOYMENT_ROLE

# Update existing stack
aws cloudformation update-stack \
  --stack-name myapp-nprd-dev-guardduty-s3 \
  --template-body file://cf-s3malwareprotection.yaml \
  --parameters file://env/parameters-s3malwareprotection.yaml \
  --capabilities CAPABILITY_NAMED_IAM \
  --role-arn arn:aws:iam::YOUR_ACCOUNT_ID:role/YOUR_DEPLOYMENT_ROLE

# Delete stack
aws cloudformation delete-stack \
  --stack-name myapp-nprd-dev-guardduty-s3 \
  --role-arn arn:aws:iam::YOUR_ACCOUNT_ID:role/YOUR_DEPLOYMENT_ROLE
```

### Deploying Multiple S3 Buckets in the Same Environment

The `BucketFunctionName` parameter enables deploying malware protection for multiple S3 buckets within the same environment without resource naming conflicts.

**Example: Multiple Bucket Deployments**

Deploy separate stacks for different buckets:

```bash
# Stack 1: Upload bucket
aws cloudformation create-stack \
  --stack-name myapp-nprd-dev-guardduty-uploads \
  --template-body file://cf-s3malwareprotection.yaml \
  --parameters file://env/parameters-uploads-bucket.yaml \
  --capabilities CAPABILITY_NAMED_IAM

# Stack 2: Documents bucket
aws cloudformation create-stack \
  --stack-name myapp-nprd-dev-guardduty-documents \
  --template-body file://cf-s3malwareprotection.yaml \
  --parameters file://env/parameters-documents-bucket.yaml \
  --capabilities CAPABILITY_NAMED_IAM

# Stack 3: Attachments bucket
aws cloudformation create-stack \
  --stack-name myapp-nprd-dev-guardduty-attachments \
  --template-body file://cf-s3malwareprotection.yaml \
  --parameters file://env/parameters-attachments-bucket.yaml \
  --capabilities CAPABILITY_NAMED_IAM
```

**Parameter file examples:**

`env/parameters-uploads-bucket.yaml`:
```yaml
AppShortName: "myapp"
EnvName: "nprd-dev"
BucketFunctionName: "uploads-bucket"
UploadBucketName: "myapp-nprd-dev-uploads"
CleanBucketName: "myapp-nprd-dev-uploads-clean"
# ... other parameters
```

`env/parameters-documents-bucket.yaml`:
```yaml
AppShortName: "myapp"
EnvName: "nprd-dev"
BucketFunctionName: "documents-bucket"
UploadBucketName: "myapp-nprd-dev-documents"
CleanBucketName: "myapp-nprd-dev-documents-clean"
# ... other parameters
```

**Resource Isolation:**

Each deployment creates independent resources:
- Separate Lambda functions: `myapp-nprd-dev-uploads-bucket-LambdaGuardduty`, `myapp-nprd-dev-documents-bucket-LambdaGuardduty`
- Separate IAM roles and policies
- Separate EventBridge rules for each bucket
- Independent CloudWatch log groups

**Benefits:**
- Independent scaling and configuration per bucket
- Isolated failure domains (one bucket's issues don't affect others)
- Fine-grained cost tracking per bucket
- Different processing logic or destinations per bucket type

## How It Works

### Scan Flow

1. **File Upload**: A file is uploaded to the `UploadBucketName` bucket
2. **GuardDuty Scan**: GuardDuty automatically scans the file for malware
3. **Event Trigger**: Upon scan completion, GuardDuty publishes an event to EventBridge
4. **Lambda Invocation**: EventBridge rule triggers the Lambda function
5. **Result Processing**: Lambda processes the scan result:
   - **NO_THREATS_FOUND**: File is copied to the clean bucket and deleted from source
   - **THREATS_FOUND**: File is copied to quarantine bucket (if configured) and deleted from source
   - **UNSUPPORTED/ACCESS_DENIED/FAILED**: File is deleted from source (logged for review)

### Scan Result Statuses

- **NO_THREATS_FOUND**: File is clean and safe to use
- **THREATS_FOUND**: Malware or threats detected in the file
- **UNSUPPORTED**: File type not supported for scanning
- **ACCESS_DENIED**: GuardDuty unable to access the file
- **FAILED**: Scan failed for other reasons

## Resources Created

| Resource Type | Resource Name | Description |
|--------------|---------------|-------------|
| IAM Managed Policy | `{AppShortName}-{EnvName}-{BucketFunctionName}-IAMS3MalwareBucketPolicy` | Policy for GuardDuty to scan and tag S3 objects |
| IAM Role | `{AppShortName}-{EnvName}-{BucketFunctionName}-IAMS3MalwareBucketRole` | Role assumed by GuardDuty for malware protection |
| GuardDuty Malware Protection Plan | `{AppShortName}-{EnvName}-{BucketFunctionName}-GuardDutyS3MalwareProtectionPlan` | Malware protection plan for the source bucket |
| EventBridge Rule | `{AppShortName}-{EnvName}-{BucketFunctionName}-GuardDutyCopyS3ObjectRule` | Triggers Lambda on scan completion |
| IAM Managed Policy | `{AppShortName}-{EnvName}-{BucketFunctionName}-IAMLambdaS3CopyObjectPolicy` | Policy for Lambda to copy/delete S3 objects |
| IAM Role | `{AppShortName}-{EnvName}-{BucketFunctionName}-IAMLambdaS3CopyObjectRole` | Role assumed by Lambda function |
| EC2 Security Group | `{AppShortName}-{EnvName}-{BucketFunctionName}-GuardDutyLambda-sg` | Security group for VPC-deployed Lambda function |
| Lambda Function | `{AppShortName}-{EnvName}-{BucketFunctionName}-LambdaGuardduty` | Processes scan results and moves files |
| CloudWatch Log Group | `/aws/lambda/{AppShortName}-{EnvName}-{BucketFunctionName}-LambdaGuardduty` | Stores Lambda execution logs |
| Lambda Permission | Auto-generated | Allows EventBridge to invoke Lambda |

## Lambda Function Details

### Creating the Lambda Deployment Package

The Lambda function code is located in `artifacts/lambda/index.py`. To create the deployment package:

**Using PowerShell (Windows):**
```powershell
cd artifacts/lambda
Compress-Archive -Path index.py -DestinationPath guardduty-s3malware-handler.zip -Force
```

**Using Bash (Linux/Mac):**
```bash
cd artifacts/lambda
zip guardduty-s3malware-handler.zip index.py
```

**Upload to S3:**
```bash
aws s3 cp artifacts/lambda/guardduty-s3malware-handler.zip s3://your-lambda-artifacts/
```

The zip file should be uploaded to the S3 bucket specified in the `LambdaS3bucket` parameter before deploying the CloudFormation template.

### Runtime and Configuration
- **Runtime**: Python 3.12 (configurable via `LambdaRuntime` parameter)
- **Handler**: index.lambda_handler (configurable via `LambdaHandler` parameter)
- **Memory**: 128 MB
- **Timeout**: 30 seconds
- **VPC Deployment**: Lambda is deployed inside VPC for enhanced security
- **Security Group**: Automatic security group with VPC CIDR and S3 endpoint access

### Environment Variables
- `DEST_BUCKET`: Destination bucket for clean files (set from `CleanBucketName`)
- `QUARANTINE_BUCKET`: Quarantine bucket for infected files (set from `MalwareQuarantineBucketName`)
- `DEST_PREFIX`: Prefix mapping for clean bucket (set from `CleanBucketPrefix`)
- `DEST_PREFIX2`: Secondary prefix for clean bucket (set from `CleanBucketPrefix2`)
- `QUARANTINE_PREFIX`: Prefix mapping for quarantine bucket (set from `MalwareQuarantineBucketPrefix`)
- `QUARANTINE_PREFIX2`: Secondary prefix for quarantine bucket (set from `MalwareQuarantineBucketPrefix2`)

### Lambda Code Flow
1. Extracts S3 object details from the EventBridge event
2. Retrieves the scan result status
3. Based on the status:
   - Clean files → Copy to destination bucket with prefix mapping (if configured), optionally to secondary prefix
   - Infected files → Copy to quarantine bucket with prefix mapping (if configured), optionally to secondary prefix, with tags
   - Other statuses → Log the event
4. Deletes the original file from the source bucket
5. Logs all operations to CloudWatch

### Prefix Mapping Logic
- If prefix mapping is configured, the Lambda function maps source prefixes to destination prefixes
- Supports wildcard (`*`) for default mapping
- Supports multiple mappings separated by commas
- If no mapping matches, files preserve their original key structure

## Resource Protection

The template includes `DeletionPolicy` and `UpdateReplacePolicy` settings that protect resources in production environments:

- **Production environments** (`EnvName` equals "prod", "prod-a", "prod-b", or "prod-c"):
  - Resources are retained even if the stack is deleted
  - Resources are retained during updates that require replacement
- **Non-production environments**:
  - Resources are deleted when the stack is deleted
  - Resources are deleted when replaced during updates

## Monitoring and Logging

### CloudWatch Logs
- Lambda function logs are stored in `/aws/lambda/{AppShortName}-{EnvName}-{BucketFunctionName}-LambdaGuardduty`
- Log retention: 30 days
- Logs include:
  - Received events from GuardDuty
  - File processing actions (copy, quarantine, delete)
  - Error messages for troubleshooting

### GuardDuty Console
- Monitor scan results in the GuardDuty console
- View malware protection findings
- Review tagged objects in S3

## Troubleshooting

### Common Issues

**GuardDuty Not Scanning Files**
- Verify GuardDuty is enabled in your account and region
- Check that the IAM role has correct permissions
- Ensure the bucket name matches exactly in the protection plan
- Review EventBridge rule to confirm it's set to "ENABLED"

**Lambda Function Not Triggering**
- Verify the EventBridge rule is active
- Check Lambda permissions allow EventBridge invocation
- Review CloudWatch Logs for Lambda function errors
- Ensure the source ARN in the Lambda permission matches the EventBridge rule

**Files Not Moving to Destination Bucket**
- Check S3 bucket policies allow Lambda to write
- Verify the Lambda IAM role has s3:PutObject permissions
- Review Lambda logs for copy errors
- Ensure destination bucket name is correct in parameters

**Access Denied Errors**
- Verify IAM policies grant necessary S3 permissions
- Check bucket policies don't explicitly deny access
- Ensure KMS permissions if buckets use encryption
- Review CloudTrail logs for detailed access denial information

**Quarantine Bucket Not Working**
- Confirm `MalwareQuarantineBucketName` parameter is not empty
- Verify the quarantine bucket exists
- Check Lambda IAM role has permissions for the quarantine bucket
- Review Lambda logs for quarantine operation errors

**Prefix Scope Not Working**
- Verify `ScanScope` is set to "PREFIXES"
- Ensure prefixes in `ScanScopePrefixList` end with `/` (e.g., "uploads/", not "uploads")
- Check that uploaded files match the specified prefixes
- Confirm prefixes are comma-separated without spaces: "uploads/,documents/"
- Review GuardDuty console to verify protection plan includes the correct prefixes

### Log Analysis

Check Lambda logs for specific events:

```bash
# View recent logs
aws logs tail /aws/lambda/{AppShortName}-{EnvName}-{BucketFunctionName}-LambdaGuardduty --follow

# Filter for errors
aws logs filter-log-events \
  --log-group-name /aws/lambda/{AppShortName}-{EnvName}-{BucketFunctionName}-LambdaGuardduty \
  --filter-pattern "ERROR"

# Filter for specific scan results
aws logs filter-log-events \
  --log-group-name /aws/lambda/{AppShortName}-{EnvName}-{BucketFunctionName}-LambdaGuardduty \
  --filter-pattern "THREATS_FOUND"
```

## Security Considerations

1. **IAM Permissions**: Follow the principle of least privilege - the template grants only necessary permissions
2. **Quarantine Bucket**: Use strict access controls on the quarantine bucket to prevent accidental access to infected files
3. **Encryption**: Consider enabling S3 bucket encryption and ensure Lambda has KMS permissions if needed
4. **Audit Logging**: Enable CloudTrail and S3 access logging for comprehensive audit trails
5. **Network Security**: Lambda runs within your VPC context based on EventBridge invocation
6. **Resource Tagging**: All resources are tagged with `IacVersion: InfraPlatform-GuardDutyS3-V1` for tracking

## Cost Considerations

- **GuardDuty Scanning**: Charged per GB of data scanned
  - Use `ScanScope: PREFIXES` to scan only specific folders and reduce costs
  - Example: Only scan "uploads/" and "attachments/" instead of entire bucket
- **Lambda Invocations**: Charged per invocation and execution time
- **S3 Operations**: Charged for GET, PUT, and DELETE operations
- **CloudWatch Logs**: Charged for log ingestion and storage
- **EventBridge**: Minimal cost for event delivery

Monitor your AWS Cost Explorer for detailed cost breakdown by service.

### Cost Optimization Tips

1. **Use Prefix Scoping**: If only certain folders contain user-uploaded files, use `ScanScope: PREFIXES` to reduce scanning costs
2. **Adjust Log Retention**: Default is 30 days - adjust based on compliance requirements
3. **Monitor Scan Volume**: Track GuardDuty scanning costs in Cost Explorer to identify optimization opportunities

## Version History

- **v1.1**: Initial release with GuardDuty S3 malware protection
  - Automated file processing based on scan results
  - Optional quarantine bucket support
  - CloudWatch logging integration
  - Production resource retention policies
  - Lambda code deployed from S3 for better version control
  - Parameterized Lambda runtime and handler for easy upgrades
  - Configurable scan scope (ALL or specific PREFIXES) for cost optimization
