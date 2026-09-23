# CloudFront Distribution with Single S3 Origin

This repository contains AWS CloudFormation templates for deploying multiple CloudFront distributions with single S3 origin for Single Page Applications (SPA).

## Template Structure

```
FrontendSPA/
└── SingleOrigin/
    ├── Env/
    │   └── parameters-frontend-spa.json
    ├── cf-cloudfront.yaml           (Child stack template)
    ├── cf-frontend-spa-main.yaml    (Main stack template)
    └── README.md
```

## Template Description

### Main Stack Template (`cf-frontend-spa-main.yaml`)
- Orchestrates deployment of multiple CloudFront distributions (up to 4)
- Uses nested stacks approach for modular deployment
- Conditional creation of distributions based on NumberOfDistributions parameter
- Supports geo-restriction configuration

### Child Stack Template (`cf-cloudfront.yaml`)
- Creates S3 bucket with secure configuration
  - Public access blocked
  - TLS 1.2 enforcement
  - Encryption enabled (AES-256)
  - Secure transport required
- Configures CloudFront distribution
  - S3 origin with Origin Access Control
  - Custom domain support with ACM certificates
  - SSL/TLS configuration (TLSv1.2_2021)
  - HTTP/3 enabled
  - Custom error pages (403/404 redirect)
  - Geo-restriction capability
  - Logging enabled

## Parameters Reference

### Main Stack Parameters

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| NumberOfDistributions | Number | 1 | Yes | Number of CloudFront distributions (1-4) |
| AppShortName | String | - | Yes | Application name |
| EnvName | String | - | Yes | Environment name (e.g., nprd-stg, prod) |
| DefaultPage | String | index.html | Yes | Default page for SPA |
| GeoLocation | String | - | Yes | Comma-separated country codes (e.g., "SG" or "VN,PH,SG") |

### Distribution-Specific Parameters
For each distribution (n = 1 to 4):

| Parameter | Type | Required | Example Value |
|-----------|------|----------|---------------|
| CloudFrontS3BucketName{n} | String | Yes* | "apidocs-stg" |
| CustomDomainName{n} | String | Yes* | "apidocs-stg.healthx.sg" |
| CloudFrontCertArn{n} | String | Yes* | "arn:aws:acm:us-east-1:123456789012:certificate/..." |

*Required for active distributions based on NumberOfDistributions value

## Deployment Example

```json
[
  {
    "ParameterKey": "NumberOfDistributions",
    "ParameterValue": "2"
  },
  {
    "ParameterKey": "AppShortName",
    "ParameterValue": "hxis"
  },
  {
    "ParameterKey": "EnvName",
    "ParameterValue": "nprd-stg"
  },
  {
    "ParameterKey": "DefaultPage",
    "ParameterValue": "index.html"
  },
  {
    "ParameterKey": "CloudFrontS3BucketName1",
    "ParameterValue": "apidocs-stg"
  },
  {
    "ParameterKey": "CustomDomainName1",
    "ParameterValue": "apidocs-stg.healthx.sg"
  },
  {
    "ParameterKey": "CloudFrontCertArn1",
    "ParameterValue": "arn:aws:acm:us-east-1:533267434948:certificate/b08f56a6-e8f0-4b08-b0f9-29be99c7362f"
  },
  {
    "ParameterKey": "CloudFrontS3BucketName2",
    "ParameterValue": "userapps-stg"
  },
  {
    "ParameterKey": "CustomDomainName2",
    "ParameterValue": "userapps-stg.healthx.sg"
  },
  {
    "ParameterKey": "CloudFrontCertArn2",
    "ParameterValue": "arn:aws:acm:us-east-1:533267434948:certificate/b08f56a6-e8f0-4b08-b0f9-29be99c7362f"
  },
  {
    "ParameterKey": "GeoLocation",
    "ParameterValue": "SG"
  }
]
```

## Important Notes

1. **ACM Certificates**:
   - Must be created in us-east-1 region
   - Required for each active distribution
   - Ensure certificates are validated before deployment

2. **Template Location**:
   - Child stack template must be accessible at:
   - `https://${AppShortName}-${EnvName}-cftemplates.s3.amazonaws.com/cf-cloudfront.yaml`

3. **Cache Configuration**:
   - Custom cache policy with caching disabled
   - Compression enabled
   - GET and HEAD methods only

4. **Security**:
   - All S3 buckets are created with public access blocked
   - TLS 1.2 minimum protocol version
   - Origin Access Control for secure S3 access
   - Geo-restriction support

## Adding Additional CloudFront Distributions

To add more distributions (up to 4):

1. Update `parameters-frontend-spa.json`:
   - Increase `NumberOfDistributions` value
   - Add required parameters for new distribution
   - Leave unused distribution parameters empty

2. Deploy using updated parameters:
   - AWS CloudFormation will handle the creation of new resources
   - Existing distributions remain unchanged

