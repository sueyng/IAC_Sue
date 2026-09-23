# NLB and VPC Link CloudFormation Template

This CloudFormation template provisions a Network Load Balancer (NLB) with an associated VPC Link for API Gateway integration in a single deployment.

## Overview

This template combines the functionality of creating both an NLB and VPC Link resources, eliminating the need for separate deployments and cross-stack dependencies. The NLB is configured with security groups, target groups, and listeners, while the VPC Link enables private API Gateway integration.

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Gateway   │    │    VPC Link     │    │      NLB        │
│                 ├────┤                 ├────┤                 │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                                              ┌─────────────────┐
                                              │      ALB        │
                                              │   (Target)      │
                                              └─────────────────┘
```

## Resources Created

- **Network Load Balancer (NLB)**: Internal-facing NLB with TCP listener on port 443
- **Security Group**: Controls inbound/outbound traffic for the NLB
- **Target Group**: Routes traffic to the specified ALB
- **Listener**: Forwards traffic from NLB to target group
- **VPC Link**: Connects API Gateway to the NLB for private integration

## Parameters

### Required Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `AppShortName` | String | Application short name | `apt` |
| `EnvName` | String | Environment name | `nprd`, `prod` |
| `NLBName` | String | Name for the NLB | `apt-nprd-nlb-vpclink` |
| `NLBSubnetIds` | CommaDelimitedList | Subnet IDs for NLB | `subnet-xxx,subnet-yyy` |
| `VpcId` | String | VPC ID where resources will be created | `vpc-xxxxxxxxx` |
| `HealthCheckPath` | String | Health check path for target group | `/ALBhealth` |
| `VPCSubnetCidrAppAZ1` | String | CIDR for AZ1 app subnet | `10.53.144.128/26` |
| `VPCSubnetCidrAppAZ2` | String | CIDR for AZ2 app subnet | `10.53.144.192/26` |

### Optional Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `TargetALBArn` | String | Target ALB ARN | `""` (empty) |
| `PrefixListNLBIngress` | String | Prefix list for NLB ingress | `""` (empty) |
| `APIGWVPCESecurityGroupID` | String | API Gateway VPC Endpoint SG ID | `""` (empty) |
| `VPCSubnetCidrAppAZ3` | String | CIDR for AZ3 app subnet | `""` (empty) |

## Environment Support

The template supports the following environments:
- `nprd`, `nprd-dev`, `nprd-sit1`, `nprd-sit2`, `nprd-sit`, `nprd-sit-a`, `nprd-sit-b`
- `nprd-uat`, `nprd-uat-a`, `nprd-uat-b`, `nprd-pt`, `nprd-pp`, `nprd-pp-a`, `nprd-pp-b`
- `prod`, `prod-a`, `prod-b`

## Outputs

The template provides the following outputs for integration with other resources:

| Output | Description |
|--------|-------------|
| `NLBArn` | ARN of the Network Load Balancer |
| `NLBDNSName` | DNS name of the NLB |
| `VpcLinkId` | ID of the VPC Link |
| `NLBSecurityGroupId` | Security Group ID for the NLB |

## Security Configuration

### NLB Security Group Rules

**Inbound Rules:**
- Port 443 (HTTPS) from specified prefix list (if provided)
- Port 443 (HTTPS) from API Gateway VPC Endpoint security group (if provided)

**Outbound Rules:**
- Port 443 (HTTPS) to App subnet CIDR ranges (AZ1, AZ2, AZ3 if specified)

## Features

### Production Safety
- **Deletion Protection**: Enabled for production environments
- **Retain Policy**: Production resources retained on stack deletion
- **Update Policy**: Production resources retained during stack updates

### Health Checks
- **Protocol**: HTTPS
- **Interval**: 30 seconds
- **Timeout**: 10 seconds
- **Healthy Threshold**: 3
- **Unhealthy Threshold**: 3
- **HTTP Codes**: 200-399

## Migration from Separate Templates

If you're migrating from separate NLB and VPC Link templates:

1. **Export Current Configuration**: Note all parameter values from existing stacks
2. **Plan Downtime**: Resources will be recreated
3. **Delete Old Stacks**: Remove VPC Link stack first, then NLB stack
4. **Deploy Combined Template**: Use this template with combined parameters
5. **Update References**: Update any external references to use new stack outputs

## Troubleshooting

### Common Issues

1. **Template Validation Errors**
   - Verify all required parameters are provided
   - Check parameter value constraints

2. **Resource Creation Failures**
   - Ensure subnets exist and are in the correct VPC
   - Verify security group references are valid
   - Check that ALB target exists (if specified)

3. **Health Check Failures**
   - Verify health check path is accessible
   - Ensure target ALB is responding correctly
   - Check security group rules allow traffic

## Version History

- **v1**: Combined NLB and VPC Link templates (AppSubSystem-nlb-vpclink-v1)

## Support

For issues or questions:
1. Check CloudFormation stack events for detailed error messages
2. Verify all prerequisites are met
3. Review parameter values and template validation
4. Contact ADO team for additional support