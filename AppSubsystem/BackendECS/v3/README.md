# Backend ECS CloudFormation Templates - v2

This repository contains AWS CloudFormation templates for deploying ECS infrastructure and services.

## Architecture Overview

The solution is split into two main deployment pipelines:

1. **Infrastructure Pipeline**:
   - Deploys core ECS infrastructure using parent-child stack approach
   - Includes ALB, ECS Cluster, and optional ADOT Collector
   - Uses `cf-backend-ecs-main.yaml` as the main template
   - ECR repository for ADOT collector image (if using ADOT)
     - Repository path: utility-images/aws-observability/aws-otel-collector
     - Image will be pulled from public.ecr.aws/aws-observability/aws-otel-collector and pushed to project ECR through CICD pipeline

2. **Service Pipeline**:
   - Deploys individual ECS services independently
   - Each service has its own parameter file
   - Uses `cf-ecs-service.yaml` template
   - Can reference existing ALB and ECS Cluster through SSM parameters

## Prerequisites

Before deploying these templates, ensure you have:

1. **AWS Resources**:
   - S3 bucket for storing CloudFormation templates
   - VPC with at least 2 private subnets
   - SSL certificates in AWS Certificate Manager (ACM)
   - SNS topics for audit logging
   - Necessary IAM permissions for CloudFormation, ECS, IAM, SSM, SNS, etc.

2. **Template Organization**:
   - All templates should be uploaded to: `https://${AppShortName}-${EnvName}-cftemplates.s3.amazonaws.com/`
   - Required templates:
     - `cf-backend-ecs-main.yaml`
     - `cf-ecs-alb.yaml`
     - `cf-ecs-cluster.yaml`
     - `cf-ecs-adot-service.yaml`
   - Service template:
     - `cf-ecs-service.yaml`

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
- Orchestrates deployment of core ECS infrastructure
- Deploys ALB, ECS Cluster, and optional ADOT collector
- Uses nested stacks approach for modularity
- Creates and manages required SSM parameters

### Sub Stack Templates

#### ALB Stack Template (`cf-ecs-alb.yaml`)
- Creates internal Application Load Balancer
- Configures HTTPS listener with SSL/TLS certificates
- Supports multiple SSL certificates (primary and additional)
- Sets up security groups with proper ingress rules
- Optional prefix list support for flexible network security
- Supports multi-AZ deployment
- Stores ALB Security Group ID and HTTPS Listener ARN in SSM Parameter Store using ALBName
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
  - SNS publishing for audit logs
  - S3 operations (including presigned URL generation)
- Stores ECS Cluster Name and Task Execution Role ARN in SSM Parameter Store using ECSClusterName

#### ADOT Service Stack Template (`cf-ecs-adot-service.yaml`)
- Optional component for observability
- Deploys AWS Distro for OpenTelemetry collector
- Configures internal ALB for ADOT traffic
- Sets up proper security groups and networking
- Provides HTTPS endpoint with custom domain support
- OTLP protocol support (gRPC/HTTP)

### Service Template

#### ECS Service Template (`cf-ecs-service.yaml`)
- Deploys ECS services using Fargate
- Configures target groups and ALB routing:
  - Configurable target group parameters
  - Configurable health check thresholds and intervals
  - Individual health check configurations for both target group and container
- Sets up auto-scaling policies based on CPU and Memory utilization
- Manages CloudWatch logs with configurable retention
- Supports up to 3 environment variables per service
- Optional ADOT integration for observability
- Advanced deployment configurations:
  - Maximum service instances: 200%
  - Minimum healthy instances: 100%
  - Circuit breaker with automatic rollback
  - Container stop timeout: 120 seconds
  - Health check grace period: 60 seconds
- Container health check configuration:
  - Configurable command
  - Customizable interval
  - Adjustable timeout
  - Configurable retries
  - Customizable start period
- Target group health check configuration:
  - Configurable interval
  - Adjustable timeout
  - Custom healthy/unhealthy thresholds

## Parameters Reference

### Infrastructure Stack Parameters

#### General Configuration
| Parameter Name | Type | Default | Mandatory | Sample Value | Description |
|---------------|------|----------|-----------|--------------|-------------|
| AppShortName | String | - | Yes | hxis | Application name |
| EnvName | String | - | Yes | nprd-dev | Environment name (nprd/prod variants) |
| EnableADOT | String | false | No | true | Enable ADOT collector deployment |
| ECSClusterName | String | - | Yes | hxis-nprd-dev-ecs-cluster | Name for the ECS cluster |


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
| PrefixListId | String | "" | No | pl-12345abcdef | ID of a prefix list to allow inbound HTTPS traffic from all addresses in the list |

#### Target Group Health Check Configuration
| Parameter Name | Type | Default | Mandatory | Sample Value | Description |
|---------------|------|----------|-----------|--------------|-------------|
| TGHealthCheckPath | String | /health | Yes | /health | Health check endpoint path |
| TGHealthCheckIntervalSeconds | Number | 15 | No | 15 | Time between health checks |
| TGHealthCheckTimeoutSeconds | Number | 10 | No | 10 | Health check response timeout |
| TGHealthyThresholdCount | Number | 2 | No | 2 | Successful checks before healthy |
| TGUnhealthyThresholdCount | Number | 5 | No | 5 | Failed checks before unhealthy |

#### ADOT Configuration
| Parameter Name | Type | Default | Mandatory if ADOT enabled | Sample Value | Description |
|---------------|------|----------|--------------------------|--------------|-------------|
| ADOTContainerImage | String | - | Yes | 533267434948.dkr.ecr.ap-southeast-1.amazonaws.com/utility-images/aws-observability/aws-otel-collector:latest | ADOT collector container image URI |
| ADOTTaskCpu | String | 256 | No | 256 | CPU units for ADOT collector |
| ADOTTaskMemory | String | 512 | No | 512 | Memory for ADOT collector |
| PrivateHostedZoneId | String | - | Yes | Z095034935AWUIQP1FGLO | Route53 private hosted zone ID |
| ADOTCustomDomainName | String | - | Yes | adot.healthx.sg | Custom domain for ADOT endpoint |
| ADOTInternalCertificateArn | String | - | Yes | arn:aws:acm:ap-southeast-1:533267434948:certificate/8293c654-7ec9-4e43-9484-90cf6679da38 | SSL certificate ARN for ADOT ALB |

### Service Stack Parameters

#### Infrastructure References
| Parameter Name | Type | Default | Mandatory | Sample Value | Description |
|---------------|------|----------|-----------|--------------|-------------|
| AppShortName | String | - | Yes | hxis | Application name |
| EnvName | String | - | Yes | nprd-dev | Environment name (nprd/prod variants) |
| ALBName | String | - | Yes | hxis-nprd-dev-alb-ecs | Name of the existing ALB to associate with the service |
| ECSClusterName | String | - | Yes | hxis-nprd-dev-ecs-cluster | Name of the existing ECS cluster |
| VpcId | String | - | Yes | vpc-09528f37a12368b13 | VPC ID where service will be deployed |
| AppSubnetIds | List | - | Yes | subnet-0e3f828d,subnet-0d1706 | Subnet IDs for ECS tasks |

#### Service Configuration
| Parameter Name | Type | Default | Mandatory | Sample Value | Description |
|---------------|------|----------|-----------|--------------|-------------|
| ServiceName | String | - | Yes | api-service | Unique service identifier |
| ECRImage | String | - | Yes | 533267434948.dkr.ecr.ap-southeast-1.amazonaws.com/hxis-fhir-ecr-repo:1.0.0 | ECR image URI |
| CPUUnits | String | - | Yes | 2048 | CPU units for the task |
| Memory | String | - | Yes | 4096 | Memory for the task |
| ServiceContainerPort | Number | 8080 | No | 8080 | Container port |
| ECSCpuArchitecture | String | ARM64 | No | ARM64 | CPU architecture (X86_64/ARM64) |
| ECSOperatingSystemFamily | String | LINUX | No | LINUX | Operating system family |

#### Task Definition
| Parameter Name | Type | Default | Mandatory | Sample Value | Description |
|---------------|------|----------|-----------|--------------|-------------|
| CreateNewTaskDefinition | String | true | No | true | Create new task definition family |
| ExistingTaskFamily | String | "" | No | hxis-nprd-dev-api-service | Existing task family name |
| ECSDesiredTaskCount | Number | 1 | Yes | 2 | Number of desired tasks |

#### Container Health Check Configuration
| Parameter Name | Type | Default | Mandatory | Sample Value | Description |
|---------------|------|----------|-----------|--------------|-------------|
| ContainerHealthCheckCommand | String | CMD-SHELL,curl -f http://localhost/health | No | CMD-SHELL,curl -f http://localhost:443/health | Health check command |
| ContainerHealthCheckInterval | Number | 30 | No | 30 | Time between checks (seconds) |
| ContainerHealthCheckTimeout | Number | 5 | No | 5 | Check timeout (seconds) |
| ContainerHealthCheckStartPeriod | Number | 60 | No | 60 | Grace period before checks start |
| ContainerHealthCheckRetries | Number | 3 | No | 3 | Failed attempts before unhealthy |

#### Network & Routing
| Parameter Name | Type | Default | Mandatory | Sample Value | Description |
|---------------|------|----------|-----------|--------------|-------------|
| VPCSubnetCidrAZ1 | String | - | Yes | 10.53.144.128/26 | CIDR for AZ1 subnet |
| VPCSubnetCidrAZ2 | String | - | Yes | 10.53.144.192/26 | CIDR for AZ2 subnet |
| VPCSubnetCidrAZ3 | String | - | No | 10.53.144.224/26 | CIDR for AZ3 subnet |
| PathPattern | String | - | Yes | /api/* | ALB path pattern |
| RulePriority | String | 2 | Yes | 100 | ALB listener rule priority |
| TGHealthCheckPath | String | /health | No | /health | Health check endpoint |
| ECSServiceProtocol | String | HTTP | No | HTTP | Protocol for port mapping |
| ContainerProtocol | String | tcp | No | tcp | Container protocol |

#### Environment Variables
| Parameter Name | Type | Default | Mandatory | Sample Value | Description |
|---------------|------|----------|-----------|--------------|-------------|
| EnvVarConnectionStringSecretName | String | - | No | hxis-nprd-dev-api-service | Name of the secret in Secrets Manager |
| EnvVar1Name | String | - | No | Logging__LogLevel | Environment variable 1 name |
| EnvVar1Value | String | - | No | Information | Environment variable 1 value |
| EnvVar2Name | String | - | No | ApiVersion | Environment variable 2 name |
| EnvVar2Value | String | - | No | v1 | Environment variable 2 value |
| EnvVar3Name | String | - | No | FeatureFlag | Environment variable 3 name |
| EnvVar3Value | String | - | No | true | Environment variable 3 value |

#### Auto-Scaling Configuration
| Parameter Name | Type | Default | Mandatory | Sample Value | Description |
|---------------|------|----------|-----------|--------------|-------------|
| EnableAutoScaling | String | false | No | true | Enable auto-scaling |
| MinContainers | Number | 1 | No | 1 | Minimum container count |
| MaxContainers | Number | 4 | No | 4 | Maximum container count |
| CPUUtilizationThreshold | String | 70 | No | 70 | CPU threshold percentage |
| MemoryUtilizationThreshold | String | 70 | No | 70 | Memory threshold percentage |

#### ADOT Configuration
| Parameter Name | Type | Default | Mandatory | Sample Value | Description |
|---------------|------|----------|-----------|--------------|-------------|
| EnableADOT | String | false | No | true | Enable ADOT integration |
| ADOTEndpoint | String | - | No | https://adot.healthx.sg | ADOT collector endpoint |


## SSM Parameters

### Created by Infrastructure Stack
| Parameter Name | Description |
|---------------|-------------|
| /{ALBName}/ecs-alb-security-group-id | ALB Security Group ID |
| /{ALBName}/alb-https-listener-arn | HTTPS Listener ARN |
| /{ECSClusterName}/ECSTaskExecutionRoleArn | Task Execution Role ARN |
| /{ECSClusterName}/secrets-manager-policy-arn | Secrets Manager Policy ARN |

### Used by Service Stack
- References ALB parameters using ALBName
- References ECS Cluster parameters using ECSClusterName

## Deployment Strategy

### 1. Infrastructure Deployment
Deploy core infrastructure first using the main stack:
```
v2/
├── Templates/
│   ├── cf-backend-ecs-main.yaml      # Main infrastructure template
│   ├── cf-ecs-alb.yaml              # ALB template
│   ├── cf-ecs-cluster.yaml          # ECS Cluster template
│   ├── cf-ecs-adot-service.yaml     # ADOT template
│   ├── cf-ecs-service.yaml          # Service template
│   ├── README.md                    # Documentation
│   ├── resource-naming-table.md     # Resource naming conventions
│   └── RELEASES.md                  # Version history
│
└── Env/
    ├── parameters-backend-ecs.json   # Main stack parameters
    ├── parameters-ecs-alb.json      # ALB stack parameters
    ├── parameters-ecs-cluster.json  # Cluster stack parameters
    └── parameters-ecs-service.json  # Service stack parameters
```

This deployment creates:
- Application Load Balancer with HTTPS listener
- ECS Cluster with required IAM roles
- ADOT Collector (if enabled)
- Required SSM parameters for service deployments

### 2. Project Repository
```
Project-A/
└── Env/
    ├── nprd-dev/
    │   ├── parameters-project-a-api-service.json      # API Service parameters
    │   └── parameters-project-a-auth-service.json     # Auth Service parameters
    └── prod/
        ├── parameters-project-a-api-service.json
        └── parameters-project-a-auth-service.json
```
The service deployment follows a two-phase approach:

#### Phase 1: Service Resources Creation
1. **Initial Service Deployment**
   - Deploy service template with `EnvVarConnectionStringSecretName` parameter empty
   - Creates:
     - Target Group
     - ALB Listener Rule
     - Security Groups
     - CloudWatch Log Group
     - Empty Secrets Manager Secret (format: `${AppShortName}-${EnvName}-${ServiceName}`)
   - Note: ECS Service will not be created in this phase

2. **Secret Configuration**
   - Manually update the created secret in AWS Secrets Manager
   - Add required connection strings and sensitive configurations
   - Secret format:
     ```json
     {
       "ConnectionStrings__Local": "connection-string-value",
       "ConnectionStrings__FhirMetadata": "metadata-connection-string"
     }
     ```

#### Phase 2: Service Deployment
1. **Update Service Parameters**
   - Update the service parameters JSON file
   - Set `EnvVarConnectionStringSecretName` to the secret name:
     ```json
     {
       "ParameterKey": "EnvVarConnectionStringSecretName",
       "ParameterValue": "hxis-nprd-stg-ccdp"
     }
     ```

2. **Final Service Deployment**
   - Run service pipeline again with updated parameters
   - CloudFormation will now:
     - Create ECS Task Definition
     - Deploy ECS Service
     - Register targets with ALB
     - Configure auto-scaling (if enabled)


## Example Deployment Flow

```
┌─────────────────────────┐
│  Infrastructure Stack   │
│  Deployment            │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│  Service Stack          │
│  Initial Deployment     │
│  (Empty Secret Name)    │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│  Manual Secret Update   │
│  in AWS Console         │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│  Service Stack          │
│  Final Deployment       │
│  (With Secret Name)     │
└─────────────────────────┘
```


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
- Dual health check system:
  1. ALB Target Group health checks:
    - Configurable path, interval, and timeouts
    - Customizable healthy/unhealthy thresholds
    - HTTP/HTTPS protocol support
  2. Container-level health checks:
    - Configurable command (e.g., curl, custom scripts)
    - Adjustable interval and timeout settings
    - Customizable start period for application warmup
    - Configurable retry attempts
- Health check grace period: 60 seconds for ECS service
- Default health check path: `/health`

## Security Considerations

### Network Security
- All ECS services run in private subnets
- Security groups limit access to required ports only
- ALB terminates SSL/TLS traffic
- Optional prefix list support for granular network access control

### IAM Security
- Least privilege principle applied to all roles
- Same role for ECS tasks and execution
- SNS publish permissions for audit logging

## Production Considerations

The templates include special handling for production environments:
- DeletionPolicy and UpdateReplacePolicy set to Retain for critical resources in production
- Production environment detection for env names: prod, prod-a, prod-b
- Enhanced retention policies for logs and backups in production
- Additional security group restrictions in production environments


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