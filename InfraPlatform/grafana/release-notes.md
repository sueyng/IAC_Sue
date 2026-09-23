# Release Notes: Grafana Infrastructure Templates

## Version Comparison: v1 vs v2 vs v3 vs v4 vs v5 vs v6

### General Updates
- **IaC Version Tag**:
  - Updated from `InfraPlatform-grafana-v1` to `InfraPlatform-grafana-v6`.

### Core Infrastructure (`cf-grafana.yaml`)
- **v2 Updates**:
  - Added support for **AWS::EC2::PrefixList**:
    - Configurable prefix lists for office networks and secure web gateways.
  - Enhanced **IAM Role**:
    - Added `AWSXrayReadOnlyAccess` managed policy for tracing.
  - Improved **Authentication Providers**:
    - Added support for `AWS_SSO` and `SAML` authentication providers.
  - Updated **Grafana Version**:
    - Default version updated to `9.4`.
  - Enhanced **Subnet Configuration**:
    - Introduced `AppSubnetIDs` parameter for multiple subnets.

- **v3 Updates**:
  - Added support for **VPC CIDR Configuration**:
    - Parameters for `VpcCidr1` and `VpcCidr2` to define IP ranges.
  - Enhanced **Security Group Rules**:
    - Conditional egress rules for multiple VPC CIDRs and hybrid connectivity.
  - Improved **IAM Policies**:
    - Added permissions for CloudWatch, EC2, and tagging services.
  - Enhanced **Prefix List**:
    - Updated prefix list entries for office networks and secure web gateways.

- **v4 Updates**:
  - Added support for **Hybrid Connectivity**:
    - Introduced `HCCVpceCidr` parameter for hybrid VPC endpoint configurations.
  - Enhanced **Logging and Observability**:
    - Added `IaCVersion` tag for better resource tracking.
  - Improved **Security Group Rules**:
    - Conditional rules for public and private Grafana workspaces based on prefix lists and CIDR ranges.
  - Updated **Grafana Workspace**:
    - Enabled `PluginAdmin` for managing plugins.

- **v5 Updates**:
  - Updated **Grafana Version**:
    - Default version updated to `9.8`.
  - Enhanced **Parameter Documentation**:
    - Added/updated parameter descriptions in the deployment documentation.
  - Improved **CIDR and Subnet Handling**:
    - Validated and clarified usage of `VpcCidr1`, `VpcCidr2`, and `AppSubnetIDs` parameters.
  - General maintenance and minor bug fixes.

- **v6 Updates**:
  - **Extended VPC CIDR Support**:
    - Added `VpcCidr3`, `VpcCidr4`, and `VpcCidr5` parameters for expanded network connectivity
    - Supports up to 5 VPC CIDR ranges for multi-VPC peering, hybrid cloud, and cross-region patterns
  - **Enhanced Security Group Rules**:
    - Added conditional egress rules for VpcCidr3, VpcCidr4, and VpcCidr5 (port 443/HTTPS)
    - New conditions: `HasVpcCidr3`, `HasVpcCidr4`, and `HasVpcCidr5`
  - **Improved Network Flexibility**:
    - Enables complex multi-VPC architectures
    - Enhanced support for peered VPCs and hybrid cloud connectivity
    - Backward compatible with existing v5 configurations

### Deployment Flow Updates
- **v2 Updates**:
  - Introduced a deployment order:
    1. Deploy prefix lists.
    2. Deploy security groups.
    3. Deploy Grafana workspace.

- **v4 Updates**:
  - Enhanced deployment documentation for hybrid connectivity and prefix list configurations.

- **v5 Updates**:
  - Updated deployment instructions to reflect new parameter requirements and Grafana version.

- **v6 Updates**:
  - Enhanced deployment guide with examples for multi-VPC CIDR configurations and peered VPC scenarios.

### Documentation Updates
- **v2 Updates**:
  - Added detailed descriptions for new parameters (`AppSubnetIDs`, `AuthProvider`).
  - Updated troubleshooting guide for common issues with authentication providers.

- **v4 Updates**:
  - Enhanced deployment guide with examples for hybrid connectivity and CIDR configurations.

- **v5 Updates**:
  - Added a parameter reference table to the README for `v5`.
  - Updated example parameter files to reflect new defaults and best practices.

- **v6 Updates**:
  - Updated parameter reference table to include VpcCidr3, VpcCidr4, and VpcCidr5.
  - Enhanced parameter documentation with multi-VPC peering and hybrid cloud use cases.

## Summary of Key Changes
| Feature/Component         | v1                                   | v2                                   | v3                                   | v4                                   | v5                                   | v6                                   |
|---------------------------|---------------------------------------|---------------------------------------|---------------------------------------|---------------------------------------|---------------------------------------|---------------------------------------|
| IaC Version               | InfraPlatform-grafana-v1             | InfraPlatform-grafana-v2             | InfraPlatform-grafana-v3             | InfraPlatform-grafana-v4             | InfraPlatform-grafana-v5             | InfraPlatform-grafana-v6             |
| Prefix List Support       | Not supported                        | Supported                            | Enhanced                             | Enhanced                             | Enhanced                             | Enhanced                             |
| Authentication Providers  | AWS_SSO                              | AWS_SSO, SAML                        | AWS_SSO, SAML                        | AWS_SSO, SAML                        | AWS_SSO, SAML                        | AWS_SSO, SAML                        |
| VPC CIDR Configuration    | Not supported                        | Not supported                        | Supported                            | Supported                            | Supported                            | **VpcCidr1/2/3/4/5 (5 ranges)**      |
| VPC CIDR Range Support    | N/A                                  | N/A                                  | VpcCidr1/2                           | VpcCidr1/2                           | VpcCidr1/2                           | **VpcCidr1/2/3/4/5**                 |
| Hybrid Connectivity       | Not supported                        | Not supported                        | Not supported                        | Supported                            | Supported                            | **Enhanced**                         |
| Grafana Version           | 8.4                                  | 9.4                                  | 9.4                                  | 9.4                                  | 9.8                                  | 9.8                                  |
| Security Group Rules      | Basic                                | Prefix list support                  | Enhanced                             | Hybrid connectivity support          | Hybrid connectivity support          | **Enhanced with 5 CIDR egress rules** |
| Plugin Admin              | Not supported                        | Not supported                        | Not supported                        | Enabled                              | Enabled                              | Enabled                              |
| Parameter Documentation   | Basic                                | Improved                             | Improved                             | Improved                             | Detailed table in README             | **Enhanced with multi-VPC guidance**  |

For detailed changes, refer to the respective `README.md` files in the `v1`, `v2`, `v3`, `v4`, `v5`, and `v6` directories.