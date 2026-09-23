# FrontendSPA Internet — CloudFront + S3

## Version 5

**IaC Version Tag:** `AppSubsystem-SPAInternet-v5`

### Changes from v4
- **NEW: Bucket1 path pattern support** — `Bucket1UsePathPattern` (true/false, default `false`) lets Bucket1 also be attached as an additional `PathPattern`-matched cache behavior alongside its existing role as the default cache behavior. `Bucket1PathPattern` sets the path pattern (required if `Bucket1UsePathPattern` is `true`).
- **NEW: Optional CloudFront CORS response headers** — `CorsConfig` is included in the existing response headers policy when `EnableCORS: "true"`.
- **NEW: Approved-origin control** — `CORSAllowedOrigins` accepts one or more comma-separated origins.
- **Static content scope** — CORS allows `GET` and `HEAD`; credentials and browser preflight are not enabled.
- **Backward compatibility** — `Bucket1UsePathPattern` and `EnableCORS` both default to `false`, preserving v4 behaviour after upgrade.

## Version 4

**IaC Version Tag:** `AppSubsystem-SPAInternet-v4`

### Changes from v3
- **NEW: CloudFront Response Headers Policy** — built-in policy with HSTS, CSP, X-Frame-Options, COOP/COEP/CORP, Permissions-Policy, plus up to 5 custom headers. Auto-attached to all cache behaviors when `EnableResponseHeadersPolicy: "true"` (default).
- **NEW: Configurable TLS Security Policy** — `CloudFrontSecurityPolicy` parameter (was hardcoded `TLSv1.2_2021` in v3; default unchanged)
- **CHANGED: CloudFront logging** — legacy CloudFront standard logging and the managed logs bucket are removed from this template. CloudFront logging v2 must be enabled manually from the CloudFront console after deployment.
- **NEW: Logging acknowledgement** — `CloudFrontLoggingV2ManualSetupRequired=CONFIRM` is required to make the manual logging-v2 follow-up explicit.
- **NEW: Stack Outputs** — `CloudFrontDistributionId`, `CloudFrontDomainName`, `ResponseHeadersPolicyId`
- **Backward compatibility**: v3 values are preserved for the CloudFront distribution and S3 origins, with one new required acknowledgement for manual CloudFront logging v2 setup. See [Migration from v3 to v4](#migration-from-v3-to-v4).

## Overview

Deploys a CloudFront distribution with 1-4 existing S3 bucket origins, Origin Access Control (OAC), and an integrated response headers policy with security headers and optional CORS. CloudFront logging v2 is not configured by this template and must be enabled manually from the CloudFront console after deployment.

## Architecture

```
Users
  |
  v
CloudFront Distribution
  ├── Response Headers Policy (HSTS, CSP, X-Frame, optional CORS, custom headers)
  ├── Cache Policy (disabled for SPA)
  ├── Origin 1 (S3 bucket — default, OAC, optional additional path-based cache behavior)
  ├── Origin 2 (S3 bucket — path-based, optional)
  ├── Origin 3 (S3 bucket — path-based, optional)
  └── Origin 4 (S3 bucket — path-based, optional)
```

## Parameters

### Required

| Parameter | Description | Example |
|-----------|-------------|---------|
| AppShortName | Application identifier | `myapp` |
| EnvName | Environment | `nprd-dev` |
| Bucket1Name | Primary S3 bucket (must exist) | `myapp-nprd-dev-frontend` |
| GeoLocation | Country whitelist (ISO codes) | `SG,VN,PH` |
| CloudFrontLoggingV2ManualSetupRequired | Confirm manual CloudFront logging v2 setup is required after deployment | `CONFIRM` |

### Optional — CloudFront

| Parameter | Default | Description |
|-----------|---------|-------------|
| NumberOfBuckets | 1 | Number of S3 origins (1-4) |
| Bucket1UsePathPattern | false | Attach Bucket1 as an additional path-based cache behavior (on top of its default cache behavior) |
| Bucket1PathPattern | "" | Path pattern for Bucket1 (required if `Bucket1UsePathPattern` is `true`) |
| DefaultPage | index.html | Default root object |
| CloudFrontSecurityPolicy | TLSv1.2_2021 | Min TLS version (TLSv1.2_2021, TLSv1.2_2025, TLSv1.3_2025) |
| UseCustomDomain | false | Enable custom domain |
| CustomDomainName | "" | Custom domain (e.g. www.example.com) |
| CloudFrontCertArn | "" | ACM cert ARN (**must be in us-east-1**) |
| WAFWebACLArn | "" | WAF Web ACL ARN |

### CloudFront Logging v2

This template does not create a CloudFront log bucket and does not enable CloudFront logging v2. Project teams must create or select a compliant S3 log bucket separately, then enable CloudFront logging v2 manually from the CloudFront console after this stack is deployed.

The required `CloudFrontLoggingV2ManualSetupRequired=CONFIRM` parameter is an acknowledgement only. It does not configure logging.

### Optional — Response Headers Policy

| Parameter | Default | Description |
|-----------|---------|-------------|
| EnableResponseHeadersPolicy | true | Master toggle for entire policy |

#### CorsConfig (new in v5)

| Parameter | Default | Description |
|-----------|---------|-------------|
| EnableCORS | false | Add CORS response headers to all CloudFront cache behaviours |
| CORSAllowedOrigins | "" | Comma-separated approved origins; required when CORS is enabled |

When CORS is enabled, `EnableResponseHeadersPolicy` must also be `true`. The policy allows cross-origin `GET` and `HEAD`, disables credentials, exposes `ETag`, and overrides origin CORS headers. Exact approved origins are recommended. `*` is not recommended and should be used only when the content is intentionally public to every website.

This template does not add `OPTIONS` preflight support or modify the existing S3 buckets. If preflight is required, configure S3 CORS and CloudFront `OPTIONS`/origin-header forwarding separately. CORS for a separate API belongs on that API.

#### SecurityHeadersConfig

| Parameter | Default | Description |
|-----------|---------|-------------|
| EnableHSTS | true | HTTP Strict-Transport-Security |
| HSTSMaxAge | 31536000 | Max-age in seconds (1 year) |
| HSTSIncludeSubdomains | true | Include subdomains |
| HSTSPreload | false | Browser preload list |
| EnableXContentTypeOptions | true | X-Content-Type-Options: nosniff |
| EnableXFrameOptions | true | X-Frame-Options |
| XFrameOptionsValue | DENY | DENY or SAMEORIGIN |
| EnableReferrerPolicy | true | Referrer-Policy |
| ReferrerPolicyValue | strict-origin-when-cross-origin | Referrer policy value |
| EnableXSSProtection | false | X-XSS-Protection (deprecated) |
| EnableCSP | true | Content-Security-Policy |
| CSPValue | default-src 'self'... | CSP directive (customize per app) |

#### CustomHeadersConfig (OWASP Cross-Origin)

| Parameter | Default | Description |
|-----------|---------|-------------|
| EnableCOOP | true | Cross-Origin-Opener-Policy |
| COOPValue | same-origin | same-origin, same-origin-allow-popups, unsafe-none |
| EnableCOEP | true | Cross-Origin-Embedder-Policy |
| COEPValue | require-corp | require-corp, credentialless, unsafe-none |
| EnableCORP | true | Cross-Origin-Resource-Policy |
| CORPValue | same-origin | same-origin, same-site, cross-origin |
| EnablePermissionsPolicy | true | Permissions-Policy |
| PermissionsPolicyValue | accelerometer=()... | Feature restrictions |

#### Custom Headers (up to 5)

| Parameter | Default | Description |
|-----------|---------|-------------|
| CustomHeader1-5Name | "" | Header name (leave empty to skip) |
| CustomHeader1-5Value | "" | Header value |
| CustomHeader1-5Override | true | Override origin headers |

### Sample response headers (deploying with defaults)

The env yaml ships with OWASP-aligned defaults. A `curl -I` against the CloudFront domain after deployment returns:

```
strict-transport-security: max-age=31536000; includeSubDomains
x-content-type-options: nosniff
x-frame-options: DENY
referrer-policy: strict-origin-when-cross-origin
content-security-policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'; frame-ancestors 'none'
cross-origin-opener-policy: same-origin
cross-origin-embedder-policy: require-corp
cross-origin-resource-policy: same-origin
permissions-policy: accelerometer=(), camera=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=()
```

A SPA deployed with defaults is **fully OWASP compliant out of the box**. Only relax specific headers if your app needs to.

### Common SPA scenarios — what to change from defaults

| Scenario | Parameter change |
|---|---|
| Internal SPA, fully self-hosted (no external assets/APIs) | None — defaults work as-is |
| SPA loads Google Fonts / FontAwesome / external CDN | Loosen `CSPValue` — add CDN hosts to `script-src`, `style-src`, `font-src`, etc. |
| SPA calls external API (3rd-party REST/GraphQL) | Loosen `CSPValue` — add API host to `connect-src` |
| SPA embedded in iframe (corporate portal, partner site) | `XFrameOptionsValue: "SAMEORIGIN"` (or remove via `EnableXFrameOptions: "false"`) |
| SPA loads third-party images / videos / scripts | `EnableCOEP: "false"` — `require-corp` blocks third-party assets that don't send CORP headers |
| SPA needs camera, microphone, or geolocation | `PermissionsPolicyValue: "camera=(self), microphone=(self), geolocation=(self), …"` (allowlist needed features) |
| Add app version header for support / debugging | `CustomHeader1Name: "X-App-Version"`, `CustomHeader1Value: "1.2.3"` |
| Another approved website loads CloudFront static assets | `EnableCORS: "true"`, `CORSAllowedOrigins: "https://portal.example.com"` |
| Disable entire policy temporarily (debugging) | `EnableResponseHeadersPolicy: "false"` |

### Operational Notes

- **CSP `default-src 'self'`** blocks ALL external resources by default — most CSP violations show up in the browser's DevTools Console (`Content Security Policy: …`). Always test in non-prod first.
- **COEP `require-corp`** is the strictest setting. Most third-party CDNs do not send CORP headers, so embedded images / fonts / scripts from external origins will be blocked. If your SPA pulls from third-party CDNs, set `EnableCOEP: "false"`.
- **HSTS preload** (`HSTSPreload: "true"`) submits your domain to browser preload lists — **irreversible at browser level**. Only enable for production with a stable, long-term domain.
- **CloudFront caches responses including headers**. After changing any header parameter and redeploying, run `aws cloudfront create-invalidation --distribution-id <id> --paths "/*"` to flush old cached responses; otherwise old headers serve until TTL expires.
- **X-XSS-Protection** is intentionally OFF (deprecated). Modern browsers ignore it; CSP is the replacement.
- **CloudFront logging v2 is a manual follow-up**. After deployment, create or select a compliant S3 log bucket separately and enable logging v2 from the CloudFront console.

## Migration from v4 to v5

v5 adds optional Bucket 1 path-pattern and CORS support. It does not create another CloudFront distribution or response headers policy.

| Action | Parameter | Guidance |
|---|---|---|
| Preserve v4 behaviour | `Bucket1UsePathPattern` | Set to `false` (default). |
| Enable Bucket 1 path behaviour | `Bucket1UsePathPattern`, `Bucket1PathPattern` | Set the toggle to `true` and provide the required path pattern. |
| Preserve existing browser access | `EnableCORS` | Set to `false` (default). |
| Enable cross-origin static reads | `EnableCORS` | Set to `true`. |
| Provide approved callers | `CORSAllowedOrigins` | Use exact origins separated by commas without spaces. `*` is not recommended and is only suitable for intentionally public content. |

When CORS is enabled, CloudFormation modifies the existing `ResponseHeadersPolicy` in place. Test in non-production and invalidate `/*` after enabling or changing CORS headers.

## Migration from v3 to v4

v4 is built on v3 as baseline for the CloudFront distribution and S3 origins. It removes legacy CloudFront logging and the managed logs bucket from this template.

### What's new in v4

| # | Feature | Parameters added | Default |
|---|---|---|---|
| 1 | **Response Headers Policy** (HSTS, CSP, X-Frame-Options, COOP/COEP/CORP, Permissions-Policy, 5× custom headers) | ~25 (`Enable*` + `*Value` + `CustomHeaderN*`) | `EnableResponseHeadersPolicy: "true"` (ON) |
| 2 | **Configurable TLS Security Policy** (was hardcoded `TLSv1.2_2021` in v3) | `CloudFrontSecurityPolicy` | `TLSv1.2_2021` (matches v3 behavior) |
| 3 | **CloudFront logging v2 acknowledgement** | `CloudFrontLoggingV2ManualSetupRequired` | Required value: `CONFIRM` |
| 4 | **Stack Outputs** | — | `CloudFrontDistributionId`, `CloudFrontDomainName`, `ResponseHeadersPolicyId` |

### Parameter file considerations

When upgrading an existing parameter file to v4:

| Action | Parameter | Guidance |
|---|---|---|
| Keep existing values | `AppShortName`, `EnvName`, `NumberOfBuckets`, bucket names, path patterns, function settings, custom domain, WAF | Existing v3 values can be carried forward. |
| Add required acknowledgement | `CloudFrontLoggingV2ManualSetupRequired` | Set to `CONFIRM`. This is only an acknowledgement; it does not enable logging. |
| Add TLS policy | `CloudFrontSecurityPolicy` | Set to `TLSv1.2_2021` to preserve v3 behavior, or choose a newer allowed value after compatibility review. |
| Decide first-upgrade header behavior | `EnableResponseHeadersPolicy` | Recommended first upgrade value is `false` to keep v3 response behavior. Enable later after non-prod testing. |
| Review header defaults before enabling | `CSPValue`, `EnableCOEP`, `XFrameOptionsValue`, `PermissionsPolicyValue` | Defaults are strict and may block external CDNs, third-party APIs, iframe embedding, or browser features. |
| Remove obsolete logging expectations | Legacy `LogsBucket` / `LogsBucketPolicy` resources and any log-bucket output usage | v4 no longer manages the legacy log bucket. Enable CloudFront logging v2 manually after deployment. |

### Upgrade considerations

⚠️ **The default behavior of v4 is NOT identical to v3.**

1. **Response Headers Policy attaches by default** to all cache behaviors. Headers added include strict CSP (`default-src 'self'; …`), HSTS 1-year, X-Frame-Options DENY, COEP `require-corp`, etc.
   - **Risk**: SPAs that load assets from external CDNs (Google Fonts, FontAwesome), call third-party APIs, or run inline scripts may break in the browser
   - **Recommended for first upgrade**: explicitly set `EnableResponseHeadersPolicy: "false"` to keep v3 behavior, then enable in non-prod, audit, then prod
2. **Legacy CloudFront logging is removed** from the distribution. Enable CloudFront logging v2 manually from the CloudFront console after deployment.

### CloudFormation impact (no replacement)

| Resource | Change | Risk |
|---|---|---|
| `CloudFrontDistribution` | Modify (gains `ResponseHeadersPolicyId` refs, reads `CloudFrontSecurityPolicy`, removes legacy `Logging`) | In-place, ~5–15min CloudFront propagation |
| `LogsBucket` | Removed from v4 template | For v3 upgrades, deploy the log-bucket retain patch first so the physical bucket is retained for all environments and removed from stack control |
| `LogsBucketPolicy` | Removed from v4 template | Old CloudFormation-managed bucket policy is removed with the resource |
| `ResponseHeadersPolicy` | **Add** (new resource) | None |
| All other resources | No-op | None |

### Recommended upgrade sequence

1. **Deploy the v3 retain patch first** — this sets the legacy `LogsBucket` to unconditional `DeletionPolicy: Retain` and `UpdateReplacePolicy: Retain`.
2. **Update parameter file** — keep v3 values, add `CloudFrontLoggingV2ManualSetupRequired: "CONFIRM"`, and add `EnableResponseHeadersPolicy: "false"` if you want the first deploy to keep v3 header behavior.
3. **Deploy v4 stack update** — verify the changeset modifies `CloudFrontDistribution`, removes `LogsBucket` / `LogsBucketPolicy`, and skips physical deletion of the retained log bucket.
4. **Smoke test SPA** in browser — confirm no functional regression.
5. **Enable CloudFront logging v2 manually** from the CloudFront console using a separately prepared compliant S3 log bucket.
6. **Run CloudFront cache invalidation** if you later turn headers on: `aws cloudfront create-invalidation --paths "/*"` (cached responses still serve old headers until TTL expires).
7. **Adopt response headers progressively** in non-prod first — flip individual `Enable*` toggles, audit browser console for CSP/COEP violations, tune `CSPValue` / `XFrameOptionsValue` for your SPA, then promote.

### If upgrading from v1 or v2

Do not skip the legacy log-bucket retain step if the existing stack still manages `LogsBucket`. Upgrade through the v3 retain patch first, or apply an equivalent retain patch to the currently deployed version, then move to v4. This prevents CloudFormation from deleting the physical legacy log bucket when v4 removes `LogsBucket` and `LogsBucketPolicy` from stack control.

For parameters, bring forward the existing v1/v2 values, add the v3 WAF parameter if missing (`WAFWebACLArn`, leave empty if not used), then apply the v4 parameter checklist above.

### Quick reference — new parameter groups

If you're new to the response headers feature, here's the lay of the land:

- **`EnableResponseHeadersPolicy`** — master kill switch. Set to `"false"` and the rest are ignored.
- **SecurityHeadersConfig** (native CloudFront support): `EnableHSTS` (+ MaxAge/Subdomains/Preload), `EnableXContentTypeOptions`, `EnableXFrameOptions` (+Value), `EnableReferrerPolicy` (+Value), `EnableXSSProtection`, `EnableCSP` (+Value)
- **CustomHeadersConfig** (OWASP cross-origin headers, sent as custom headers): `EnableCOOP` (+Value), `EnableCOEP` (+Value), `EnableCORP` (+Value), `EnablePermissionsPolicy` (+Value)
- **Custom headers** (up to 5 arbitrary headers): `CustomHeaderN{Name,Value,Override}` for `N=1..5` — leave Name empty to skip the slot

## Deployment

```bash
aws cloudformation deploy \
  --template-file cf-frontend.spa.yaml \
  --parameter-overrides file://Env/parameters-frontend-spa.json \
  --stack-name {AppShortName}-{EnvName}-frontend-spa \
  --region ap-southeast-1
```

## Prerequisites

- S3 bucket(s) must exist before deployment
- ACM certificate must be in **us-east-1** (if using custom domain)
- WAF Web ACL must exist (if using WAF)
- CloudFront logging v2 S3 destination bucket must be created or selected separately before enabling logging v2 from the CloudFront console

## Security Features

- Origin Access Control (OAC) — secure S3 access
- TLS 1.2+ enforcement on all bucket policies
- SSL-only access enforcement
- Configurable security response headers (HSTS, CSP, X-Frame, etc.)
- OWASP cross-origin headers (COOP, COEP, CORP)
- Permissions-Policy (restrict browser features)
- Geo-restriction whitelist
- Optional WAF integration
