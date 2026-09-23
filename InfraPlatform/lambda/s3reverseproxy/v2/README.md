# Lambda S3 Reverse Proxy CloudFormation Template

This CloudFormation template creates a Lambda function that serves as a reverse proxy to access content from multiple S3 buckets based on API Gateway mappings. The template follows the `AppShortName-EnvName` naming pattern for resources.

## Overview

The Lambda S3 Reverse Proxy solution allows you to:

- Serve content from multiple S3 buckets through a single Lambda function
- Map different API Gateway endpoints to different S3 buckets
- Maintain consistent access patterns across multiple environments
- Leverage AWS Lambda for dynamic routing and content serving
- Deploy the Lambda function within a VPC with secure networking configuration

The solution consists of:
- Lambda function that routes requests to appropriate S3 buckets
- IAM role with permissions to access S3 buckets and CloudWatch logs
- Security group with granular inbound access control
- API Gateway integration (configured separately)
- S3 buckets containing frontend content (created separately)

## Prerequisites

Before deploying this template, ensure you have:

1. IAM deployment role configured with appropriate permissions
2. S3 bucket containing the Lambda deployment package
3. Lambda code zip file uploaded to the S3 bucket
4. API Gateway IDs (if API Gateways are already created)
5. Target S3 buckets for storing frontend content (follow the naming pattern `{AppShortName}-{EnvName}-*`)
6. VPC and subnets where the Lambda function will be deployed
7. CIDR blocks for the subnets that need to access the Lambda function

## Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| AppShortName | Short name for the application | "myapp" |
| EnvName | Environment name | "nprd-dev", "prod" |
| LambdaS3bucket | S3 bucket where Lambda code is stored | "my-lambda-code-bucket" |
| CodeZipFileName | Zip file name for Lambda function code | "s3ReverseProxy-v1.zip" |
| LambdaRuntime | Runtime for Lambda | "nodejs20.x" |
| LambdaHandler | Handler for Lambda function | "index.handler" |
| APIGatewayToS3BucketMapping | Mapping of API Gateway IDs to S3 bucket names | "abcd1234:myapp-nprd-dev-bucket-1, efgh5678:myapp-nprd-dev-bucket-2" |
| LogRetentionInDays | Number of days for Log Retention | 14 |
| VpcId | ID of the VPC where the Lambda will be deployed | "vpc-09528f37a12368b13" |
| SubnetIds | List of subnet IDs where Lambda will be deployed | "subnet-abc123,subnet-def456" |
| VPCSubnetCidrAZ1 | CIDR block for the first subnet (AZ1) | "10.53.144.128/26" |
| VPCSubnetCidrAZ2 | CIDR block for the second subnet (AZ2) | "10.53.144.192/26" |
| VPCSubnetCidrAZ3 | CIDR block for the third subnet (AZ3) | "10.53.144.0/26" or "" if not needed |

### Important Note on APIGatewayToS3BucketMapping Parameter

The `APIGatewayToS3BucketMapping` parameter requires a specific format as a comma-separated list of API Gateway ID to S3 bucket mappings:

```
"abcd1234:myapp-nprd-dev-bucket-1, efgh5678:myapp-nprd-dev-bucket-2"
```

Each mapping consists of an API Gateway ID, followed by a colon, followed by the S3 bucket name. Multiple mappings are separated by commas.

### VPC and Security Group Configuration

The Lambda function is deployed within a VPC with a security group that has:
- Inbound rules allowing HTTPS (port 443) traffic from specified subnet CIDR blocks
- Outbound rules allowing all traffic to any destination (0.0.0.0/0)

Up to three subnet CIDR blocks can be specified for inbound rules, allowing fine-grained access control. Leave the CIDR parameter empty if fewer than three are needed.

## Deployment

### Parameter File

Create a parameters json file with your configuration:

```json
[
    {
        "ParameterKey": "AppShortName",
        "ParameterValue": "myapp"
    },
    {
        "ParameterKey": "EnvName",
        "ParameterValue": "nprd-dev"
    },
    {
        "ParameterKey": "LambdaS3bucket",
        "ParameterValue": "my-lambda-code-bucket"
    },
    {
        "ParameterKey": "CodeZipFileName",
        "ParameterValue": "s3ReverseProxy-v1.zip"
    },
    {
        "ParameterKey": "LambdaRuntime",
        "ParameterValue": "nodejs20.x"
    },
    {
        "ParameterKey": "LambdaHandler",
        "ParameterValue": "index.handler"
    },
    {
        "ParameterKey": "APIGatewayToS3BucketMapping",
        "ParameterValue": "abcd1234:myapp-nprd-dev-bucket-1, efgh5678:myapp-nprd-dev-bucket-2"
    },
    {
        "ParameterKey": "LogRetentionInDays",
        "ParameterValue": "14"
    },
    {
        "ParameterKey": "VpcId",
        "ParameterValue": "vpc-09528f37a12368b13"
    },
    {
        "ParameterKey": "SubnetIds",
        "ParameterValue": "subnet-abcdef1234567890,subnet-0987654321fedcba"
    },
    {
        "ParameterKey": "VPCSubnetCidrAZ1",
        "ParameterValue": "10.53.144.128/26"
    },
    {
        "ParameterKey": "VPCSubnetCidrAZ2",
        "ParameterValue": "10.53.144.192/26"
    },
    {
        "ParameterKey": "VPCSubnetCidrAZ3",
        "ParameterValue": ""
    }
]
```

## Lambda Environment Variables

The Lambda function receives the API Gateway to S3 bucket mapping via the `API_TO_S3_BUCKET_MAP` environment variable, which is set based on the `APIGatewayToS3BucketMapping` parameter. The Lambda code parses this string format to create the mapping between API Gateway IDs and S3 buckets.

## Resource Protection

The template includes `DeletionPolicy` and `UpdateReplacePolicy` settings that protect resources in production environments:

- In production (`EnvName` equals "prod", "prod-a", or "prod-b"), resources are retained even if the stack is deleted or resources are replaced during an update
- In non-production environments, resources are deleted when the stack is deleted or when resources are replaced during an update

## Troubleshooting

- **API Gateway Mapping Issues**: Ensure the API Gateway IDs in the mapping match your actual API Gateway IDs
- **S3 Bucket Access**: Verify that bucket names follow the `{AppShortName}-{EnvName}-*` pattern
- **Lambda Errors**: Check CloudWatch Logs at `/aws/lambda/{AppShortName}-{EnvName}-s3ReverseProxy`
- **Format Errors**: If you encounter errors related to the `API_TO_S3_BUCKET_MAP` environment variable, check your `APIGatewayToS3BucketMapping` parameter for proper formatting - it should be a comma-separated list of colon-separated key-value pairs
- **VPC Connectivity Issues**: Ensure the Lambda function has access to both the S3 service and API Gateway through VPC endpoints or NAT gateways
- **Security Group Rules**: Verify the CIDR blocks specified match the actual subnet CIDRs that need to access the Lambda function

---

# v2 Implementation (Current Template)

## Overview - v2

The v2 implementation is a **simplified standalone version** designed for ease of deployment without VPC configuration. This version is compatible with FrontendSPA-Intranet v5 as a nested stack.

### Key Differences from v1

| Feature | v1 | v2 (Current) |
|---------|-------|--------------|
| VPC Deployment | Required | Not Required |
| S3 Bucket Configuration | Multiple buckets via mapping | Single bucket |
| Parameters | 13 parameters | 8 parameters |
| Security Groups | Custom security group with ingress rules | Not applicable |
| Environment Variable | API_TO_S3_BUCKET_MAP | S3_BUCKET_NAME |
| Deployment Complexity | Advanced (VPC-based) | Simple (Standalone) |

## v2 Parameters

| Parameter | Description | Example | Default |
|-----------|-------------|---------|---------|
| AppShortName | Short name for the application | "myapp" | - |
| EnvName | Environment name | "nprd-dev", "prod", "prod-a", "prod-b", "prod-c" | - |
| LambdaS3bucket | S3 bucket where Lambda code is stored | "my-lambda-code-bucket" | - |
| CodeZipFileName | Zip file name for Lambda function code | "s3reverseproxy.zip" | - |
| LambdaRuntime | Runtime for Lambda | "nodejs20.x" | nodejs20.x |
| LambdaHandler | Handler for Lambda function | "index.handler" | index.handler |
| **FrontendSPABucketName** | S3 bucket name for frontend assets | "myapp-nprd-dev-frontendspa-bucket" | - |
| LogRetentionInDays | Number of days for Log Retention | 14 | 14 |

### v2 Important Notes

- **FrontendSPABucketName**: This is the S3 bucket that contains your frontend application assets. The bucket must exist before deploying this template.
- **No VPC Configuration**: Lambda is deployed outside of VPC for simplified setup and direct S3 access.
- **Automatic S3 Bucket Policy**: The template automatically creates a bucket policy with security constraints (TLS 1.2+, SSL only).

## v2 Deployment

### v2 Parameter File

Create a parameters json file (`env/parameters-s3reverseproxy.json`):

```json
[
    {
        "ParameterKey": "AppShortName",
        "ParameterValue": "myapp"
    },
    {
        "ParameterKey": "EnvName",
        "ParameterValue": "nprd-dev"
    },
    {
        "ParameterKey": "LambdaS3bucket",
        "ParameterValue": "my-lambda-code-bucket"
    },
    {
        "ParameterKey": "CodeZipFileName",
        "ParameterValue": "s3reverseproxy.zip"
    },
    {
        "ParameterKey": "LambdaRuntime",
        "ParameterValue": "nodejs20.x"
    },
    {
        "ParameterKey": "LambdaHandler",
        "ParameterValue": "index.handler"
    },
    {
        "ParameterKey": "FrontendSPABucketName",
        "ParameterValue": "myapp-nprd-dev-frontendspa-bucket"
    },
    {
        "ParameterKey": "LogRetentionInDays",
        "ParameterValue": "14"
    }
]
```

### Deploy v2 Stack

```bash
aws cloudformation create-stack \
  --stack-name myapp-nprd-dev-s3reverseproxy \
  --template-body file://cf-lambda-s3reverseproxy.yaml \
  --parameters file://env/parameters-s3reverseproxy.json \
  --capabilities CAPABILITY_NAMED_IAM \
  --region ap-southeast-1
```

## v2 Resources Created

The v2 template creates the following AWS resources:

1. **S3BucketPolicy**: Bucket policy with security constraints
   - Allows Lambda execution role to perform s3:GetObject and s3:PutObject
   - Enforces TLS 1.2 or higher
   - Requires SSL/TLS for all requests

2. **LambdaLogGroup**: CloudWatch Log Group with configurable retention

3. **LambdaS3ReverseProxy**: Lambda function that serves content from S3
   - X-Ray tracing enabled
   - Tagged with IaCVersion: "InfraPlatform-lambda-s3reverseproxy-v2"

4. **LambdaExecutionRole**: IAM role with policies for CloudWatch Logs and S3 access

5. **APIGatewayInvokeLambdaPolicy**: Permission allowing API Gateway to invoke Lambda

6. **ParameterLambdaArn**: SSM Parameter storing Lambda function ARN
   - Parameter Name: `/{AppShortName}/{EnvName}/Lambda-s3ReverseProxy-Arn`
   - Tagged with IaCVersion: "InfraPlatform-lambda-s3reverseproxy-v2"

## v2 Lambda Environment Variables

The Lambda function receives the S3 bucket name via the `S3_BUCKET_NAME` environment variable.

## v2 Integration with FrontendSPA-Intranet

This v2 template is designed to be used standalone or as a nested stack within FrontendSPA-Intranet v5. The parent stack deploys:
1. Lambda S3 Reverse Proxy (this template)
2. Private API Gateway
3. ALB routing to API Gateway VPC Endpoint

## v2 Troubleshooting

- **S3 Bucket Not Found**: Ensure `FrontendSPABucketName` exists before deployment
- **S3 Bucket Access Denied**: Verify the bucket policy (automatically created)
- **Lambda Errors**: Check CloudWatch Logs at `/aws/lambda/{AppShortName}-{EnvName}-s3ReverseProxy`
- **Stack Creation Fails**: Verify all parameters and that Lambda code bucket exists

## v2 Prerequisites

1. IAM deployment role with appropriate permissions
2. S3 bucket containing Lambda deployment package
3. Lambda code zip file uploaded to S3
4. Target S3 bucket for frontend content (must exist)
5. API Gateway (if integration needed, configured separately)