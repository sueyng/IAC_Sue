# Release Notes: GuardDuty S3 Malware Protection Templates

## Version 2 (Latest)

### Release Date
April 2026

### New Features

#### BucketFunctionName Parameter for Multi-Bucket Support
- **New Parameter**: `BucketFunctionName` - Unique identifier for differentiating multiple S3 malware protection deployments in the same environment
- **Resource Naming**: Enables deploying malware protection for multiple S3 buckets within the same environment without naming conflicts
- **Format**: String identifier (e.g., "uploads-bucket", "documents-bucket", "user-files")
- **Usage**: All resources (IAM roles, policies, Lambda function, EventBridge rules, security groups) are named using `${AppShortName}-${EnvName}-${BucketFunctionName}` pattern
- **Benefits**:
  - Support multiple S3 buckets with independent malware protection in the same environment
  - Clear identification and separation of resources per bucket
  - No conflicts when deploying multiple stacks
  - Improved resource management and tracking

#### AWS X-Ray Tracing Support
- **New Parameter**: `EnableXRayTracing` - Enable/disable AWS X-Ray distributed tracing (default: 'true')
- **TracingConfig**: Lambda function configured with Active or PassThrough mode based on parameter
- **IAM Policy**: Automatic inclusion of `AWSXRayDaemonWriteAccess` managed policy when tracing is enabled
- **Benefits**:
  - Visualize Lambda execution flow and identify performance bottlenecks
  - Track distributed requests across S3, Lambda, and GuardDuty
  - Quickly identify and debug errors in the malware processing workflow
  - Generate service maps showing dependencies and call patterns
  - No Lambda code changes required

#### Lambda Memory Size and Timeout Configuration
- **New Parameter**: `LambdaMemorySize` - Configure Lambda memory in MB (128, 256, 512, 1024, 2048, 3008; default: 128)
- **New Parameter**: `LambdaTimeout` - Configure Lambda timeout in seconds (1–900; default: 30)
- Allows tuning Lambda performance and cost per environment without template modifications

#### Custom Environment Variables Support
- **7 Custom Environment Variables**: Added support for up to 7 custom environment variables for the Lambda function
- **New Parameters** (16 total):
  - `CustomEnvVar1Name` to `CustomEnvVar7Name` - Document the purpose/name of each variable
  - `CustomEnvVar1Value` to `CustomEnvVar7Value` - Store the actual values
- **Lambda Environment Variables**: Variables are exposed as `CUSTOM_ENV_VAR_1` through `CUSTOM_ENV_VAR_7`
- **Flexible Configuration**: All custom variables are optional and conditionally included only when values are provided
- **Use Cases**:
  - API keys and credentials
  - Database connection strings
  - Feature flags and configuration settings
  - Log levels and timeout values
  - External service endpoints
  - Custom business logic parameters

#### Selective Scanning Capability
- **New Parameter**: `ScanScope` - Choose between "ALL" (entire bucket) or "PREFIXES" (specific folders)
- **New Parameter**: `ScanScopePrefixList` - Comma-separated list of S3 prefixes to scan when using PREFIXES mode
- **Cost Optimization**: Scan only critical folders instead of entire bucket (e.g., "uploads/,documents/")
- **Flexibility**: Reduces scanning costs by limiting scope to sensitive areas

#### Advanced Prefix Mapping
- **New Parameter**: `CleanBucketPrefix` - Map source prefixes to destination prefixes for clean files
  - Format: `source-prefix>dest-prefix,source-prefix>dest-prefix`
  - Example: `uploads/>scanned/,documents/>reviewed/,*>other/`
  - Single prefix mode: `scanned/` (all files to one prefix)
  - Default mapping: `*>default/` (wildcard for unmatched sources)
- **New Parameter**: `CleanBucketPrefix2` - Secondary prefix for dual-copy capability
  - Enables redundancy or multi-location archiving
  - Useful for compliance or backup requirements
- **New Parameter**: `MalwareQuarantineBucketPrefix` - Map source prefixes for quarantined files
- **New Parameter**: `MalwareQuarantineBucketPrefix2` - Secondary quarantine prefix for dual-copy

#### VPC Deployment and Enhanced Security
- **Lambda VPC Deployment**: Lambda now runs inside VPC for enhanced security
- **New Parameter**: `VpcId` - VPC where Lambda will be deployed
- **New Parameter**: `AppSubnetIds` - List of 2-4 private app subnets (minimum 2 for HA)
- **New Parameter**: `VpcCidr1` - Primary VPC CIDR block (required)
- **New Parameters**: `VpcCidr2-5` - Additional VPC CIDR blocks for multi-VPC scenarios (optional)
  - Support for up to 5 VPC CIDR ranges
  - Enables VPC peering, hybrid connectivity, and cross-region networking
- **New Parameter**: `S3PrefixListId` - S3 VPC Endpoint Prefix List ID for secure S3 access
  - Enables S3 access without NAT Gateway
  - Reduces data transfer costs

#### New Security Group
- **Resource**: `{AppShortName}-{EnvName}-GuardDutyLambda-sg` - Security group for Lambda function
- **Egress Rules**:
  - VPC CIDRs for internal communication (port 443)
  - S3 Prefix List for secure S3 access (HTTPS - port 443)
- **Conditional Rules**: Automatically adapts based on configured VPC CIDRs

### Benefits
- **Distributed Tracing**: Monitor and debug Lambda execution with AWS X-Ray
- **No Template Modifications**: Users can add custom configuration without editing the CloudFormation template
- **Documentation Built-in**: Name parameters provide self-documenting configuration
- **Environment-Specific Values**: Different values can be set per environment (dev, sit, uat, prod)
- **Lambda Code Portability**: Same Lambda code can be used across environments with different configurations
- **Cost Optimization**: Selective scanning and VPC endpoint integration reduce costs
- **Enhanced Security**: VPC deployment and security group controls

### Migration from v1 to v2

**Breaking Changes:**
- Parameter name change: `MalwareProtectedBucketName` → `UploadBucketName`
- New required parameter: `BucketFunctionName` - Unique identifier for resource naming
- Lambda now requires VPC configuration (new required parameters: `VpcId`, `AppSubnetIds`, `VpcCidr1`)

**Migration Steps:**
1. Update parameter files:
   - Rename `MalwareProtectedBucketName` to `UploadBucketName`
   - Add new `BucketFunctionName` parameter (e.g., "uploads-bucket", "user-files")
   - Add VPC configuration parameters (`VpcId`, `AppSubnetIds`, `VpcCidr1`)
   - Optionally add new parameters for selective scanning, prefix mapping, and X-Ray tracing
2. Ensure S3 VPC Endpoint is configured in your VPC
3. Update Lambda code if using prefix mapping features
4. Deploy v2 template (CloudFormation will replace Lambda function due to VPC changes)
5. Test thoroughly in non-production environment first

**Note on Resource Naming:**
- v1 resources: `{AppShortName}-{EnvName}-ResourceType`
- v2 resources: `{AppShortName}-{EnvName}-{BucketFunctionName}-ResourceType`
- All resources will be recreated with new names including BucketFunctionName

**Example Configuration for X-Ray:**
```json
{
    "ParameterKey": "EnableXRayTracing",
    "ParameterValue": "true"
}
```

**Example Configuration for Custom Variables:**
```json
{
    "ParameterKey": "CustomEnvVar1Name",
    "ParameterValue": "API_KEY"
},
{
    "ParameterKey": "CustomEnvVar1Value",
    "ParameterValue": "your-api-key-here"
},
{
    "ParameterKey": "CustomEnvVar2Name",
    "ParameterValue": "LOG_LEVEL"
},
{
    "ParameterKey": "CustomEnvVar2Value",
    "ParameterValue": "INFO"
}
```

---

## Version Comparison: v1 vs v2

### General Updates
- **IaC Version Tag**:
  - v1: `InfraPlatform-GuardDutyS3-V1`
  - v2: `InfraPlatform-GuardDutyS3-V2` (updated)

### Core Functionality (`cf-s3malwareprotection.yaml`)

#### v1 Features
- **Basic GuardDuty S3 Malware Protection**:
  - Enable malware scanning for an entire S3 bucket
  - Automated processing of scan results via EventBridge and Lambda
  - Clean files moved to destination bucket
  - Infected files quarantined to separate bucket (optional)
  - Lambda deployed without VPC (internet-facing)

- **Parameters**:
  - `MalwareProtectedBucketName`: Source S3 bucket for scanning
  - `MalwareCleanBucketName`: Destination bucket for clean files
  - `MalwareQuarantineBucketName`: Optional quarantine bucket for infected files
  - Basic Lambda configuration (S3 bucket, zip file, runtime, handler)
  - AppShortName and EnvName for resource naming

- **Resources Created**:
  - IAM policies and roles for GuardDuty and Lambda
  - GuardDuty Malware Protection Plan
  - EventBridge rule for scan completion events
  - Lambda function (non-VPC deployment)
  - CloudWatch Logs for Lambda
  - Lambda permission for EventBridge invocation

#### v2 Updates (Major Enhancements)

- **Parameter Renaming for Clarity**:
  - `MalwareProtectedBucketName` → `UploadBucketName` (better describes the source bucket's purpose)
  - `MalwareCleanBucketName` → `CleanBucketName` (simplified naming)
  - `MalwareCleanBucketPrefix` → `CleanBucketPrefix` (consistent with bucket name)
  - `MalwareCleanBucketPrefix2` → `CleanBucketPrefix2` (consistent with bucket name)

- **Selective Scanning Capability**:
  - **New Parameter**: `ScanScope` - Choose between "ALL" (entire bucket) or "PREFIXES" (specific folders)
  - **New Parameter**: `ScanScopePrefixList` - Comma-separated list of S3 prefixes to scan when using PREFIXES mode
  - **Cost Optimization**: Scan only critical folders instead of entire bucket (e.g., "uploads/,documents/")
  - **Flexibility**: Reduces scanning costs by limiting scope to sensitive areas

- **Advanced Prefix Mapping**:
  - **New Parameter**: `CleanBucketPrefix` - Map source prefixes to destination prefixes for clean files
    - Format: `source-prefix>dest-prefix,source-prefix>dest-prefix`
    - Example: `uploads/>scanned/,documents/>reviewed/,*>other/`
    - Single prefix mode: `scanned/` (all files to one prefix)
    - Default mapping: `*>default/` (wildcard for unmatched sources)
  - **New Parameter**: `CleanBucketPrefix2` - Secondary prefix for dual-copy capability
    - Enables redundancy or multi-location archiving
    - Useful for compliance or backup requirements
  - **New Parameter**: `MalwareQuarantineBucketPrefix` - Map source prefixes for quarantined files
    - Same flexible mapping as clean bucket prefix
    - Example: `uploads/>infected/uploads/,*>quarantine/`
  - **New Parameter**: `MalwareQuarantineBucketPrefix2` - Secondary quarantine prefix for dual-copy

- **VPC Deployment and Enhanced Security**:
  - **Lambda VPC Deployment**: Lambda now runs inside VPC for enhanced security
  - **New Parameter**: `VpcId` - VPC where Lambda will be deployed
  - **New Parameter**: `AppSubnetIds` - List of 2-4 private app subnets (minimum 2 for HA)
  - **New Parameter**: `VpcCidr1` - Primary VPC CIDR block (required)
  - **New Parameter**: `VpcCidr2-5` - Additional VPC CIDR blocks for multi-VPC scenarios (optional)
    - Support for up to 5 VPC CIDR ranges
    - Enables VPC peering, hybrid connectivity, and cross-region networking
  - **New Parameter**: `S3PrefixListId` - S3 VPC Endpoint Prefix List ID for secure S3 access
    - Enables S3 access without NAT Gateway
    - Reduces data transfer costs

- **New Security Group**:
  - **Resource**: `{AppShortName}-{EnvName}-SG-Lambda` - Security group for Lambda function
  - **Ingress Rules**: All VPC CIDRs (VpcCidr1-5) on all protocols
  - **Egress Rules**:
    - VPC CIDRs for internal communication
    - S3 Prefix List for secure S3 access (HTTPS - port 443)
  - **Conditional Rules**: Automatically adapts based on configured VPC CIDRs

- **Enhanced Lambda Configuration**:
  - **VPC Configuration**: Lambda deployed with VPC ID and subnet IDs
  - **Security Group**: Attached to Lambda for network security
  - **New Environment Variables**:
    - `DEST_PREFIX`: Prefix mapping for clean bucket
    - `DEST_PREFIX2`: Secondary prefix for clean bucket
    - `QUARANTINE_PREFIX`: Prefix mapping for quarantine bucket
    - `QUARANTINE_PREFIX2`: Secondary prefix for quarantine bucket
  - **Existing Variables**: `DEST_BUCKET`, `QUARANTINE_BUCKET`

- **Improved IAM Policies**:
  - Lambda policy includes VPC network interface management permissions
  - Enhanced S3 access controls for prefix-based operations
  - Support for cross-bucket operations with prefix mapping

### Key Features by Version

#### v1: Basic Malware Protection
- Full bucket scanning
- Simple clean/quarantine workflow
- Lambda without VPC
- Basic prefix preservation
- Suitable for simple use cases

#### v2: Enterprise-Grade Malware Protection
- Selective scanning (cost optimization)
- Advanced prefix mapping (flexible organization)
- Dual-copy capability (redundancy/compliance)
- VPC deployment (enhanced security)
- Multi-VPC support (complex networking)
- S3 VPC Endpoint integration (cost optimization)
- Suitable for complex enterprise requirements

### Migration from v1 to v2

**Breaking Changes:**
- Parameter name change: `MalwareProtectedBucketName` → `UploadBucketName`
- Lambda now requires VPC configuration (new required parameters: `VpcId`, `AppSubnetIds`, `VpcCidr1`)

**Migration Steps:**
1. Update parameter files:
   - Rename `MalwareProtectedBucketName` to `UploadBucketName`
   - Add VPC configuration parameters (`VpcId`, `AppSubnetIds`, `VpcCidr1`)
   - Optionally add new parameters for selective scanning and prefix mapping
2. Ensure S3 VPC Endpoint is configured in your VPC
3. Update Lambda code if using prefix mapping features
4. Deploy v2 template (CloudFormation will replace Lambda function due to VPC changes)
5. Test thoroughly in non-production environment first

**Backward Compatibility:**
- All new parameters have defaults or are optional except VPC configuration
- Core functionality remains the same (scan, clean, quarantine workflow)
- Resource naming convention unchanged (`AppShortName-EnvName` pattern)

### Use Cases by Version

**Use v1 if:**
- Simple malware scanning needs
- No VPC requirements
- Scanning entire buckets
- Basic file organization acceptable

**Use v2 if:**
- Need selective scanning for cost optimization
- Require VPC deployment for security compliance
- Need advanced prefix mapping for file organization
- Require dual-copy for redundancy or compliance
- Multi-VPC or hybrid cloud environment
- Enterprise-grade security and flexibility required

### Resource Count Comparison

**v1 Resources:** ~9 AWS resources
- 2 IAM Policies
- 2 IAM Roles
- 1 GuardDuty Malware Protection Plan
- 1 EventBridge Rule
- 1 Lambda Function (non-VPC)
- 1 CloudWatch Log Group
- 1 Lambda Permission

**v2 Resources:** ~10 AWS resources
- 2 IAM Policies (enhanced)
- 2 IAM Roles (enhanced)
- 1 GuardDuty Malware Protection Plan (enhanced with scope)
- 1 EventBridge Rule
- 1 Security Group (new)
- 1 Lambda Function (VPC-deployed, enhanced)
- 1 CloudWatch Log Group
- 1 Lambda Permission

### Version Recommendations

- **New Deployments**: Use v2.1 for all new deployments to leverage the latest features
  - Custom environment variables for flexible configuration
  - All v2 enterprise features (VPC deployment, selective scanning, prefix mapping)
  - Enhanced security and cost optimization
  
- **Existing v2 Deployments**: Upgrade to v2.1 if you need:
  - Custom environment variables for Lambda configuration
  - No breaking changes - seamless migration
  
- **Existing v1 Deployments**: Migrate to v2.1 if you need:
  - VPC security compliance
  - Cost optimization through selective scanning
  - Advanced file organization with prefix mapping
  - Multi-VPC connectivity
  - Custom environment variables
  
- **Production Migration**: Test thoroughly in non-production before migrating production workloads

### Version Summary

| Feature | v1 | v2 | v2.1 |
|---------|----|----|------|
| Basic Malware Scanning | ✓ | ✓ | ✓ |
| Clean/Quarantine Workflow | ✓ | ✓ | ✓ |
| VPC Deployment | ✗ | ✓ | ✓ |
| Selective Scanning (Cost Optimization) | ✗ | ✓ | ✓ |
| Advanced Prefix Mapping | ✗ | ✓ | ✓ |
| Dual-Copy Capability | ✗ | ✓ | ✓ |
| Multi-VPC Support | ✗ | ✓ | ✓ |
| S3 VPC Endpoint Integration | ✗ | ✓ | ✓ |
| Custom Environment Variables | ✗ | ✗ | ✓ (7 variables) |
| Lambda Configuration Flexibility | Basic | Enhanced | Maximum |

### Future Enhancements (Potential v3)
- Support for multiple source buckets
- Advanced tagging and metadata management
- Integration with AWS Security Hub
- Custom scan result notifications (SNS/SES)
- Enhanced logging with structured JSON format
- Support for Lambda Layers for custom dependencies
