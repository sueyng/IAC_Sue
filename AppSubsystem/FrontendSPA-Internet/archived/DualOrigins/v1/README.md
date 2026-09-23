# CloudFront Distribution with Dual S3 Origins

## Overview
This template creates a CloudFront distribution with two S3 bucket origins and path-based routing. It's designed for scenarios where you need to serve content from two different S3 buckets under the same CloudFront distribution.

## Template Structure

```
FrontendSPA/
└── DualOrigins/
    ├── Env/
    │   └── parameters-frontend-spa-dualorigins.json
    ├── cf-cloudfront-dualorigins.yaml
    └── README.md
```

### Main Components
- `cf-cloudfront-duals3.yaml`: Standalone CloudFront template with dual S3 origins
- `parameters-frontend-spa-duals3.json`: Parameter file for deployment

## Features

1. **Dual Origin Configuration**:
   - Primary S3 bucket for main content
   - Secondary S3 bucket for `/swagger/*` path pattern
   - Separate Origin Access Controls for each bucket

2. **Security Features**:
   - Public access blocked on all S3 buckets
   - Server-side encryption enabled (AES-256)
   - TLS 1.2 enforcement
   - HTTPS-only access
   - Geo-restriction support

3. **Logging Configuration**:
   - Automated logging bucket creation
   - Cookie logging enabled
   - Logs stored with prefix "logs/"

## Parameter Configuration

| Parameter | Description | Example Value | Required |
|-----------|-------------|---------------|----------|
| AppShortName | Application name | "hxis" | Yes |
| EnvName | Environment name | "nprd-stg" | Yes |
| CloudFrontCertArn | ACM certificate ARN | "arn:aws:acm:us-east-1:..." | Yes |
| DefaultPage | Default page | "index.html" | Yes |
| CustomDomainName | Custom domain | "apidocs-stg.healthx.sg" | Yes |
| PrimaryBucketName | Primary S3 bucket name | "apidocs-stg" | Yes |
| SecondaryBucketName | Secondary S3 bucket name | "swagger.apidocs-stg" | Yes |
| GeoLocation | Geo-restriction codes | "SG" | Yes |

## Path-Based Routing Configuration

The template implements the following routing rules:
1. Default Path (`/*`):
   - Routes to the primary S3 bucket
   - Used for main application content

2. Swagger Path (`/swagger/*`):
   - Routes to the secondary S3 bucket
   - Specifically for Swagger/API documentation

## Deployment Example

```json
[
  {
    "ParameterKey": "AppShortName",
    "ParameterValue": "hxis"
  },
  {
    "ParameterKey": "EnvName",
    "ParameterValue": "nprd-stg"
  },
  {
    "ParameterKey": "CloudFrontCertArn",
    "ParameterValue": "arn:aws:acm:us-east-1:533267434948:certificate/2f491a72-f346-4404-8a5a-083f5fc05632"
  },
  {
    "ParameterKey": "DefaultPage",
    "ParameterValue": "index.html"
  },
  {
    "ParameterKey": "CustomDomainName",
    "ParameterValue": "apidocs-stg.healthx.sg"
  },
  {
    "ParameterKey": "PrimaryBucketName",
    "ParameterValue": "apidocs-stg"
  },
  {
    "ParameterKey": "SecondaryBucketName",
    "ParameterValue": "swagger.apidocs-stg"
  },
  {
    "ParameterKey": "GeoLocation",
    "ParameterValue": "SG"
  }
]
```

## Cache Configuration

- Custom cache policy with caching disabled
- Configuration applies to both origins:
  - No query string caching
  - No header caching
  - No cookie caching
  - Compression enabled

## Error Handling

The distribution is configured to handle errors as follows:
- 403 and 404 errors redirect to the default page
- 10-second error caching TTL
- Applies to content from both origins

## Important Notes

1. ACM certificates must be in the us-east-1 region
2. All S3 buckets are created with public access blocked
3. The secondary bucket is only accessible through the `/swagger/*` path
4. Geo-restriction applies to all content regardless of origin
5. HTTP/3 is enabled by default