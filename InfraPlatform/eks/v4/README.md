# ELASTIC KUBERNETES SERVICE (EKS)

**Amazon Elastic Kubernetes Service** (Amazon EKS) is a managed service that eliminates the need to install, operate, and maintain your own Kubernetes control plane on Amazon Web Services (AWS). Kubernetes is an open-source system that automates the management, scaling, and deployment of containerized applications. For more information visit this [site](https://docs.aws.amazon.com/eks/latest/userguide/what-is-eks.html).

## Resources Provisioned

These templates provision a complete EKS infrastructure with the following key resources:

### Security and Access Management
* KMS Key and Alias for encryption (with automatic key rotation)
* IAM Managed Policies and Roles for access control
* Security Groups for network security

### Compute and Orchestration
* EKS Cluster (fully managed control plane)
* Fargate Profiles (serverless compute)
* EKS Add-ons (CoreDNS, cert-manager, kube-state-metrics, metrics-server)

### Monitoring and Observability
* OpenTelemetry (OTEL) service account role
* Fargate Log Group for centralized logging
* CloudWatch integration
* Custom namespace for Fargate Container Insights

### Networking and Load Balancing
* Network Load Balancer (NLB)
* Application Load Balancer (ALB) Target Group
* Security group configurations

### Secrets and Configuration
* Secret Manager Secrets
* SSM Parameters for cross-stack references

## Template Overview

### 1. **cf-eks.yaml**: Core EKS Infrastructure
* **Purpose**: Creates the main EKS cluster and fundamental resources
* **Key Components**:
  - EKS Cluster with private endpoints
  - KMS encryption key for secret encryption (with automatic key rotation)
  - Default Fargate profiles
    - `fp_default` (default, kube-system)
    - `fp_observability` (fargate-container-insights, opentelemetry-operator-system, cert-manager, aws-observability, kube-state-metrics)
  - EKS Add-ons:
    - CoreDNS
    - cert-manager
    - kube-state-metrics
    - metrics-server
  - CloudWatch log group for Fargate logs with 365-day retention
* **IAM Configuration**:
  - Roles:
    - EKS Node Role (for worker nodes)
    - Fargate Pod Execution Role (for Fargate pods)
    - EKS Cluster Service Role (for control plane)
    - Load Balancer Controller Role (for AWS Load Balancer Controller)
    - OpenTelemetry Service Account Role (for monitoring)
  - Managed Policies:
    - Secrets Manager Access Policy (for secrets access)
    - Load Balancer Controller Policy (for ALB/NLB management)
    - CloudWatch Metrics Policy (for metrics access)
    - ELB Permissions Policy (for load balancer operations)
    - SQS Access Policy (for queue operations)
* **Security Groups**:
  - App Ingress Controller SG (for frontend traffic)
  - Internal Ingress Controller SG (for backend traffic)
  - Cluster Shared Node SG (for node communication)
  - Control Plane SG (for EKS control plane)
* **Security Features**:
  - Automatic KMS key rotation for secrets encryption
  - Configurable rotation period (defaults to 365 days)
  - Pending window for key rotation (7 days)
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
| HIPDeploymentServer01 | String | 10.0.2.4 | - | Yes | IP address of first deployment server |
| HIPDeploymentServer02 | String | 10.0.2.5 | - | Yes | IP address of second deployment server |
| HIPDeploymentServer03 | String | 10.0.2.6 | - | No | Optional IP address of third deployment server |
| DeploymentServerUTL01 | String | 10.0.2.8 | - | Yes | IP address of utility deployment server |
| NLBIngressSecurityGroupId | String | sg-0123456789abcdef0 | - | No | Optional security group ID for NLB ingress |
| HSGWSubnet01 | String | 10.0.4.0/24 | - | No | Optional CIDR for first HSGW subnet |
| HSGWSubnet02 | String | 10.0.5.0/24 | - | No | Optional CIDR for second HSGW subnet |
| HSGWSubnet03 | String | 10.0.6.0/24 | - | No | Optional CIDR for third HSGW subnet |
| KMSKeyRotationPeriod | Number | 365 | 365 | No | Number of days for KMS key rotation period |

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

## EKS Add-ons and Monitoring

The template now includes several key EKS add-ons that improve cluster functionality:

### Core Add-ons
* **CoreDNS**: Service discovery within the cluster
* **cert-manager**: Certificate management for Kubernetes
* **metrics-server**: Cluster resource metrics collection
* **kube-state-metrics**: Kubernetes objects state metrics collection

### Observability Components
* Dedicated Fargate profile for observability components
* OpenTelemetry service account with appropriate permissions
* Fargate Log Group with 365-day retention
* Integration with AWS managed observability services
* Support for:
  - fargate-container-insights
  - opentelemetry-operator-system
  - cert-manager
  - aws-observability
  - kube-state-metrics namespaces

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

1. The EKS Cluster stack (`cf-eks.yaml`) must be fully created before provisioning other stacks.
2. The KMS key SSM parameter created by the EKS Cluster stack is required for the EKS Secrets stack.
3. The Fargate Profile stack uses SSM parameters created by the EKS Cluster stack.
4. The NLB stack can use the Ingress ALB ARN as a target. This ALB is typically created by the development team using the AWS Load Balancer Controller, which deploys the ALB based on Kubernetes Ingress resources.
5. For production environments (prod, prod-a, prod-b), resources have a DeletionPolicy and UpdateReplacePolicy set to 'Retain'.
6. The EKS Secrets stack uses a mapping for sub-environments (e.g., sit-a, sit-b) to determine the parent environment for KMS key lookup.
7. The NLB stack creates conditional security group rules based on provided subnet CIDRs and HSGW subnets.
8. The EKS template now supports up to 3 HSGW subnets for more flexible network configurations.
9. The template includes a dedicated Fargate Log Group with 365-day retention period for centralized logging.
10. The EKS Cluster now automatically deploys core add-ons (CoreDNS, cert-manager, kube-state-metrics, metrics-server) to improve cluster functionality.

Remember to ensure you have the necessary permissions and have configured your deployment tools correctly before deploying these templates.