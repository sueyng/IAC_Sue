# Private API Swagger Samples

The existing VPC Link V1 Swagger is retained unchanged. The VPC Link V2 file
is a new common starting point for `PrivateApi/v4`. Copy the appropriate file
for each application and environment; do not deploy the sample values
unchanged.

## Choose a Sample

| File | Use When | Backend Target |
| --- | --- | --- |
| `swagger-api.json` | Existing reference for legacy, HCC-provisioned VPC Link V1 | NLB already associated with the VPC Link V1 resource |
| `swagger-api-vpclink-v2.json` | The project team deploys VPC Link V2 from `AppSubsystem/APIGateway/VPCLinkV2/v1` | Private ALB or NLB selected by `integrationTarget` |

VPC Link V1 and V2 both use `connectionType: VPC_LINK`. VPC Link V2 additionally requires `integrationTarget` because the V2 link is reusable and is not bound to one load balancer when it is created.

## Provisioning Responsibility

- **VPC Link V1:** Project teams must raise a ticket to HCC for creation in project environments. `AppSubsystem/APIGateway/VPCLink/v1/cf-vpclink.yaml` is for sandbox testing only.
- **VPC Link V2:** Project teams can deploy `AppSubsystem/APIGateway/VPCLinkV2/v1/cf-vpclink-v2.yaml` directly.

## Values to Replace

Replace the application- and environment-specific values in the selected copy
before uploading it to S3. The existing V1 file contains historical sample
values, while the V2 file uses explicit placeholders.

| Value | V1 | V2 | Description |
| --- | --- | --- | --- |
| `info.title` | Required | Required | Application/API name |
| CORS origin | Required | Required | Exact frontend CORS origin |
| Backend integration URI | Required | Required | HTTPS backend hostname and path |
| Existing V1 connection ID | Required | Not used | HCC-provisioned VPC Link V1 ID |
| `replace-with-vpclink-v2-id` | Not used | Required | `VpcLinkV2Id` stack output |
| Example `integrationTarget` ARN | Not used | Required | Sandbox/environment ALB or NLB ARN |
| Existing V1 VPC endpoint ID | Required | Not used | Environment execute-api VPC endpoint used by the embedded policy and endpoint configuration |

The backend hostname must match the certificate presented by the HTTPS listener. For VPC Link V2, `uri` supplies the integration Host header while `integrationTarget` selects the load balancer.

## VPC Link V1 Usage

1. Deploy the backend NLB and confirm its listener and targets are healthy.
2. Obtain the VPC Link V1:
   - Sandbox: deploy `AppSubsystem/APIGateway/VPCLink/v1/cf-vpclink.yaml` with the NLB ARN.
   - Project environment: raise a ticket to HCC and provide the required NLB/environment details.
3. Wait for the VPC Link V1 status to become `AVAILABLE` and obtain the ID from the sandbox stack or HCC.
4. Copy `swagger-api.json` and replace the V1 values listed above.
5. Validate and upload the environment-specific copy to a versioned S3 key.
6. Set `SwaggerBucket`, `SwaggerKey`, and the other `PrivateApi/v4` parameters, then deploy `cf-private-apigw.yaml`.
7. Redeploy the API stage after any later integration changes.

## VPC Link V2 Usage

1. Deploy the private ALB or NLB and confirm its HTTPS listener and targets are healthy.
2. Ensure the backend security group permits TCP 443 from the VPC Link V2 path.
3. Deploy `AppSubsystem/APIGateway/VPCLinkV2/v1/cf-vpclink-v2.yaml`.
4. Wait for the link to become `AVAILABLE` and capture the `VpcLinkV2Id` output.
5. Copy `swagger-api-vpclink-v2.json` and replace the V2 link ID, `integrationTarget` ARN, backend URI, CORS origin, and API title.
6. Validate and upload the environment-specific copy to a versioned S3 key.
7. Set `SwaggerBucket`, `SwaggerKey`, and the other `PrivateApi/v4` parameters, then deploy `cf-private-apigw.yaml`.
8. Redeploy the API stage after any later integration changes.

The VPC Link V2, load balancer, and private API must be in the same AWS account and Region.

## VPC Link V2 Configuration Owned by CloudFormation

The new VPC Link V2 sample intentionally omits the following
environment-specific API Gateway fields:

- `host` and `basePath`
- `x-amazon-apigateway-policy`
- `x-amazon-apigateway-endpoint-configuration`
- API Gateway custom-domain configuration

`cf-private-apigw.yaml` configures the private API's execute-api endpoint association and resource policy from `ApigwVpceId`. It controls the client-facing custom domain through `CustomDomainName` and `SSLCertificateArn`; leaving both empty keeps the custom domain disabled.

The existing `swagger-api.json` V1 reference remains unchanged and retains its
embedded `x-amazon-apigateway-policy` and
`x-amazon-apigateway-endpoint-configuration`. Replace its historical
environment-specific values before reuse.

The V2 sample does not attach an authorizer. Add the application's authorizer
and method security configuration when authorization is required.

## Validation and Testing

Validate the JSON before uploading:

```bash
jq -e . swagger-api.json
jq -e . swagger-api-vpclink-v2.json
```

Use a new/versioned S3 object key for each release. Replacing only the contents of an existing key may not create a new `AWS::ApiGateway::Deployment`; explicitly redeploy the stage after updating an integration.

After deployment, verify the imported integration and invoke at least one real backend method plus the mock `OPTIONS` method. When testing a catch-all `ANY` method with `test-invoke-method`, provide the real verb such as `GET` or `POST`, not `ANY`.
