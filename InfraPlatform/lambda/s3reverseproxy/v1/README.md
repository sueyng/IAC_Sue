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