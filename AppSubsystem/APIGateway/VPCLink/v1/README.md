# VPC Link with Network Load Balancer Integration

This CloudFormation template deploys a VPC Link that connects API Gateway to private resources through a Network Load Balancer (NLB). It enables API Gateway to access resources within a VPC through private networking.

## Architecture Flow

```
+----------------+     +------------------+     +----------------+     +------------------+     +----------------+
|    Client      |     |   API Gateway    |     |    VPC Link    |     |      NLB         |     |   Backend      |
|(API Gateway)   |---->|   (Private)      |---->|                |---->|                  |---->|   Services     |
|                |     |                  |     |                |     |                  |     |                |
+----------------+     +------------------+     +----------------+     +------------------+     +----------------+

----------------------------------------------------------------
Flow:
1. Client -> API Gateway    : API request through private API
2. API GW -> VPC Link      : Route request through VPC Link
3. VPC Link -> NLB         : Forward to Network Load Balancer
4. NLB -> Backend Services : Distribute traffic to backend services
```

## Relationship with API Gateway

The VPC Link serves as a crucial component in the private API Gateway architecture:

1. Integration Point:
   - VPC Link acts as a bridge between API Gateway and private resources
   - Enables API Gateway to route traffic to internal services through private networking
   - Works in conjunction with the private API Gateway deployment

2. Security Benefits:
   - Allows keeping backend services completely private
   - Traffic stays within AWS network
   - No need for public internet exposure

3. Architectural Connection:
   - Private API Gateway uses VPC Link for backend integration
   - Configured in API Gateway's integration request settings
   - Enables HTTP(S) endpoint integration with private resources

## Prerequisites

Before deploying this template, ensure you have:

1. Network Load Balancer:
   - Deployed and configured NLB
   - NLB ARN available (either directly or in SSM Parameter Store)
   - Proper target groups configured

2. VPC Infrastructure:
   - Properly configured VPC
   - Appropriate subnets for NLB
   - Required security groups

3. API Gateway:
   - Private API Gateway deployment
   - Integration ready to use VPC Link

## Template Parameters

| Parameter | Type | Required | Sample Value | Description |
|-----------|------|----------|--------------|-------------|
| AppShortName | String | Yes | fhir | Application identifier for resource naming |
| EnvName | String | Yes | nprd | Environment name (e.g., nprd, prod) |
| NLBArn | String | No | "" | Network Load Balancer ARN (if empty, fetched from SSM) |

## Resource Details

### VPC Link
- Name Format: `${AppShortName}-${EnvName}-vpclink-nlb`
- Type: AWS::ApiGateway::VpcLink
- Properties:
  - Links to specified NLB
  - Environment-specific naming
  - Conditional ARN resolution


## Troubleshooting

Common issues and solutions:

1. VPC Link Creation Failures:
   - Verify NLB exists and ARN is correct
   - Check SSM parameter if using parameter store
   - Validate NLB configuration

2. Integration Issues:
   - Verify VPC Link ID in API Gateway integration
   - Check NLB target group health
   - Validate security group rules

3. Connectivity Problems:
   - Verify NLB listener configuration
   - Check target group settings
   - Validate network routing and security groups


## Security Considerations

1. Network Security:
   - All traffic stays within AWS network
   - No public internet exposure required
   - Security group controls at NLB level

2. Access Control:
   - API Gateway authorization still applies
   - NLB security group restrictions
   - VPC-level network ACLs

3. Monitoring:
   - CloudWatch metrics for NLB
   - API Gateway access logs
   - VPC Flow Logs if enabled
