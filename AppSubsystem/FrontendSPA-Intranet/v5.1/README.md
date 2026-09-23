# FrontendSPA with Lambda Reverse Proxy, Private API Gateway, and Application Load Balancer

## Version 5.1

**IaC Version Tag:** `AppSubsystem-SPAIntranet-v5.1`

### Changes from v5
- **Public ALB Ingress via Prefix List**: Added `PrefixListIdInternet` parameter to control inbound traffic on internet-facing ALB using a managed prefix list.
- **Configurable TLS Policy**: Added `ALBSslPolicy` parameter for HTTPS listener. Supports TLS 1.3, TLS 1.2, and post-quantum (PQ) policies. Default: `ELBSecurityPolicy-TLS13-1-2-2021-06`.

## Overview

This project deploys a frontend SPA infrastructure with the following key components:

1. **Lambda Reverse Proxy**: Handles requests and routes them to S3 or other resources
2. **Private API Gateway**: Secures API communication within a VPC
3. **Application Load Balancer (ALB)**: Balances traffic between endpoints or Lambda functions with optional S3 file upload support

## Architecture Flow

```
+----------------+       +------------------+       +----------------+       +------------------+       +----------------+
|    ALB         |       |   API Gateway    |       |    VPC Link    |       |      NLB         |       |   Backend      |
|                |------>|   (Private)      |------>|                |------>|                  |------>|   Services     |
|                |       |                  |       |                |       |                  |       |                |
+----------------+       +------------------+       +----------------+       +------------------+       +----------------+
        |
        |                +------------------+
        |                |   S3 VPC         |
        +--------------->|   Endpoint       |  (Optional File Upload Feature)
                         |                  |
                         +------------------+
```

### Flow:
1. Client → ALB: API request through private API
2. API GW → VPC Link: Route request through VPC Link
3. VPC Link → NLB: Forward to Network Load Balancer
4. NLB → Backend Services: Distribute traffic to backend services
5. (Optional) ALB → S3 VPC Endpoint: Route file upload requests using path-based routing

## Template Structure

```
FrontendSPA/
└── Intranet/
    ├── artifacts/
    │   ├── apispec/
    │   │   └── swagger-frontend.json
    │   └── lambda/
    │       └── s3ReverseProxy.zip
    ├── env/
    │   ├── parameters-alb-vpce.json              (ALB and VPC endpoint configuration)
    │   ├── parameters-intranet-frontend-spa-main.json    (Main stack parameters)
    │   └── parameters-lambda-s3reverseproxy.json (Lambda reverse proxy configuration)
    ├── cf-private-apigw.yaml
    ├── cf-lambda-s3reverseproxy.yaml
    ├── cf-alb-vpce.yaml
    ├── cf-intranet-frontend-spa-main.yaml
    └── README.md
```

### Template Main Components
- cf-intranet-frontend-spa-main.yaml: Main CloudFormation template to execute nested stacks.

- cf-private-apigw.yaml: CloudFormation template for the private API Gateway.

- cf-lambda-s3reverseproxy.yaml: Template to configure Lambda as a reverse proxy for S3.

- cf-alb-vpce.yaml: Template to set up the ALB and target groups.

- **parameters-intranet-frontend-spa-main.json: Parameter file for deployment.**

## Features

1. **Lambda Reverse Proxy**

        Processes requests routed from the ALB.
        Deployed as a serverless function with adjustable runtime.
        Logs managed with configurable retention.

2. **Private API Gateway**

        Secure API access through VPC Endpoint.
        Optional custom domain support with SSL certificate integration.
        Stage-based configuration for development and production environments.

3. **Application Load Balancer**

        Routes traffic to Lambda reverse proxy or backend services.
        Supports internet-facing or internal schemes for public or private access.
        Configurable subnets, VPC, and security groups.

4. **Security Features**

        Enforces HTTPS-only connections.
        Configurable AWS Prefix List for inbound traffic (both internal and internet-facing ALB).
        Configurable TLS policy via `ALBSslPolicy` parameter (default: TLS 1.3 with TLS 1.2 fallback, includes post-quantum options).
        Comprehensive logging and monitoring setup.

## Parameter Configuration

### Main Stack Parameters (parameters-intranet-frontend-spa-main.json)
| Parameter | Description | Example Value | Required |
|-----------|-------------|---------------|----------|
| AppShortName | Application identifier | "apt" | Yes |
| EnvName | Environment name | "nprd" | Yes |
| LambdaS3bucket | Lambda code bucket | "apt-lambda-artifact" | Yes |
| CodeZipFileName | Lambda function code zip file | "s3ReverseProxy-v2.zip" | Yes |
| LambdaRuntime | Runtime for Lambda function | "nodejs20.x" | No |
| LambdaHandler | Lambda function handler | "index.mjs.handler" | No |
| FrontendSPABucketName | Frontend assets bucket | "frontend.seedideation.com" | Yes |
| LambdaLogRetentionInDays | Number of days to retain Lambda logs | 14 | No |
| SwaggerFile | API spec location | "fhir-apigw-swagger/Frontendportal-api-swagger.json" | Yes |
| ApigwVpceId | VPC Endpoint ID for API Gateway (execute-api) | "vpce-0123456789abcdef0" | Yes |
| APIName | API Gateway name | "fhir" | Yes |
| StageName | API Gateway stage | "dev" | Yes |
| CustomDomainName | Custom domain for API Gateway | "api.example.com" | No |
| SSLCertificateArn | SSL certificate ARN for custom domain | "arn:aws:acm:region:account:certificate/id" | No |
| AdditionalCertArn | Additional SSL certificate ARN for ALB HTTPS listener | "arn:aws:acm:region:account:certificate/id" | Yes |
| LambdaAuthorizerFunctionArn | Lambda authorizer function ARN | "arn:aws:lambda:region:account:function:authorizer" | No |
| ALBName | Name for Application Load Balancer | "frontend-alb" | Yes |
| ALBScheme | ALB type (internal/internet-facing) | "internal" | Yes |
| ALBSslPolicy | ELB Security Policy for HTTPS listener (TLS 1.2+ only) | "ELBSecurityPolicy-TLS13-1-2-2021-06" | No |
| VpcId | VPC ID for ALB deployment | "vpc-0123456789abcdef0" | Yes |
| IngressSubnetIds | Subnet IDs for ALB deployment (comma-separated) | "subnet-123,subnet-456" | Yes |
| VPCEndpointIP1 | VPC Interface Endpoint IP - AZ1 | "10.0.0.1" | Yes |
| VPCEndpointIP2 | VPC Interface Endpoint IP - AZ2 | "10.0.1.1" | No |
| VPCEndpointIP3 | VPC Interface Endpoint IP - AZ3 | "10.0.2.1" | No |
| PrefixListIdIntranet | Prefix List ID for intranet traffic (internal ALB) | "pl-0123456789abcdef0" | No |
| PrefixListIdInternet | Prefix List ID for internet traffic (internet-facing ALB) | "pl-0123456789abcdef0" | No |
| EnableS3Upload | Enable S3 upload functionality through ALB | "false" | No |
| S3EndpointIP1 | S3 VPC Interface Endpoint IP - AZ1 | "10.0.0.2" | No* |
| S3EndpointIP2 | S3 VPC Interface Endpoint IP - AZ2 | "10.0.1.2" | No* |
| S3EndpointIP3 | S3 VPC Interface Endpoint IP - AZ3 | "10.0.2.2" | No |
| S3UploadPath | Path pattern for S3 upload route | "/appartifacts/*" | No |

*Required if EnableS3Upload is set to "true"

### Network Security Parameters
Additional network security parameters are available in the YAML parameter files for fine-grained control:

| Parameter | Description | Required |
|-----------|-------------|----------|
| VpcCidr1 | Primary VPC CIDR block for security group rules | Yes |
| VpcCidr2 | Secondary VPC CIDR block (optional) | No |
| VpcCidr3 | Tertiary VPC CIDR block (optional) | No |
| VpcCidr4 | Quaternary VPC CIDR block (optional) | No |
| VpcCidr5 | Quinary VPC CIDR block (optional) | No |
| S3PrefixListId | S3 prefix list ID for egress (optional) | No |

These parameters support up to 5 VPC CIDR ranges for complex multi-VPC architectures, VPC peering, and hybrid cloud connectivity. Configure these in `parameters-alb-vpce.yaml` and `parameters-intranet-frontend-spa-main.yaml`.


### Supported Environment Names
- Non-Production: nprd, nprd-dev, nprd-stg, nprd-sit1, nprd-sit2, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b
- Production: prod, prod-a, prod-b

## Important Notes

1. Regional Limitations:
Custom domain ACM certificates must be in the same region as the API Gateway.
2. Subnets:
Ensure that subnets provided for ALB are in the same VPC and span at least two Availability Zones.
3. Lambda Handler:
Ensure the handler matches the entry point in the uploaded Lambda code.
4. Environment Names:
Consistent naming conventions ensure smooth deployment across environments.

## Migration from v5 to v5.1

1. Add `PrefixListIdInternet` and `ALBSslPolicy` to your parameter file (ALBSslPolicy defaults to `ELBSecurityPolicy-TLS13-1-2-2021-06` if not specified)
2. **If using internet-facing ALB**: Create a managed prefix list with the required inbound CIDRs and provide `PrefixListIdInternet` value **before** updating the stack. Without this, all inbound traffic to the public ALB will be blocked after the update.
   - **If using internal ALB**: No impact. The private ALB ingress is unchanged.
   - To provision prefix lists via CloudFormation, refer to `InfraPlatform/prefixlist/v1` template.
3. Update the stack with the new templates

## Deployment Steps

1. HIP release will upload the Lambda code to the specified S3 bucket.

2. Update the parameter file parameters-intranet-frontend-spa-main.json with the appropriate values for your environment.
3. Deploy the stack using the AWS CLI:
```
aws cloudformation deploy \
  --template-file cf-intranet-frontend-spa-main.yaml \
  --parameter-overrides file://parameters-intranet-frontend-spa-main.json \
  --stack-name FrontendSPA \
  --capabilities CAPABILITY_NAMED_IAM
```
4. Monitor the stack creation progress in the AWS Management Console.
5. Verify resources (Lambda, API Gateway, ALB) are correctly deployed and configured.