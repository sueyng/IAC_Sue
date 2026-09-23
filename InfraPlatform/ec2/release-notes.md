# Release Notes: EC2 Infrastructure

## Version Comparison: v1 vs v2 vs v3 vs v4 vs v5 vs v6 vs v7

### General Updates
- **IaC Version Tag**:
  - Updated from `InfraPlatform-EC2-v1` through `InfraPlatform-EC2-v7`.

### Core Infrastructure (`cf-ec2-launchTemplate.yaml`, `cf-ec2-securitygroups.yaml`, `cf-ec2.yaml`)
- **v2 Updates**:
  - Added support for **IAM Instance Profiles** for EC2 instances.
  - Introduced **Data Volume Configuration**:
    - Optional data volume with configurable size (`DataVolumeSize` parameter).
  - Enhanced **Security Groups**:
    - Added support for `ALBSecurityGroupId` for Application Load Balancer integration.
    - Introduced `EC2DeploymentSecurityGroup` for deployment scenarios.
  - Improved **Tagging**:
    - Added tags for backup schedules (`BACKUP-DAILY`, `BACKUP-WEEKLY`, etc.).

- **v3 Updates**:
  - Enhanced **Launch Template**:
    - Added support for `MetadataOptions` with `HttpTokens: required`.
    - Improved tagging for network interfaces and volumes.
  - Enhanced **Security Groups**:
    - Added conditional rules for Ansible server IPs (`AnsibleServerIP1`, `AnsibleServerIP2`).
    - Introduced `EC2AppSecurityGroup` for application-specific rules.
  - Improved **Volume Configuration**:
    - Added support for `OSVolumeSize` parameter for root volume size.

- **v4 Updates**:
  - Enhanced **Security Policies**:
    - Enforced TLS v1.2 for all connections.
    - Improved handling of multiple VPC CIDR ranges (`VpcCidr1`, `VpcCidr2`, `VpcCidr3`).
  - Enhanced **Launch Template**:
    - Added support for `CW-CONFIG` and `CREATE-AUTO-ALARMS` tags.
  - Improved **Deployment Flow**:
    - Introduced a sequential deployment process for launch templates, security groups, and EC2 instances.

- **v5 Updates**:
  - Added support for **S3 VPC Endpoint Integration**:
    - Configurable via `S3PrefixListId` parameter.
  - Enhanced **Hybrid Connectivity**:
    - Added `HCCVpceCidr` parameter for hybrid connectivity scenarios.
  - Improved **Security Group Rules**:
    - Added conditional egress rules for database subnets.
  - Updated **Engine Version**:
    - Default AMI updated to the latest HCC-hardened version.

- **v6 Updates**:
  - **Two Deployment Approaches** - v6 now offers flexibility:
    - **Option 1**: Original 3-Phase Deployment (Standard)
      - `cf-ec2-launchTemplate.yaml`, `cf-ec2-securitygroups.yaml`, `cf-ec2.yaml`
      - For complex scenarios requiring separate security groups
      - Multiple specialized security groups (Infra, App, Deployment)
    - **Option 2**: NEW - Single-Template Deployment (Simplified)
      - `cf-ec2-deployment.yaml` (all-in-one template)
      - For deployment/utility servers with simplified requirements
      - Console-first deployment experience

  - **Single-Template Deployment Features** (`cf-ec2-deployment.yaml`):
    - **Integrated Security Group**: No separate security group template needed
      - Deployment SG includes infrastructure + Ansible + database rules
      - Reduces deployment from 3 phases to 1 single stack
    - **No Public IP by Default**:
      - `AssociatePublicIpAddress: false` in NetworkInterfaces configuration
      - Private deployment servers for enhanced security
    - **EC2 Key Pair Auto-Creation**:
      - Template automatically creates EC2 key pair
      - Private key stored in SSM Parameter Store automatically
      - Stack output provides EC2KeyPairID for easy retrieval
    - **Custom IAM Role Support**:
      - Option to use existing IAM role or create new one
      - Same functionality as 3-phase deployment
    - **IMDSv2 Enforcement**: Metadata options with `HttpTokens: required`
    - **Optional EBS Data Volume**: Configurable via `DataVolumeSize` parameter
    - **No CloudFormation Exports**: Outputs without Export names for easier stack deletion

  - **Added support for Custom IAM Role Integration** (both deployment options):
    - New parameter `HasCustomEC2IAMRole` to specify whether to use an existing custom IAM role.
    - New parameter `CustomEC2IAMRoleName` for specifying the name of an existing custom IAM role.
    - Enhanced conditional logic to create instance profiles based on custom or template-created IAM roles.

  - **Template Descriptions Updated**:
    - All template descriptions now include version number (v6) for better identification.

  - **Improved IAM Role Management**:
    - Templates can now work with pre-existing custom IAM roles or create new ones as needed.
    - Better separation of concerns between IAM role creation and EC2 provisioning.

  - **Enhanced Parameter Files** (single-template deployment):
    - JSON format (compact) for pipelines: `parameters-ec2-deployment.json`
    - YAML format (with inline documentation) for human readability: `parameters-ec2-deployment.yaml`
      - Quick Start Guide
      - Detailed parameter descriptions with allowed values
      - AWS Console navigation instructions
      - "What's New" section explaining v6 features

- **v7 Updates**:
  - **Extended VPC CIDR Support** (both deployment options):
    - Added `VpcCidr4` parameter for quaternary VPC CIDR range
    - Added `VpcCidr5` parameter for quinary VPC CIDR range
    - Now supports up to 5 VPC CIDR ranges (previously limited to 3)
    - Enhanced infrastructure HTTPS egress rules to include VpcCidr4 and VpcCidr5
    - Better support for complex multi-VPC and hybrid cloud architectures
  
  - **Enhanced Network Flexibility**:
    - Conditional egress rules for VpcCidr4 and VpcCidr5 (HasVpcCidr4, HasVpcCidr5)
    - Optional parameters with empty string defaults (backward compatible with v6)
    - Improved support for organizations with multiple VPC peering connections
    - Better accommodation for large-scale hybrid cloud deployments
  
  - **Template Descriptions Updated**:
    - All template descriptions now properly reference version 7 (v7)
    - cf-ec2-deployment.yaml: "EC2 Template v7 - Single Template Deployment"
    - cf-ec2-launchTemplate.yaml: "EC2 Launch Template v7"
    - cf-ec2-securitygroups.yaml: "EC2 Security Group Conditional Creation based on user choice v7"
    - cf-ec2.yaml: "EC2 v7"
  
  - **Backward Compatibility**:
    - All v7 templates remain fully backward compatible with v6 parameter files
    - VpcCidr4 and VpcCidr5 are optional parameters with default empty values
    - Existing v6 deployments can be upgraded to v7 without parameter changes

### Deployment Flow Updates
- **v2 Updates**:
  - Introduced a deployment order:
    1. Deploy launch templates.
    2. Deploy security groups.
    3. Deploy EC2 instances.

- **v5 Updates**:
  - Enhanced deployment documentation for hybrid connectivity and S3 VPC endpoint integration.

- **v6 Updates**:
  - **Two Deployment Options**:
    - **Option 1**: Original 3-Phase Deployment (Standard)
      1. Deploy launch templates (`cf-ec2-launchTemplate.yaml`)
      2. Deploy security groups (`cf-ec2-securitygroups.yaml`)
      3. Deploy EC2 instances (`cf-ec2.yaml`)
    - **Option 2**: NEW - Single-Template Deployment (Simplified)
      1. Single step: Deploy all resources (`cf-ec2-deployment.yaml`)
         - Creates Deployment SG, IAM role, instance profile, key pair, launch template, and EC2 instance
         - No multi-phase orchestration required
         - Ideal for deployment/utility servers

- **v7 Updates**:
  - **Deployment Flow Unchanged**: 
    - Both deployment options (3-phase and single-template) maintain the same deployment flows as v6
    - New VpcCidr4 and VpcCidr5 parameters are optional and don't affect deployment procedures
  - **Parameter Updates**:
    - VpcCidr4 and VpcCidr5 parameters can be added to existing parameter files (optional)
    - Backward compatible with v6 parameter files (no changes required for upgrade)

### Documentation Updates
- **v2 Updates**:
  - Added detailed descriptions for new parameters (`DataVolumeSize`, `ALBSecurityGroupId`).
  - Updated troubleshooting guide for common issues with security groups.

- **v5 Updates**:
  - Enhanced deployment guide with examples for hybrid connectivity and S3 endpoint configurations.

- **v6 Updates**:
  - **Added Single-Template Deployment Documentation**:
    - README.md updated to document both deployment options (3-phase vs single-template)
    - When to use each deployment approach
    - Parameter reference for `cf-ec2-deployment.yaml`
    - Console-based deployment instructions
    - EC2 Key Pair retrieval guide (SSM Parameter Store)
  - **Enhanced Parameter Files** (single-template deployment):
    - `parameters-ec2-deployment.json` (compact JSON for pipelines)
    - `parameters-ec2-deployment.yaml` (YAML with inline documentation)
    - Quick Start Guide and "What's New" section
  - Added documentation for custom IAM role integration.
  - Updated parameter descriptions for IAM role parameters.

- **v7 Updates**:
  - **README.md Updates**:
    - Updated main heading from "EC2 Instance Template v6" to "EC2 Instance Template v7"
    - Added "What's New in v7" section highlighting extended VPC CIDR support
    - Updated parameter tables to include VpcCidr4 and VpcCidr5 descriptions
    - Version references updated from v6 to v7 throughout
  - **Release Notes Updates**:
    - Added comprehensive v7 section documenting new features
    - Updated version comparison header to include v7
    - Added summary table updates for v7 capabilities
  - **Parameter Documentation**:
    - Documented VpcCidr4 and VpcCidr5 parameters with examples
    - Clarified that new parameters are optional and backward compatible

## Summary of Key Changes
| Feature/Component         | v1                                   | v2                                   | v3                                   | v4                                   | v5                                   | v6                                   |
|---------------------------|---------------------------------------|---------------------------------------|---------------------------------------|---------------------------------------|---------------------------------------|---------------------------------------|
| IaC Version               | InfraPlatform-EC2-v1                 | InfraPlatform-EC2-v2                 | InfraPlatform-EC2-v3                 | InfraPlatform-EC2-v4                 | InfraPlatform-EC2-v5                 | InfraPlatform-EC2-v6                 |
| Deployment Options        | 3-phase only                         | 3-phase only                         | 3-phase only                         | 3-phase only                         | 3-phase only                         | **3-phase OR single-template**       |
| Templates                 | 3 templates                          | 3 templates                          | 3 templates                          | 3 templates                          | 3 templates                          | **3 templates OR 1 template**        |
| Public IP Assignment      | Default (subnet-based)               | Default (subnet-based)               | Default (subnet-based)               | Default (subnet-based)               | Default (subnet-based)               | **Disabled by default (single-template)** |
| EC2 Key Pair Management   | Manual creation                      | Manual creation                      | Manual creation                      | Manual creation                      | Manual creation                      | **Auto-created with SSM storage (single-template)** |
| IAM Instance Profile      | Not supported                        | Supported                            | Supported                            | Supported                            | Supported                            | Supported                            |
| Custom IAM Role Support   | Not supported                        | Not supported                        | Not supported                        | Not supported                        | Not supported                        | **Supported (both options)**         |
| Data Volume Configuration | Not supported                        | Supported                            | Supported                            | Supported                            | Supported                            | Supported                            |
| Security Groups           | Basic                                | ALB integration                      | Ansible IP rules                     | Multi-VPC CIDR support               | S3 VPC Endpoint, Hybrid Connectivity | S3 VPC Endpoint, Hybrid Connectivity |
| Metadata Options          | Not supported                        | Not supported                        | HttpTokens: required                 | HttpTokens: required                 | HttpTokens: required                 | HttpTokens: required                 |
| Volume Configuration      | Basic                                | Data volume                          | OS volume                            | OS volume                            | OS volume                            | OS volume                            |
| Hybrid Connectivity       | Not supported                        | Not supported                        | Not supported                        | Not supported                        | Supported                            | Supported                            |
| Parameter File Formats    | JSON only                            | JSON only                            | JSON only                            | JSON only                            | JSON only                            | **JSON + YAML with docs (single-template)** |

For detailed changes, refer to the respective `README.md` files in the `v1`, `v2`, `v3`, `v4`, `v5`, and `v6` directories.