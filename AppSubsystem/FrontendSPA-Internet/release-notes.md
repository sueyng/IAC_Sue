# Release Notes: FrontendSPA-Internet Infrastructure

## Version Comparison: v1 vs v2 vs v3 vs v4 vs v5

### v5 Updates:
- **NEW: Bucket1 path pattern support**:
  - `Bucket1UsePathPattern` parameter (default `false`) — attaches Bucket1 as an additional `PathPattern`-matched cache behavior alongside its existing default cache behavior
  - `Bucket1PathPattern` parameter — path pattern used when `Bucket1UsePathPattern` is `true`
  - Backward compatible: default behavior (Bucket1 as default cache behavior only) is unchanged when `Bucket1UsePathPattern` is left `false`
- **NEW: Optional CloudFront CORS support**:
  - Adds `CorsConfig` to the existing CloudFront response headers policy.
  - `EnableCORS` controls the feature and defaults to `false` for backward compatibility.
  - `CORSAllowedOrigins` accepts approved comma-separated origins and is required when CORS is enabled.
  - Allows static cross-origin `GET` and `HEAD` responses, disables credentials, exposes `ETag`, and overrides origin CORS headers.
  - Does not add browser preflight (`OPTIONS`) or S3 bucket CORS; those require a separate reviewed design when needed.
- **NO NEW RESOURCE**: CORS updates the existing `ResponseHeadersPolicy` and distribution association.

### v4 Updates:
- **NEW: CloudFront Response Headers Policy** (built into main template):
  - SecurityHeadersConfig: HSTS, X-Content-Type-Options, X-Frame-Options, Referrer-Policy, X-XSS-Protection, Content-Security-Policy
  - CustomHeadersConfig: OWASP cross-origin headers (COOP, COEP, CORP, Permissions-Policy)
  - Up to 5 additional custom headers with per-header `Override` toggle
  - Master toggle `EnableResponseHeadersPolicy` (default `true`) plus per-header `Enable*` toggles
  - Auto-attached to all cache behaviors when enabled
- **NEW: Configurable TLS Security Policy**:
  - `CloudFrontSecurityPolicy` parameter — was hardcoded `TLSv1.2_2021` in v3
  - Allowed values: `TLSv1.2_2021` (default — preserves v3 behavior), `TLSv1.2_2025`, `TLSv1.3_2025`
- **CHANGED: CloudFront logging**:
  - Legacy CloudFront standard logging and the managed logs bucket are removed from v4
  - CloudFront logging v2 must be enabled manually from the CloudFront console after deployment
  - `CloudFrontLoggingV2ManualSetupRequired=CONFIRM` is required to acknowledge the manual follow-up
- **NEW: Stack Outputs**: `CloudFrontDistributionId`, `CloudFrontDomainName`, `ResponseHeadersPolicyId`
- **Backward compatibility**: v3 CloudFront distribution and S3 origin parameters are preserved. v4 adds response headers, configurable TLS, and one required manual logging-v2 acknowledgement.

### Core Infrastructure

#### v2 Updates:
- Added support for **CloudFront Functions**:
  - Configurable per S3 bucket origin.
  - Supports `viewer-request` event type.
  - Placeholder function code provided for customization.
- Enhanced **S3 bucket policies**:
  - Enforced TLS v1.2 or higher for all S3 requests.
  - Improved bucket access policies for CloudFront.
- Improved **Origin Access Control (OAC)**:
  - Replaced legacy Origin Access Identity (OAI) with OAC for secure S3 access.
- Enhanced **cache configuration**:
  - Added Brotli and Gzip compression support.
  - Improved cache behavior for custom path patterns.

#### v3 Updates:
- **NEW: AWS WAF Integration**:
  - Optional `WAFWebACLArn` parameter — leave empty to disable, populate to associate a Web ACL with the CloudFront distribution
  - Two-stage deployment workflow: deploy CloudFront with empty `WAFWebACLArn`, coordinate with HCC team for WAF setup, then update parameter with the WAF ARN
- **Legacy LogsBucket Retain Patch**:
  - `CloudFrontDistribution` uses production-only retain, while `LogsBucket` uses unconditional `DeletionPolicy: Retain` and `UpdateReplacePolicy: Retain`
  - This prepares v3 stacks for v4 migration where the legacy logs bucket is removed from CloudFormation control and retained for all environments
- **Standardized Resource Tagging**:
  - All taggable resources now include `IaCVersion: AppSubsystem-SPAInternet-v3` tag for governance/cost allocation
- **Backward compatibility**: All v2 parameters preserved.

### Security Enhancements

#### v2 Updates:
- Enforced HTTPS-only access for all S3 buckets.
- Updated CloudFront Viewer Protocol Policy to `redirect-to-https`.
- Enhanced geo-restriction support with configurable country codes.

#### v3 Updates:
- **Application Layer Security**:
  - WAF protection against SQL injection and XSS attacks.
  - Custom security rules for application-specific threats.
  - Real-time monitoring and blocking capabilities.
- **Enhanced Access Control**:
  - Maintained all v2 security features.
  - Added optional WAF layer for comprehensive protection.
- **Security Compliance**:
  - Support for enterprise-grade security requirements.
  - Integration with HCC team security policies.
- **Resource Security Governance**:
  - Consistent tagging for security auditing and compliance.

### Deployment Flow Updates

#### v2 Updates:
- Introduced a deployment order:
  1. Deploy S3 bucket policies.
  2. Deploy CloudFront distributions.
  3. Configure CloudFront Functions (if enabled).

#### v3 Updates:
- **WAF-Aware Deployment Process**:
  1. **Initial Deployment**: Deploy CloudFront with WAF parameter empty.
  2. **WAF Enablement**: Coordinate with HCC team for manual WAF setup.
  3. **Stack Update**: Capture WAF ARN and update CloudFormation parameters.
  4. **Maintenance**: Subsequent updates maintain WAF integration.
- **HCC Team Coordination**:
  - Structured workflow for WAF requests.
  - Clear handoff process from manual to automated management.
  - Documentation for WAF ARN capture and parameter updates.

### Documentation Updates

#### v2 Updates:
- Added detailed descriptions for new parameters (`BucketFunctionEnabled`, `BucketFunctionName`).
- Updated troubleshooting guide for common issues with CloudFront and S3 configurations.
- Enhanced deployment guide with examples for multi-origin configurations.

#### v3 Updates:
- **WAF Integration Documentation**:
  - Comprehensive WAF deployment process documentation.
  - HCC team coordination procedures.
  - Step-by-step WAF enablement workflow.
- **Security Best Practices**:
  - Enhanced security configuration guidelines.
  - WAF rule recommendations and examples.
- **Troubleshooting Guide**:
  - WAF-related issue resolution.
  - Common deployment scenarios and solutions.
- **Parameter Reference**:
  - Updated parameter tables with WAF configuration.
  - Example parameter files for different scenarios.
- **Resource Tagging Guidelines**:
  - Documentation for consistent resource tagging.
  - Cost allocation and governance best practices.

## Summary of Key Changes

| Feature/Component          | v1                       | v2                                    | v3                                    | v4                                                    | v5 |
|----------------------------|--------------------------|---------------------------------------|---------------------------------------|---------------------------------------------------------|---|
| IaC Version                | AppSubsystem-SPAInternet-v1 | AppSubsystem-SPAInternet-v2          | AppSubsystem-SPAInternet-v3           | AppSubsystem-SPAInternet-v4                           | AppSubsystem-SPAInternet-v5 |
| CloudFront Functions       | Not supported            | Supported                             | Supported                             | Supported                                             | Supported |
| S3 Bucket Policies         | Basic                    | Enforced TLS v1.2, improved access    | Enforced TLS v1.2, improved access    | Enforced TLS v1.2, improved access                    | Enforced TLS v1.2, improved access |
| Origin Access Control      | Legacy OAI               | Modern OAC                            | Modern OAC                            | Modern OAC                                            | Modern OAC |
| Cache Configuration        | Basic                    | Brotli/Gzip compression, custom paths | Brotli/Gzip compression, custom paths | Brotli/Gzip compression, custom paths                 | Adds Bucket1 path-pattern support |
| TLS Security Policy        | Hardcoded TLSv1.2_2021   | Hardcoded TLSv1.2_2021                | Hardcoded TLSv1.2_2021                | **Configurable** (TLSv1.2_2021 / TLSv1.2_2025 / TLSv1.3_2025) | Same as v4 |
| CloudFront Logging         | Legacy standard logging  | Legacy standard logging               | Legacy standard logging; log bucket retained for migration | Legacy logging removed; logging v2 manual setup required | Same as v4 |
| WAF Integration            | Not supported            | Not supported                         | Supported (HCC workflow)              | Supported (HCC workflow)                              | Supported |
| Response Headers Policy    | Not supported            | Not supported                         | Not supported                         | **Built-in** security and custom headers              | Adds optional CORS |
| Stack Outputs              | Not exposed              | Not exposed                           | Not exposed                           | **3 outputs** (DistributionId, DomainName, ResponseHeadersPolicyId) | Same as v4 |
| Resource Tagging           | Not standardised         | Not standardised                      | `IaCVersion` tag                      | `IaCVersion` tag                                      | `AppSubsystem-SPAInternet-v5` |

## Migration Path

### v1 → v2 Migration:
- Update template file and parameters
- No breaking changes to existing deployments
- Enhanced security and functionality automatically applied

### v2 → v3 Migration:
- Add `WAFWebACLArn` parameter (set to empty initially)
- Deploy updated template — fully backward compatible, no existing functionality affected
- (When ready) Coordinate with HCC team for WAF enablement → update parameter with WAF ARN

### v3 → v4 Migration:
- **Deploy v3 retain patch first** so the legacy `LogsBucket` is retained when removed from CloudFormation control during v4 upgrade.
- **CloudFormation impact**: in-place modify on `CloudFrontDistribution`, removal of `LogsBucket` / `LogsBucketPolicy` from v4 stack control, plus one new `ResponseHeadersPolicy` resource added.
- ⚠️ **v4 behavior changes**:
  - `EnableResponseHeadersPolicy: "true"` → adds HSTS, CSP, X-Frame-Options DENY, COEP `require-corp`, etc. to all responses. May break SPAs loading from external CDNs / iframes / inline scripts.
- Legacy CloudFront logging is removed; enable CloudFront logging v2 manually from the CloudFront console after deployment using a separately prepared compliant S3 log bucket.
- **Required new parameter**: set `CloudFrontLoggingV2ManualSetupRequired: "CONFIRM"` to acknowledge the manual logging-v2 follow-up.
- **Recommended first deploy**: explicitly set `EnableResponseHeadersPolicy: "false"` in parameter file to keep v3 response-header behavior, deploy, smoke test.
- **Then**: enable headers progressively in non-prod, audit browser console for CSP/COEP violations, tune `CSPValue` / `XFrameOptionsValue` for your SPA, then promote.
- **CloudFront cache invalidation** required when headers are first turned on (`aws cloudfront create-invalidation --paths "/*"`)

### v4 → v5 Migration:
- Carry forward the existing v4 parameters.
- Add `Bucket1UsePathPattern: "false"` and `Bucket1PathPattern: ""` to preserve the existing default behaviour.
- Enable the new Bucket 1 path behaviour only when the project requires an additional path-pattern cache behaviour for Bucket 1.
- Add `EnableCORS: "false"` and `CORSAllowedOrigins: ""` to preserve v4 browser behaviour.
- To allow another approved website to read CloudFront static content, set `EnableCORS: "true"` and provide exact comma-separated origins.
- `*` is not recommended for `CORSAllowedOrigins`; use it only for intentionally public content.
- Review the change set: `ResponseHeadersPolicy` should be modified in place; no new resource or replacement is expected.
- Test in non-production and invalidate `/*` after enabling or changing CORS headers.

### Direct v1 / v2 → v4 Migration:
- Follow v1 → v2 then v2 → v3 then v3 → v4 steps in sequence

## Version Recommendations

- **v1, v2**: Legacy — upgrade recommended
- **v3**: Stable — WAF integration baseline and retain patch for legacy logs bucket migration
- **v4**: Stable — response headers and configurable TLS.
- **v5**: **Recommended** for new deployments — adds optional Bucket 1 path-pattern support and optional, disabled-by-default CloudFront CORS support.

For detailed changes and deployment instructions, refer to the respective version-folder `README.md` files.
