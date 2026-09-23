# CloudFront Distribution with Multiple S3 Origins

## Overview
This template creates a CloudFront distribution with support for 1-4 S3 bucket origins and path-based routing. It's designed for scenarios where you need to serve content from multiple S3 buckets under the same CloudFront distribution, with flexible configuration options for custom domains, geo-restrictions, and CloudFront Functions.

## Template Structure

```
FrontendSPA-Internet/
└── v1/
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
   - Support for 1-4 S3 bucket origins
   - Configurable path patterns for each additional bucket
   - Separate Origin Access Controls for each bucket
   - Default root object configuration

2. **Security Features**:
   - Public access blocked on all S3 buckets
   - Server-side encryption enabled (AES-256)
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
   - Secure logging bucket configuration with same security controls as origin buckets

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
| NumberOfBuckets | Number of S3 bucket origins (1-4) | 2 | Yes |
| DefaultPage | Default page for root and error responses | "index.html" | Yes |
| UseCustomDomain | Enable custom domain | "true" | Yes |
| CustomDomainName | Custom domain name | "app.example.com" | If UseCustomDomain is true |
| CloudFrontCertArn | ACM certificate ARN | "arn:aws:acm:us-east-1:..." | If UseCustomDomain is true |
| GeoLocation | Comma-separated geo-restriction codes | "VN,PH,SG" | Yes |
| Bucket1Name | Primary bucket name | "main-content" | Yes |
| Bucket1FunctionEnabled | Enable function for first bucket | "true" | No |
| Bucket1FunctionName | Function name for first bucket | "rewrite-function" | If Bucket1FunctionEnabled is true |
| Bucket2Name | Second bucket name | "api-docs" | If NumberOfBuckets > 1 |
| Bucket2PathPattern | Second bucket path pattern | "/api/*" | If NumberOfBuckets > 1 |
| Bucket2FunctionEnabled | Enable function for second bucket | "true" | If NumberOfBuckets > 1 |
| Bucket2FunctionName | Function name for second bucket | "auth-function" | If Bucket2FunctionEnabled is true |
| Bucket3Name | Third bucket name | "assets" | If NumberOfBuckets > 2 |
| Bucket3PathPattern | Third bucket path pattern | "/assets/*" | If NumberOfBuckets > 2 |
| Bucket3FunctionEnabled | Enable function for third bucket | "true" | If NumberOfBuckets > 2 |
| Bucket3FunctionName | Function name for third bucket | "redirect-function" | If Bucket3FunctionEnabled is true |
| Bucket4Name | Fourth bucket name | "media" | If NumberOfBuckets > 3 |
| Bucket4PathPattern | Fourth bucket path pattern | "/media/*" | If NumberOfBuckets > 3 |
| Bucket4FunctionEnabled | Enable function for fourth bucket | "true" | If NumberOfBuckets > 3 |
| Bucket4FunctionName | Function name for fourth bucket | "header-function" | If Bucket4FunctionEnabled is true |

### Supported Environment Names
- Non-Production: nprd, nprd-dev, nprd-stg, nprd-sit1, nprd-sit2, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b
- Production: prod, prod-a, prod-b

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

### S3 Bucket Security
- Server-side encryption with AES-256
- Public access blocking enabled
- Bucket owner preferred ownership
- TLS 1.2 minimum requirement
- HTTPS-only access enforced

### CloudFront Security
- TLSv1.2_2021 minimum protocol version
- SNI-enabled SSL when using custom domains
- Geo-restriction support with whitelist configuration
- Origin Access Control for secure S3 access

## Important Notes

1. **Regional Requirements**:
   - ACM certificates must be in the us-east-1 region
   - S3 buckets are created in the stack's region

2. **Naming and Uniqueness**:
   - S3 bucket names must be globally unique
   - Logging bucket automatically named as `${AppShortName}-${EnvName}-cf-logs-${Stackid}`

3. **Access Controls**:
   - All S3 buckets are created with public access blocked
   - Access only through CloudFront using Origin Access Control
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
   - Comprehensive bucket policies with security controls

8. **CloudFront Functions**:
   - Functions require unique names within the account
   - Maximum function code size is 10KB
   - Limited to viewer-request event type
   - Code updates managed through CloudFront console
