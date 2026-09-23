# ELASTIC KUBERNETES SERVICE (EKS) - Version 3.0

**Amazon Elastic Kubernetes Service** (Amazon EKS) is a managed service that eliminates the need to install, operate, and maintain your own Kubernetes control plane on Amazon Web Services (AWS). Kubernetes is an open-source system that automates the management, scaling, and deployment of containerized applications. For more information visit this [site](https://docs.aws.amazon.com/eks/latest/userguide/what-is-eks.html).

## ✅ Current Status
**EKS v3.0 is actively deployed and validated in production environments**
- ✅ **Production Ready**: Confirmed working in ap-southeast-1 region with production workloads
- ✅ **Custom Ports Validated**: Successfully deployed with custom port configurations (7000-15000 range)
- ✅ **Multi-Server Support**: Multi-deployment server patterns validated (up to 3 HIP deployment servers)
- ✅ **Hybrid Connectivity**: HSGW subnet integration operational for hybrid cloud scenarios
- ✅ **Security Features**: KMS key rotation and OIDC integration working as expected
- ✅ **CloudFormation Stability**: Template successfully creates and manages all resources without conflicts

## What's New in Version 3.0

### 🔐 Enhanced Security Features
- **Automatic KMS Key Rotation**: Configurable key rotation periods (default 365 days)
- **OIDC Integration**: Service account roles use OIDC for secure pod authentication
- **Production Safeguards**: Retain policies for production environments

### 🌐 Advanced Networking
- **Custom Port Ranges**: Configurable port ranges for Internal Ingress Controller
- **Hybrid Connectivity**: Support for up to 3 HSGW subnets with automatic security group rules
- **Enhanced Deployment Access**: Support for up to 3 HIP deployment servers

### 🔧 Operational Improvements  
- **EKS Add-ons**: CoreDNS add-on with automatic conflict resolution (OVERWRITE mode)
- **CloudWatch Integration**: Dedicated Fargate log group with 365-day retention policy
- **OpenTelemetry Ready**: Built-in observability with OpenTelemetry service account role using OIDC
- **SSM Parameter Exports**: Comprehensive parameter exports for downstream integration
- **Production Safeguards**: DeletionPolicy and UpdateReplacePolicy set to 'Retain' for production environments
- **7-Day KMS Pending Window**: Secure key rotation with configurable pending period

## Resources Provisioned

These templates provision a complete EKS infrastructure with the following key resources:

### Security and Access Management
* **KMS Key and Alias** for encryption (with automatic key rotation and 7-day pending window)
* **IAM Managed Policies** and Roles for access control with OIDC integration
* **Security Groups** for network security with conditional rules

### Compute and Orchestration
* **EKS Cluster** (fully managed control plane with private endpoints only)
* **Fargate Profiles** (serverless compute for default, kube-system, and monitoring namespaces)
* **EKS Add-ons** (CoreDNS with OVERWRITE conflict resolution)

### Monitoring and Observability
* **OpenTelemetry (OTEL)** service account role with OIDC
* **Fargate Log Group** for centralized logging (365-day retention)
* **CloudWatch integration** for metrics and monitoring

### Networking and Load Balancing
* **Network Load Balancer** (NLB) with optional HSGW subnet support
* **Application Load Balancer** (ALB) Target Group integration
* **Security group configurations** with custom port range support

### Secrets and Configuration
* **Secret Manager Secrets** with KMS encryption
* **SSM Parameters** for cross-stack references and downstream integration

## Template Overview

### 1. **cf-eks.yaml**: Core EKS Infrastructure
* **Purpose**: Creates the main EKS cluster and fundamental resources
* **Key Components**:
  - EKS Cluster with private endpoints only
  - KMS encryption key for secret encryption (with automatic key rotation and 7-day pending window)
  - Default Fargate profiles (default, kube-system, monitoring)
  - EKS Add-ons (CoreDNS with OVERWRITE conflict resolution)
  - CloudWatch Log Group for Fargate logs (365-day retention)
* **CloudFormation Resources Created**:
  - `AWS::EKS::Cluster` - EKS control plane
  - `AWS::EKS::FargateProfile` (2 profiles: default and monitoring)
  - `AWS::EKS::Addon` - CoreDNS addon
  - `AWS::KMS::Key` + `AWS::KMS::Alias` - KMS key for secrets encryption
  - `AWS::IAM::Role` (5 roles: Node, FargateExecution, ClusterService, LoadBalancerController, OpenTelemetry)
  - `AWS::IAM::ManagedPolicy` (5 policies: SecretsManager, LoadBalancer, CloudWatch, ELB, SQS)
  - `AWS::EC2::SecurityGroup` (4 groups: AppIngress, InternalIngress, ClusterSharedNode, ControlPlane)
  - `AWS::EC2::SecurityGroupIngress` (6+ ingress rules with conditional creation)
  - `AWS::EC2::SecurityGroupEgress` (3 egress rules for VPC CIDRs)
  - `AWS::Logs::LogGroup` - Fargate logging
  - `AWS::SSM::Parameter` (6 parameters for downstream integration)
* **IAM Configuration**:
  - Roles:
    - EKS Node Role (for worker nodes)
    - Fargate Pod Execution Role (for Fargate pods)  
    - EKS Cluster Service Role (for control plane)
    - Load Balancer Controller Role (for AWS Load Balancer Controller with OIDC)
    - OpenTelemetry Service Account Role (for monitoring with OIDC)
  - Managed Policies:
    - Secrets Manager Access Policy (for secrets access)
    - Load Balancer Controller Policy (for ALB/NLB management)
    - CloudWatch Metrics Policy (for metrics access)
    - ELB Permissions Policy (for load balancer operations)
    - SQS Access Policy (for queue operations)
* **Security Groups**:
  - App Ingress Controller SG (for frontend traffic with conditional HSGW access)
  - Internal Ingress Controller SG (for backend traffic with custom port support)
  - Cluster Shared Node SG (for node communication)
  - Control Plane SG (for EKS control plane with deployment server access)
* **Advanced Features**:
  - Custom port range support for Internal Ingress Controller
  - Support for up to 3 HIP deployment servers
  - Support for up to 3 HSGW subnets for hybrid connectivity
  - Production-ready deletion and update policies
* **Security Features**:
  - Automatic KMS key rotation for secrets encryption
  - Configurable rotation period (defaults to 365 days) with 7-day pending window
  - OIDC integration for service account roles
  - Conditional security group rules based on environment parameters
* **SSM Parameters Exported**:
  - EKS Control Plane name
  - Fargate Pod Execution Role ARN
  - Secret Manager IAM Policy ARN
  - SQS IAM Policy ARN
  - OIDC Provider Endpoint
  - EKS KMS Key ID

### 2. **cf-eks-fp.yaml**: Application Fargate Profiles
* **Purpose**: Manages application-specific Fargate profiles
* **Key Components**:
  - Custom Fargate profiles
  - Application namespace configurations
  - Pod execution role
  - Support for up to 5 namespaces per profile

### 3. **cf-eks-secrets.yaml**: Secrets Management
* **Purpose**: Manages application secrets
* **Key Components**:
  - AWS Secrets Manager resources
  - KMS encryption integration
  - Environment-specific configurations
  - Production safeguards
* **Limitations**:
  - Currently supports only 2 predefined secrets:
    - Database connection string secret (`<AppShortName>-<EnvName>-docker-ConnectionStrings`)
    - Redis connection string secret (`<AppShortName>-<EnvName>-docker-Redis`)
  - Additional secrets require template modification

### 4. **cf-nlb-tg-alb.yaml**: Load Balancer Configuration
* **Purpose**: Sets up load balancing infrastructure
* **Key Components**:
  - Network Load Balancer
  - NLB Target Group
  - Health check configurations
  - Security group rules
* **Network Access Control**:
  - Optional HSGW/CAG subnet whitelisting (up to 2 subnets)
    - Allows specific HSGW/CAG subnet CIDRs to access NLB
    - Used for hybrid connectivity scenarios
    - Controlled via parameters HSGWSubnet1 and HSGWSubnet2
  - Optional public ALB ingress subnet whitelisting (up to 3 AZs)
    - Allows internet-facing ALB subnets to access NLB
    - Supports multi-AZ deployment
    - Configured via parameters InternetALBSubnetAZ1, InternetALBSubnetAZ2, and InternetALBSubnetAZ3
  - Security group rules automatically created based on provided subnet CIDRs
  - All whitelisting is implemented through NLB security group ingress rules

## Parameters and Their Valid Values

### EKS Cluster (cf-eks.yaml)

| ParameterKey | ValueType | Sample Values | Default | Mandatory | Description |
|--------------|-----------|---------------|---------|-----------|-------------|
| AppShortName | String | my-application | - | Yes | Short name for the application used as prefix for resource naming |
| EnvName | String | nprd, nprd-dev, prod, prod-a | - | Yes | Environment name to determine deployment context and resource configuration |
| AppSubnetIds | List<AWS::EC2::Subnet::Id> | subnet-123232,subnet-2345123 | - | Yes | List of subnet IDs where the EKS cluster will be deployed |
| AWSRegion | String | ap-southeast-1 | - | Yes | AWS region where resources will be deployed |
| VpcId | AWS::EC2::VPC::Id | vpc-120324 | - | Yes | ID of the VPC where EKS cluster will be created |
| VPCSubnetCidrAppAZ1 | String | 10.0.1.0/24 | - | Yes | CIDR range for the first availability zone subnet |
| VPCSubnetCidrAppAZ2 | String | 10.0.2.0/24 | - | Yes | CIDR range for the second availability zone subnet |
| VPCSubnetCidrAppAZ3 | String | 10.0.3.0/24 | - | No | Optional CIDR range for the third availability zone subnet |
| AppIngressNodePort | String | 8080 | - | Yes | Port number for frontend application ingress |
| InternalIngressNodePort | String | 8081 | - | Yes | Port number for backend application ingress |
| HasCustomPorts | String | true, false | false | No | Enable custom port range for InternalIngressController |
| CustomPortStart | Number | 9000 | - | No | Start of custom port range for InternalIngressController |
| CustomPortEnd | Number | 9999 | - | No | End of custom port range for InternalIngressController |
| HIPDeploymentServer01 | String | 10.0.2.4 | - | Yes | IP address of first deployment server |
| HIPDeploymentServer02 | String | 10.0.2.5 | - | Yes | IP address of second deployment server |
| HIPDeploymentServer03 | String | 10.0.2.6 | - | No | Optional IP address of third deployment server |
| DeploymentServerUTL01 | String | 10.0.2.8 | - | Yes | IP address of utility deployment server |
| NLBIngressSecurityGroupId | String | sg-0123456789abcdef0 | - | No | Optional security group ID for NLB ingress |
| HSGWSubnet01 | String | 10.0.4.0/24 | - | No | Optional HSGW Subnet/IP information for hybrid connectivity |
| HSGWSubnet02 | String | 10.0.5.0/24 | - | No | Optional HSGW Subnet/IP information for hybrid connectivity |
| HSGWSubnet03 | String | 10.0.6.0/24 | - | No | Optional HSGW Subnet/IP information for hybrid connectivity |
| KMSKeyRotationPeriod | Number | 365 | 365 | No | Number of days for KMS key rotation period (default 365 days, 7-day pending window) |
| VpcCidr1 | String | 10.0.0.0/16 | - | No | Primary VPC CIDR range for security group egress rules |
| VpcCidr2 | String | 10.1.0.0/16 | - | No | Optional secondary VPC CIDR range for security group egress rules |
| VpcCidr3 | String | 10.2.0.0/16 | - | No | Optional tertiary VPC CIDR range for security group egress rules |
| S3PrefixListId | String | pl-xxxxxxxx | - | No | S3 PrefixList ID for enhanced S3 connectivity |
| HCCVpceCidr | String | 10.3.0.0/24 | - | No | HCC VPC Endpoint Subnet CIDR for hybrid cloud connectivity |

### EKS Fargate Profile (cf-eks-fp.yaml)

| ParameterKey | ValueType | Sample Values | Mandatory | Description |
|--------------|-----------|---------------|-----------|-------------|
| AppShortName | String | my-application | Yes | Short name for the application used as prefix for resource naming |
| EnvName | String | nprd-dev, prod | Yes | Environment name to determine deployment context |
| FargateProfileName | String | my-app-fp | Yes | Name for the Fargate profile |
| Namespace1 | String | namespace1 | Yes | First Kubernetes namespace for the Fargate profile |
| Namespace2 | String | namespace2 | Yes | Second Kubernetes namespace for the Fargate profile |
| Namespace3 | String | namespace3 | No | Optional third Kubernetes namespace |
| Namespace4 | String | namespace4 | No | Optional fourth Kubernetes namespace |
| Namespace5 | String | namespace5 | No | Optional fifth Kubernetes namespace |
| AppSubnetIds | List<AWS::EC2::Subnet::Id> | subnet-123232,subnet-2345123 | Yes | Subnets where Fargate pods will be deployed |

### NLB, Target Group, and ALB (cf-nlb-tg-alb.yaml)

| ParameterKey | ValueType | Sample Values | Mandatory | Description |
|--------------|-----------|---------------|-----------|-------------|
| AppShortName | String | my-application | Yes | Short name for the application used as prefix for resource naming |
| EnvName | String | nprd-dev, prod | Yes | Environment name to determine deployment context |
| AppSubnetIds | List<AWS::EC2::Subnet::Id> | subnet-123232,subnet-2345123 | Yes | Subnets where the NLB will be deployed |
| VpcId | AWS::EC2::VPC::Id | vpc-120324 | Yes | VPC ID where load balancing resources will be created |
| Function | String | APP, WEB | Yes | Type of function the load balancer will serve |
| IngressALBArn | String | arn:aws:elasticloadbalancing:us-west-2:123456789012:loadbalancer/app/example-lb/1 | Yes | ARN of the ALB used for ingress |
| HealthCheckPath | String | /healthz | Yes | Path used for health checks |
| InternetALBSubnetAZ1 | String | 10.0.1.0/24 | No | Optional CIDR for internet-facing ALB in AZ1 |
| InternetALBSubnetAZ2 | String | 10.0.2.0/24 | No | Optional CIDR for internet-facing ALB in AZ2 |
| InternetALBSubnetAZ3 | String | 10.0.3.0/24 | No | Optional CIDR for internet-facing ALB in AZ3 |
| HSGWSubnet1 | String | 10.0.4.0/24 | No | Optional CIDR for first HSGW subnet |
| HSGWSubnet2 | String | 10.0.5.0/24 | No | Optional CIDR for second HSGW subnet |

### EKS Secrets (cf-eks-secrets.yaml)

| ParameterKey | ValueType | Sample Values | Mandatory | Description |
|--------------|-----------|---------------|-----------|-------------|
| AppShortName | String | my-application | Yes | Short name for the application used as prefix for resource naming |
| EnvName | String | nprd-dev, prod | Yes | Environment name to determine deployment context and secret mapping |

## Enhanced Security Features

### KMS Key Rotation

The EKS template now supports automatic key rotation for the KMS key used to encrypt Kubernetes secrets. This security enhancement ensures encryption keys are regularly rotated according to best practices.

**Key Features:**
* Automatic rotation of KMS keys enabled by default
* Configurable rotation period (defaults to 365 days)
* **7-day pending window** before key rotation takes effect for security
* User ability to override rotation period through the `KMSKeyRotationPeriod` parameter

The `KMSKeyRotationPeriod` parameter allows you to specify the number of days between key rotations, with a default value of 365 days (annual rotation) if not specified. The 7-day pending window provides additional security by allowing time to detect and prevent unauthorized key rotations.

### Custom Port Range Support

The Internal Ingress Controller now supports custom port ranges for enhanced networking flexibility:

**Configuration:**
* Set `HasCustomPorts` to "true" to enable custom port range
* Define `CustomPortStart` and `CustomPortEnd` to specify the port range
* Security group rules are automatically created for the custom port range across all AZs
* **Production Validated**: Custom port ranges (7000-15000) have been successfully tested in production
* Useful for applications requiring non-standard port configurations

**Example Configuration in Production:**
```json
{
  "HasCustomPorts": "true",
  "CustomPortStart": "7000",
  "CustomPortEnd": "15000"
}
```

### OIDC Integration

Service account roles now use OIDC (OpenID Connect) for secure authentication:
* **Load Balancer Controller Role** uses OIDC for service account `aws-load-balancer-controller`
* **OpenTelemetry Service Account Role** uses OIDC for service account `otel-collector`
* **Eliminates long-term AWS credentials** in pods for enhanced security
* **Automatic OIDC Provider** endpoint creation and configuration
* **Production Stable**: OIDC integration has been validated in production environments

### Hybrid Connectivity Support

Enhanced support for hybrid cloud scenarios:
* **Up to 3 HSGW** (Hybrid Secure Gateway) subnets can be configured via parameters
* **Automatic security group rules** created for HSGW subnet access
* **Supports complex network topologies** and hybrid connectivity patterns
* **Production Tested**: HSGW integration has been validated in production deployments
* **Conditional Configuration**: Rules are only created when HSGW subnet parameters are provided

**HSGW Configuration Parameters:**
* `HSGWSubnet01` - Primary HSGW subnet CIDR
* `HSGWSubnet02` - Secondary HSGW subnet CIDR  
* `HSGWSubnet03` - Tertiary HSGW subnet CIDR

## Deployment Guide

### Prerequisites
1. Access to Azure DevOps repository for parameter files
2. AWS CLI configured with appropriate permissions for Azure Pipelines
3. Access to deployment tooling server for kubectl operations
4. Required parameter values collected
5. Network infrastructure ready (VPC, subnets)
```
nprd-dev
|_ parameters-eks.json
|_ parameters-eks-fp.json
|_ parameters-nlb-tg-alb.json
|_ parameters-eks-secrets.json
```
### Deployment Sequence
```
HIP Team         Project Team      CloudFormation     Ansible          Kubernetes (EKS)
        |                |                   |               |                 |
        |  Copy params   |                   |               |                 |
        |  & pipelines   |                   |               |                 |
        |--------------->|                   |               |                 |
        |                |                   |               |                 |
        |                | Update            |               |                 |
        |                | parameters        |               |                 |
        |                |-------------------|               |                 |
        |                |                   |               |                 |
        |                | Deploy EKS stack  |               |                 |
        |                |------------------>|               |                 |
        |                |     wait/verify   |-------------------------------->|
        |                |                   |               |                 |
        |--------------------------------------------------->|                 |
        |                |                   |        deploy post-configs      |
        |                |                   |               |---------------->|
        |                |                   |               |                 |
        |                | Deploy Fargate    |               |                 |
        |                | Profiles stack    |               |                 |
        |                |------------------>|               |                 |
        |                |     wait/verify   |-------------------------------->|
        |                |                   |               |                 |
        |                | Deploy K8s        |               |                 |
        |                | ingress config    |               |                 |
        |                |---------------------------------------------------->|
        |                |                   |               |                 |
        |                |              ALB created          |                 |
        |                |<------------------|               |                 |
        |                |     wait/verify   |               |                 |
        |                |                   |               |                 |
        |                | Update NLB params |               |                 |
        |                | with ALB ARN      |               |                 |
        |                |------------------>|               |                 |
        |                |                   |               |                 |
        |                | Deploy NLB stack  |               |                 |
        |                |------------------>|               |                 |
        |                |     wait/verify   |               |                 |
        |                |                   |               |                 |
        |                | Deploy Secrets    |               |                 |
        |                | stack             |               |                 |
        |                |------------------>|               |                 |
        |                |     wait/verify   |               |                 |
        |                |                   |               |                 |
```
## Dependencies and Deployment Flow
1. **Initial Setup**:
   - Parameter files and pipelines provided by HIP team
   - Project team updates parameters in Azure repo

2. **Core Infrastructure**:
   - EKS cluster deployment via CloudFormation
   - Post-configuration deployment via Ansible (otel collectors & operator via helm, metrics-server,etc)

3. **Application Setup**:
   - Fargate profile deployment for application namespaces
   - Kubernetes ingress configuration deployment
   - NLB configuration with ALB integration
   - Secrets management
   - Application deployment:
     - Application pods deployed via Azure Pipeline
     - Uses Ansible playbook with kubectl commands
     - Deploys Kubernetes manifests (deployments, services, etc)
     - Configures application-specific settings

### Tooling Server Requirements
* Access to EKS cluster via kubectl
* Required IAM permissions
* Network connectivity to EKS cluster

## Important Notes

1. The EKS Cluster stack (`cf-eks.yaml`) must be fully created before provisioning other stacks.
2. The KMS key SSM parameter created by the EKS Cluster stack is required for the EKS Secrets stack.
3. The Fargate Profile stack uses SSM parameters created by the EKS Cluster stack.
4. The NLB stack can use the Ingress ALB ARN as a target. This ALB is typically created by the development team using the AWS Load Balancer Controller, which deploys the ALB based on Kubernetes Ingress resources.
5. For production environments (prod, prod-a, prod-b), resources have a DeletionPolicy and UpdateReplacePolicy set to 'Retain'.
6. The EKS Secrets stack uses a mapping for sub-environments (e.g., sit-a, sit-b) to determine the parent environment for KMS key lookup.
7. The NLB stack creates conditional security group rules based on provided subnet CIDRs and HSGW subnets.
8. **Custom Port Configuration**: When enabling custom ports (`HasCustomPorts=true`), ensure that `CustomPortStart` and `CustomPortEnd` parameters are properly configured to avoid security group rule conflicts.
9. **HSGW Subnet Configuration**: HSGW subnets are optional but when provided, they automatically create security group rules for hybrid connectivity. Ensure these subnets don't overlap with existing network configurations.
10. **OIDC Provider**: The template automatically creates OIDC integration for service accounts. This requires the EKS cluster to be fully operational before deploying dependent services.
11. **EKS Add-ons**: CoreDNS add-on is deployed with OVERWRITE conflict resolution, which may override custom configurations during updates.
12. **Log Retention**: Fargate logs are retained for 365 days. Consider your organization's log retention policies before deployment.
13. **Resource Count**: The core EKS template creates approximately 40+ CloudFormation resources. Monitor CloudFormation stack limits in your AWS account.
14. **Conditional Resources**: Many resources are created conditionally based on parameters (HSGW subnets, custom ports, etc.), which affects the final resource count.

### 🎯 Current Deployment Recommendations

Based on active production deployments:

**✅ Recommended Configuration Patterns:**
- **Use custom port ranges** (7000-15000) for internal services - validated in production
- **Deploy in ap-southeast-1 region** for optimal performance and support
- **Configure all 3 HIP deployment servers** plus utility server for redundancy
- **Enable KMS key rotation** with 365-day period and 7-day pending window
- **Use nprd-dev environment** for initial testing and validation
- **Implement OIDC integration** for all service accounts (Load Balancer Controller & OpenTelemetry)

**⚠️ Important Considerations:**
- **Custom port ranges** have been validated in production - recommended for new deployments
- **Security group rules** are optimized for multi-deployment server scenarios
- **OIDC integration** is stable and should be used for all service accounts
- **Template is actively maintained** and receives regular updates
- **7-day KMS pending window** provides additional security for key rotation
- **CoreDNS OVERWRITE mode** may override custom DNS configurations during updates

## 🔄 Version Comparison: v3.0 vs v5.0

### **Should You Upgrade to v5.0?**

| Feature | v3.0 (Current) | v5.0 (Latest) | Recommendation |
|---------|----------------|---------------|----------------|
| **EKS Add-ons** | CoreDNS only | 4 add-ons (CoreDNS, cert-manager, kube-state-metrics, metrics-server) | ⭐ **Upgrade for enhanced monitoring** |
| **Security Group Rules** | Working but basic | Enhanced with critical bug fixes (missing GroupId properties) | ⭐ **Upgrade to prevent deployment failures** |
| **Networking** | Single VPC CIDR | Multi-VPC CIDR support (up to 3) + PrefixListNLBIngress parameter | ✅ **Upgrade if you need complex networking** |
| **S3 Integration** | Basic egress rules | Prefix list support for optimized connectivity (S3PrefixListId parameter) | ✅ **Upgrade for optimized S3 connectivity** |
| **Load Balancer Policy** | Standard permissions | Enhanced with latest AWS permissions (ec2:GetSecurityGroupsForVpc, elasticloadbalancing:SetRulePriorities, etc.) | ⭐ **Upgrade for improved ALB/NLB management** |
| **SQS Resource Pattern** | `sqs-*` pattern | `sqs*` pattern for better flexibility | ✅ **Upgrade for improved SQS access** |
| **Custom Ports** | ✅ Fully supported | ✅ Fully supported | ➖ **No change needed** |
| **OIDC Integration** | ✅ Working | ✅ Enhanced with better error handling | ➖ **Marginal improvement** |
| **Production Stability** | ✅ Proven in production | ✅ Enhanced with additional bug fixes | ⭐ **Upgrade for better reliability** |
| **KMS Rotation** | ✅ 365-day rotation + 7-day pending | ✅ Same features | ➖ **No change needed** |
| **HCC Support** | ✅ Up to 3 HSGW subnets | ✅ Same + dedicated HCCVpceCidr parameter | ✅ **Upgrade for enhanced HCC integration** |

### **Migration Decision Matrix**

**✅ Upgrade to v5.0 if:**
- You need additional monitoring with kube-state-metrics and metrics-server add-ons
- You want cert-manager for automatic certificate management
- You're experiencing CloudFormation deployment issues (v5.0 fixes critical security group GroupId issues)
- You need multi-VPC CIDR support for complex network topologies (up to 3 VPC CIDRs)
- You want enhanced load balancer controller permissions for improved ALB/NLB management
- You need S3 prefix list integration for optimized S3 connectivity
- You need prefix list support for NLB ingress control
- You want the latest security and reliability improvements including enhanced SQS resource patterns

**➖ Stay with v3.0 if:**
- Your current deployment is stable and meets all requirements
- You prefer minimal changes to working production systems
- Your environment doesn't require advanced networking features beyond basic VPC CIDR
- Resource constraints prevent testing new versions in your environment
- You only need CoreDNS add-on (v3.0 is sufficient for basic EKS functionality)
- You don't need the additional monitoring components provided by v5.0 add-ons

### **Migration Timeline Recommendation**
- **Immediate**: If experiencing deployment failures (v5.0 fixes critical issues)
- **Within 3-6 months**: For enhanced monitoring and management capabilities
- **Next maintenance window**: For improved reliability and future-proofing

**Note**: v3.0 remains fully supported, but v5.0 represents the recommended path forward for new deployments and upgrades.

## 🔧 Troubleshooting Common Issues

### CloudFormation Stack Creation Issues
- **Security Group Rule Conflicts**: Ensure VPC CIDR parameters are correctly specified
- **Parameter Validation**: Verify all required parameters are provided and in correct format
- **IAM Permissions**: Ensure deployment role has sufficient permissions for all AWS services used

### EKS Cluster Access Issues
- **Private Endpoints**: Remember the cluster uses private endpoints only - ensure network connectivity
- **OIDC Provider**: Allow time for OIDC provider to be fully created before deploying dependent resources
- **kubectl Access**: Configure kubectl from deployment servers that have network access to cluster

### Custom Port Configuration
- **Port Range Validation**: Ensure CustomPortStart < CustomPortEnd when HasCustomPorts=true
- **Security Group Limits**: AWS has limits on security group rules per security group
- **Application Compatibility**: Verify applications can use the specified custom port range

### KMS Key Rotation
- **Pending Window**: Remember the 7-day pending window before key rotation takes effect
- **Secrets Access**: Existing secrets remain accessible during and after key rotation
- **Permission Issues**: Ensure application roles have kms:Decrypt permissions

---