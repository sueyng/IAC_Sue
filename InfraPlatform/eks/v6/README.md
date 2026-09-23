# ELASTIC KUBERNETES SERVICE (EKS) - Version 6.0

**Amazon Elastic Kubernetes Service** (Amazon EKS) is a managed service that eliminates the need to install, operate, and maintain your own Kubernetes control plane on Amazon Web Services (AWS). Kubernetes is an open-source system that automates the management, scaling, and deployment of containerized applications. For more information visit this [site](https://docs.aws.amazon.com/eks/latest/userguide/what-is-eks.html).

## ✅ Current Status
**EKS v6.0 represents the latest production-ready template with EKS Access Entry API authentication, multi-project support and enhanced networking**
- ✅ **EKS Access Entry API Authentication**: Modern authentication using AWS EKS Access Entry API, replacing deprecated aws-auth ConfigMap
- ✅ **Configurable Authentication Mode**: Choose between API, CONFIG_MAP, or API_AND_CONFIG_MAP (Hybrid) modes
- ✅ **Multi-Project Support**: Deploy multiple projects to a single EKS cluster with automatic IAM policy creation
- ✅ **Extended VPC CIDR Support**: Now supports up to 5 VPC CIDR blocks for complex network topologies
- ✅ **Simplified Fargate Profile Deployment**: Automatic Pod Execution Role creation for second projects
- ✅ **Enhanced Conditional Logic**: Streamlined template conditions for better maintainability
- ✅ **CloudFormation Outputs**: EKS cluster name, OIDC provider endpoint, authentication mode, and cluster ARN exposed
- ✅ **Consistent Tagging**: All resources tagged with InfraPlatform-EKS-v6

## What's New in Version 6.0

### 🔐 **EKS Access Entry API Authentication (NEW)**
- **Modern Authentication**: Uses AWS EKS Access Entry API (API mode) for cluster authentication
- **Configurable Authentication Mode**: New `EKSAuthenticationMode` parameter allows selection between:
  - `API` - Uses EKS Access Entry API only (recommended for new clusters)
  - `CONFIG_MAP` - Uses aws-auth ConfigMap only (legacy mode)
  - `API_AND_CONFIG_MAP` - Uses both methods (Hybrid mode, **use this for v5 migration**)
- **Seamless v5 Migration**: Simply update CloudFormation parameter to `API_AND_CONFIG_MAP` and deploy
- **Replaces aws-auth ConfigMap**: No longer relies on deprecated aws-auth ConfigMap approach by default
- **Cluster Creator Admin Access**: The IAM principal deploying the stack automatically gets cluster admin access
- **Benefits**:
  - Manage access via AWS Console, CLI, or CloudFormation
  - Better audit trail via CloudTrail
  - No need to kubectl into cluster to manage access
  - Simplified IAM integration

**For v5 to v6 Migration**: See [v5 to v6 Migration Guide](#v5-to-v6-migration-guide) section below.

### 🎯 **Multi-Project Support**
- **Second Project Deployment**: Deploy additional projects to existing EKS clusters without recreating infrastructure
- **Automatic IAM Policy Creation**: SecretManager and SQS policies created automatically for second projects
- **Automatic Pod Execution Role**: No manual IAM role creation needed when deploying second projects
- **Simplified Parameters**: Reduced complexity with automatic resource creation based on deployment mode

### 🌐 **Extended Networking Capabilities**
- **5 VPC CIDR Support**: Expanded from 3 to 5 VPC CIDR blocks (VpcCidr1-5) for complex network architectures
- **Comprehensive Security Group Rules**: Automatic security group egress rules for all 5 CIDR blocks
- **Enhanced DNS Support**: TCP and UDP DNS rules for all VPC CIDRs

### 🔧 **Template Enhancements**
- **Streamlined Conditions**: Removed redundant conditions (UseSSMParameters replaced with IsSecondProject)
- **Removed Mappings**: Simplified FargatePodExecutionRole by removing ServicePrincipalPartitionMap
- **CloudFormation Outputs**: Added EKSClusterName, OIDCProviderEndpoint, and EKSAuthenticationMode outputs for easy integration
- **Fixed Fn::Or Limits**: Resolved CloudFormation Fn::Or 10-item limit in cf-eks-secrets.yaml

### 📋 **Deployment Modes**
- **First Project Mode** (SecondProjectForExistingEKS="no"):
  - Uses SSM parameters from main EKS stack
  - References existing Pod Execution Role
  - Standard deployment for primary project
  
- **Second Project Mode** (SecondProjectForExistingEKS="yes"):
  - Creates dedicated Pod Execution Role automatically
  - Creates dedicated SecretManager and SQS IAM policies
  - Uses direct parameter values (ClusterName, OidcProviderEndpoint)
  - Enables multiple independent projects on same cluster

## What's New in Version 5.0

### 🚀 **Enhanced EKS Add-ons**
- **Multiple Add-ons**: CoreDNS, cert-manager, kube-state-metrics, and metrics-server deployed automatically
- **Conflict Resolution**: OVERWRITE policy ensures consistent add-on configurations
- **Dependency Management**: Proper sequencing of add-on deployments

### 🐛 **Critical Bug Fixes**
- **Security Group Rules**: Fixed missing GroupId properties in egress controller rules
- **CIDR Property Names**: Corrected CIDRIP → CidrIp naming inconsistencies
- **Add-on Dependencies**: Resolved deployment sequence issues causing failures

### 🔐 **Advanced Security Features**
- **Enhanced Load Balancer Controller Policy**: Additional permissions including ec2:GetSecurityGroupsForVpc, ec2:DescribeIpamPools, elasticloadbalancing:ModifyListenerAttributes, elasticloadbalancing:ModifyCapacityReservation, elasticloadbalancing:ModifyIpPools, and elasticloadbalancing:SetRulePriorities
- **Comprehensive Egress Rules**: Fixed and enhanced security group egress rules for proper cluster communication
- **Production Safeguards**: Improved retention policies for production environments
- **Enhanced IAM Policies**: Updated policies with latest AWS permissions and best practices

### 🌐 **Advanced Networking & Connectivity**
- **Multi-VPC CIDR Support**: Up to 3 VPC CIDR ranges for complex network topologies
- **HCC VPC Endpoint Support**: Dedicated support for Hybrid Cloud Connectivity via HCCVpceCidr parameter
- **S3 Prefix List Integration**: Enhanced connectivity to S3 services via S3PrefixListId parameter
- **Prefix List NLB Ingress**: New PrefixListNLBIngress parameter for whitelisted NLB ingress control
- **Improved Security Group Rules**: Comprehensive ingress and egress rules for all scenarios
- **Enhanced SQS Resource Pattern**: Updated SQS policy resource pattern from `${AppShortName}-${EnvName}-sqs-*` to `${AppShortName}-${EnvName}-sqs*` for better flexibility

### 📊 **Enhanced Observability**
- **Dedicated Observability Profile**: Separate Fargate profile for monitoring components
- **Extended Namespace Support**: Support for kube-state-metrics namespace
- **Enhanced Logging**: Improved log group configuration with consistent tagging

### 🔧 **Operational Improvements**
- **Consistent Tagging**: All resources tagged with `InfraPlatform-EKS-v6`
- **Enhanced SSM Parameters**: Comprehensive parameter exports for integration
- **Improved Resource Naming**: Consistent naming conventions across all resources

---

## Resources Provisioned

These templates provision a complete EKS infrastructure with the following key resources:

### Security and Access Management
* **KMS Key and Alias** for encryption (with automatic key rotation and 7-day pending window)
* **IAM Managed Policies** and Roles for access control with OIDC integration
* **Security Groups** for network security with enhanced multi-VPC CIDR support

### Compute and Orchestration
* **EKS Cluster** (fully managed control plane with private endpoints only)
* **Fargate Profiles** (serverless compute)
* **EKS Add-ons** (CoreDNS, cert-manager, kube-state-metrics, metrics-server) with automatic deployment and dependency management

### Monitoring and Observability
* **OpenTelemetry (OTEL)** service account role with OIDC integration
* **Fargate Log Group** for centralized logging (365-day retention)
* **CloudWatch integration** for metrics and monitoring
* **Dedicated observability namespace** support (kube-state-metrics, cert-manager, aws-observability)

### Networking and Load Balancing
* **Network Load Balancer** (NLB) with prefix list ingress support
* **Application Load Balancer** (ALB) Target Group integration
* **Enhanced security group configurations** with multi-VPC CIDR and HCC support

### Secrets and Configuration
* **Secret Manager Secrets** with KMS encryption
* **SSM Parameters** for cross-stack references and downstream integration
* **Enhanced SQS access policy** with flexible resource patterns

## Template Overview

### 1. **cf-eks.yaml**: Core EKS Infrastructure
* **Purpose**: Creates the main EKS cluster and fundamental resources
* **Key Components**:
  - EKS Cluster with private endpoints only and configurable authentication mode
  - KMS encryption key for secret encryption (with automatic key rotation and 7-day pending window)
  - Default Fargate profiles:
    - `fp_default` (default, kube-system namespaces)
    - `fp_observability` (fargate-container-insights, opentelemetry-operator-system, cert-manager, aws-observability, kube-state-metrics namespaces)
  - EKS Add-ons with automatic deployment and dependency management:
    - CoreDNS (service discovery)
    - cert-manager (certificate management) - depends on fp_observability
    - kube-state-metrics (Kubernetes objects metrics) - depends on fp_observability
    - metrics-server (resource metrics) - runs in kube-system namespace
  - CloudWatch log group for Fargate logs with 365-day retention
* **CloudFormation Resources Created**:
  - `AWS::EKS::Cluster` - EKS control plane
  - `AWS::EKS::FargateProfile` (2 profiles: fp_default and fp_observability)
  - `AWS::EKS::Addon` (4 add-ons: CoreDNS, cert-manager, kube-state-metrics, metrics-server)
  - `AWS::KMS::Key` + `AWS::KMS::Alias` - KMS key for secrets encryption
  - `AWS::IAM::Role` (5 roles: Node, FargateExecution, ClusterService, LoadBalancerController, OpenTelemetry)
  - `AWS::IAM::ManagedPolicy` (5 policies: SecretsManager, Enhanced LoadBalancer, CloudWatch, ELB, SQS)
  - `AWS::EC2::SecurityGroup` (4 groups: AppIngress, InternalIngress, ClusterSharedNode, ControlPlane)
  - `AWS::EC2::SecurityGroupIngress` (6+ ingress rules with conditional creation)
  - `AWS::EC2::SecurityGroupEgress` (3+ egress rules for VPC CIDRs and HCC)
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
    - Enhanced Load Balancer Controller Policy (for ALB/NLB management with latest AWS permissions)
    - CloudWatch Metrics Policy (for metrics access)
    - ELB Permissions Policy (for load balancer operations)
    - SQS Access Policy (for queue operations with flexible resource patterns)
* **Security Groups with Enhanced Rules**:
  - App Ingress Controller SG (for frontend traffic with HSGW access and egress rules)
  - Internal Ingress Controller SG (for backend traffic with VPC CIDR egress support and prefix list ingress)
  - Cluster Shared Node SG (for node communication with VPC-wide egress and HCC support)
  - Control Plane SG (comprehensive ingress/egress rules for EKS control plane)
* **Advanced Networking Features**:
  - Support for up to 3 VPC CIDR ranges for complex network topologies
  - HCC (Hybrid Cloud Connectivity) VPC endpoint support via HCCVpceCidr parameter
  - S3 prefix list integration for enhanced S3 connectivity via S3PrefixListId parameter
  - Prefix list NLB ingress support via PrefixListNLBIngress parameter
  - Comprehensive egress rules for proper cluster communication
* **Security Features**:
  - Automatic KMS key rotation for secrets encryption
  - Configurable rotation period (defaults to 365 days) with 7-day pending window
  - OIDC integration for service account roles
  - Production-ready deletion and update policies
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
  - Optional HSGW/CAG subnet whitelisting (up to 3 subnets)
    - Allows specific HSGW/CAG subnet CIDRs to access NLB
    - Used for hybrid connectivity scenarios
    - Controlled via parameters HSGWSubnet01, HSGWSubnet02, and HSGWSubnet03
  - Security group rules automatically created based on provided subnet CIDRs
  - All whitelisting is implemented through security group ingress rules

## Parameters and Their Valid Values

### EKS Cluster (cf-eks.yaml)

| ParameterKey | ValueType | Sample Values | Default | Mandatory | Description |
|--------------|-----------|---------------|---------|-----------|-------------|
| AWSRegion | String | ap-southeast-1 | ap-southeast-1 | Yes | AWS region where resources will be deployed |
| AppShortName | String | my-application | - | Yes | Short name for the application used as prefix for resource naming |
| EnvName | String | nprd, nprd-dev, nprd-sit1, nprd-sit2, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b, prod, prod-a, prod-b | - | Yes | Environment name to determine deployment context and resource configuration |
| EKSAuthenticationMode | String | API, CONFIG_MAP, API_AND_CONFIG_MAP | API | No | EKS cluster authentication mode. API uses Access Entry API only (recommended), CONFIG_MAP uses aws-auth ConfigMap only (legacy), API_AND_CONFIG_MAP uses both (Hybrid, required for v5 migration) |
| VpcId | AWS::EC2::VPC::Id | vpc-120324 | - | Yes | ID of the VPC where EKS cluster will be created |
| AppSubnetIds | List<AWS::EC2::Subnet::Id> | subnet-123232,subnet-2345123 | - | Yes | List of subnet IDs where the EKS cluster will be deployed |
| VPCSubnetCidrAppAZ1 | String | 10.0.1.0/24 | - | Yes | CIDR range for the first availability zone subnet |
| VPCSubnetCidrAppAZ2 | String | 10.0.2.0/24 | - | Yes | CIDR range for the second availability zone subnet |
| VPCSubnetCidrAppAZ3 | String | 10.0.3.0/24 | - | No | Optional CIDR range for the third availability zone subnet |
| AppIngressNodePort | String | 8080 | - | Yes | Port number for frontend application ingress |
| InternalIngressNodePort | String | 8081 | - | Yes | Port number for backend application ingress |
| HasCustomPorts | String | true, false | false | No | Enable custom port range for InternalIngressController |
| CustomPortStart | String | 9000 | "" | No | Start of custom port range for InternalIngressController |
| CustomPortEnd | String | 9999 | "" | No | End of custom port range for InternalIngressController |
| HIPDeploymentServer01 | String | 10.0.2.4 | - | Yes | IP address of first deployment server |
| HIPDeploymentServer02 | String | 10.0.2.5 | - | Yes | IP address of second deployment server |
| HIPDeploymentServer03 | String | 10.0.2.6 | - | No | Optional IP address of third deployment server |
| DeploymentServerUTL01 | String | 10.0.2.8 | - | Yes | IP address of utility deployment server |
| NLBIngressSecurityGroupId | String | sg-0123456789abcdef0 | - | No | Optional security group ID for NLB ingress |
| HSGWSubnet01 | String | 10.0.4.0/24 | - | No | Optional CIDR for first HSGW subnet |
| HSGWSubnet02 | String | 10.0.5.0/24 | - | No | Optional CIDR for second HSGW subnet |
| HSGWSubnet03 | String | 10.0.6.0/24 | - | No | Optional CIDR for third HSGW subnet |
| KMSKeyRotationPeriod | Number | 365 | 365 | No | Number of days for KMS key rotation period |
| VpcCidr1 | String | 10.0.0.0/16 | "" | No | Primary VPC CIDR IP Range for enhanced networking |
| VpcCidr2 | String | 172.16.0.0/16 | "" | No | Optional secondary VPC CIDR IP Range |
| VpcCidr3 | String | 192.168.0.0/16 | "" | No | Optional tertiary VPC CIDR IP Range |
| VpcCidr4 | String | 10.10.0.0/16 | "" | No | Optional fourth VPC CIDR IP Range |
| VpcCidr5 | String | 10.20.0.0/16 | "" | No | Optional fifth VPC CIDR IP Range |
| S3PrefixListId | String | pl-12345678 | "" | No | S3 PrefixList ID for enhanced S3 connectivity |
| HCCVpceCidr | String | 10.1.0.0/24 | "" | No | HCC VPC Endpoint Subnet CIDR for hybrid connectivity |
| PrefixListNLBIngress | String | pl-87654321 | "" | No | Prefix list for Whitelisted NLB Ingress control |


### EKS Fargate Profile (cf-eks-fp.yaml)

| ParameterKey | ValueType | Sample Values | Mandatory | Description |
|--------------|-----------|---------------|-----------|-------------|
| AppShortName | String | my-application | Yes | Short name for the application used as prefix for resource naming |
| EnvName | String | nprd-dev, prod | Yes | Environment name to determine deployment context |
| SecondProjectForExistingEKS | String | yes, no | No (default: no) | Set to 'yes' when deploying a second project to existing EKS cluster |
| ClusterName | String | my-eks-cluster | Conditional | Required when SecondProjectForExistingEKS='yes' |
| OidcProviderEndpoint | String | oidc.eks.region.amazonaws.com/id/XXX | Conditional | Required when SecondProjectForExistingEKS='yes' (without https://) |
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
| HSGWSubnet3 | String | 10.0.6.0/24 | No | Optional CIDR for third HSGW subnet |

### EKS Secrets (cf-eks-secrets.yaml)

| ParameterKey | ValueType | Sample Values | Mandatory | Description |
|--------------|-----------|---------------|-----------|-------------|
| AppShortName | String | my-application | Yes | Short name for the application used as prefix for resource naming |
| EnvName | String | nprd-dev, prod | Yes | Environment name to determine deployment context and secret mapping |

## Enhanced Security Features

### KMS Key Rotation

The EKS template supports automatic key rotation for the KMS key used to encrypt Kubernetes secrets. This security enhancement ensures encryption keys are regularly rotated according to best practices.

**Key Features:**
* Automatic rotation of KMS keys enabled by default
* Configurable rotation period (defaults to 365 days)
* User ability to override rotation period through the `KMSKeyRotationPeriod` parameter
* 7-day pending window for key rotation

The `KMSKeyRotationPeriod` parameter allows you to specify the number of days between key rotations, with a default value of 365 days (annual rotation) if not specified.

### Enhanced Load Balancer Controller Permissions

Version 5.0 includes updated IAM policies for the Load Balancer Controller with additional permissions:

**New Permissions Added:**
* `ec2:GetSecurityGroupsForVpc` - Enhanced VPC security group discovery
* `ec2:DescribeIpamPools` - IPAM pool management support
* `elasticloadbalancing:ModifyListenerAttributes` - Advanced listener configuration
* `elasticloadbalancing:ModifyCapacityReservation` - Capacity reservation management
* `elasticloadbalancing:ModifyIpPools` - IP pool management
* `elasticloadbalancing:SetRulePriorities` - Rule priority management

### Advanced Networking Security

**Multi-VPC CIDR Support:**
* Support for up to 3 VPC CIDR ranges in security group rules
* Enables complex network topologies and multi-tenant scenarios
* Automatic conditional creation of security group rules based on provided CIDRs

**Enhanced Egress Rules:**
* Comprehensive egress rules for cluster communication
* Support for DNS resolution (port 53 TCP/UDP)
* HTTPS egress to VPC CIDRs and HCC endpoints
* S3 prefix list integration for secure S3 access
* Fixed security group rule configurations for reliable deployment

**Custom Port Range Support:**
* Configurable custom port ranges for Internal Ingress Controller
* Dynamic security group rule creation based on custom port configuration
* Multi-AZ support for custom port ranges

### Hybrid Cloud Connectivity (HCC)

**HCC VPC Endpoint Support:**
* Dedicated parameter for HCC VPC endpoint subnet CIDR
* Automatic security group rules for HCC connectivity
* Support for hybrid cloud scenarios and on-premises integration

### OIDC Integration

Service account roles use OIDC (OpenID Connect) for secure authentication:
* Load Balancer Controller Role uses OIDC for service account `aws-load-balancer-controller`
* OpenTelemetry Service Account Role uses OIDC for service account `otel-collector`
* Eliminates need for long-term AWS credentials in pods
* Enhanced security through federated identity

### Production Safeguards

Enhanced protection for production environments:
* DeletionPolicy and UpdateReplacePolicy set to 'Retain' for production environments
* Comprehensive resource tagging with `InfraPlatform-EKS-V5`
* Consistent naming conventions across all resources
* Enhanced error handling and validation

## EKS Add-ons and Monitoring

The template now includes comprehensive EKS add-ons that are automatically deployed with the cluster:

### Core Add-ons (Automatic Deployment)
* **CoreDNS**: Service discovery within the cluster
  - Deployed with OVERWRITE conflict resolution
  - Ensures consistent DNS configuration
  - Required for basic cluster functionality

* **cert-manager**: Certificate management for Kubernetes
  - Automates certificate lifecycle management
  - Supports Let's Encrypt and other certificate authorities
  - Deployed in cert-manager namespace on fp_observability Fargate profile

* **metrics-server**: Cluster resource metrics collection
  - Provides CPU and memory metrics for pods and nodes
  - Required for Horizontal Pod Autoscaler (HPA)
  - Deployed in kube-system namespace on fp_default Fargate profile

* **kube-state-metrics**: Kubernetes objects state metrics collection
  - Exposes metrics about Kubernetes object states
  - Supports monitoring and alerting workflows
  - Deployed in kube-state-metrics namespace on fp_observability Fargate profile

### Add-on Deployment Features
* **Dependency Management**: Proper sequencing ensures observability Fargate profile is ready before dependent add-ons
* **Conflict Resolution**: All add-ons use OVERWRITE policy for consistent configuration
* **Production Ready**: DeletionPolicy and UpdateReplacePolicy set for production environments
* **Consistent Tagging**: All add-ons tagged with `InfraPlatform-EKS-V5`

### Observability Components

**Dedicated Fargate Profile (`fp_observability`):**
* Optimized for observability and monitoring workloads
* Supports namespaces:
  - `fargate-container-insights` - AWS Container Insights
  - `opentelemetry-operator-system` - OpenTelemetry components
  - `cert-manager` - Certificate management
  - `aws-observability` - AWS observability tools
  - `kube-state-metrics` - Kubernetes state metrics

**OpenTelemetry Integration:**
* Dedicated service account role with OIDC
* Integrated with AWS managed observability services:
  - Amazon Prometheus (AMP) for metrics
  - AWS X-Ray for distributed tracing
  - CloudWatch for logs and metrics
* Supports custom observability pipelines

**Centralized Logging:**
* Dedicated Fargate Log Group with 365-day retention
* Consistent tagging and naming conventions
* Production-ready retention policies

### Monitoring Capabilities

**Built-in Metrics Collection:**
* Cluster-level metrics via metrics-server
* Object state metrics via kube-state-metrics
* Custom application metrics via OpenTelemetry

**Integration Ready:**
* Pre-configured for AWS managed services
* Support for custom monitoring solutions
* Extensible through additional Fargate profiles

## Deployment Guide

### Prerequisites
1. Access to Azure DevOps repository for parameter files
2. AWS CLI configured with appropriate permissions for Azure Pipelines
3. Access to deployment tooling server for kubectl operations
4. Required parameter values collected
5. Network infrastructure ready (VPC, subnets)
```
nprd-dev
|_ parameters-eks.yaml
|_ parameters-eks-fp.yaml
|_ parameters-nlb-tg-alb.yaml
|_ parameters-eks-secrets.yaml
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
   - EKS Add-ons deployment (part of CloudFormation)
   - Post-configuration deployment via Ansible (if needed)

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

1. **Deployment Order**: The EKS Cluster stack (`cf-eks.yaml`) must be fully created before provisioning other stacks.

2. **SSM Parameter Dependencies**: The KMS key SSM parameter created by the EKS Cluster stack is required for the EKS Secrets stack.

3. **Fargate Profile Integration**: The Fargate Profile stack uses SSM parameters created by the EKS Cluster stack.

4. **ALB Integration**: The NLB stack can use the Ingress ALB ARN as a target. This ALB is typically created by the development team using the AWS Load Balancer Controller.

5. **Production Safeguards**: For production environments (prod, prod-a, prod-b), resources have DeletionPolicy and UpdateReplacePolicy set to 'Retain'.

6. **EKS Authentication Mode**:
   - v6 uses configurable authentication mode via the `EKSAuthenticationMode` parameter
   - **API** (default): Uses EKS Access Entry API only - recommended for new clusters
   - **CONFIG_MAP**: Uses aws-auth ConfigMap only - legacy mode for backward compatibility
   - **API_AND_CONFIG_MAP**: Uses both methods (Hybrid) - **recommended for v5 to v6 migration**
   - The cluster creator (IAM principal deploying the stack) automatically gets admin access in API and Hybrid modes
   - **Migration from v5**: Simply set `EKSAuthenticationMode` to `API_AND_CONFIG_MAP` and deploy - CloudFormation handles the update
   - **Migration from Hybrid to API**: Requires manual Console step (AWS limitation), then update parameter to `API`
   - For full migration details, see the [v5 to v6 Migration Guide](#v5-to-v6-migration-guide) section

7. **Managing EKS Access Entries** (Project Team Responsibility):

   Access entries are **NOT managed by this CloudFormation template**. Project teams should manage access entries via AWS Console or CLI to avoid drift issues.

   **Available Access Policies**:
   | Policy | Description |
   |--------|-------------|
   | `AmazonEKSClusterAdminPolicy` | Full cluster admin access |
   | `AmazonEKSAdminPolicy` | Admin access (excludes access management) |
   | `AmazonEKSEditPolicy` | Read/write access to most resources |
   | `AmazonEKSViewPolicy` | Read-only access |

   **Via AWS Console**:
   1. Navigate to EKS → Clusters → Your Cluster → Access
   2. Click "Create access entry"
   3. Select IAM principal (role or user)
   4. Associate access policy and scope

   **Via AWS CLI**:
   ```bash
   # List current access entries
   aws eks list-access-entries --cluster-name <cluster-name> --region ap-southeast-1

   # Create access entry for an IAM role
   aws eks create-access-entry --cluster-name <cluster-name> \
     --principal-arn arn:aws:iam::<account-id>:role/<role-name> \
     --type STANDARD \
     --region ap-southeast-1

   # Associate admin policy (cluster-wide)
   aws eks associate-access-policy --cluster-name <cluster-name> \
     --principal-arn arn:aws:iam::<account-id>:role/<role-name> \
     --policy-arn arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy \
     --access-scope type=cluster \
     --region ap-southeast-1

   # Associate policy with namespace scope
   aws eks associate-access-policy --cluster-name <cluster-name> \
     --principal-arn arn:aws:iam::<account-id>:role/<role-name> \
     --policy-arn arn:aws:eks::aws:cluster-access-policy/AmazonEKSEditPolicy \
     --access-scope type=namespace,namespaces=app-namespace \
     --region ap-southeast-1

   # Remove access entry
   aws eks delete-access-entry --cluster-name <cluster-name> \
     --principal-arn arn:aws:iam::<account-id>:role/<role-name> \
     --region ap-southeast-1
   ```

   **Note**: The cluster creator (IAM principal that deployed the CloudFormation stack) automatically gets admin access when using API or Hybrid authentication mode.

8. **Cluster Creator Admin Access**: The IAM principal that deploys the CloudFormation stack automatically receives cluster admin access via EKS Access Entry (when using API or Hybrid mode).

9. **Environment Mapping**: The EKS Secrets stack uses a mapping for sub-environments (e.g., sit-a, sit-b) to determine the parent environment for KMS key lookup.

10. **Security Group Automation**: Security group rules are automatically created based on provided subnet CIDRs and HSGW subnets.

11. **Enhanced Networking**: 
   - **VPC CIDR Configuration**: Up to 3 VPC CIDR ranges can be configured for complex network topologies
   - **HCC Support**: HCC VPC endpoint subnet can be configured for hybrid connectivity via HCCVpceCidr parameter
   - **S3 Integration**: S3 prefix list ID can be specified for enhanced S3 connectivity via S3PrefixListId parameter
   - **Prefix List NLB Ingress**: New PrefixListNLBIngress parameter for whitelisted NLB ingress control

12. **Enhanced Load Balancer Controller**:
    - **Additional Permissions**: Added 6 new IAM permissions for advanced features:
      - `ec2:GetSecurityGroupsForVpc` - Enhanced security group operations
      - `ec2:DescribeIpamPools` - IPAM pool integration
      - `elasticloadbalancing:ModifyListenerAttributes` - Advanced listener configuration
      - `elasticloadbalancing:ModifyCapacityReservation` - Capacity management
      - `elasticloadbalancing:ModifyIpPools` - IP pool management
      - `elasticloadbalancing:SetRulePriorities` - Rule priority management

13. **SQS Access Enhancement**: Updated SQS policy resource pattern from `${AppShortName}-${EnvName}-sqs-*` to `${AppShortName}-${EnvName}-sqs*` for improved flexibility in SQS resource naming

14. **Custom Port Configuration**: When enabling custom ports (`HasCustomPorts=true`), ensure that `CustomPortStart` and `CustomPortEnd` parameters are properly configured.

15. **EKS Add-ons Behavior**:
    - All add-ons use OVERWRITE conflict resolution, which may override custom configurations during updates
    - Add-ons have proper dependency management to ensure correct deployment order
    - cert-manager and kube-state-metrics depend on the observability Fargate profile
    - metrics-server deploys to kube-system namespace on fp_default profile

16. **OIDC Provider Requirements**: The template automatically creates OIDC integration for service accounts. This requires the EKS cluster to be fully operational before deploying dependent services.

17. **Log Retention**: Fargate logs are retained for 365 days. Consider your organization's log retention policies before deployment.

18. **Resource Tagging**: All resources are consistently tagged with `IaCVersion: InfraPlatform-EKS-v6` for improved traceability and management.

19. **Egress Rule Configuration**: Enhanced egress rules have been implemented for proper cluster communication. Ensure VPC CIDR parameters are correctly configured.

20. **Multi-AZ Support**: The template supports deployments across multiple availability zones with conditional resource creation based on provided parameters.

21. **Hybrid Connectivity**: HSGW subnet configurations are optional but when provided, they automatically create security group rules for hybrid connectivity scenarios.

22. **Resource Count**: The v6.0 template creates approximately 50+ CloudFormation resources due to additional add-ons and enhanced security group rules.

23. **Prefix List Integration**: Both S3PrefixListId and PrefixListNLBIngress parameters provide enhanced networking control for specific use cases.

Remember to ensure you have the necessary permissions and have configured your deployment tools correctly before deploying these templates.

## v5 to v6 Migration Guide

For existing v5 clusters (using CONFIG_MAP authentication mode), migration is straightforward via CloudFormation parameter update.

### Migration via CloudFormation Parameter (Recommended)

For **existing v5 clusters**, simply update your CloudFormation parameter file and deploy:

1. Add the `EKSAuthenticationMode` parameter to your parameter file:
   ```yaml
   EKSAuthenticationMode: "API_AND_CONFIG_MAP"
   ```
2. Deploy the v6 template - CloudFormation will update the cluster's authentication mode to Hybrid

**Available Authentication Modes:**
| Mode | Use Case |
|------|----------|
| `API` | New clusters only (default, recommended) |
| `API_AND_CONFIG_MAP` | Migration from v5 (Hybrid mode) - **use this for v5 migration** |
| `CONFIG_MAP` | Legacy compatibility (not recommended for new deployments) |

### Optional: Upgrade from Hybrid to API-Only Mode

If you want to fully migrate to API-only mode after deploying with Hybrid mode, this requires a **manual step via AWS Console** (AWS limitation - cannot go directly from CONFIG_MAP to API):

**Step 1: Ensure Hybrid Mode is Active**
- Your cluster should already be in `API_AND_CONFIG_MAP` mode after v6 deployment

**Step 2: Migrate Access Entries**
- Migrate any aws-auth ConfigMap entries to EKS Access Entries via Console/CLI
- Verify all required access is configured via Access Entries

**Step 3: Update to API Mode (via AWS Console)**
1. Navigate to **AWS Console** → **EKS** → **Clusters** → Select your cluster
2. Go to **Access** tab → Click **Manage access configuration**
3. Change **Authentication mode** from `EKS API and ConfigMap` to `EKS API`
4. Click **Save changes**
5. Wait for the cluster to finish updating

**Step 4: Update CloudFormation Parameter**
1. Update your parameter file to match:
   ```yaml
   EKSAuthenticationMode: "API"
   ```
2. Deploy to sync CloudFormation state with the cluster

### Important Notes for Migration
- **v5 to Hybrid**: Can be done directly via CloudFormation parameter update
- **Hybrid to API**: Requires manual Console/CLI step (AWS limitation)
- **Access entries**: After migrating to Hybrid or API mode, you can manage access via EKS Access Entries
- **Existing access**: The cluster creator automatically gets admin access; other users/roles need to be added via Access Entries
- **aws-auth ConfigMap**: In Hybrid mode, both aws-auth ConfigMap AND Access Entries work simultaneously

## Troubleshooting Common Issues

### Deployment Failures

**EgressController Security Group Errors:**
- **Error**: "Property GroupId cannot be empty"
- **Solution**: Ensure VpcCidr1 parameter is provided as it's required for egress rules
- **Note**: This issue has been resolved in v5.0 with proper GroupId configuration

**Add-on Deployment Issues:**
- **Error**: Add-ons fail to deploy
- **Solution**: Ensure the observability Fargate profile is created before cert-manager and kube-state-metrics add-ons
- **Note**: Dependencies are properly configured in v5.0

**OIDC Provider Issues:**
- **Error**: Service account roles cannot assume roles
- **Solution**: Ensure the EKS cluster is fully deployed before creating dependent resources
- **Note**: OIDC provider endpoint is automatically exported via SSM parameter

**Authentication Mode Errors:**
- **Error**: Cannot change authentication mode from CONFIG_MAP to API directly
- **Solution**: Use `API_AND_CONFIG_MAP` (Hybrid) mode first, then optionally migrate to API via Console
- **Note**: v5 to Hybrid can be done via CloudFormation parameter; Hybrid to API requires manual Console step

## 🚀 Production Readiness

### **v5.0 Critical Improvements Over v3.0**

**🐛 Fixed Critical Issues:**
- **Security Group Deployment Failures** ✅ Resolved missing GroupId properties
- **CIDR Property Inconsistencies** ✅ Fixed CIDRIP → CidrIp naming issues  
- **Add-on Dependency Conflicts** ✅ Proper sequencing prevents deployment failures
- **CloudFormation Validation Errors** ✅ Enhanced parameter validation

**📈 Enhanced Capabilities:**
- **4 EKS Add-ons** vs 1 in v3.0 (CoreDNS, cert-manager, kube-state-metrics, metrics-server)
- **Multi-VPC CIDR Support** for complex network topologies
- **S3 Prefix List Integration** for optimized S3 connectivity
- **HCC VPC Endpoint Support** for hybrid cloud scenarios
- **Enhanced Load Balancer Permissions** with 6 additional IAM permissions

### **Proven Foundation**
v5.0 builds upon the successful v3.0 deployment patterns currently operational in production:
- ✅ Custom port configurations (7000-15000) validated
- ✅ Multi-deployment server patterns confirmed working
- ✅ ap-southeast-1 regional deployment proven
- ✅ OIDC integration stable and reliable

### **Deployment Confidence**
- **Zero Breaking Changes**: All v3.0 parameters remain compatible
- **Enhanced Reliability**: Better error handling and validation
- **Production Tested**: Based on proven v3.0 configurations
- **Quick Rollback**: v3.0 remains fully supported if needed

---

## 🚀 Quick Start Guide

### **For Teams Migrating from v5.0 to v6.0**
If you're upgrading from EKS v5.0 to v6.0, follow these steps:

```yaml
# 1. Copy your existing v5.0 parameter files
# cp parameters-eks-v5.yaml parameters-eks-v6.yaml

# 2. Add the new v6.0 EKSAuthenticationMode parameter
# For v5 migration, use API_AND_CONFIG_MAP (Hybrid mode)
EKSAuthenticationMode: "API_AND_CONFIG_MAP"

# 3. Deploy v6 template - CloudFormation will update the authentication mode
```

**Authentication Mode Options:**
| Mode | Use Case |
|------|----------|
| `API` | New clusters (recommended default) |
| `API_AND_CONFIG_MAP` | **Migration from v5** - use this for existing clusters |
| `CONFIG_MAP` | Legacy compatibility only (not recommended) |

**Migration Path:**
- **v5 → Hybrid**: Simply update CloudFormation parameter to `API_AND_CONFIG_MAP` and deploy ✅
- **Hybrid → API**: Requires manual Console step (see Migration Guide), then update parameter to `API`

**After Migration to Hybrid:**
- Both aws-auth ConfigMap AND EKS Access Entries work
- Migrate your aws-auth ConfigMap entries to Access Entries via Console/CLI
- Once all entries are migrated, you can optionally upgrade to `API` mode (requires manual Console step)

### **For Teams Currently Using v3.0**
If you're already running EKS v3.0 successfully, here's how to evaluate v5.0:

```yaml
# 1. Copy your existing v3.0 parameter files
# cp parameters-eks-v3.yaml parameters-eks-v5.yaml

# 2. Add the new v5.0 parameters (all optional)
VpcCidr1: "10.0.0.0/16"       # Your VPC CIDR
VpcCidr2: ""                   # Optional secondary CIDR
S3PrefixListId: ""             # Optional S3 prefix list
HCCVpceCidr: ""                # Optional HCC VPC endpoint

# 3. Deploy to test environment first
# Your existing configurations will work unchanged
```

### **For New Deployments**
Use the validated configuration pattern from current production deployments:

```yaml
EKSAuthenticationMode: "API"
HasCustomPorts: "true"
CustomPortStart: "7000"
CustomPortEnd: "15000"
AWSRegion: "ap-southeast-1"
```

### **Expected Deployment Results**
- **EKS Cluster**: ~25-30 minutes
- **4 Add-ons**: Automatically deployed (CoreDNS, cert-manager, kube-state-metrics, metrics-server)  
- **Fargate Profiles**: Default + observability profiles
- **Security Groups**: Enhanced rules with proper validation
- **OIDC Integration**: Ready for service account authentication
- **Authentication Mode**: Configurable via parameter (API, CONFIG_MAP, or API_AND_CONFIG_MAP)

## 📊 **Version 6.0 Summary: What's Changed from v5.0**

### **🎯 Key Improvements from v5.0 to v6.0**

| Category | v5.0 Features | v6.0 Enhancements | Impact |
|----------|---------------|-------------------|--------|
| **Authentication** | Hardcoded API mode | Configurable via `EKSAuthenticationMode` parameter | Flexible authentication strategy |
| **Auth Options** | API only | API, CONFIG_MAP, API_AND_CONFIG_MAP | Supports migration and legacy compatibility |
| **VPC CIDR Support** | Up to 3 CIDRs | Up to 5 CIDRs (VpcCidr1-5) | Better support for complex topologies |
| **CloudFormation Outputs** | Basic outputs | + EKSAuthenticationMode output | Better integration and visibility |
| **Migration Support** | Manual only | Parameter-based + manual options | Easier upgrade path |

### **🔧 New Parameter Added**
| Parameter | Type | Values | Default | Description |
|-----------|------|--------|---------|-------------|
| `EKSAuthenticationMode` | String | API, CONFIG_MAP, API_AND_CONFIG_MAP | API | EKS cluster authentication mode |

### **🚀 Migration Flexibility**
- **New Clusters**: Use `API` mode (default, recommended)
- **Migrating from v5**: Use `API_AND_CONFIG_MAP` (Hybrid) mode
- **Legacy Requirements**: Use `CONFIG_MAP` mode (not recommended for new deployments)

**Bottom Line**: v6.0 adds authentication mode flexibility while maintaining all v5.0 capabilities, making it suitable for both new deployments and migrations from earlier versions.

---