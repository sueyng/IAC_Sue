# API Gateway VPC Link V2 with Private ALB/NLB Integration

This CloudFormation template deploys an API Gateway VPC Link V2 that connects API Gateway private integrations to private backend resources through VPC Link ENIs. It enables API Gateway to access private ALB/NLB-backed services without requiring the legacy NLB-only VPC Link v1 pattern.

Use this component for new VPC Link V2 deployments. Do not use it as an in-place replacement for existing `AppSubsystem/APIGateway/VPCLink/v1` stacks.

## Architecture Flow

```
+----------------+     +------------------+     +-------------------+     +------------------+     +----------------+
|    Client      |     |   API Gateway    |     |   VPC Link V2     |     | Private ALB/NLB  |     |   Backend      |
|(API Gateway)   |---->|   (Private)      |---->| ENIs + SG         |---->|                  |---->|   Services     |
|                |     |                  |     |                   |     |                  |     |                |
+----------------+     +------------------+     +-------------------+     +------------------+     +----------------+

----------------------------------------------------------------
Flow:
1. Client -> API Gateway       : API request through private API
2. API GW -> VPC Link V2      : Route request through VPC Link V2
3. VPC Link V2 -> ALB/NLB     : Forward to private load balancer target
4. ALB/NLB -> Backend Services: Route traffic to backend services
```

## Relationship with API Gateway

The VPC Link V2 resource is one part of the private API Gateway architecture:

1. Integration Point:
   - VPC Link V2 acts as the private network bridge between API Gateway and backend ALB/NLB targets.
   - The API Gateway OpenAPI/Swagger integration must reference the VPC Link V2 ID.
   - The API Gateway stage must be redeployed after the integration is updated.

2. Security Benefits:
   - Keeps backend services private.
   - Avoids direct public exposure of backend ALB/NLB targets.
   - Uses a dedicated VPC Link V2 security group for egress control.

3. Architectural Connection:
   - Private API Gateway uses VPC Link V2 for backend private integration.
   - VPC Link V2 creates ENIs in the supplied private subnets.
   - Backend target security groups must allow traffic from the VPC Link V2 path.

## Pipeline Reference

```yaml
MasterCFTemplateFolder: "AppSubsystem/APIGateway/VPCLinkV2/v1"
MasterCFTemplateFilename: "cf-vpclink-v2.yaml"
```

## Prerequisites

Before deploying this template, ensure you have:

1. VPC Infrastructure:
   - VPC ID available.
   - Private subnet IDs available for VPC Link V2 ENIs.
   - Subnets must have network reachability to the backend private ALB/NLB target.

2. Backend Target:
   - Private ALB or NLB deployed and reachable from the selected VPC Link V2 subnets.
   - Backend listener available on HTTPS port `443`.
   - Backend target security group allows inbound traffic from the VPC Link V2 ENI/security group path.

3. API Gateway:
   - Private API Gateway deployment.
   - OpenAPI/Swagger integration ready to reference VPC Link V2.
   - Stage redeployment planned after integration update.

## Template Parameters

| Parameter | Type | Required | Sample Value | Description |
|-----------|------|----------|--------------|-------------|
| AppShortName | String | Yes | fhir | Application identifier for resource naming |
| EnvName | String | Yes | nprd-dev | Environment name |
| VpcId | AWS::EC2::VPC::Id | Yes | vpc-0123456789abcdef0 | VPC where VPC Link V2 ENIs and security group are created |
| VpcLinkSubnetIds | List<AWS::EC2::Subnet::Id> | Yes | subnet-aaa,subnet-bbb | Subnets where API Gateway creates VPC Link V2 ENIs |
| VpcLinkSubnetCidr1 | String | Yes | 10.10.1.0/24 | Primary backend target subnet CIDR allowed for egress |
| VpcLinkSubnetCidr2 | String | No | 10.10.2.0/24 | Secondary backend target subnet CIDR allowed for egress |
| VpcLinkSubnetCidr3 | String | No | 10.10.3.0/24 | Tertiary backend target subnet CIDR allowed for egress |

## Resource Details

### VPC Link V2
- Name Format: `${AppShortName}-${EnvName}-vpclink-v2`
- Type: `AWS::ApiGatewayV2::VpcLink`
- Properties:
  - Creates VPC Link V2 ENIs in the supplied subnets.
  - Associates the VPC Link V2 ENIs with the managed security group.
  - Outputs the VPC Link V2 ID for API Gateway integration usage.

### VPC Link V2 Security Group
- Name Format: `${AppShortName}-${EnvName}-vpclink-v2-sg`
- Type: `AWS::EC2::SecurityGroup`
- Rules:
  - Ingress: none
  - Egress: TCP `443` to `VpcLinkSubnetCidr1`
  - Optional egress: TCP `443` to `VpcLinkSubnetCidr2` and `VpcLinkSubnetCidr3`

## Usage

1. Deploy this VPC Link V2 template as a separate stack.
2. Capture the `VpcLinkV2Id` output.
3. Update the API Gateway OpenAPI/Swagger private integration to reference the VPC Link V2 ID and backend target.
4. Redeploy the API Gateway stage.
5. Test backend connectivity through API Gateway.

Example pipeline values:

```yaml
MasterCFTemplateFolder: "AppSubsystem/APIGateway/VPCLinkV2/v1"
MasterCFTemplateFilename: "cf-vpclink-v2.yaml"
```

## Migration from VPC Link v1

Existing `AppSubsystem/APIGateway/VPCLink/v1` stacks should not be switched in place.

Recommended cutover pattern:

1. Keep the existing VPC Link v1 stack running.
2. Provision this VPC Link V2 stack separately.
3. Update the API Gateway integration/swagger to use the new VPC Link V2 ID.
4. Redeploy the API Gateway stage.
5. Test traffic through the VPC Link V2 path.
6. Remove the old VPC Link v1 stack only after successful cutover.

## Troubleshooting

Common issues and solutions:

1. VPC Link V2 Creation Failures:
   - Verify `VpcId` exists.
   - Verify all subnet IDs belong to the selected VPC.
   - Verify API Gateway has permission to create VPC Link ENIs.

2. Integration Issues:
   - Verify the API Gateway integration references the VPC Link V2 ID.
   - Verify the API Gateway stage was redeployed after integration changes.
   - Verify the backend integration target is the intended private ALB/NLB.

3. Connectivity Problems:
   - Verify backend listener is available on port `443`.
   - Verify VPC Link V2 subnet routing to the backend target.
   - Verify backend security group inbound rules allow the VPC Link V2 path.
   - Verify VPC Link V2 security group egress CIDRs match the backend target subnet ranges.

## Security Considerations

1. Network Security:
   - Backend services remain private.
   - VPC Link V2 ENIs are created only in the supplied private subnets.
   - VPC Link V2 security group egress is limited to TCP `443` for supplied CIDRs.

2. Access Control:
   - API Gateway authorization still applies.
   - Backend ALB/NLB security group controls still apply.
   - VPC-level routing and network ACLs still apply.

3. Operations:
   - Changes to VPC Link V2 subnet IDs or security group IDs can require replacement.
   - API Gateway stage redeployment is required after integration changes.
   - Keep v1 and v2 side by side during migration until traffic testing is complete.
