# Application Load Balancer with VPC Endpoint Target CloudFormation Template

This CloudFormation template creates an Application Load Balancer (ALB) that can route traffic to VPC Interface Endpoint IP addresses. The template supports both public (internet-facing) and private (internal) ALB configurations with SSL/TLS termination.

## Features

- Supports both internal and internet-facing ALB deployments
- IP-based target group for VPC Interface Endpoint targets
- Support for up to 24 additional SSL certificates
- Prefix list support for private ALB security group rules
- Environment-based resource retention policies
- Configurable health checks
- TLS 1.3 and 1.2 security policy support

## Prerequisites

Before deploying this template, ensure you have:

1. VPC ID where the ALB will be deployed
2. At least two subnet IDs for ALB deployment
3. VPC Interface Endpoint IP addresses
4. SSL certificate ARN from AWS Certificate Manager (ACM)
5. Prefix List ID (for private ALB configuration)

## Parameters

### Required Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| EnvName | Environment name | nprd, prod, nprd-sit, etc. |
| ALBName | Name for the Application Load Balancer | apt-nprd-public-alb-portal |
| ALBScheme | ALB type (internal/internet-facing) | internet-facing |
| VpcId | VPC ID for ALB deployment | vpc-0d99a0c727b301d67 |
| IngressSubnetIds | Comma-separated list of subnet IDs | subnet-123,subnet-456 |
| VPCEndpointIP1 | First VPC endpoint IP address | 10.1.154.147 |
| VPCEndpointIP2 | Second VPC endpoint IP address | 10.1.138.43 |
| SSLCertificateArn | SSL certificate ARN from ACM | arn:aws:acm:region:account:certificate/id |

### Optional Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| VPCEndpointIP3 | Third VPC endpoint IP address (optional) | "" |
| PrefixListIdIntranet | Prefix List ID for private ALB | "" |
| ListenerSslPolicy | SSL Policy for ALB listener | ELBSecurityPolicy-TLS13-1-2-2021-06 |
| AdditionalCertificateArn1 | Additional SSL certificate ARN 1 | "" |
| AdditionalCertificateArn2 | Additional SSL certificate ARN 2 | "" |
| AdditionalCertificateArn3 | Additional SSL certificate ARN 3 | "" |
| ... | ... | ... |
| AdditionalCertificateArn24 | Additional SSL certificate ARN 24 | "" |

## Additional SSL Certificates

The template supports up to 24 additional SSL certificates. For each certificate, provide the ARN in the corresponding parameter (AdditionalCertificateArn1 through AdditionalCertificateArn24). Leave any unused certificate parameters as empty strings.

Each non-empty certificate ARN will create a corresponding ListenerCertificate resource attached to the ALB listener. This allows multiple domains to be served from the same ALB.

## Usage

### Parameter File Example

Create a parameters.json file:

```json
[
    {
        "ParameterKey": "EnvName",
        "ParameterValue": "nprd"
    },
    {
        "ParameterKey": "ALBName",
        "ParameterValue": "apt-nprd-public-alb-portal"
    },
    {
        "ParameterKey": "ALBScheme",
        "ParameterValue": "internet-facing"
    },
    {
        "ParameterKey": "VpcId",
        "ParameterValue": "vpc-0d99a0c727b301d67"
    },
    {
        "ParameterKey": "IngressSubnetIds",
        "ParameterValue": "subnet-0dea7db2634fdcb74,subnet-0c0884fe76edfe546"
    },
    {
        "ParameterKey": "VPCEndpointIP1",
        "ParameterValue": "10.1.154.147"
    },
    {
        "ParameterKey": "VPCEndpointIP2",
        "ParameterValue": "10.1.138.43"
    },
    {
        "ParameterKey": "SSLCertificateArn",
        "ParameterValue": "arn:aws:acm:ap-southeast-1:781576980265:certificate/5e10a9f8-f3b4-4e6b-8dd7-cfc26a0eaf08"
    },
    {
        "ParameterKey": "AdditionalCertificateArn1",
        "ParameterValue": "arn:aws:acm:ap-southeast-1:781576980265:certificate/example-cert-1"
    },
    {
        "ParameterKey": "AdditionalCertificateArn2",
        "ParameterValue": "arn:aws:acm:ap-southeast-1:781576980265:certificate/example-cert-2"
    },
    {
        "ParameterKey": "AdditionalCertificateArn3",
        "ParameterValue": ""
    },
    ...
]
```

## Resource Management

### Production Environment

For production environments (prod, prod-a, prod-b), the template applies the following policies:
- DeletionPolicy: Retain
- UpdateReplacePolicy: Retain

This ensures that resources are not accidentally deleted during stack updates or deletion.

### Non-Production Environment

For non-production environments, resources will be deleted when the stack is deleted.

## Security Groups

### Public ALB
- Allows inbound HTTPS (443) from anywhere (0.0.0.0/0)

### Private ALB
- Allows inbound HTTPS (443) only from specified Prefix List IDs
- Requires PrefixListIdIntranet parameter to be set

## Health Checks
The template configures the following health check settings for the target group:
- Protocol: HTTPS
- Port: traffic-port (443)
- Path: /
- Success codes: 200, 403
- Health check enabled by default