# Release Notes: EKS Infrastructure Templates

## Version History

### General Updates
- **IaC Version Tag**:
  - Updated from `InfraPlatform-EKS-v1` to `InfraPlatform-EKS-v7` across all templates.

### Core EKS Infrastructure (`cf-eks.yaml`)
- **v2 Updates**:
  - Added support for **Fargate Profiles** for serverless compute.
  - Introduced **IAM Roles** for Fargate Pod Execution.
  - Enhanced **Security Group Rules**:
    - Added rules for deployment servers and ingress controllers.
  - Improved **KMS Key Management**:
    - Added KMS key for secrets encryption.

- **v3 Updates**:
  - Enhanced **KMS Key Rotation**:
    - Automatic key rotation enabled with configurable rotation period (`KMSKeyRotationPeriod`).
    - 7-day pending window for enhanced security during key rotation.
  - Added **OpenTelemetry Service Account Role** for observability with OIDC integration.
  - Introduced **EKS Secrets Management**:
    - Managed via AWS Secrets Manager with KMS encryption.
  - Improved **Load Balancer Configuration**:
    - Added support for hybrid connectivity with up to 3 HSGW subnets.
  - **Custom Port Range Support**:
    - Configurable port ranges for Internal Ingress Controller.
    - Production-validated custom port configurations (7000-15000).
  - **Enhanced Security Groups**:
    - Support for up to 3 HIP deployment servers.
    - Conditional security group rules based on environment parameters.
  - **Production Features**:
    - DeletionPolicy and UpdateReplacePolicy for production environments.
    - 365-day Fargate log retention.

- **v4 Updates**:
  - Added support for **EKS Add-ons**:
    - CoreDNS, cert-manager, kube-state-metrics, metrics-server.
  - Enhanced **Observability**:
    - Dedicated Fargate profile for observability components.
    - Integration with AWS managed observability services.
  - Improved **Security Policies**:
    - Enforced TLS v1.2 for all connections.
    - Enhanced security group rules for multi-AZ deployments.

- **v5 Updates**:
  - **Critical Bug Fixes**:
    - Fixed missing GroupId properties in security group egress rules that were causing deployment failures.
    - Corrected CIDR property naming inconsistencies (CIDRIP → CidrIp) in security group rules.
    - Resolved add-on dependency sequencing issues preventing proper add-on deployment.
    - Fixed security group reference issues that caused stack creation failures.
  - **Enhanced Load Balancer Controller Policy**:
    - Added 6 new IAM permissions for advanced AWS Load Balancer Controller features:
      - `ec2:GetSecurityGroupsForVpc` - Enhanced security group operations for VPC-wide management
      - `ec2:DescribeIpamPools` - IPAM (IP Address Manager) pool integration for advanced networking
      - `elasticloadbalancing:ModifyListenerAttributes` - Advanced listener configuration and customization
      - `elasticloadbalancing:ModifyCapacityReservation` - Load balancer capacity management
      - `elasticloadbalancing:ModifyIpPools` - IP pool management for advanced networking scenarios
      - `elasticloadbalancing:SetRulePriorities` - Rule priority management for complex routing scenarios
  - **Advanced Networking Features**:
    - **Multi-VPC CIDR Support**: Up to 3 VPC CIDR ranges (`VpcCidr1`, `VpcCidr2`, `VpcCidr3`) for complex network topologies.
    - **S3 Prefix List Integration**: Enhanced S3 connectivity via `S3PrefixListId` parameter for secure S3 access.
    - **HCC VPC Endpoint Support**: Hybrid Cloud Connectivity via `HCCVpceCidr` parameter for on-premises integration.
    - **NLB Prefix List Control**: Advanced NLB ingress control via `PrefixListNLBIngress` parameter for network security.
    - **Enhanced Security Group Rules**: Comprehensive ingress and egress rules supporting all networking scenarios.
  - **Enhanced SQS Integration**:
    - Updated SQS policy resource pattern from `${AppShortName}-${EnvName}-sqs-*` to `${AppShortName}-${EnvName}-sqs*` for improved resource pattern matching and flexibility.
  - **Comprehensive Add-on Management**:
    - **4 Core Add-ons**: CoreDNS, cert-manager, kube-state-metrics, metrics-server with automatic deployment.
    - **Proper Dependency Management**: Correct sequencing ensures add-ons deploy without conflicts.
    - **Dedicated Observability Profile**: Fargate profile (`fp_observability`) specifically for monitoring and observability components.
    - **Conflict Resolution**: OVERWRITE policy ensures consistent add-on configurations.
  - **Production Enhancements**:
    - **Consistent Tagging**: All resources tagged with `IaCVersion: InfraPlatform-EKS-V5` for version tracking.
    - **Enhanced Security Groups**: Improved rules for hybrid connectivity, multi-AZ scenarios, and complex network topologies.
    - **Comprehensive SSM Parameters**: 6+ parameters exported for downstream integration and automation.
    - **Production Logging**: Dedicated Fargate Log Group with 365-day retention for audit and compliance.
    - **Production Safeguards**: DeletionPolicy and UpdateReplacePolicy set to 'Retain' for critical production resources.
    - **Resource Count**: Provisions 50+ AWS resources for a complete EKS infrastructure.

- **v6 Updates**:
  - **EKS Access Entry API Authentication**: Modern authentication using AWS EKS Access Entry API, replacing deprecated aws-auth ConfigMap.
  - **Multi-Project Support**: Deploy additional projects to existing EKS clusters with automatic IAM policy creation and Pod Execution Role.
  - **Extended VPC CIDR Support**: Expanded from 3 to 5 VPC CIDR blocks.
  - **CloudFormation Outputs**: EKS cluster name, OIDC provider endpoint, authentication mode, and cluster ARN.

- **v7 Updates**:
  - **EKS etcd Secrets Encryption**: Added conditional `EncryptionConfig` to encrypt Kubernetes secrets at rest using existing KMS key (`EKSkmsKey`).
  - **Encryption Toggle**: Added `EnableEKSSecretsEncryption` parameter, default `true`, so new clusters are encrypted by default while existing v5/v6 cluster upgrades can explicitly set `false` to avoid CloudFormation cluster replacement.
  - **Authentication Migration**: Preserved configurable `EKSAuthenticationMode` for v5 migration; use `API_AND_CONFIG_MAP` during migration before moving to `API`.
  - **Security Group Hardening**: Replaced `IpProtocol: '-1'` (all protocols) with specific port rules — TCP 443 (HTTPS), TCP 10250 (Kubelet), TCP/UDP 53 (DNS) per AWS EKS minimum requirements.
  - Addresses Checkmarx high severity finding for undefined `EncryptionConfig` when encryption is enabled, and medium findings for "Security Group Ingress With All Protocols".
  - **Existing cluster upgrade**: Existing clusters can upgrade only when `EnableEKSSecretsEncryption` is set to `false`; enabling encryption through CloudFormation on an existing cluster still causes replacement. Enable encryption manually via AWS Console if needed.
  - **JSON parameter files removed**: v7 uses YAML parameter files only.

### Fargate Profiles (`cf-eks-fp.yaml`)
- **v7 Updates**:
  - **Multiple-profile IAM naming**: Uses `{AppShortName}-{EnvName}-{FargateProfileName}` for the Secrets Manager, SQS and S3 managed policies, Fargate Pod Execution role and Pod service-account role. Project teams supply only a short application profile purpose such as `frontend`, `backend` or `batch`.
  - **Managed-policy ARN parameters**: Publishes the effective Secrets Manager, SQS and S3 managed-policy ARNs to three profile-specific SSM parameters for downstream reuse.
  - **Name-length validation**: Limits the purpose-only `FargateProfileName` to 15 characters to reduce the risk of generated IAM role names exceeding the 64-character limit.
  - **Existing-stack impact**: Managed policy and Pod service-account role names are replaced during an update. Changing an existing `FargateProfileName` to the purpose-only format also replaces the immutable Fargate profile. When `SecondProjectForExistingEKS` is `yes`, replacing the Pod Execution role changes its ARN and also replaces the profile. Review the change set, Kubernetes service-account annotation and pod rescheduling impact; retained production IAM resources may require controlled cleanup.

- **v2 Updates**:
  - Introduced default Fargate profiles for `default` and `kube-system` namespaces.

- **v3 Updates**:
  - Added support for up to 5 namespaces per Fargate profile.
  - Enhanced namespace configurations for application-specific workloads.

- **v4 Updates**:
  - Added namespaces for observability components:
    - `fargate-container-insights`, `opentelemetry-operator-system`, `cert-manager`, `aws-observability`, `kube-state-metrics`.
  - Enhanced Fargate profile management with dedicated observability support.

- **v5 Updates**:
  - **Enhanced Fargate Profile Management**:
    - Renamed observability profile from `fp_fargate_observability` to `fp_observability` for clarity and consistency.
    - **5 Observability Namespaces**: Support for fargate-container-insights, opentelemetry-operator-system, cert-manager, aws-observability, and kube-state-metrics.
    - **Enhanced SSM Parameter Integration**: Improved cross-stack parameter references for better automation.
    - **Consistent Tagging**: All profiles tagged with `IaCVersion: InfraPlatform-EKS-V5` for version tracking.
    - **Improved Dependency Management**: Better integration with add-on deployment sequences.
  - **Production Features**:
    - Leverages enhanced SSM parameter outputs from core EKS template for seamless integration.
    - Production-ready configurations with proper retention policies.
    - Enhanced error handling for multi-environment deployment scenarios.

### Secrets Management (`cf-eks-secrets.yaml`)
- **v3 Updates**:
  - Introduced AWS Secrets Manager integration for managing application secrets.
  - Added KMS encryption for secrets with production safeguards.

- **v4 Updates**:
  - No major changes.

- **v5 Updates**:
  - **Enhanced Secrets Integration**:
    - Improved integration with SSM parameters for seamless KMS key lookup and cross-stack references.
    - **Production Safeguards**: Enhanced retention policies and consistent tagging with `IaCVersion: InfraPlatform-EKS-V5`.
    - **Better Error Handling**: Improved error handling and validation for environment mapping scenarios.
    - **Multi-Environment Compatibility**: Enhanced compatibility and reliability for multi-environment deployments.
  - **Security Enhancements**:
    - Leverages enhanced KMS key management from core EKS template.
    - Improved secret rotation and lifecycle management capabilities.
    - Better integration with OIDC and service account roles.

### Load Balancer Configuration (`cf-nlb-tg-alb.yaml`)
- **v2 Updates**:
  - Added support for NLB and ALB integration.
  - Configurable health check paths and security group rules.

- **v3 Updates**:
  - Enhanced hybrid connectivity with HSGW subnet support.
  - Improved conditional security group rules for multi-AZ deployments.

- **v4 Updates**:
  - Added support for up to 3 HSGW subnets.
  - Improved ingress listener configuration with support for `TCP` protocol on port `443`.

- **v5 Updates**:
  - **Enhanced Network Load Balancer Features**:
    - **Prefix List Integration**: Advanced NLB ingress control via `PrefixListNLBIngress` parameter for fine-grained network access control.
    - **Enhanced Security Group Rules**: Comprehensive security group rules for hybrid connectivity and multi-AZ scenarios.
    - **Improved Multi-AZ Support**: Better support for complex multi-AZ deployments with enhanced conditional resource creation.
  - **Production Enhancements**:
    - **Consistent Tagging**: All resources tagged with `IaCVersion: InfraPlatform-EKS-V5` for better resource management and tracking.
    - **Enhanced SSM Parameter Outputs**: Improved parameter exports for better downstream integration and automation.
    - **Conditional Resource Creation**: Enhanced logic for optional parameter-based resource creation (HSGW subnets, prefix lists).
    - **Improved Health Checks**: Better health check configuration and target group management.
    - **Enhanced Hybrid Connectivity**: Improved support for on-premises integration scenarios.

### Observability Enhancements
- **v3 Updates**:
  - Introduced OpenTelemetry integration for monitoring.
  - Added Fargate Log Group with a 365-day retention period.

- **v4 Updates**:
  - Enhanced observability with AWS managed services.
  - Added namespaces for observability components.

- **v5 Updates**:
  - **Enhanced Observability Infrastructure**:
    - **Consistent Tagging**: All observability resources tagged with `IaCVersion: InfraPlatform-EKS-V5` for better resource tracking.
    - **Improved Log Group Configuration**: Enhanced Fargate log group setup with production-ready retention policies (365 days).
    - **Better Fargate Profile Integration**: Seamless integration with enhanced observability Fargate profile (`fp_observability`).
    - **Enhanced Monitoring**: Improved integration with CloudWatch and AWS managed observability services.
  - **Production Features**:
    - **Leverages Enhanced Infrastructure**: Built on improved foundation from core EKS template with bug fixes and enhancements.
    - **Better Cross-Stack Integration**: Enhanced SSM parameter integration for seamless observability stack deployment.
    - **Improved Reliability**: Benefits from resolved dependency issues and enhanced error handling.

### Deployment Flow Updates
- **v2 Updates**:
  - Introduced a deployment order:
    1. Deploy EKS cluster.
    2. Deploy Fargate profiles.
    3. Deploy load balancer configurations.

- **v3 Updates**:
  - Added dependencies for secrets management and observability components.

- **v4 Updates**:
  - EKS Add-ons are now deployed as part of the CloudFormation stack.
  - Post-configuration deployment via Ansible is optional.

- **v5 Updates**:
  - **Enhanced Deployment Reliability**:
    - **Critical Bug Fixes**: Resolved security group dependency issues and add-on sequencing problems that could cause deployment failures.
    - **Production Safeguards**: Emphasized comprehensive production safeguards with proper retention policies and resource protection.
    - **Improved Automation**: Enhanced SSM parameter outputs enable better automation and downstream integration.
    - **Consistent Resource Management**: All resources properly tagged and managed with `IaCVersion: InfraPlatform-EKS-V5`.
  - **Deployment Flow Improvements**:
    - **Reliable Add-on Deployment**: All 4 add-ons (CoreDNS, cert-manager, kube-state-metrics, metrics-server) deploy consistently as part of CloudFormation stack.
    - **Enhanced Error Handling**: Better error handling and validation throughout the deployment process.
    - **Streamlined Process**: Improved deployment sequence with proper dependency management reduces manual intervention.

### Documentation Updates
- **v2 Updates**:
  - Added deployment guide for Fargate profiles and load balancer configurations.

- **v3 Updates**:
  - Enhanced documentation for KMS key rotation and secrets management.

- **v4 Updates**:
  - Updated deployment guide to reflect new features and dependencies.
  - Added detailed descriptions for new parameters and features.

- **v5 Updates**:
  - **Comprehensive Documentation Updates**:
    - **Enhanced README Files**: Updated both v3 and v5 README.md files with detailed feature descriptions, troubleshooting guides, and comprehensive parameter documentation.
    - **Version Comparison Tables**: Added detailed comparison tables highlighting differences between template versions and their capabilities.
    - **Parameter Documentation**: Complete parameter reference with valid values, defaults, and usage examples for all templates.
    - **Troubleshooting Guides**: Added common issues and solutions for deployment and operational challenges.
    - **Resource Count Documentation**: Detailed resource counts (50+ resources for v5) to help with planning and capacity management.
    - **Feature Explanations**: Detailed explanations of new features including advanced networking, enhanced security, and add-on management.
  - **Technical Improvements**:
    - **Deployment Guides**: Updated deployment sequences and dependencies for reliable infrastructure provisioning.
    - **Integration Examples**: Added examples for downstream integration using SSM parameters.
    - **Best Practices**: Documented production best practices and configuration recommendations.

## Summary of Key Changes
| Feature/Component | v1 | v2 | v3 | v4 | v5 | v6 | v7 |
|---|---|---|---|---|---|---|---|
| **Authentication** | Basic | Basic | Basic | Basic | ConfigMap | Access Entry API | Access Entry API |
| **Fargate Profiles** | No | Default | 5 namespaces | Observability NS | Enhanced | Multi-project | Multi-project |
| **EKS Add-ons** | No | No | CoreDNS | 4 add-ons | 4 add-ons | 4 add-ons | 4 add-ons |
| **VPC CIDR Support** | Basic | Basic | Basic | Up to 3 | Up to 5 | Up to 5 | Up to 5 |
| **KMS & Encryption** | Basic | KMS | Auto rotation | Enhanced TLS | Production safeguards | Production safeguards | **etcd secrets encryption** |
| **Multi-Project** | No | No | No | No | No | Yes | Yes |
| **etcd Encryption** | No | No | No | No | No | No | **Yes by default; optional opt-out for upgrade** |
| **Parameter Format** | JSON | JSON | JSON | JSON | JSON | JSON + YAML | **YAML only** |

### Key v7 Summary:
- **etcd Secrets Encryption**: Kubernetes secrets encrypted at rest using KMS key by default (`EnableEKSSecretsEncryption: "true"`)
- **Security Group Hardening**: All-protocols rules replaced with specific ports (443, 10250, 53 TCP/UDP)
- **S3 Access Policy**: cf-eks-fp.yaml now includes S3 read/write access for application pods, scoped to `AppShortName*` buckets (GetObject, PutObject, ListBucket, GetBucketLocation)
- Addresses Checkmarx findings for encryption and security group protocols
- Existing clusters: set `EnableEKSSecretsEncryption: "false"` during CloudFormation upgrade to avoid cluster replacement, then enable encryption manually via AWS Console if required
- YAML parameter files only (JSON removed)

For detailed changes, refer to the respective `README.md` files in each version directory.
