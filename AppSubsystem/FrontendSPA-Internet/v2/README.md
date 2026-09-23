# CloudFront Distribution with Multiple S3 Origins

## Overview
This template creates a CloudFront distribution with support for 1-4 existing S3 bucket origins and path-based routing. It's designed for scenarios where you need to serve content from multiple existing S3 buckets under the same CloudFront distribution, with flexible configuration options for custom domains, geo-restrictions, and CloudFront Functions.

## Template Structure

```
FrontendSPA-Internet/
└── v2/
    ├── Env/
    │   └── parameters-frontend-spa.json
    ├── cf-cloudfront-spa.yaml
    └── README.md
```

### Main Components
- `cf-cloudfront-spa.yaml`: CloudFront template with configurable S3 origins
- `parameters-frontend-spa.json`: Parameter file for deployment

## Features

1. **Flexible Origin Configuration**:
   - Support for 1-4 existing S3 bucket origins
   - Configurable path patterns for each additional bucket
   - Separate Origin Access Controls for each bucket
   - Default root object configuration

2. **Security Features**:
   - Updates bucket policies for CloudFront access
   - TLS 1.2 enforcement
   - HTTPS-only access (redirect-to-https viewer protocol policy)
   - Configurable geo-restriction support
   - Origin Access Control (OAC) for S3 buckets

3. **Custom Domain Support**:
   - Optional custom domain configuration
   - ACM certificate integration
   - SNI-enabled SSL support with TLSv1.2_2021 minimum protocol version

4. **Logging Configuration**:
   - Automated logging bucket creation with encryption
   - Cookie logging enabled
   - Structured log storage with 'logs/' prefix
   - Secure logging bucket configuration

5. **Performance and Protocol Support**:
   - HTTP/2 and HTTP/3 enabled
   - Brotli and Gzip compression support
   - PriceClass_200 configuration

6. **CloudFront Functions Support**:
   - Optional CloudFront Functions for each origin
   - Viewer-request event type support
   - Placeholder function code with easy console updates
   - Secure function naming validation
   - Independent function enablement per origin

## Parameter Configuration

| Parameter | Description | Example Value | Required |
|-----------|-------------|---------------|----------|
| AppShortName | Application name | "myapp" | Yes |
| EnvName | Environment name (supports multiple environments) | "nprd-stg" | Yes |
| NumberOfBuckets | Number of S3 bucket origins to use (1-4) | 2 | Yes |
| DefaultPage | Default page for root and error responses | "index.html" | Yes |
| UseCustomDomain | Enable custom domain | "true" | Yes |
| CustomDomainName | Custom domain name | "app.example.com" | If UseCustomDomain is true |
| CloudFrontCertArn | ACM certificate ARN | "arn:aws:acm:us-east-1:..." | If UseCustomDomain is true |
| GeoLocation | Comma-separated geo-restriction codes | "VN,PH,SG" | Yes |
| Bucket1Name | Existing primary bucket name | "myapp-nprd-stg-main-content" | Yes |
| Bucket1FunctionEnabled | Enable function for first bucket | "true" | No |
| Bucket1FunctionName | Function name for first bucket | "rewrite-function" | If Bucket1FunctionEnabled is true |
| Bucket2Name | Existing second bucket name | "myapp-nprd-stg-api-docs" | If NumberOfBuckets > 1 |
| Bucket2PathPattern | Second bucket path pattern | "/api/*" | If NumberOfBuckets > 1 |
| Bucket2FunctionEnabled | Enable function for second bucket | "true" | If NumberOfBuckets > 1 |
| Bucket2FunctionName | Function name for second bucket | "auth-function" | If Bucket2FunctionEnabled is true |
| Bucket3Name | Existing third bucket name | "myapp-nprd-stg-assets" | If NumberOfBuckets > 2 |
| Bucket3PathPattern | Third bucket path pattern | "/assets/*" | If NumberOfBuckets > 2 |
| Bucket3FunctionEnabled | Enable function for third bucket | "true" | If NumberOfBuckets > 2 |
| Bucket3FunctionName | Function name for third bucket | "redirect-function" | If Bucket3FunctionEnabled is true |
| Bucket4Name | Existing fourth bucket name | "myapp-nprd-stg-media" | If NumberOfBuckets > 3 |
| Bucket4PathPattern | Fourth bucket path pattern | "/media/*" | If NumberOfBuckets > 3 |
| Bucket4FunctionEnabled | Enable function for fourth bucket | "true" | If NumberOfBuckets > 3 |
| Bucket4FunctionName | Function name for fourth bucket | "header-function" | If Bucket4FunctionEnabled is true |

### Supported Environment Names
- Non-Production: nprd, nprd-dev, nprd-stg, nprd-sit1, nprd-sit2, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b
- Production: prod, prod-a, prod-b

## Prerequisites

Before deploying this template, ensure:
1. All required S3 buckets exist in your AWS account
2. You have the full bucket names of all S3 buckets you plan to use
3. The existing buckets are in the same region where you're deploying the stack

## Path-Based Routing Configuration

The template implements the following routing hierarchy:
1. Default Path (`/*`):
   - Routes to the primary S3 bucket (Bucket1)
   - Used for main application content
   - Handles default root object and error pages

2. Additional Paths:
   - Configurable path patterns for each additional bucket
   - Each path pattern must be unique
   - Paths are evaluated in order of creation
   - All paths inherit the same cache and security settings

## CloudFront Functions Configuration

The template supports attaching CloudFront Functions to each origin:

1. **Function Naming Requirements**:
   - Must be between 1-64 characters
   - Can only contain letters, numbers, hyphens, and underscores
   - Must be provided when function is enabled

2. **Function Deployment**:
   - Functions are created with placeholder code
   - Code can be updated via CloudFront console
   - Runtime: cloudfront-js-2.0
   - Event type: viewer-request

3. **Per-Origin Configuration**:
   - Each origin can have its own function
   - Functions are optional for each origin
   - Independent enable/disable control
   - Functions only created when both enabled and name provided

4. **Default Function Code**:
   - Placeholder handler that returns unmodified request
   - Ready for custom implementation via console
   - AutoPublish enabled for immediate deployment

## Cache Configuration

The template uses a custom cache policy with the following settings:
- Caching disabled by default (TTL: 0)
- No query string forwarding or caching
- No header forwarding or caching
- No cookie forwarding or caching
- Compression enabled
- Configurable through CloudFrontCachePolicy resource

## Error Handling

The distribution includes comprehensive error handling:
- 403 and 404 errors redirect to the default page
- 10-second error caching TTL
- Custom error responses apply uniformly across all origins
- SPA-friendly configuration for client-side routing

## Security Configurations

### S3 Bucket Policies
- Template updates existing bucket policies to allow CloudFront access
- Enforces TLS 1.2 minimum requirement
- Enforces HTTPS-only access
- Implements Origin Access Control for secure CloudFront access

### CloudFront Security
- TLSv1.2_2021 minimum protocol version
- SNI-enabled SSL when using custom domains
- Geo-restriction support with whitelist configuration
- Origin Access Control for secure S3 access

## Important Notes

1. **Regional Requirements**:
   - ACM certificates must be in the us-east-1 region
   - Existing S3 buckets must be in the stack's region

2. **Bucket Requirements**:
   - All referenced S3 buckets must exist before deployment
   - Bucket policies will be updated by the template
   - Ensure you have proper permissions to modify bucket policies

3. **Access Controls**:
   - Existing bucket configurations are preserved except for the policy updates
   - Access through CloudFront using Origin Access Control
   - Additional buckets are only accessible through their specified path patterns

4. **Logging and Monitoring**:
   - CloudFront logs stored in dedicated logging bucket
   - Cookie logging enabled for detailed access analysis
   - Structured log prefix for organized log management

5. **Performance and Cost**:
   - Uses PriceClass_200 for optimal cost/performance balance
   - HTTP/2 and HTTP/3 enabled for improved performance
   - Compression enabled for reduced bandwidth usage

6. **Error Handling**:
   - Default page serves as fallback for errors
   - Configured for Single Page Application (SPA) support

7. **Compliance and Security**:
   - TLS 1.2 enforcement on all connections
   - HTTPS-only access
   - Geo-restriction applies to all content
   - Updated bucket policies with security controls

8. **CloudFront Functions**:
   - Functions require unique names within the account
   - Maximum function code size is 10KB
   - Limited to viewer-request event type
   - Code updates managed through CloudFront console