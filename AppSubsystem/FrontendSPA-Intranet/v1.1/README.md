# FrontendSPA with Lambda Reverse Proxy, Private API Gateway, and Application Load Balancer

## Version 1.1

**IaC Version Tag:** `AppSubsystem-SPAIntranet-v1.1`

### Changes from v1
- **Security Group Egress Rules**: Added explicit egress rules to ALB security groups, restricting outbound to specific VPC CIDRs and optional S3/HCC endpoints.
- **Public ALB Ingress via Prefix List**: Added `PrefixListIdInternet` parameter to control inbound traffic on internet-facing ALB using a managed prefix list.
- **Configurable TLS Security Policy**: Added `ALBSslPolicy` parameter for the HTTPS listener (default: `ELBSecurityPolicy-TLS13-1-2-2021-06`, TLS 1.2+ only).
- **ALB Deletion Protection**: Enabled `deletion_protection.enabled` on the ALB to prevent accidental deletion.
- **Lambda Runtime/Handler Bug Fix**: `LambdaRuntime` and `LambdaHandler` parameters were declared but the Lambda resource had hardcoded values instead of referencing them. Now correctly wired via `!Ref`.

## Overview
This project deploys a frontend SPA infrastructure with the following key components:
1. **Lambda Reverse Proxy**: Handles requests and routes them to S3 or other resources.
2. **Private API Gateway**: Secures API communication within a VPC.
3. **Application Load Balancer (ALB)**: Balances traffic between endpoints or Lambda functions.

## Architecture Flow

```
+----------------+     +------------------+     +----------------+     +------------------+     +----------------+
|    ALB         |     |   API Gateway    |     |    VPC Link    |     |      NLB         |     |   Backend      |
|                |---->|   (Private)      |---->|                |---->|                  |---->|   Services     |
|                |     |                  |     |                |     |                  |     |                |
+----------------+     +------------------+     +----------------+     +------------------+     +----------------+

----------------------------------------------------------------
Flow:
1. Client -> ALB           : API request through private API
2. API GW -> VPC Link      : Route request through VPC Link
3. VPC Link -> NLB         : Forward to Network Load Balancer
4. NLB -> Backend Services : Distribute traffic to backend services
```

## Template Structure

```
FrontendSPA/
└── Intranet/
    └── v1.1/
        ├── Env/
        │   └── parameters-intranet-frontend-spa-main.json
        ├── cf-private-apigw.yaml          (Child stack template for API Gateway)
        ├── cf-lambda-s3reverseproxy.yaml  (Child stack template for Lambda reverse proxy)
        ├── cf-alb-vpce.yaml               (Child stack template for ALB with egress rules)
        ├── cf-intranet-frontend-spa-main.yaml  (Main stack template)
        └── README.md                      (Documentation for the deployment)
```

### Template Main Components
- **cf-intranet-frontend-spa-main.yaml**: Main CloudFormation template to execute nested stacks.
- **cf-private-apigw.yaml**: CloudFormation template for the private API Gateway.
- **cf-lambda-s3reverseproxy.yaml**: Template to configure Lambda as a reverse proxy for S3.
- **cf-alb-vpce.yaml**: Template to set up the ALB, security groups with egress rules, and target groups.

## Features

1. **Lambda Reverse Proxy**
   - Processes requests routed from the ALB.
   - Deployed as a serverless function with adjustable runtime.
   - Logs managed with configurable retention.

2. **Private API Gateway**
   - Secure API access through VPC Endpoint.
   - Optional custom domain support with SSL certificate integration.
   - Stage-based configuration for development and production environments.

3. **Application Load Balancer**
   - Routes traffic to Lambda reverse proxy or backend services.
   - Supports internet-facing or internal schemes for public or private access.
   - Configurable subnets, VPC, and security groups.

4. **Security Features**
   - Enforces HTTPS-only connections.
   - Configurable AWS Prefix List for inbound traffic (both internal and internet-facing ALB).
   - Configurable TLS security policy via `ALBSslPolicy` parameter (TLS 1.2+ only).
   - ALB deletion protection enabled to prevent accidental removal.
   - **Explicit security group egress rules** (new in v1.1):
     - Restricts outbound traffic to specified VPC CIDRs only
     - Optional S3 prefix list for S3 endpoint access
     - Optional HCC VPC endpoint CIDR support
   - Comprehensive logging and monitoring setup.

## Parameter Configuration

### Base Parameters (same as v1)

| Parameter | Description | Example Value | Required |
|-----------|-------------|---------------|----------|
| AppShortName | Application name | "myapp" | Yes |
| EnvName | Environment name | "nprd" | Yes |
| LambdaS3bucket | S3 bucket for Lambda code | "apt-nprd-cftemplates" | Yes |
| CodeZipFileName | Lambda function code zip file name | "s3ReverseProxy-v2.zip" | Yes |
| LambdaRuntime | Lambda function runtime | "nodejs20.x" | No (default: nodejs20.x) |
| LambdaHandler | Lambda function handler entry point | "index.mjs.handler" | No (default: index.mjs.handler) |
| FrontendPortalDNSName | DNS name for frontend portal | "frontend.example.com" | Yes |
| SwaggerFile | API Gateway Swagger file location | "apt-nprd-cftemplates/swagger.json" | Yes |
| ApigwVpceId | API Gateway VPC Endpoint ID | "vpce-098e2a3947c5c353b" | Yes |
| APIName | API Gateway name | "myapp-apigw" | Yes |
| StageName | API Gateway stage name | "dev" | Yes |
| CustomDomainName | Custom domain for API Gateway | "frontend.example.com" | Optional |
| SSLCertificateArn | SSL Certificate ARN | "arn:aws:acm:ap-southeast-1:..." | Yes |
| ALBSslPolicy | ELB Security Policy for HTTPS listener (TLS 1.2+ only) | "ELBSecurityPolicy-TLS13-1-2-2021-06" | Optional |
| LambdaAuthorizerFunctionArn | Lambda Authorizer Function ARN | "arn:aws:lambda:..." | Optional |
| ALBName | Application Load Balancer name | "myapp-nprd-alb" | Yes |
| ALBScheme | ALB scheme (internet-facing or internal) | "internal" | Yes |
| VpcId | VPC ID for ALB | "vpc-0d99a0c727b301d67" | Yes |
| IngressSubnetIds | Subnets for ALB | "subnet-xxx,subnet-yyy" | Yes |
| VPCEndpointIP1 | VPC Endpoint IP for AZ1 | "10.1.154.147" | Yes |
| VPCEndpointIP2 | VPC Endpoint IP for AZ2 | "10.1.138.43" | Yes |
| VPCEndpointIP3 | VPC Endpoint IP for AZ3 | "" | Optional |
| PrefixListIdIntranet | Prefix List ID for intranet traffic (internal ALB) | "pl-xxx" | Optional |
| PrefixListIdInternet | Prefix List ID for internet traffic (internet-facing ALB) | "pl-xxx" | Optional |

### New Parameters in v1.1 (Security Group Egress)

| Parameter | Description | Example Value | Required |
|-----------|-------------|---------------|----------|
| VpcCidr1 | VPC CIDR 1 for egress rules | "10.0.0.0/16" | Yes* |
| VpcCidr2 | VPC CIDR 2 for egress rules | "10.1.0.0/16" | Optional |
| VpcCidr3 | VPC CIDR 3 for egress rules | "10.2.0.0/16" | Optional |
| VpcCidr4 | VPC CIDR 4 for egress rules | "" | Optional |
| VpcCidr5 | VPC CIDR 5 for egress rules | "" | Optional |
| S3PrefixListId | S3 Prefix List ID for S3 endpoint access | "pl-xxx" | Optional |
| HCCVpceCidr | HCC VPC Endpoint Subnet CIDR | "10.100.0.0/24" | Optional |

> *At least one VpcCidr should be provided to allow outbound traffic. If no egress CIDRs are specified, the security group will block all outbound traffic.

### Supported Environment Names
- **Non-Production**: nprd, nprd-dev, nprd-stg, nprd-sit1, nprd-sit2, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-sit-c, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-uat-c, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b, nprd-pp-c
- **Production**: prod, prod-a, prod-b, prod-c

## Important Notes

1. **Regional Limitations**:
   Custom domain ACM certificates must be in the same region as the API Gateway.

2. **Subnets**:
   Ensure that subnets provided for ALB are in the same VPC and span at least two Availability Zones.

3. **Lambda Handler**:
   Ensure the handler matches the entry point in the uploaded Lambda code.

4. **Environment Names**:
   Consistent naming conventions ensure smooth deployment across environments.

5. **Egress Rules (v1.1 specific)**:
   - At least one `VpcCidr` parameter must be provided for ALB to communicate with backend services
   - Add `S3PrefixListId` if ALB needs to route traffic to S3 endpoints
   - Add `HCCVpceCidr` if integration with HCC VPC endpoints is required

## Migration from v1 to v1.1

To migrate from v1 to v1.1:

1. Identify the VPC CIDRs used by your backend services
2. Add the new egress parameters to your parameter file:
   - `VpcCidr1` (required)
   - `VpcCidr2-5` (optional, as needed)
   - `S3PrefixListId` (if using S3 endpoints)
   - `HCCVpceCidr` (if using HCC integration)
3. **If using internet-facing ALB**: Create a managed prefix list with the required inbound CIDRs and add `PrefixListIdInternet` to your parameter file **before** updating the stack. Without this, all inbound traffic to the public ALB will be blocked after the update.
   - **If using internal ALB**: No impact. The private ALB ingress is unchanged.
   - To provision prefix lists via CloudFormation, refer to `InfraPlatform/prefixlist/v1` template.
4. Update the stack with the new templates
