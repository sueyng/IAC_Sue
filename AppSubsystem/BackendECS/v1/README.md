# Backend ECS CloudFormation Templates - v1

This repository contains AWS CloudFormation templates for deploying ECS clusters with multiple services behind an Application Load Balancer.

## Prerequisites

Before deploying these templates, ensure you have:

1. **AWS Resources**:
   - S3 bucket for storing CloudFormation templates
   - VPC with at least 2 private subnets
   - SSL certificates in AWS Certificate Manager (ACM)
   - Necessary IAM permissions for CloudFormation, ECS, IAM, SSM, etc.

2. **Template Organization**:
   - All templates should be uploaded to: `https://${AppShortName}-${EnvName}-cftemplates.s3.amazonaws.com/`
   - Required templates:
     - `cf-backend-ecs-main.yaml`
     - `cf-ecs-alb.yaml`
     - `cf-ecs-cluster.yaml`
     - `cf-ecs-service.yaml`
     - `cf-ecs-adot-service.yaml`

3. **Required VPC Endpoints**:
   - Core endpoints:
     - ECR endpoints (API and Docker)
     - S3 endpoint
     - CloudWatch Logs endpoint
     - Secrets Manager endpoint
     - SSM endpoint
   - Feature-specific endpoints:
     - ECS endpoints (recommended)
     - X-Ray endpoint (if using ADOT)
   
   Note: VPC endpoints will be provisioned through a separate pipeline.


## Template Description

### Main Stack Template (`cf-backend-ecs-main.yaml`)
- Orchestrates deployment of ECS cluster and services
- Uses nested stacks approach for modular deployment
- Supports up to 4 ECS services
- Configurable auto-scaling for each service
- OpenTelemetry (ADOT) collector integration for observability (optional)

### Sub Stack Templates

#### ALB Stack Template (`cf-ecs-alb.yaml`)
- Creates internal Application Load Balancer
- Configures HTTPS listener with SSL/TLS certificates
- Supports multiple SSL certificates (primary and additional)
- Sets up security groups with proper ingress rules
- Supports multi-AZ deployment
- Stores ALB Security Group ID and HTTPS Listener ARN in SSM Parameter Store
- Default 404 response for unmatched routes
- Configurable health check endpoint

#### ECS Cluster Stack Template (`cf-ecs-cluster.yaml`)
- Creates ECS Cluster with Container Insights enabled
- Configures IAM roles and policies for ECS tasks
- Provides comprehensive IAM permissions for:
  - ECR access
  - CloudWatch logs
  - SSM operations
  - Secrets Manager
  - X-Ray integration
- Stores ECS Cluster Name and Task Execution Role ARN in SSM Parameter Store

#### ECS Service Stack Template (`cf-ecs-service.yaml`)
- Deploys ECS services using Fargate
- Configures target groups and ALB routing
- Sets up auto-scaling policies based on CPU and Memory utilization
- Manages CloudWatch logs with configurable retention
- Supports up to 3 environment variables per service
- Optional ADOT integration for observability
- Configurable health checks and deployment parameters

#### ADOT Service Stack Template (`cf-ecs-adot-service.yaml`)
- Deploys AWS Distro for OpenTelemetry collector
- Configures internal ALB for ADOT traffic
- Sets up proper security groups and networking
- Provides HTTPS endpoint with custom domain support
- Configurable CPU and memory allocation

## Parameters Reference

### Main Stack Parameters

#### General Configuration
| Parameter Name | Type | Default | Mandatory | Sample Value | Description |
|---------------|------|----------|-----------|--------------|-------------|
| AppShortName | String | - | Yes | hxis | Application name |
| EnvName | String | - | Yes | nprd-dev | Environment name (nprd/prod variants) |
| NumberOfServices | Number | 1 | Yes | 1 | Number of ECS services (1-4) |
| EnableADOT | String | false | No | true | Enable ADOT collector deployment |

#### Network Configuration
| Parameter Name | Type | Default | Mandatory | Sample Value | Description |
|---------------|------|----------|-----------|--------------|-------------|
| VpcId | String | - | Yes | vpc-09528f37a12368b13 | VPC ID for deployment |
| AppSubnetIds | List | - | Yes | subnet-0e3f828d570c58f11,subnet-0d1706693a418f5a3 | Subnet IDs for ECS services |
| VPCSubnetCidrAZ1 | String | - | Yes | 10.53.144.128/26 | CIDR for AZ1 subnet |
| VPCSubnetCidrAZ2 | String | - | Yes | 10.53.144.192/26 | CIDR for AZ2 subnet |
| VPCSubnetCidrAZ3 | String | - | No | "" | CIDR for AZ3 subnet |
| VPCSubnetCidrInternetIngressAlbAZ1 | String | - | No | "" | Internet Ingress ALB Subnet CIDR for AZ1 |
| VPCSubnetCidrInternetIngressAlbAZ2 | String | - | No | "" | Internet Ingress ALB Subnet CIDR for AZ2 |
| VPCSubnetCidrInternetIngressAlbAZ3 | String | - | No | "" | Internet Ingress ALB Subnet CIDR for AZ3 |

#### ALB Configuration
| Parameter Name | Type | Default | Mandatory | Sample Value | Description |
|---------------|------|----------|-----------|--------------|-------------|
| ALBName | String | - | Yes | hxis-nprd-dev-alb-ecs | Name for the new Application Load Balancer to be created |
| DefaultCertificateArn | String | - | Yes | arn:aws:acm:ap-southeast-1:533267434948:certificate/8293c654-7ec9-4e43-9484-90cf6679da38 | ARN of default SSL certificate |
| AdditionalCertificateArn | String | "" | No | "" | ARN of additional SSL certificate |

#### ADOT Configuration
| Parameter Name | Type | Default | Mandatory if ADOT enabled | Sample Value | Description |
|---------------|------|----------|--------------------------|--------------|-------------|
| ADOTContainerImage | String | - | Yes | 533267434948.dkr.ecr.ap-southeast-1.amazonaws.com/utility-images/aws-observability/aws-otel-collector:latest | ADOT collector container image URI |
| ADOTTaskCpu | String | 256 | No | 256 | CPU units for ADOT collector |
| ADOTTaskMemory | String | 512 | No | 512 | Memory for ADOT collector |
| PrivateHostedZoneId | String | - | Yes | Z095034935AWUIQP1FGLO | Route53 private hosted zone ID |
| ADOTCustomDomainName | String | - | Yes | adot.healthx.sg | Custom domain for ADOT endpoint |
| ADOTInternalCertificateArn | String | - | Yes | arn:aws:acm:ap-southeast-1:533267434948:certificate/8293c654-7ec9-4e43-9484-90cf6679da38 | SSL certificate ARN for ADOT ALB |

### Service-Specific Parameters (n = 1-4)
For each service:

#### Basic Configuration
| Parameter Name | Type | Default | Mandatory for n=1 | Sample Value | Description |
|---------------|------|----------|-------------------|--------------|-------------|
| Service{n}Name | String | - | Yes | ccdp | Service name |
| Service{n}ECRImage | String | - | Yes | 533267434948.dkr.ecr.ap-southeast-1.amazonaws.com/hxis-fhir-ecr-repo-ccdp:1.0.0.20 | ECR image URI |
| Service{n}CPUUnits | String | - | Yes | 2048 | CPU units for the task |
| Service{n}Memory | String | - | Yes | 4096 | Memory for the task |
| Service{n}ContainerPort | Number | 8080 | No | 8080 | Container port |
| ECSCpuArchitecture | String | ARM64 | No | ARM64 | CPU architecture (X86_64/ARM64) |
| ECSOperatingSystemFamily | String | LINUX | No | LINUX | Operating system family |
| CreateNewTaskDefinition | String | true | No | true | Create new task definition family |
| ExistingTaskFamily | String | "" | No | "" | Existing task family name |

#### Routing Configuration
| Parameter Name | Type | Default | Mandatory | Sample Value | Description |
|---------------|------|----------|-----------|--------------|-------------|
| Service{n}PathPattern | String | - | Yes | /ccdp/* | ALB path pattern for routing |
| Service{n}RulePriority | String | - | Yes | 10 | ALB listener rule priority |
| HealthCheckPath | String | /health | No | /health | Health check endpoint |

#### Environment Variables and Secrets
| Parameter Name | Type | Default | Mandatory | Sample Value | Description |
|---------------|------|----------|-----------|--------------|-------------|
| Service{n}EnvVarConnectionStringSecretName | String | - | No | "" (first deployment), "hxis-nprd-dev-ccdp" (second deployment) | Name of the secret in Secrets Manager |
| Service{n}EnvVar1Name | String | - | No | Logging__LogLevel__Microsoft | Environment variable 1 name |
| Service{n}EnvVar1Value | String | - | No | Information | Environment variable 1 value |
| Service{n}EnvVar2Name | String | - | No | "" | Environment variable 2 name |
| Service{n}EnvVar2Value | String | - | No | "" | Environment variable 2 value |
| Service{n}EnvVar3Name | String | - | No | "" | Environment variable 3 name |
| Service{n}EnvVar3Value | String | - | No | "" | Environment variable 3 value |

#### Auto-Scaling Configuration
| Parameter Name | Type | Default | Mandatory | Sample Value | Description |
|---------------|------|----------|-----------|--------------|-------------|
| Service{n}EnableAutoScaling | String | false | No | false | Enable auto-scaling |
| Service{n}MinContainers | Number | 1 | No | 1 | Minimum container count |
| Service{n}MaxContainers | Number | 4 | No | 4 | Maximum container count |
| CPUUtilizationThreshold | String | 70 | No | 70 | CPU threshold for scaling |
| MemoryUtilizationThreshold | String | 70 | No | 70 | Memory threshold for scaling |

## SSM Parameters Created

The templates create the following SSM parameters:

| Parameter Name | Description |
|---------------|-------------|
| /{AppShortName}/{EnvName}/ecs-cluster-name | ECS Cluster Name |
| /{AppShortName}/{EnvName}/ECSTaskExecutionRoleArn | Task Execution Role ARN |
| /{AppShortName}/{EnvName}/ecs-alb-security-group-id | ALB Security Group ID |
| /{AppShortName}/{EnvName}/alb-https-listener-arn | HTTPS Listener ARN |
| /{AppShortName}/{EnvName}/secrets-manager-policy-arn | Secrets Manager Policy ARN |

## Monitoring & Logging

### CloudWatch Logs
- All ECS services log to CloudWatch Logs
- Log groups follow pattern: `/ecs/${AppShortName}/${EnvName}/${ServiceName}`
- Configurable retention period via `LogsRetentionInDays` parameter
- Container Insights enabled by default on ECS cluster

### ADOT Integration
When ADOT is enabled:
- Traces exported to AWS X-Ray
- Metrics available in CloudWatch
- OTLP endpoint available at custom domain
- Supports both OTLP/gRPC (4317) and OTLP/HTTP (4318)

### Health Checks
- ALB health checks configurable per service
- Default path: `/health`
- Customizable interval, timeout, and healthy/unhealthy thresholds
- Health check grace period: 60 seconds

## Security Considerations

### Network Security
- All ECS services run in private subnets
- Security groups limit access to required ports only
- ALB terminates SSL/TLS traffic

### IAM Security
- Least privilege principle applied to all roles
- Same role for ECS tasks and execution

## Production Considerations

The templates include special handling for production environments:
- DeletionPolicy and UpdateReplacePolicy set to Retain for critical resources in production
- Production environment detection for env names: prod, prod-a, prod-b
- Enhanced retention policies for logs and backups in production
- Additional security group restrictions in production environments

## Scaling ECS Services

### Adding Additional ECS Services

The template supports scaling from 1 to 4 ECS services using AWS CloudFormation change sets. To add more services:

**Update Parameters File**
   - Modify parameters JSON file
   - Increase `NumberOfServices` value (allowed values: 1-4)
   - Add parameters for the new service
   - Ensure unique path patterns and rule priorities

Important considerations when adding services:

1. **Path Pattern Conflicts**
   - Ensure each service has a unique path pattern
   - Consider rule priorities carefully (lower numbers have higher priority)
   - Example pattern progression:
     - Service1: `/api/v1/*` (Priority: 10)
     - Service2: `/api/v2/*` (Priority: 20)
     - Service3: `/admin/*` (Priority: 30)
     - Service4: `/public/*` (Priority: 40)

2. **Resource Allocation**
   - Plan CPU and memory allocation across services
   - Consider available VPC and subnet resources
   - Account for auto-scaling requirements

3. **Environment Variables**
   - Each service supports up to 4 environment variables
   - Plan variable names and values carefully

4. **Health Checks**
   - Ensure each service has a valid health check endpoint
   - Default health check path is `/health`
   - Can be customized per service using `HealthCheckPath` parameter

5. **ADOT Integration**
   - If using ADOT, ensure `EnableADOT` is set to true
   - New services will automatically integrate with ADOT collector if enabled


## Deployment Flow

The deployment process follows a specific sequence to ensure proper resource provisioning and secret management. Understanding this flow is important, especially for the initial deployment of ECS services.

```
┌────────────────────┐
│  Parameter JSON    │
│  Configuration     │
└────────┬───────────┘
         │
         ▼
┌────────────────────┐
│  Azure Pipeline    │     ┌─────────────────────┐
│  Change Set Review │────▶│   ALB Deployment    │
└────────┬───────────┘     └──────────┬──────────┘
         │                            │
         │                            ▼
         │                 ┌─────────────────────┐
         │                 │   ECS Cluster       │
         │                 └──────────┬──────────┘
         │                            │
         │                            ▼
         │                 ┌─────────────────────┐
         │                 │   ADOT Collector    │ (if enabled)
         │                 └──────────┬──────────┘
         │                            │
         │                            ▼
         │                 ┌──────────────────────────────┐
         └───────────────▶│   Target Group Creation       │
                           │   Initial Secret Creation    │
                           │   (no ECS Service/Task)      │
                           └───────────┬──────────────────┘
                                       │
                                       ▼
                         ┌─────────────────────┐
                         │  Manual Secret      │
                         │  Value Update       │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │  Update Parameters   │
                         │  with Secret Name    │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌─────────────────────────────┐
                         │  Second Deployment:         │
                         │  ECS Service + TG           │
                         │  Registration               │
                         │   + Environment Variables:  │
                         │   1. Updated Secret Name    │
                         │   2. ADOT Endpoint Config   │
                         │   3. Custom Env Variables   │
                         └─────────────────────────────┘
```

## Initial Deployment
1. **Parameter Configuration**
   - Prepare parameter JSON file with all required configurations
   - Leave `Service{n}EnvVarConnectionStringSecretName` empty for initial deployment
   - Configure other service parameters including environment variables if needed
   - Note: ECS service will not be provisioned in first deployment even with all parameters configured

2. **Azure Pipeline Execution**
   - Pipeline creates CloudFormation change set
   - Deploys resources in sequence:
     1. Application Load Balancer (ALB)
     2. ECS Cluster
     3. ADOT Collector (if enabled)
     4. Creates Target Group with configuration:
        - Name pattern: `${AppShortName}-${EnvName}-tg-ecs-${ServiceName}`
        - Health check path: Configurable via `HealthCheckPath` parameter (default: `/health`)
        - Protocol: HTTP/HTTPS (configurable)
        - Target type: IP
        - Deregistration delay: 30 seconds
     5. Creates ALB listener rule for service path pattern

3. **Environment Variables Setup**
   - **Secret-based Environment Variables**:
     - Creates empty secret in AWS Secrets Manager
     - Secret name format: `{AppShortName}-{EnvName}-{ServiceName}`
     - For connection strings and sensitive configurations
   
   - **ADOT Configuration** (if ADOT enabled):
     - Sets required OTEL environment variables:
       ```
       OTEL_EXPORTER_OTLP_ENDPOINT: https://{ADOTCustomDomainName}
       OTEL_EXPORTER_OTLP_PROTOCOL: grpc
       OTEL_EXPORTER_OTLP_INSECURE: false
       ```
   
   - **Additional Environment Variables**:
     - Up to 3 custom environment variables can be configured via parameters:
       ```
       Service{n}EnvVar1Name/Value
       Service{n}EnvVar2Name/Value
       Service{n}EnvVar3Name/Value
       ```
     - Used for non-sensitive configuration (e.g., logging levels, feature flags)

4. **Initial Deployment State**
   - ECS service deployment is skipped due to empty `EnvVarConnectionStringSecretName`
   - Target Group and ALB rules are created but not yet associated with any tasks

## Second Deployment
1. **Manual Secret Update**
   - Project team updates secret values in AWS Secrets Manager console
   - Add required connection strings and configuration values
   - Secret is created by the ECS service template during first deployment

2. **Parameter Update**
   - Update parameter file with the secret name:
     ```json
      {
      "ParameterKey": "Service1EnvVarConnectionStringSecretName",
      "ParameterValue": "hxis-nprd-stg-ccdp"
      }
     ```
   - No other parameter changes are needed

3. **Redeployment**
   - Execute pipeline again with updated parameters
   - CloudFormation now deploys ECS service with access to populated secrets
   - Service will be provisioned as all required configurations are now in place

## Important Notes
- The two-phase deployment is necessary because the ECS service template creates the secret first
- First deployment won't show ECS service provisioned even though all service parameters are configured
- This is by design to ensure secrets are properly populated before service deployment
- Second deployment is required only to update the `EnvVarConnectionStringSecretName` parameter
- This approach ensures secure secret management and prevents service deployment failures due to missing secret values


## Troubleshooting

### Common Issues

1. **Stack Creation Failures**:
   - Check CloudWatch Logs for service deployment issues
   - Verify subnet and CIDR configurations
   - Ensure certificate ARNs are valid
   - Check IAM Role permissions

2. **Service Health Issues**:
   - Verify health check endpoint responds correctly
   - Check security group rules
   - Validate container port configurations
   - Review task definition environment variables

3. **ADOT Issues**:
   - Check SSL certificate validity
   - Review collector logs
   - Check Route53 DNS resolution
