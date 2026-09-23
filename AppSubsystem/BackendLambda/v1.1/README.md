# AWS Lambda API Infrastructure (v1.1)

This repository contains AWS CloudFormation templates for deploying a serverless API infrastructure using AWS Lambda, API Gateway, and related services.

## Version Changelog

| Version | Description |
|---------|-------------|
| v1 | Initial release — Security Group, IAM Role, API Gateway, Lambda Authorizer, up to 20 Lambda functions |
| v1.1 | **Security Group Egress Fix** — Replaced `0.0.0.0/0:1-65535` wide-open egress with CIDR-based rules for HTTPS (443), Database, S3/HCC VPC Endpoints, HCC Forward Proxy, ElastiCache Redis (6379-6380). IaCVersion tag: `AppSubsystem-BackendLambda-v1.1` |

## Architecture Overview

The infrastructure is organized as a set of nested CloudFormation stacks:

```
Infrastructure Stack (cf-lambda-api-infra-main.yaml)
├── Network & IAM Stack (cf-lambda-network-iamrole.yaml)
│   ├── Lambda Security Group (CIDR-based egress rules)
│   ├── Lambda Execution Role + Base Policy
│   └── SSM Parameters (role ARN, SG ID)
├── Lambda Authorizer Stack (cf-lambda-api-authorizer.yaml)
└── API Gateway Stack (cf-lambda-api-gateway.yaml)

Lambda Applications Stack (cf-lambda-api-apps-main.yaml)
└── Individual Lambda Functions (cf-lambda-api-app.yaml)
```

### Key Components

1. **Base Infrastructure**
   - VPC Configuration
   - Security Groups with CIDR-based egress rules (HTTPS, Database, S3, HCC, Forward Proxy, ElastiCache Redis)
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
   - CIDR-based security group egress (no `0.0.0.0/0` wide-open rules)

## Prerequisites

- AWS CLI configured with appropriate permissions
- S3 bucket for storing Lambda deployment packages and CloudFormation templates
- VPC and subnets configured
- SSL certificate in AWS Certificate Manager (for custom domain)
- Azure AD configuration (if using Azure AD authentication)

## File Structure

```
BackendLambda/
└── v1.1/
    ├── env/
    │   ├── parameters-lambda-api-apps-main.json
    │   ├── parameters-lambda-api-infra-main.json
    │   ├── parameters-lambda-api-infra-main.yaml   # NEW: YAML self-documenting format
    │   ├── parameters-lambda-auth.json
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
   └── v1.1/
       ├── env/
       │   ├── parameters-lambda-api-apps-main.json
       │   ├── parameters-lambda-api-infra-main.json
       │   ├── parameters-lambda-api-infra-main.yaml
       │   ├── parameters-lambda-auth.json
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

#### VPC CIDRs (v1.1 - Security Group Egress)
| Parameter Name | Type | Default | Mandatory | Sample Value | Description |
|---------------|------|----------|-----------|--------------|-------------|
| VpcCidr1 | String | "" | Yes | 10.55.53.0/24 | Primary VPC CIDR range |
| VpcCidr2 | String | "" | No | 10.55.54.0/24 | Secondary VPC CIDR range |
| VpcCidr3 | String | "" | No | 10.55.55.0/24 | Tertiary VPC CIDR range |
| VpcCidr4 | String | "" | No | | Quaternary VPC CIDR range |
| VpcCidr5 | String | "" | No | | Quinary VPC CIDR range |

#### Database Subnets (v1.1 - Security Group Egress)
| Parameter Name | Type | Default | Mandatory | Sample Value | Description |
|---------------|------|----------|-----------|--------------|-------------|
| VPCSubnetCidrDBAZ1 | String | "" | No | 10.55.53.128/27 | Database subnet AZ1 |
| VPCSubnetCidrDBAZ2 | String | "" | No | 10.55.53.160/27 | Database subnet AZ2 |
| VPCSubnetCidrDBAZ3 | String | "" | No | | Database subnet AZ3 |
| ProdDBPort | String | 53341 | No | 53341 | Production database port |
| NProdDBPort | String | 53331 | No | 53331 | Non-production database port |

#### S3 & HCC VPC Endpoints (v1.1 - Security Group Egress)
| Parameter Name | Type | Default | Mandatory | Sample Value | Description |
|---------------|------|----------|-----------|--------------|-------------|
| S3PrefixListId | String | "" | No | pl-0f8e90357f89b3f45 | S3 VPC endpoint prefix list ID |
| HCCVpceCidr | String | "" | No | 10.48.42.0/24 | HCC VPC endpoint CIDR |

#### HCC Forward Proxy (v1.1 - Security Group Egress)
| Parameter Name | Type | Default | Mandatory | Sample Value | Description |
|---------------|------|----------|-----------|--------------|-------------|
| EnableBCSProxy | String | false | No | true | Enable HCC Forward Proxy egress rules |
| HCCProxyPort | Number | 4000 | No | 4000 | Forward proxy port |
| ProdHCCProxyCidr1 | String | "" | No | 10.x.x.x/xx | Production proxy subnet CIDR 1 |
| ProdHCCProxyCidr2 | String | "" | No | 10.x.x.x/xx | Production proxy subnet CIDR 2 |
| NprdHCCProxyCidr1 | String | "" | No | 10.x.x.x/xx | Non-production proxy subnet CIDR 1 |
| NprdHCCProxyCidr2 | String | "" | No | 10.x.x.x/xx | Non-production proxy subnet CIDR 2 |

#### ElastiCache Redis (v1.1 - Security Group Egress)
| Parameter Name | Type | Default | Mandatory | Sample Value | Description |
|---------------|------|----------|-----------|--------------|-------------|
| ElastiCacheSubnetAZ1 | String | "" | No | 10.x.x.x/xx | Dedicated ElastiCache subnet AZ1 |
| ElastiCacheSubnetAZ2 | String | "" | No | 10.x.x.x/xx | Dedicated ElastiCache subnet AZ2 |
| ElastiCacheSubnetAZ3 | String | "" | No | 10.x.x.x/xx | Dedicated ElastiCache subnet AZ3 |

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
- Sets up security groups with CIDR-based egress rules for Lambda functions
- Manages SSM parameters for role and security group IDs

#### Security Group Egress Rules (v1.1)

| # | Rule | Port(s) | Destination | Condition |
|---|------|---------|-------------|-----------|
| 1 | HTTPS | 443 | VpcCidr1 | HasVpcCidr1 |
| 2 | HTTPS | 443 | VpcCidr2 | HasVpcCidr2 |
| 3 | HTTPS | 443 | VpcCidr3 | HasVpcCidr3 |
| 4 | HTTPS | 443 | VpcCidr4 | HasVpcCidr4 |
| 5 | HTTPS | 443 | VpcCidr5 | HasVpcCidr5 |
| 6 | Database | 53341 (prod) / 53331 (nprd) | VPCSubnetCidrDBAZ1 | HasVPCSubnetCidrDBAZ1 |
| 7 | Database | 53341 (prod) / 53331 (nprd) | VPCSubnetCidrDBAZ2 | HasVPCSubnetCidrDBAZ2 |
| 8 | Database | 53341 (prod) / 53331 (nprd) | VPCSubnetCidrDBAZ3 | HasVPCSubnetCidrDBAZ3 |
| 9 | S3 Endpoint | 443 | S3PrefixListId | HasS3PrefixListId |
| 10 | HCC VPC Endpoint | 443 | HCCVpceCidr | HasHCCVpceCidr |
| 11 | HCC Forward Proxy | HCCProxyPort (default 4000) | Prod/NprdHCCProxyCidr1 | HasHCCProxyCidr1 |
| 12 | HCC Forward Proxy | HCCProxyPort (default 4000) | Prod/NprdHCCProxyCidr2 | HasHCCProxyCidr2 |
| 13 | ElastiCache Redis | 6379-6380 | VpcCidr1 | HasVpcCidr1 |
| 14 | ElastiCache Redis | 6379-6380 | VpcCidr2 | HasVpcCidr2 |
| 15 | ElastiCache Redis | 6379-6380 | VpcCidr3 | HasVpcCidr3 |
| 16 | ElastiCache Redis | 6379-6380 | VpcCidr4 | HasVpcCidr4 |
| 17 | ElastiCache Redis | 6379-6380 | VpcCidr5 | HasVpcCidr5 |
| 18 | ElastiCache Redis | 6379-6380 | ElastiCacheSubnetAZ1 | HasElastiCacheSubnetAZ1 |
| 19 | ElastiCache Redis | 6379-6380 | ElastiCacheSubnetAZ2 | HasElastiCacheSubnetAZ2 |
| 20 | ElastiCache Redis | 6379-6380 | ElastiCacheSubnetAZ3 | HasElastiCacheSubnetAZ3 |

> **v1 → v1.1 Change**: Replaced single `0.0.0.0/0:1-65535` egress rule with 20 conditional CIDR-based rules. All rules are conditional — only created when the corresponding parameter is provided.

#### Conditions (v1.1)

| Condition | Logic | Purpose |
|-----------|-------|---------|
| IsProduction | EnvName = prod/prod-a/prod-b/prod-c | DB port and proxy CIDR selection |
| HasVpcCidr1-5 | CIDR not empty | HTTPS + Redis egress rules |
| HasVPCSubnetCidrDBAZ1-3 | CIDR not empty | Database egress rules |
| HasS3PrefixListId | ID not empty | S3 endpoint egress rule |
| HasHCCVpceCidr | CIDR not empty | HCC VPC endpoint egress rule |
| EnableBCSProxy | EnableBCSProxy = true | Master toggle for forward proxy |
| HasProdHCCProxyCidr1/2 | CIDR not empty | Helper for compound condition |
| HasNprdHCCProxyCidr1/2 | CIDR not empty | Helper for compound condition |
| HasHCCProxyCidr1/2 | EnableBCSProxy AND (IsProduction AND HasProd... OR NOT IsProduction AND HasNprd...) | Auto prod/nprd proxy selection |
| HasElastiCacheSubnetAZ1-3 | CIDR not empty | Dedicated ElastiCache egress rules |

#### Traffic Flow

```
Lambda Function
  → Lambda Security Group (egress rule allows outbound)
    → VPC Endpoint (private network, port 443)
      → AWS Service (S3, SES, Secrets Manager, SSM, CloudWatch, etc.)

Lambda Function
  → Lambda Security Group (egress rule allows outbound)
    → Database Subnet (port 53341/53331)
      → RDS Instance

Lambda Function
  → Lambda Security Group (egress rule allows outbound)
    → HCC Forward Proxy Subnet (port 4000)
      → External Service (via proxy)
```

> **Note**: Lambda functions using AWS SDK to call services (SES, DynamoDB, S3, etc.) go through VPC endpoints on port 443. SMTP port 587 is not needed — the HTTPS 443 rules to VPC CIDRs cover all AWS service API traffic via VPC endpoints.

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
- Non-production: `nprd`, `nprd-dev`, `nprd-dev1`, `nprd-dev2`, `nprd-stg`, `nprd-sit1`, `nprd-sit2`, `nprd-sit3`, `nprd-sit`, `nprd-sit-a`, `nprd-sit-b`, `nprd-sit-c`, `nprd-uat`, `nprd-uat-a`, `nprd-uat-b`, `nprd-uat-c`, `nprd-pt`, `nprd-pp`, `nprd-pp-a`, `nprd-pp-b`, `nprd-pp-c`
- Production: `prod`, `prod-a`, `prod-b`, `prod-c`

> **v1.1**: Added `nprd-dev1`, `nprd-dev2` to AllowedValues.

## v1 → v1.1 Migration Guide

### Breaking Change
- Security group egress changes from `0.0.0.0/0:1-65535` to CIDR-based rules
- **If no VPC CIDRs are provided**, the security group will have **no egress rules** and Lambda functions will lose all outbound connectivity
- You **must** provide at least `VpcCidr1` to maintain HTTPS connectivity

### New Parameters Required
Add these to your `parameters-lambda-api-infra-main.json`:

```json
{"ParameterKey": "VpcCidr1", "ParameterValue": "10.x.x.x/xx"}
```

### Optional Parameters
All other new parameters default to empty and can be added as needed:
- `VpcCidr2-5` — additional VPC CIDRs
- `VPCSubnetCidrDBAZ1-3`, `ProdDBPort`, `NProdDBPort` — database access
- `S3PrefixListId`, `HCCVpceCidr` — VPC endpoint access
- `EnableBCSProxy`, `HCCProxyPort`, `ProdHCCProxyCidr1/2`, `NprdHCCProxyCidr1/2` — forward proxy
- `ElastiCacheSubnetAZ1-3` — ElastiCache Redis dedicated subnets

### IaCVersion Tag
All resources updated from `AppSubsystem-BackendLambda-v1` to `AppSubsystem-BackendLambda-v1.1`

## Security Considerations

1. Network Security
   - VPC isolation
   - Private API Gateway endpoints
   - CIDR-based security group egress rules (no `0.0.0.0/0` wide-open rules)
   - S3 and HCC VPC endpoint egress via prefix list / CIDR
   - HCC Forward Proxy with prod/nprd auto-selection

2. Authentication/Authorization
   - Lambda authorizer integration
   - Azure AD support
   - API key option

3. Access Control
   - IAM roles and policies
   - Resource-based policies
   - Least privilege principle

4. Security Group Design (v1.1)
   - All egress rules are conditional — only created when parameters are provided
   - Database port auto-selects based on environment (prod: 53341, nprd: 53331)
   - Forward proxy CIDRs auto-select based on environment (prod vs nprd)
   - AWS service API calls (SES, DynamoDB, S3, etc.) use VPC endpoints on port 443, not direct internet access

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

4. Security Group Egress Issues (v1.1)
   - **Timeout calling AWS service** — Verify VPC CIDR egress (port 443) covers the VPC endpoint subnet, and the VPC endpoint SG allows inbound 443 from the Lambda SG
   - **Timeout calling database** — Verify DB subnet CIDRs are provided and correct port is used (53341 for prod, 53331 for nprd)
   - **Timeout calling external service via proxy** — Verify `EnableBCSProxy` is `true` and the correct prod/nprd proxy CIDRs are provided
   - **AccessDeniedException** — Security group is fine; check Lambda IAM role permissions for the specific service action
   - **No outbound connectivity after v1 → v1.1 upgrade** — Ensure at least `VpcCidr1` is provided; empty CIDRs mean no egress rules are created

5. Timezone Issues
   - Verify the correct Lambda{N}TimeZone parameter is set
   - Check that the timezone value is a valid IANA timezone name
   - Confirm the TZ environment variable is properly set in Lambda configuration