# ELASTIC KUBERNETES SERVICE (EKS) - Version 5.0

**Amazon Elastic Kubernetes Service** (Amazon EKS) is a managed service that eliminates the need to install, operate, and maintain your own Kubernetes control plane on Amazon Web Services (AWS). Kubernetes is an open-source system that automates the management, scaling, and deployment of containerized applications. For more information visit this [site](https://docs.aws.amazon.com/eks/latest/userguide/what-is-eks.html).

## ✅ Current Status
**EKS v5.0 represents the latest production-ready template with critical bug fixes and enhancements**
- ✅ **Security Group Issues Fixed**: Resolved missing GroupId properties causing deployment failures
- ✅ **Enhanced Add-on Support**: All 4 add-ons (CoreDNS, cert-manager, kube-state-metrics, metrics-server) deploy reliably with proper dependencies
- ✅ **Multi-VPC CIDR Ready**: Advanced networking features available for complex topologies (up to 3 VPC CIDRs)
- ✅ **Prefix List Support**: New PrefixListNLBIngress parameter for enhanced NLB ingress control
- ✅ **Production Validated**: Based on proven v3.0 configurations with critical improvements and bug fixes
- ✅ **Enhanced Load Balancer Policy**: Updated with latest AWS permissions for improved ALB/NLB management

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
- **Consistent Tagging**: All resources tagged with `InfraPlatform-EKS-V5`
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
  - EKS Cluster with private endpoints only
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
| S3PrefixListId | String | pl-12345678 | "" | No | S3 PrefixList ID for enhanced S3 connectivity |
| HCCVpceCidr | String | 10.1.0.0/24 | "" | No | HCC VPC Endpoint Subnet CIDR for hybrid connectivity |
| PrefixListNLBIngress | String | pl-87654321 | "" | No | Prefix list for Whitelisted NLB Ingress control |

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

6. **Environment Mapping**: The EKS Secrets stack uses a mapping for sub-environments (e.g., sit-a, sit-b) to determine the parent environment for KMS key lookup.

7. **Security Group Automation**: Security group rules are automatically created based on provided subnet CIDRs and HSGW subnets.

8. **Enhanced Networking**: 
   - **VPC CIDR Configuration**: Up to 3 VPC CIDR ranges can be configured for complex network topologies
   - **HCC Support**: HCC VPC endpoint subnet can be configured for hybrid connectivity via HCCVpceCidr parameter
   - **S3 Integration**: S3 prefix list ID can be specified for enhanced S3 connectivity via S3PrefixListId parameter
   - **Prefix List NLB Ingress**: New PrefixListNLBIngress parameter for whitelisted NLB ingress control

9. **Enhanced Load Balancer Controller**: 
   - **Additional Permissions**: Added 6 new IAM permissions for advanced features:
     - `ec2:GetSecurityGroupsForVpc` - Enhanced security group operations
     - `ec2:DescribeIpamPools` - IPAM pool integration
     - `elasticloadbalancing:ModifyListenerAttributes` - Advanced listener configuration
     - `elasticloadbalancing:ModifyCapacityReservation` - Capacity management
     - `elasticloadbalancing:ModifyIpPools` - IP pool management
     - `elasticloadbalancing:SetRulePriorities` - Rule priority management

10. **SQS Access Enhancement**: Updated SQS policy resource pattern from `${AppShortName}-${EnvName}-sqs-*` to `${AppShortName}-${EnvName}-sqs*` for improved flexibility in SQS resource naming

9. **Custom Port Configuration**: When enabling custom ports (`HasCustomPorts=true`), ensure that `CustomPortStart` and `CustomPortEnd` parameters are properly configured.

10. **EKS Add-ons Behavior**: 
    - All add-ons use OVERWRITE conflict resolution, which may override custom configurations during updates
    - Add-ons have proper dependency management to ensure correct deployment order
    - cert-manager and kube-state-metrics depend on the observability Fargate profile
    - metrics-server deploys to kube-system namespace on fp_default profile

11. **OIDC Provider Requirements**: The template automatically creates OIDC integration for service accounts. This requires the EKS cluster to be fully operational before deploying dependent services.

12. **Log Retention**: Fargate logs are retained for 365 days. Consider your organization's log retention policies before deployment.

13. **Resource Tagging**: All resources are consistently tagged with `IaCVersion: InfraPlatform-EKS-V5` for improved traceability and management.

14. **Enhanced Load Balancer Permissions**: The Load Balancer Controller now has 6 additional permissions for advanced features like capacity reservations and IP pool management.

15. **Egress Rule Configuration**: Enhanced egress rules have been implemented for proper cluster communication. Ensure VPC CIDR parameters are correctly configured.

16. **Multi-AZ Support**: The template supports deployments across multiple availability zones with conditional resource creation based on provided parameters.

17. **Hybrid Connectivity**: HSGW subnet configurations are optional but when provided, they automatically create security group rules for hybrid connectivity scenarios.

18. **Resource Count**: The v5.0 template creates approximately 50+ CloudFormation resources (increased from 40+ in v3.0) due to additional add-ons and enhanced security group rules.

19. **Prefix List Integration**: Both S3PrefixListId and PrefixListNLBIngress parameters provide enhanced networking control for specific use cases.

Remember to ensure you have the necessary permissions and have configured your deployment tools correctly before deploying these templates.

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

### **For Teams Currently Using v3.0**
If you're already running EKS v3.0 successfully, here's how to evaluate v5.0:

```bash
# 1. Copy your existing v3.0 parameter files
cp parameters-eks-v3.json parameters-eks-v5.json

# 2. Add the new v5.0 parameters (all optional)
{
  "ParameterKey": "VpcCidr1",
  "ParameterValue": "10.0.0.0/16"  # Your VPC CIDR
},
{
  "ParameterKey": "VpcCidr2", 
  "ParameterValue": ""             # Optional secondary CIDR
},
{
  "ParameterKey": "S3PrefixListId",
  "ParameterValue": ""             # Optional S3 prefix list
},
{
  "ParameterKey": "HCCVpceCidr",
  "ParameterValue": ""             # Optional HCC VPC endpoint
}

# 3. Deploy to test environment first
# Your existing configurations will work unchanged
```

### **For New Deployments**
Use the validated configuration pattern from current production deployments:

```json
{
  "ParameterKey": "HasCustomPorts",
  "ParameterValue": "true"
},
{
  "ParameterKey": "CustomPortStart", 
  "ParameterValue": 7000
},
{
  "ParameterKey": "CustomPortEnd",
  "ParameterValue": 15000
},
{
  "ParameterKey": "AWSRegion",
  "ParameterValue": "ap-southeast-1"
}
```

### **Expected Deployment Results**
- **EKS Cluster**: ~25-30 minutes
- **4 Add-ons**: Automatically deployed (CoreDNS, cert-manager, kube-state-metrics, metrics-server)  
- **Fargate Profiles**: Default + observability profiles
- **Security Groups**: Enhanced rules with proper validation
- **OIDC Integration**: Ready for service account authentication

## 📊 **Version 5.0 Summary: What's Changed**

### **🎯 Key Improvements from v3.0 to v5.0**

| Category | v3.0 Features | v5.0 Enhancements | Impact |
|----------|---------------|-------------------|--------|
| **EKS Add-ons** | CoreDNS only | + cert-manager, kube-state-metrics, metrics-server | Enhanced monitoring & certificate management |
| **Load Balancer Policy** | Standard IAM permissions | + 6 additional permissions for advanced features | Better ALB/NLB management capabilities |
| **Networking** | Basic VPC CIDR support | Multi-VPC CIDR + prefix list support | Complex topology support |
| **Security Groups** | Working implementation | Fixed critical GroupId issues | Prevents deployment failures |
| **SQS Integration** | `sqs-*` pattern | `sqs*` pattern | Improved resource naming flexibility |
| **Observability** | Basic logging | Dedicated Fargate profile + multiple add-ons | Comprehensive monitoring stack |
| **Resource Count** | ~40 CloudFormation resources | ~50+ CloudFormation resources | Enhanced functionality |

### **🔧 Technical Debt Resolved**
- ✅ **Missing GroupId Properties**: Fixed egress controller security group rules
- ✅ **Property Naming**: Corrected CIDRIP → CidrIp inconsistencies
- ✅ **Add-on Dependencies**: Proper sequencing prevents deployment conflicts
- ✅ **Parameter Validation**: Enhanced CloudFormation validation

### **🚀 New Capabilities Unlocked**
- **Automatic Certificate Management** via cert-manager add-on
- **Advanced Monitoring** via kube-state-metrics and metrics-server
- **Complex Network Topologies** via multi-VPC CIDR support
- **Enhanced S3 Connectivity** via prefix list integration
- **Improved Load Balancer Features** via enhanced IAM permissions
- **Flexible SQS Naming** via updated resource patterns

**Bottom Line**: v5.0 delivers the stability of v3.0 with significant operational improvements and new capabilities, making it the recommended choice for new deployments and upgrades.

---