# Release Notes: Network Load Balancer (NLB) Infrastructure

## Version Comparison: v1 vs v2 vs v3 vs v4 vs v5

### General Updates
- **IaC Version Tag**:
  - Updated from `InfraPlatform-nlb-v1` to `InfraPlatform-nlb-v5`.

### Core Infrastructure (`cf-nlb-tg-alb.yaml`, `cf-nlb-vpclink-tg-alb.yaml`)
- **v5 Updates**:
  - Enhanced **Security Group Inbound/Outbound Rules**:
    - Supports `TargetALBSecurityGroupId` for direct target ECS ALB security group egress forwarding on port 443.
  - Standardized **IaCVersion** tagging across all v5 templates to `InfraPlatform-nlb-v5`.
  - Maintained **TCP Port 443 Pass-Through** architecture:
    - Per AWS Elastic Load Balancing constraints, when an NLB routes to an ALB target group (`TargetType: alb`), the NLB listener protocol must remain `TCP`. TLS termination and ACM certificates are managed at the target ECS ALB HTTPS listener.

- **v2 Updates**:
  - Added support for **VPC Link Integration**:
    - Introduced `cf-nlb-vpclink-tg-alb.yaml` for creating VPC links.
  - Enhanced **Security Group Rules**:
    - Added support for prefix lists (`PrefixListNLBIngress`) for whitelisted ingress traffic.
  - Improved **Health Check Configuration**:
    - Configurable health check path and success codes (`200-399`).
  - Updated **NLB Attributes**:
    - Enabled deletion protection by default.

- **v3 Updates**:
  - Enhanced **Target Group Configuration**:
    - Added support for multiple ALB targets via `TargetALBArn`.
  - Improved **Security Policies**:
    - Enforced TLS v1.2 for all connections.
  - Enhanced **Logging**:
    - Added tagging for better resource tracking (`IaCVersion`).

- **v4 Updates**:
  - Added support for **Hybrid Connectivity**:
    - Parameters for `VPCSubnetCidrAppAZ1`, `VPCSubnetCidrAppAZ2`, and `VPCSubnetCidrAppAZ3` for hybrid connectivity scenarios.
  - Enhanced **Security Group Rules**:
    - Conditional rules for public and private NLBs based on prefix lists and CIDR ranges.
  - Improved **Observability**:
    - Added support for `EnforceSecurityGroupInboundRulesOnPrivateLinkTraffic` for private link traffic.

### Deployment Flow Updates
- **v2 Updates**:
  - Introduced a deployment order:
    1. Deploy security groups.
    2. Deploy NLB and target groups.
    3. Configure listeners and VPC links.

- **v4 Updates**:
  - Enhanced deployment documentation for hybrid connectivity and prefix list configurations.

- **v5 Updates**:
  - Enhanced deployment documentation for direct ALB security group association and TCP 443 pass-through flow.

### Documentation Updates
- **v2 Updates**:
  - Added detailed descriptions for new parameters (`PrefixListNLBIngress`, `TargetALBArn`).
  - Updated troubleshooting guide for common issues with VPC links.

- **v4 Updates**:
  - Enhanced deployment guide with examples for hybrid connectivity and CIDR configurations.

- **v5 Updates**:
  - Updated README with architectural guidance on TCP pass-through and ALB HTTPS TLS termination.

## Summary of Key Changes
| Feature/Component         | v1                                   | v2                                   | v3                                   | v4                                   | v5                                   |
|---------------------------|---------------------------------------|---------------------------------------|---------------------------------------|---------------------------------------|---------------------------------------|
| IaC Version               | InfraPlatform-nlb-v1                 | InfraPlatform-nlb-v2                 | InfraPlatform-nlb-v3                 | InfraPlatform-nlb-v4                 | InfraPlatform-nlb-v5                 |
| Listener Protocol         | TCP                                  | TCP                                  | TCP                                  | TCP                                  | TCP (Pass-Through to ALB)            |
| ACM Certificate Support   | At ECS ALB                           | At ECS ALB                           | At ECS ALB                           | At ECS ALB                           | At ECS ALB                           |
| VPC Link Integration      | Not supported                        | Supported                            | Supported                            | Supported                            | Supported                            |
| Prefix List Support       | Not supported                        | Supported                            | Supported                            | Enhanced                             | Enhanced                             |
| Hybrid Connectivity       | Not supported                        | Not supported                        | Not supported                        | Supported                            | Supported                            |
| Health Check Configuration| Basic                                | Configurable                         | Configurable                         | Configurable                         | Configurable                         |
| Security Group Rules      | Basic                                | Prefix list support                  | Enhanced                             | Hybrid connectivity support          | Target ALB SG support (`TargetALBSecurityGroupId`) |
| Logging                   | Basic                                | Basic                                | Enhanced                             | Enhanced                             | Enhanced                             |

For detailed changes, refer to the respective `README.md` files in the `v1`, `v2`, `v3`, `v4`, and `v5` directories.