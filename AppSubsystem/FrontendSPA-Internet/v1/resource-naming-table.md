# AWS Resources Naming Convention - Frontend SPA Template

## Resource Naming Patterns

### Storage Resources
| Resource Type | Resource Name Pattern |
|--------------|----------------------|
| S3 Bucket (Content) | `{Bucket1Name}` to `{Bucket4Name}` (as specified in parameters) |
| S3 Bucket (Logs) | `{AppShortName}-{EnvName}-cf-logs-{UniqueId}` |

### CDN Resources
| Resource Type | Resource Name Pattern |
|--------------|----------------------|
| CloudFront Distribution | Default CloudFront domain or `{CustomDomainName}` |
| CloudFront Origin Access Control | Name matches associated S3 bucket name |
| CloudFront Cache Policy | `{AppShortName}-{EnvName}-CacheDisabledPolicy-{UniqueId}` |
| CloudFront Function | `{Bucket1FunctionName}` to `{Bucket4FunctionName}` (as specified in parameters) |

### Function Naming Requirements
| Requirement | Description |
|------------|-------------|
| Character Length | 1-64 characters |
| Allowed Characters | Letters (a-z, A-Z), numbers (0-9), hyphens (-), underscores (_) |
| Uniqueness | Must be unique within the AWS account |
| Format Validation | Enforced through CloudFormation parameter constraints |

## Variable Definitions
- `{AppShortName}`: Application short name (lowercase)
- `{EnvName}`: Environment name (e.g., prod, nprd, nprd-dev, etc.)
- `{Bucket1Name}` to `{Bucket4Name}`: Names specified for content buckets
- `{CustomDomainName}`: Optional custom domain for CloudFront
- `{UniqueId}`: Unique identifier from stack ID
- `{Bucket1FunctionName}` to `{Bucket4FunctionName}`: Names specified for CloudFront Functions (optional)

## Resource Name Examples

### Example with CloudFront Functions
```
S3 Content Bucket: "my-app-content"
S3 Logs Bucket: "myapp-nprd-dev-cf-logs-a1b2c3"
CloudFront Cache Policy: "myapp-nprd-dev-CacheDisabledPolicy-a1b2c3"
CloudFront Function: "myapp-nprd-dev-url-rewrite"
```
