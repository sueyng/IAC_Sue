# Release Notes: Private API Gateway with Lambda Authorizer

## Version Comparison: v1 vs v2 vs v3 vs v4 vs v4.1

### General Updates
- **IaC Version Tag**:
  - Updated from `PrivateApi-v1` to `PrivateApi-v2`, `PrivateApi-v3`, `PrivateApi-v4`, and `PrivateApi-v4.1` across all templates.

### Core API Gateway Infrastructure (`cf-private-apigw.yaml`)
- **v2 Updates**:
  - Added support for **custom domain names** with SSL certificates.
  - Introduced **X-Ray tracing** for API Gateway stages.
  - Enhanced **logging and observability**:
    - Enabled detailed CloudWatch metrics and request/response logging.
  - Improved **VPC endpoint integration** for private API access.

- **v3 Updates**:
  - Replaced `SwaggerFile` parameter with `SwaggerBucket` and `SwaggerKey` for S3-based Swagger file integration.
  - Added **conditional access logging**:
    - Configurable via `AccessLogFormat` parameter.
    - Log retention period configurable via `LogRetentionInDays`.
  - Enhanced **stage configuration**:
    - Added support for custom log formats and retention policies.
  - Improved **security policies**:
    - Fine-grained access control for VPC endpoint policies.

- **v4 Updates** (Checkmarx Remediation):
  - **Optional API Gateway Response Compression**: Added `EnableCompression` (yes/no, default `no`) + `MinimumCompressionSize` (default `10240` = 10 KB) parameters. When enabled, `MinimumCompressionSize` is applied to the `PrivateApi` — responses ≥ threshold are gzipped when the client sends `Accept-Encoding: gzip`. When `no`, the property is omitted entirely (matches v3 behavior).
    - Addresses Checkmarx finding "API Gateway with invalid compression".
    - Default `no` — project teams should verify their API consumers handle gzip-encoded responses correctly before enabling.
    - Application layer already supports compression; gateway compression is defense-in-depth.
  - **Optional API Gateway Stage Client Certificate**: Added `ApiGatewayClientCertificateId` parameter (default `""`). When provided, `ClientCertificateId` is attached to the REST API stage for backend authentication.
    - Addresses AWS Security Hub control APIGateway.2.
    - Empty default is passed directly as `ClientCertificateId: ""` so a stack update can clear/unset any certificate previously attached to the stage.
    - Project teams create and rotate the API Gateway client certificate outside CloudFormation.
  - IaC Version Tag bumped to `AppSubsystem-PrivateApi-v4`.

- **Version 4.1** (Configurable and support SecurityPolicy from harcoded TLS_1_2)
  - Implemented configurable Security Policy on API Gateway and customDomain
  - Support TLS1.3 (SecurityPolicy_*) by implemented new logical ID `ApiGatewayDomainNameEnhanced`, only apply for new project, required seek SEET Infra Team advise for existing project migration from TLS_1_2 to `SecurityPolicy_*`
  - ⛔ **No direct migration from `TLS_1_2` to `SecurityPolicy_*`**: a v4 stack with a custom domain cannot be upgraded to v4.1 and switched from `TLS_1_2` to a `SecurityPolicy_*` value in the same or a later deployment — the update fails with "domain name already exists" and rolls back. Do not delete the custom domain or the stack to work around this; contact the **SEET Infra team** for assistance.
  
### Lambda Authorizer (`cf-lambda-authorizer.yaml`)
- **v2 Updates**:
  - Added support for **Azure AD integration**:
    - Parameters for `AzureAdClientId` and `AzureAdTenantId`.
  - Introduced **forward proxy support** for outbound requests.
  - Enhanced **IAM policies** for VPC access and logging.

- **v3 Updates**:
  - Updated Lambda runtime to `.NET 8`.
  - Improved **logging configuration**:
    - Dedicated log group for Lambda authorizer logs.
  - Added support for **custom environment variables**.

- **v4 Updates** (Checkmarx Remediation + TISO Compliance):
  - **Lambda X-Ray Tracing**: Added `TracingConfig.Mode: Active` to `LambdaAuthorizerFunction`. Addresses Checkmarx finding "Lambda functions without X-Ray tracing".
  - **Least-privilege X-Ray IAM policy**: Added new inline policy `LambdaAuthorizerXRayWriteAccessPolicy` on `LambdaAuthorizerRole` with scoped `xray:PutTraceSegments` and `xray:PutTelemetryRecords` permissions.
  - **Lambda VPC Configuration (TISO compliance)**: Mandatory `VpcConfig` on `LambdaAuthorizerFunction` for egress control + VPC Flow Log visibility. Aligns with FrontendSPA-Intranet v6 pattern.
    - New dedicated `LambdaAuthorizerSecurityGroup` with least-privilege egress: HTTPS (443) → `VpcCidr1-5` for Logs/X-Ray Interface Endpoints and the organisation's centralised egress path (Azure AD).
    - New required params: `VpcId`, `LambdaSubnetIds`, `VpcCidr1`. New optional params: `VpcCidr2-5`.
    - **Breaking change from v3**: v3 parameter files must add `VpcId`, `LambdaSubnetIds`, `VpcCidr1` (and optionally `VpcCidr2-5`) before upgrading. `ForwardProxyAddress` is unchanged from v3 (still mandatory) — keep the existing value.
  - **Pre-deployment requirements**: target VPC must have `com.amazonaws.<region>.logs` and `com.amazonaws.<region>.xray` Interface Endpoints reachable from `LambdaSubnetIds`; subnets must route to Azure AD via the organisation's centralised egress.
  - IaC Version Tag bumped to `AppSubsystem-PrivateApi-v4`.

- **v4.1 Updates**:
  - No changes. `cf-lambda-authorizer.yaml` is unaffected by the v4.1 TLS/security policy work, which is scoped entirely to `cf-private-apigw.yaml`.

### API Specification (`swagger-api.json`)
- **v2 Updates**:
  - Added support for **CORS headers**:
    - Configurable `Access-Control-Allow-Origin`, `Access-Control-Allow-Methods`, and `Access-Control-Allow-Headers`.
  - Improved **integration with VPC link** for backend services.

- **v3 Updates**:
  - Enhanced **mock integration** for testing API endpoints.
  - Updated API definition to include **custom headers** for security.

### Deployment Flow Updates
- **v2 Updates**:
  - Introduced a deployment order:
    1. Deploy CloudWatch setup.
    2. Deploy Lambda Authorizer.
    3. Deploy Private API Gateway.

- **v3 Updates**:
  - Added support for S3-based Swagger file integration.
  - Improved deployment documentation for custom domain and logging configurations.

- **v4.1 Updates**:
  - Adding new logical ID `ApiGatewayDomainNameEnhanced` to support SecurityPolicy_* by using `ApiGatewayDomainName` — see `v4.1/README.md` for the recommended upgrade procedure.

### Documentation Updates
- **v2 Updates**:
  - Added detailed descriptions for Azure AD integration and VPC endpoint configuration.
  - Updated troubleshooting guide for common issues.

- **v3 Updates**:
  - Enhanced deployment guide with S3-based Swagger integration.
  - Added examples for configuring access logs and retention policies.

- **v4.1 Updates**:
  - Added "Upgrading from v4 to v4.1" section covering the parameter rename and custom domain resource type change.
  - Documented the enhanced `SecurityPolicy_*` values and the AWS resource types that do/don't support them (`AWS::ApiGatewayV2::DomainName` vs `AWS::ApiGateway::DomainName` vs `AWS::ApiGateway::DomainNameV2`).

## Summary of Key Changes
| Feature/Component         | v1                                   | v2                                   | v3                                   | v4                                              | v4.1 |
|---------------------------|---------------------------------------|---------------------------------------|---------------------------------------|---------------------------------------------------|------|
| IaC Version               | PrivateApi-v1                        | PrivateApi-v2                        | PrivateApi-v3                        | PrivateApi-v4                                   | **PrivateApi-v4.1** |
| Custom Domain Support     | Not supported                        | Supported                            | Supported                            | Supported                                       | Supported |
| Custom Domain TLS Policy  | N/A                                   | Hardcoded `TLS_1_2`                  | Hardcoded `TLS_1_2`                  | Hardcoded `TLS_1_2`                             | **Parameterized: `TLS_1_2` + 6 enhanced TLS 1.3 policies (`ApiSecurityPolicy`)** |
| API's Own Endpoint TLS Policy | AWS default                      | AWS default                          | AWS default                          | AWS default                                     | **Parameterized (`ApiSecurityPolicy` on `PrivateApi` directly)** |
| Logging                   | Basic logging                        | Detailed CloudWatch metrics          | Conditional access logging           | Conditional access logging                      | Conditional access logging |
| Lambda Runtime            | .NET 6                               | .NET 6                               | .NET 8                               | .NET 8                                          | .NET 8 |
| Swagger Integration       | Local file                           | Local file                           | S3-based integration                 | S3-based integration                            | S3-based integration |
| Security                  | Basic VPC endpoint policy            | Enhanced VPC endpoint policy         | Fine-grained access control          | Fine-grained access control                     | Fine-grained access control |
| Response Compression      | Not configured                       | Not configured                       | Not configured                       | Optional toggle (default no; 10 KB threshold)   | Optional toggle (default no; 10 KB threshold) |
| Lambda X-Ray Tracing      | Disabled                             | Disabled                             | Disabled                             | Active (authorizer; scoped X-Ray IAM)           | Active (authorizer; scoped X-Ray IAM) |
| Lambda VPC Config         | Not applied                          | Not applied                          | Not applied                          | Mandatory (TISO compliance; dedicated SG, VpcCidr1-5 egress) | Mandatory (TISO compliance; dedicated SG, VpcCidr1-5 egress) |

For detailed changes, refer to the respective `README.md` files in the `v1`, `v2`, `v3`, `v4`, and `v4.1` directories.
