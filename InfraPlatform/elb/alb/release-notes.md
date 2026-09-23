# Release Notes: Application Load Balancer (ALB) Infrastructure

## Version Comparison: v1 vs v2 vs v3 vs v4 vs v5

### General Updates
- **IaC Version Tag**:
  - Updated from `InfraPlatform-alb-v1` to `InfraPlatform-alb-v5`.

### Core Infrastructure (`cf-alb-vpce.yaml`)
- **v5 Updates (post-release patch — ELB.4)**:
  - Added **`routing.http.drop_invalid_header_fields.enabled: "true"`** to `ALB.LoadBalancerAttributes` — remediates AWS Security Hub control **ELB.4** ("Application Load Balancer should be configured to drop invalid HTTP headers"). AWS defaults this attribute to `false`, so prior v5 deployments fail ELB.4 until they re-deploy with this patch.
  - **Tag-only attribute change** — `LoadBalancerAttributes` is `Update requires: No interruption`. No ALB replacement, no ARN/DNS change, no listener/target-group impact, no downtime. CloudFormation issues a single `ModifyLoadBalancerAttributes` API call that applies live.
  - **Behavioral note** — after the patch, the ALB drops requests with malformed HTTP headers (RFC 7230 violations). Compliant clients are unaffected. Legacy SOAP/EDI integrations or homegrown HTTP clients that send non-RFC-compliant headers may see HTTP 400s — verify against ALB access logs / `RejectedConnectionCount` in non-prod first.

- **v2 Updates**:
  - Added support for **Additional SSL Certificates**:
    - One additional certificate supported via `AdditionalCertificateArn` parameter.
  - Introduced **TLS Security Policy**:
    - Configurable via `ListenerSslPolicy` parameter (default: `ELBSecurityPolicy-TLS13-1-2-2021-06`).
  - Enhanced **Health Checks**:
    - Configurable health check path and success codes (`200,403`).
  - Improved **Security Group Rules**:
    - Added support for prefix lists for private ALBs.

- **v3 Updates**:
  - Expanded support for **Additional SSL Certificates**:
    - Up to 24 additional certificates supported (`AdditionalCertificateArn1` to `AdditionalCertificateArn24`).
  - Enhanced **Security Policies**:
    - Enforced TLS v1.2 and v1.3 for all connections.
  - Improved **Resource Management**:
    - Added environment-based retention policies for production and non-production environments.
  - Enhanced **Logging**:
    - Added `deletion_protection.enabled` attribute for ALB.

- **v4 Updates**:
  - Added support for **VPC CIDR Configuration**:
    - Parameters for `VpcCidr1`, `VpcCidr2`, and `VpcCidr3` to define IP ranges.
  - Enhanced **Prefix List Support**:
    - Added `PrefixListIdInternet` for whitelisted internet IP ranges.
  - Improved **Security Group Rules**:
    - Conditional rules for public and private ALBs based on prefix lists and CIDR ranges.
  - Enhanced **Logging and Observability**:
    - Improved tagging with `IaCVersion` for better resource tracking.
  - Added support for **HTTP Strict Transport Security (HSTS)**:
    - New parameter `StrictTransportSecurityHeaderValue` for configuring HSTS headers.
    - Conditional `ListenerAttributes` configuration in ALB listener.
    - Support for standard HSTS values: `max-age`, `includeSubDomains`, `preload`.
  - Enhanced **Security Posture**:
    - Optional HSTS enforcement to protect against protocol downgrade attacks.
    - Backward compatibility maintained - HSTS disabled by default.
  - Improved **Documentation**:
    - Added HSTS configuration examples and usage guidelines.

### Deployment Flow Updates
- **v2 Updates**:
  - Introduced a deployment order:
    1. Deploy security groups.
    2. Deploy ALB and target groups.
    3. Configure listeners and certificates.

- **v3 Updates**:
  - Added support for multiple SSL certificates and enhanced logging configurations.

- **v4 Updates**:
  - Enhanced deployment documentation for VPC CIDR and prefix list configurations.
  - Updated parameter files to include HSTS configuration options.
  - Enhanced security best practices documentation.

### Documentation Updates
- **v2 Updates**:
  - Added detailed descriptions for new parameters (`AdditionalCertificateArn`, `ListenerSslPolicy`).
  - Updated troubleshooting guide for common issues with SSL certificates.

- **v3 Updates**:
  - Enhanced deployment guide with examples for multiple SSL certificates.

- **v4 Updates**:
  - Added examples for configuring VPC CIDR ranges and prefix lists.
  - Added comprehensive HSTS configuration guide with security recommendations.
  - Updated parameter file examples to include HSTS settings.
  - Enhanced security features section in README.

## Summary of Key Changes
| Feature/Component         | v1                                   | v2                                   | v3                                   | v4                                   |
|---------------------------|--------------------------------------|--------------------------------------|--------------------------------------|--------------------------------------|
| IaC Version               | InfraPlatform-alb-v1                 | InfraPlatform-alb-v2                 | InfraPlatform-alb-v3                 | InfraPlatform-alb-v4                 | 
| SSL Certificates          | Single certificate                   | One additional certificate           | Up to 24 additional certificates     | Up to 24 additional certificates     | 
| TLS Security Policy       | Basic                                | Configurable                         | Enforced TLS v1.2 and v1.3           | Enforced TLS v1.2 and v1.3           |
| HSTS Support              | Not supported                        | Not supported                        | Not supported                        | **Configurable HSTS headers**        |
| Prefix List Support       | Not supported                        | Supported for private ALBs           | Enhanced                             | Enhanced                             | 
| VPC CIDR Configuration    | Not supported                        | Not supported                        | Not supported                        | Supported                            | 
| Resource Management       | Basic                                | Environment-based retention policies | Environment-based retention policies | Environment-based retention policies | 
| Security Features         | Basic SSL                            | Enhanced SSL + TLS policies          | Multiple certificates + retention    | **HSTS + comprehensive security**    | 



## Migration Guide
### Upgrading to v4
1. **Update CloudFormation template** to the latest v4 version.
2. **Optional**: Add `StrictTransportSecurityHeaderValue` parameter to enable HSTS:
   ```json
   {
       "ParameterKey": "StrictTransportSecurityHeaderValue",
       "ParameterValue": "max-age=31536000; includeSubDomains; preload"
   }
   ```
3. **Deploy** using standard CloudFormation update procedures.
4. **Verify** HSTS headers in HTTP responses (if enabled).

## Security Recommendations
- **Enable HSTS** for public-facing ALBs to enhance security posture.
- **Use strong HSTS policies** with `includeSubDomains` and `preload` directives when appropriate.
- **Test HSTS configuration** in non-production environments before deploying to production.

For detailed changes, refer to the respective `README.md` files in the `v1`, `v2`, `v3`, `v4` and directories.