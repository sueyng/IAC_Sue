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

- **v4.1 Updates** (Security Enhancement — TLS 1.3 / Configurable Security Policy):
  - **`SecurityPolicy` parameterized** (was hardcoded `TLS_1_2` on the custom domain name): new parameter `ApiSecurityPolicy` with `AllowedValues` enforced by CloudFormation:
    - Legacy: `TLS_1_0`, `TLS_1_2`
    - Enhanced (TLS 1.3, optional FIPS/PFS/post-quantum cipher suites): `SecurityPolicy_TLS13_1_2_2021_06`, `SecurityPolicy_TLS13_1_2_PQ_2025_09`, `SecurityPolicy_TLS13_1_2_FIPS_PQ_2025_09`, `SecurityPolicy_TLS13_1_2_PFS_PQ_2025_09`, `SecurityPolicy_TLS13_1_3_2025_09`, `SecurityPolicy_TLS13_1_3_FIPS_2025_09`
    - Default remains `TLS_1_2` — zero behavior change unless a project explicitly opts into an enhanced policy.
  - **Custom Domain Name resource type changed**: `ApiGatewayDomainName` switched from `AWS::ApiGatewayV2::DomainName` to `AWS::ApiGateway::DomainName` (the classic REST API custom domain resource — not `AWS::ApiGateway::DomainNameV2`, which is scoped to private-endpoint-type domain names and was evaluated and rejected for this use case).
    - `AWS::ApiGatewayV2::DomainName`'s `SecurityPolicy` only ever supported `TLS_1_0`/`TLS_1_2` per AWS's own CloudFormation resource schema — it cannot enable TLS 1.3 regardless of what value is supplied.
    - `AWS::ApiGateway::DomainName` was extended by AWS (Nov 2025) with the enhanced `SecurityPolicy_*` values for `REGIONAL`/public custom domain names, which is what this template uses.
    - Property shape changed accordingly: nested `DomainNameConfigurations` list → flat `RegionalCertificateArn` + `EndpointConfiguration.Types: [REGIONAL]`.
  - **New `EndpointAccessMode` parameter** (`BASIC` | `STRICT`, default `BASIC`): required by AWS whenever `ApiSecurityPolicy` is set to an enhanced (`SecurityPolicy_`-prefixed) value. AWS recommends rolling out with `BASIC` first, verifying traffic/access logs, then moving to `STRICT`; mode changes can take up to 15 minutes to fully propagate.
  - **`ApiSecurityPolicy`/`EndpointAccessMode` also applied directly to `PrivateApi`**: `AWS::ApiGateway::RestApi` carries its own independent `SecurityPolicy`/`EndpointAccessMode` properties, separate from the custom domain name's — these are two different TLS termination points. Both must be set for the chosen policy to take effect end-to-end; setting it only on the custom domain leaves the API's own native endpoint (reached directly via the VPC endpoint, bypassing the custom domain) on its default `TLS_1_2`.
  - IaC Version Tag bumped to `AppSubsystem-PrivateApi-v4.1`.

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
  - Changing `ApiGatewayDomainName`'s resource `Type` (`AWS::ApiGatewayV2::DomainName` → `AWS::ApiGateway::DomainName`) means CloudFormation treats it as a resource replacement on an in-place `update-stack` from v4. Review the changeset before applying, and prefer a full stack delete/recreate where feasible — see `v4.1/README.md` for the recommended upgrade procedure.

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
| Custom Domain TLS Policy  | N/A                                   | Hardcoded `TLS_1_2`                  | Hardcoded `TLS_1_2`                  | Hardcoded `TLS_1_2`                             | **Parameterized: `TLS_1_0`/`TLS_1_2` + 6 enhanced TLS 1.3 policies (`ApiSecurityPolicy`)** |
| API's Own Endpoint TLS Policy | AWS default                      | AWS default                          | AWS default                          | AWS default                                     | **Parameterized (`ApiSecurityPolicy` on `PrivateApi` directly)** |
| Logging                   | Basic logging                        | Detailed CloudWatch metrics          | Conditional access logging           | Conditional access logging                      | Conditional access logging |
| Lambda Runtime            | .NET 6                               | .NET 6                               | .NET 8                               | .NET 8                                          | .NET 8 |
| Swagger Integration       | Local file                           | Local file                           | S3-based integration                 | S3-based integration                            | S3-based integration |
| Security                  | Basic VPC endpoint policy            | Enhanced VPC endpoint policy         | Fine-grained access control          | Fine-grained access control                     | Fine-grained access control |
| Response Compression      | Not configured                       | Not configured                       | Not configured                       | Optional toggle (default no; 10 KB threshold)   | Optional toggle (default no; 10 KB threshold) |
| Lambda X-Ray Tracing      | Disabled                             | Disabled                             | Disabled                             | Active (authorizer; scoped X-Ray IAM)           | Active (authorizer; scoped X-Ray IAM) |
| Lambda VPC Config         | Not applied                          | Not applied                          | Not applied                          | Mandatory (TISO compliance; dedicated SG, VpcCidr1-5 egress) | Mandatory (TISO compliance; dedicated SG, VpcCidr1-5 egress) |

For detailed changes, refer to the respective `README.md` files in the `v1`, `v2`, `v3`, `v4`, and `v4.1` directories.
