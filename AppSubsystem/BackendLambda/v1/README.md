# AWS Lambda API Infrastructure

This repository contains AWS CloudFormation templates for deploying a serverless API infrastructure using AWS Lambda, API Gateway, and related services.

## Architecture Overview

The infrastructure is organized as a set of nested CloudFormation stacks:

```
Infrastructure Stack (cf-lambda-api-infra-main.yaml)
├── Network & IAM Stack (cf-lambda-network-iamrole.yaml)
├── Lambda Authorizer Stack (cf-lambda-api-authorizer.yaml)
└── API Gateway Stack (cf-lambda-api-gateway.yaml)

Lambda Applications Stack (cf-lambda-api-apps-main.yaml)
└── Individual Lambda Functions (cf-lambda-api-app.yaml)
```

### Key Components

1. **Base Infrastructure**
   - VPC Configuration
   - Security Groups
   - IAM Roles and Policies
   - Lambda Authorizer
   - API Gateway with Private Endpoints
   - Custom Domain Configuration

2. **Lambda Applications**
   - Support for up to 20 Lambda functions
   - Standardized configuration
   - Individual function deployment control
   - API Gateway integration
   - Configurable timezone settings per Lambda function

3. **Security**
   - Azure AD integration
   - Custom Lambda authorizer
   - VPC isolation
   - Private API Gateway endpoints

## Prerequisites

- AWS CLI configured with appropriate permissions
- S3 bucket for storing Lambda deployment packages and CloudFormation templates
- VPC and subnets configured
- SSL certificate in AWS Certificate Manager (for custom domain)
- Azure AD configuration (if using Azure AD authentication)

## File Structure

```
BackendLambda/
└── v1/
    ├── env/
    │   ├── parameters-lambda-api-apps-main.json
    │   ├── parameters-lambda-api-infra-main.json
    │   └── swagger-1.0.json
    ├── cf-lambda-api-app.yaml
    ├── cf-lambda-api-apps-main.yaml
    ├── cf-lambda-api-authorizer.yaml
    ├── cf-lambda-api-gateway.yaml
    ├── cf-lambda-api-infra-main.yaml
    ├── cf-lambda-network-iamrole.yaml
    └── README.md
```

## Deployment Process

The deployment process is managed through Azure DevOps pipelines. CloudFormation templates are stored in the SEED innersource repository and referenced by individual project repositories.

### Repository Structure

1. **SEED Innersource Repository**
   ```
   BackendLambda/
   └── v1/
       ├── env/
       │   ├── parameters-lambda-api-apps-main.json
       │   ├── parameters-lambda-api-infra-main.json
       │   └── swagger-1.0.json
       ├── cf-lambda-api-app.yaml
       ├── cf-lambda-api-apps-main.yaml
       ├── cf-lambda-api-authorizer.yaml
       ├── cf-lambda-api-gateway.yaml
       ├── cf-lambda-api-infra-main.yaml
       ├── cf-lambda-network-iamrole.yaml
       └── README.md
   ```

2. **Project Repository (Sample)**
   ```
   Project-A/
   └── Infrastructure/
       └── Lambda/
           └── env/
               ├── dev/
               │   ├── parameters-lambda-api-infra-main.json
               │   └── parameters-lambda-api-apps-main.json
               ├── sit/
               │   ├── parameters-lambda-api-infra-main.json
               │   └── parameters-lambda-api-apps-main.json
               └── prod/
                   ├── parameters-lambda-api-infra-main.json
                   └── parameters-lambda-api-apps-main.json
   ```

### Deployment Workflow

1. **Infrastructure Deployment**
   - Project team updates infrastructure parameters in `parameters-lambda-api-infra-main.json`
   - Create release in Azure DevOps pipeline
   - Pipeline references master templates from SEED innersource repo
   - Deploys core infrastructure including:
     - Security groups and IAM roles
     - Lambda authorizer
     - API Gateway configuration
     - Required SSM parameters

2. **Lambda Applications Deployment**
   - Project team updates Lambda parameters in `parameters-lambda-api-apps-main.json`
   - Create release in Azure DevOps pipeline
   - Pipeline deploys Lambda functions using master templates
   - Each function can be deployed independently through its parameter configuration

### Parameter File Management

1. **Parameter File Location**
   - Parameter files are maintained in the project repository
   - Separate parameter files for each environment (dev, sit, prod)
   - Templates are referenced from SEED innersource repository

2. **Parameter Update Process**
   - Project team updates relevant parameter files
   - Commit changes to project repository
   - Create new release in Azure DevOps
   - Select target environment for deployment
   - Pipeline automatically uses corresponding parameter files

## Parameter Reference

### Infrastructure Stack Parameters (parameters-lambda-api-infra-main.json)

#### Common Parameters
| Parameter Name | Type | Default | Mandatory | Sample Value | Description |
|---------------|------|----------|-----------|--------------|-------------|
| AppShortName | String | healthb | Yes | healthb | Application short name |
| EnvName | String | nprd | Yes | nprd-dev | Environment name (nprd/prod variants) |
| LambdaS3bucket | String | health-nprd-cftemplates | Yes | health-nprd-cftemplates | S3 bucket for Lambda code |
| LogRetentionInDays | Number | 14 | No | 14 | Log retention period in days |

#### Network Configuration
| Parameter Name | Type | Default | Mandatory | Sample Value | Description |
|---------------|------|----------|-----------|--------------|-------------|
| VpcId | String | - | Yes | vpc-02fb2e32bbb6ff24e | VPC ID for deployment |
| SubnetIds | List | - | Yes | subnet-0fe7a1d34484c75cf,subnet-0610b1fee398eb38b | Private subnet IDs |
| SecurityGroupName | String | - | Yes | healthbuddy-nprd-lambda-securitygroup | Security group name |

#### API Gateway Configuration
| Parameter Name | Type | Default | Mandatory | Sample Value | Description |
|---------------|------|----------|-----------|--------------|-------------|
| CustomDomainName | String | healthbapi.seedideation.com | Yes | healthbapi.seedideation.com | API custom domain name |
| SSLCertificateArn | String | - | Yes | arn:aws:acm:ap-southeast-1:961341547198:certificate/fd6c2b82-e1ab-4ab0-a607-054fddd8a86a | SSL certificate ARN |
| SwaggerFile | String | - | Yes | parent-child-stacks/swagger.json | API Swagger definition file |

#### Azure AD Configuration
| Parameter Name | Type | Default | Mandatory | Sample Value | Description |
|---------------|------|----------|-----------|--------------|-------------|
| AzureAdClientId | String | - | No | 12345678-1234-1234-1234-123456789012 | Azure AD Client ID |
| AzureAdTenantId | String | - | No | 12345678-1234-1234-1234-123456789012 | Azure AD Tenant ID |

### Lambda Applications Parameters (parameters-lambda-api-apps-main.json)

#### Basic Configuration
| Parameter Name | Type | Default | Mandatory | Sample Value | Description |
|---------------|------|----------|-----------|--------------|-------------|
| NumberOfLambdaFunctions | Number | 1 | Yes | 1 | Number of Lambda functions to deploy |
| CodeZipFileName | String | - | Yes | parent-child-stacks/HealthBuddy.Admission.SubmitPayment-1.0.0.4.zip | Lambda function code zip file |

#### Lambda Function Configuration (per function)
| Parameter Name | Type | Default | Mandatory | Sample Value | Description |
|---------------|------|----------|-----------|--------------|-------------|
| Lambda{N}FunctionName | String | - | Yes | HealthBuddyAdmissionSubmitPayment | Function name |
| Lambda{N}Runtime | String | dotnet8 | Yes | dotnet8 | Runtime environment |
| Lambda{N}Handler | String | - | Yes | HealthBuddy.Admission.SubmitPayment::HealthBuddy.Admission.SubmitPayment.Function::FunctionHandler | Function handler |
| Lambda{N}MemorySize | Number | 1024 | No | 1024 | Memory allocation in MB |
| Lambda{N}Timeout | Number | 25 | No | 25 | Function timeout in seconds |
| Lambda{N}ApiResourcePath | String | - | Yes | admissions/submit-payment | API resource path |
| Lambda{N}ApiHttpMethod | String | POST | Yes | POST | HTTP method |
| Lambda{N}TimeZone | String | Asia/Singapore | No | Asia/Singapore | Timezone for Lambda function |

Note: Replace {N} with the function number (1-20)

## Template Details

### cf-lambda-api-infra-main.yaml
- Main infrastructure orchestration template
- Manages child stacks for networking, security, and API Gateway
- Handles environment-specific configurations

#### Resource Naming Pattern
| Resource Type | Resource Name Pattern |
|--------------|----------------------|
| CloudFormation Stack | `NetworkAndIAMStack` |
| CloudFormation Stack | `LambdaAuthorizerStack` |
| CloudFormation Stack | `ApiGatewayStack` |

### cf-lambda-network-iamrole.yaml
- Creates Lambda execution role with necessary permissions
- Sets up security groups for Lambda functions
- Manages SSM parameters for role and security group IDs

#### Resource Naming Pattern
| Resource Type | Resource Name Pattern |
|--------------|----------------------|
| IAM Role | `{LambdaRoleName}` |
| IAM Policy | `${LambdaRoleName}-policy` |
| Security Group | `{SecurityGroupName}` |
| SSM Parameter | `/lambda/{AppShortName}/{EnvName}/execution-role-arn` |
| SSM Parameter | `/lambda/{AppShortName}/{EnvName}/security-group-id` |

### cf-lambda-api-authorizer.yaml
- Implements Lambda authorizer for API Gateway
- Configures Azure AD integration
- Sets up necessary IAM permissions

#### Resource Naming Pattern
| Resource Type | Resource Name Pattern |
|--------------|----------------------|
| Lambda Function | `{AppShortName}-{EnvName}-LambdaAuthorizer` |
| Log Group | `/aws/lambda/{AppShortName}-{EnvName}-LambdaAuthorizer` |
| IAM Role | `{AppShortName}-{EnvName}-lambda-authorizer-role` |
| IAM Policy | `{AppShortName}-{EnvName}-LambdaAuthorizerExecutionPolicy` |

### cf-lambda-api-gateway.yaml
- Creates private API Gateway
- Manages custom domain configuration
- Integrates with Lambda authorizer
- Handles VPC endpoint integration

#### Resource Naming Pattern
| Resource Type | Resource Name Pattern |
|--------------|----------------------|
| API Gateway | `{APIName}` |
| Domain Name | `{CustomDomainName}` |
| API Gateway Authorizer | `LambdaAuthorizer` |
| SSM Parameter | `/lambda/{AppShortName}/{EnvName}/apigw_id` |

### cf-lambda-api-apps-main.yaml
- Manages deployment of multiple Lambda functions
- Uses conditions to control function deployment
- Standardizes function configuration
- Passes individual timezone settings to each Lambda function

#### Resource Naming Pattern
| Resource Type | Resource Name Pattern |
|--------------|----------------------|
| CloudFormation Stack | `LambdaApp{N}` (where N is 1-20) |

### cf-lambda-api-app.yaml
- Individual Lambda function template
- Configures function settings
- Sets up CloudWatch logging
- Manages API Gateway permissions
- Configures timezone environment variable (TZ)

#### Resource Naming Pattern
| Resource Type | Resource Name Pattern |
|--------------|----------------------|
| Lambda Function | `{LambdaFunctionName}` |
| Log Group | `/aws/lambda/{LambdaFunctionName}` |
| Lambda Permission | `APIGatewayInvokeLambdaPermission` |

### Variable Definitions
- `{AppShortName}`: Application short name (lowercase)
- `{EnvName}`: Environment name (e.g., prod, nprd, nprd-dev, etc.)
- `{LambdaRoleName}`: Name of the Lambda execution role
- `{SecurityGroupName}`: Name for the security group
- `{APIName}`: Name of the API Gateway
- `{CustomDomainName}`: Custom domain name for API Gateway
- `{LambdaFunctionName}`: Name of the Lambda function

## Swagger Configuration

The `swagger-1.0.json` file defines the API structure including:
- Endpoints and methods
- Security definitions
- CORS configuration
- Integration settings

## Environment Support

The infrastructure supports multiple environments:
- Non-production (nprd, nprd-dev, nprd-sit, etc.)
- Production (prod, prod-a, prod-b)

## Security Considerations

1. Network Security
   - VPC isolation
   - Private API Gateway endpoints
   - Security group controls

2. Authentication/Authorization
   - Lambda authorizer integration
   - Azure AD support
   - API key option

3. Access Control
   - IAM roles and policies
   - Resource-based policies
   - Least privilege principle

## Monitoring and Logging

- CloudWatch Logs integration
- X-Ray tracing enabled
- Custom metrics support
- Log retention configuration

## Maintenance

1. Updating Lambda Functions
   - Upload new code to S3
   - Update parameter file version
   - Deploy stack update

2. API Changes
   - Update Swagger definition
   - Deploy API Gateway stack
   - Update Lambda integrations

3. Security Updates
   - Regular role and policy review
   - Security group rule maintenance
   - Authorization configuration updates

4. Timezone Configuration Updates
   - Update the appropriate Lambda{N}TimeZone parameter
   - Deploy the Lambda applications stack

## Troubleshooting

Common issues and solutions:

1. Deployment Failures
   - Check CloudFormation events
   - Verify parameter values
   - Ensure S3 artifacts exist

2. API Gateway Issues
   - Verify VPC endpoint configuration
   - Check Lambda authorizer logs
   - Validate custom domain setup

3. Lambda Function Problems
   - Check CloudWatch logs
   - Verify VPC connectivity
   - Validate IAM permissions
   
4. Timezone Issues
   - Verify the correct Lambda{N}TimeZone parameter is set
   - Check that the timezone value is a valid IANA timezone name
   - Confirm the TZ environment variable is properly set in Lambda configuration