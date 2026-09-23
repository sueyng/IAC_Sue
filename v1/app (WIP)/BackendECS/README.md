# Backend ECS CloudFormation Templates

This repository contains AWS CloudFormation templates for deploying ECS clusters with multiple services behind an Application Load Balancer.

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
  - Secrets Manager (commented out for future use)
  - X-Ray integration
- Stores ECS Cluster Name and Task Execution Role ARN in SSM Parameter Store

#### ECS Service Stack Template (`cf-ecs-service.yaml`)
- Deploys ECS services using Fargate
- Configures target groups and ALB routing
- Sets up auto-scaling policies based on CPU and Memory utilization
- Manages CloudWatch logs with configurable retention
- Supports up to 4 environment variables per service
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
| Parameter Name | Type | Default | Mandatory | Description |
|---------------|------|----------|-----------|-------------|
| AppShortName | String | - | Yes | Application name |
| EnvName | String | - | Yes | Environment name (nprd/prod variants) |
| NumberOfServices | Number | 1 | Yes | Number of ECS services (1-4) |
| EnableADOT | String | false | No | Enable ADOT collector deployment |

#### Network Configuration
| Parameter Name | Type | Default | Mandatory | Description |
|---------------|------|----------|-----------|-------------|
| VpcId | String | - | Yes | VPC ID for deployment |
| AppSubnetIds | List | - | Yes | Subnet IDs for ECS services |
| VPCSubnetCidrAppAZ1 | String | - | Yes | CIDR for AZ1 subnet |
| VPCSubnetCidrAppAZ2 | String | - | Yes | CIDR for AZ2 subnet |
| VPCSubnetCidrAppAZ3 | String | - | No | CIDR for AZ3 subnet |
| VPCSubnetCidrInternetAlbAZ1 | String | - | No | Internet ALB Subnet CIDR for AZ1 |
| VPCSubnetCidrInternetAlbAZ2 | String | - | No | Internet ALB Subnet CIDR for AZ2 |
| VPCSubnetCidrInternetAlbAZ3 | String | - | No | Internet ALB Subnet CIDR for AZ3 |

#### ALB Configuration
| Parameter Name | Type | Default | Mandatory | Description |
|---------------|------|----------|-----------|-------------|
| DefaultCertificateArn | String | - | Yes | ARN of default SSL certificate |
| AdditionalCertificateArn | String | "" | No | ARN of additional SSL certificate |

### Service-Specific Parameters (n = 1-4)
For each service:

#### Basic Configuration
| Parameter Name | Type | Default | Mandatory for n=1 | Description |
|---------------|------|----------|-------------------|-------------|
| Service{n}Name | String | - | Yes | Service name |
| Service{n}ECRImage | String | - | Yes | ECR image URI |
| Service{n}CPUUnits | String | - | Yes | CPU units for the task |
| Service{n}Memory | String | - | Yes | Memory for the task |
| Service{n}ContainerPort | Number | 8080 | No | Container port |
| ECSCpuArchitecture | String | X86_64 | No | CPU architecture (X86_64/ARM64) |
| ECSOperatingSystemFamily | String | LINUX | No | Operating system family |
| CreateNewTaskDefinition | String | true | No | Create new task definition family |
| ExistingTaskFamily | String | "" | No | Existing task family name |

#### Routing Configuration
| Parameter Name | Type | Default | Mandatory | Description |
|---------------|------|----------|-----------|-------------|
| Service{n}PathPattern | String | - | Yes | ALB path pattern for routing |
| Service{n}RulePriority | String | - | Yes | ALB listener rule priority |
| HealthCheckPath | String | /health | No | Health check endpoint |

#### Auto-Scaling Configuration
| Parameter Name | Type | Default | Mandatory | Description |
|---------------|------|----------|-----------|-------------|
| Service{n}EnableAutoScaling | String | false | No | Enable auto-scaling |
| Service{n}MinContainers | Number | 1 | No | Minimum container count |
| Service{n}MaxContainers | Number | 4 | No | Maximum container count |
| CPUUtilizationThreshold | String | 70 | No | CPU threshold for scaling |
| MemoryUtilizationThreshold | String | 70 | No | Memory threshold for scaling |

## SSM Parameters Created

The templates create the following SSM parameters:

| Parameter Name | Description |
|---------------|-------------|
| /{AppShortName}/{EnvName}/ecs-cluster-name | ECS Cluster Name |
| /{AppShortName}/{EnvName}/ECSTaskExecutionRoleArn | Task Execution Role ARN |
| /{AppShortName}/{EnvName}/ecs-alb-security-group-id | ALB Security Group ID |
| /{AppShortName}/{EnvName}/alb-https-listener-arn | HTTPS Listener ARN |

## Production Considerations

The templates include special handling for production environments:
- DeletionPolicy and UpdateReplacePolicy set to Retain for critical resources in production
- Production environment detection for env names: prod, prod-a, prod-b
- Enhanced retention policies for logs and backups in production
- Additional security group restrictions in production environments

## Scaling ECS Services

### Adding Additional ECS Services

The template supports scaling from 1 to 4 ECS services using AWS CloudFormation change sets. To add more services:

1. **Update Parameters File**
   - Modify parameters JSON file
   - Increase `NumberOfServices` value (allowed values: 1-4)
   - Add parameters for the new service
   - Ensure unique path patterns and rule priorities

Example: Adding a second service
```json
{
  "Parameters": {
    "NumberOfServices": "2",
    
    /* Existing Service 1 parameters remain unchanged */
    
    /* Add Service 2 parameters */
    "Service2Name": "api-service",
    "Service2ECRImage": "123456789012.dkr.ecr.ap-southeast-1.amazonaws.com/repo:latest",
    "Service2CPUUnits": "1024",
    "Service2Memory": "2048",
    "Service2ContainerPort": "8080",
    "Service2PathPattern": "/api/v2/*",
    "Service2RulePriority": "20",
    "Service2EnableAutoScaling": "true",
    "Service2MinContainers": "2",
    "Service2MaxContainers": "4",
    
    /* Optional environment variables */
    "Service2EnvVar1Name": "API_VERSION",
    "Service2EnvVar1Value": "v2",
    "Service2EnvVar2Name": "LOG_LEVEL",
    "Service2EnvVar2Value": "INFO"
  }
}
```

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
   - Consider using AWS Secrets Manager for sensitive values (when enabled)

4. **Health Checks**
   - Ensure each service has a valid health check endpoint
   - Default health check path is `/health`
   - Can be customized per service using `HealthCheckPath` parameter

5. **ADOT Integration**
   - If using ADOT, ensure `EnableADOT` is set to true
   - New services will automatically integrate with ADOT collector if enabled
