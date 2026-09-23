# FrontendSPA with Lambda Reverse Proxy, Private API Gateway, and Application Load Balancer

## Overview
This project deploys a frontend SPA infrastructure with the following key components:
1. **Lambda Reverse Proxy: Handles requests and routes them to S3 or other resources.**
2. **Private API Gateway: Secures API communication within a VPC.**
3. **Application Load Balancer (ALB): Balances traffic between endpoints or Lambda functions.**

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
    ├── Env/
    │   └── parameters-intranet-frontend-spa-main.json
    ├── cf-private-apigw.yaml          (Child stack template for API Gateway)
    ├── cf-lambda-s3reverseproxy.yaml  (Child stack template for Lambda reverse proxy)
    ├── cf-alb-vpce.yaml               (Child stack template for ALB)
    ├── cf-intranet-frontend-spa-main.yaml  (Main stack template)
    └── README.md                      (Documentation for the deployment)

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
        Configurable AWS Prefix List for inbound traffic.
        TLS 1.2 minimum protocol enforced for all connections.
        Comprehensive logging and monitoring setup.

## Parameter Configuration

| Parameter | Description | Example Value | Required |
|-----------|-------------|---------------|----------|
| AppShortName | Application name | "myapp" | Yes |
| EnvName | Environment name (supports multiple environments) | "nprd" | Yes |
| LambdaS3bucket | S3 bucket for Lambda code | "apt-nprd-cftemplates" | Yes |
| CodeZipFileName | Lambda function code zip file name | "s3ReverseProxy-v2.zip" | Yes |
| FrontendPortalDNSName | DNS name for frontend portal | "frontend.seedideation.com" | Yes |
| SwaggerFile | API Gateway Swagger file location | "apt-nprd-cftemplates/swagger.json" | Yes |
| ApigwVpceId | API Gateway VPC Endpoint ID	| "vpce-098e2a3947c5c353b" | Yes |
| APIName | API Gateway name | "fhir-apigw" | Yes |
| StageName | API Gateway stage name | "dev" | Yes |
| CustomDomainName | Custom domain for API Gateway | "frontend.seedideation.com" | Optional |
| SSLCertificateArn | SSL Certificate ARN | "arn:aws:acm:ap-southeast-1:781576980265:certificate/....." | Yes |
| LambdaAuthorizerFunctionArn | Lambda Authorizer Function ARN | "arn:aws....." | Optional |
| ALBName | Application Load Balancer name | "apt-nprd-ingress-alb-portal" | Yes |
| ALBScheme | ALB scheme (internet-facing or internal) | "internal" | Yes |
| VpcId | VPC ID for ALB | "vpc-0d99a0c727b301d67" | Yes |
| IngressSubnetIds | Subnets for ALB | "subnet-0dea7db2634fdcb74,subnet-0c0884fe76edfe546" | Yes |
| VPCEndpointIP1 | VPC Endpoint IP for AZ1 | "10.1.154.147" | Yes |
| VPCEndpointIP2 | VPC Endpoint IP for AZ2 | "10.1.138.43" | Yes |
| VPCEndpointIP3 | VPC Endpoint IP for AZ3 | "" | Optional |
| PrefixListIdIntranet | Prefix List ID for intranet traffic | Optional |

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