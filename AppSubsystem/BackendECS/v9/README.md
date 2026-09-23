# Backend ECS CloudFormation Templates - v9

This repository contains AWS CloudFormation templates for deploying ECS infrastructure and services.

## Key Features in v9

- **ECS.20 Security Hub remediation**: ECS task definitions configure non-root users in Linux container definitions via new `ContainerUser` parameter (default: `"1000"`)
- **`IsLinuxOS` condition**: `User` property applied only to Linux containers — Windows containers are unaffected
- **ELB.4 Security Hub remediation** *(post-release patch)*: Both ALBs (`PrivateALB` in `cf-ecs-alb.yaml` and `ADOTInternalALB` in `cf-ecs-adot-service.yaml`) now set `routing.http.drop_invalid_header_fields.enabled: "true"` in `LoadBalancerAttributes`. ALBs reject requests with malformed HTTP headers (RFC 7230 violations). **Stack update applies live — no ALB replacement, no DNS change, no downtime.** Compliant clients unaffected; legacy non-RFC clients may see HTTP 400s — verify in non-prod first.
- **S3 scope extension** *(post-release patch)*: New optional `AdditionalS3BucketArns` parameter on `cf-ecs-cluster.yaml` (and wired through `cf-backend-ecs-main.yaml`) allows project teams with domain-named buckets (e.g. `*.hcc.sg`) to extend the S3 IAM grant beyond `${AppShortName}*` without abandoning the v8 scope tightening. Wildcards permitted in prefix/suffix/middle (`myapp-*`, `*.hcc.sg`, `data-*-prod`); bare wildcards (`arn:aws:s3:::*` or `arn:aws:s3:::*/*`) are rejected by `AllowedPattern` at deploy time. Default `""` — no behavior change for stacks that don't set it. **Stack update applies in-place — IAM policy update only, no resource replacement.**
- **RDS Proxy IAM authentication** *(post-release patch)*: New optional `RDSProxyIAMDbUserArns` parameter on `cf-ecs-cluster.yaml` (and wired through `cf-backend-ecs-main.yaml`) grants `rds-db:connect` only to the supplied RDS Proxy `dbuser` ARN(s). Supports multiple comma-separated users. Default `""` — no `rds-db:connect` permission is granted, so existing stacks are unchanged. **Stack update applies in-place — IAM policy update only, no resource replacement.**
- All v8 features retained (see [v8 highlights](#key-features-carried-forward-from-v8) below)

### Key Features Carried Forward from v8

- **S3 permissions scoped** to `${AppShortName}*` — limits ECS task S3 access to application-owned buckets only (addresses Checkmarx IAM wildcard finding)
- **Optional CloudFormation stack notifications** via `EnableStackNotifications` toggle — publishes nested stack events to SNS topic (recommended for new stack creation only)
- **`secretsmanager:PutSecretValue`** permission added for runtime secret rotation
- **Fixed duplicate `LoadBalancerAttributes`** on ADOT ALB — both `idle_timeout` and `deletion_protection` now applied
- **Optional RDS Proxy egress** on ECS service security group via `UseRDSProxy` toggle (default `no`) and configurable `RDSProxyPort` (default `1433`) — opens egress to existing DB subnet CIDRs on the proxy listener port; reuses `VPCSubnetCidrDBAZ1/2/3` (proxy ENIs live in DB subnets)

### ⚠️ v7 → v8 Upgrade: S3 Scope Risk
The S3 permission scope change from `arn:aws:s3:::*` to `arn:aws:s3:::${AppShortName}*` means any application reading/writing S3 buckets that do **not** start with `${AppShortName}` will lose access after upgrading to v8. Before cutover:
1. Verify all S3 bucket names used by the application follow the `${AppShortName}*` naming convention.
2. If any bucket names violate the convention, options are:
   - **(a) — Recommended (v9 patch onwards):** populate the new `AdditionalS3BucketArns` parameter with the extra bucket ARNs. Supports wildcards in prefix/suffix/middle (`myapp-*`, `*.hcc.sg`, `data-*-prod`); bare `arn:aws:s3:::*` is rejected. Provide both bucket and object ARNs comma-separated, e.g. `"arn:aws:s3:::*.hcc.sg,arn:aws:s3:::*.hcc.sg/*"`.
   - **(b)** Rename the bucket to follow the convention (note: S3 buckets cannot be renamed in place — requires create-new + data copy + cutover).
   - **(c)** Attach an additional inline policy out-of-band via a separate stack.
3. Deploy to non-production environments first and verify ECS tasks can still read/write their S3 buckets before promoting to production.

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
- Supports multi-AZ deployment (2-3 AZs)
- Configurable container ports (default: 8080 for HTTP, 8443 for HTTPS)
- Optional NLB security group integration
- Stores ALB Security Group ID and HTTPS Listener ARN in SSM Parameter Store using ALBName
- Default 404 response for unmatched routes
- Health check endpoint at `/ALBhealth` with 200 OK response

#### ECS Cluster Stack Template (`cf-ecs-cluster.yaml`)
- Creates ECS Cluster with Container Insights enabled
- Configures IAM roles and policies for ECS tasks
- Provides comprehensive IAM permissions for:
  - ECR access
  - CloudWatch logs
  - SSM operations
  - Secrets Manager (scoped to `${AppShortName}*`)
  - X-Ray integration
  - SNS publishing for audit logs
  - S3 operations (scoped to `${AppShortName}*`, including presigned URL generation)
  - SQS operations
  - DynamoDB operations
  - SES email sending
  - AWS Batch Service
  - Lambda invocation
- Stores ECS Cluster Name and Task Execution Role ARN in SSM Parameter Store using ECSClusterName
- Single role used for both task execution and task runtime
- **AWS Batch job submission** (SubmitJob, DescribeJobs, TerminateJob, ListJobs, DescribeJobDefinitions, DescribeJobQueues)

#### ADOT Service Stack Template (`cf-ecs-adot-service.yaml`)
- Optional component for observability
- Deploys AWS Distro for OpenTelemetry collector
- Configures internal ALB for ADOT traffic
- Sets up proper security groups and networking
- Provides HTTPS endpoint with custom domain support
- OTLP protocol support (gRPC port 4317 and HTTP port 4318)
- Health check endpoint on port 13133
- Exports traces to AWS X-Ray
- Custom AOT_CONFIG_CONTENT for collector configuration
- Log group: `${AppShortName}-${EnvName}-adot-collector-service` (7 days retention)

### Service Template

#### ECS Service Template (`cf-ecs-service.yaml`)
- Deploys ECS services using Fargate
- Configures target groups and ALB routing:
  - Supports up to 3 path patterns per service
  - Configurable target group parameters
  - Configurable health check thresholds and intervals
  - Individual health check configurations for both target group and container
- Sets up auto-scaling policies based on CPU and Memory utilization
- Manages CloudWatch logs with configurable retention (default: 7 days)
- Supports up to 3 custom environment variables per service
- Optional ADOT integration for observability
- Advanced deployment configurations:
  - Maximum service instances: 200%
  - Minimum healthy instances: 100%
  - Circuit breaker with automatic rollback
  - Container stop timeout: 120 seconds
  - Health check grace period: 60 seconds
- Container health check configuration (optional):
  - Configurable command
  - Customizable interval (default: 30s)
  - Adjustable timeout (default: 5s)
  - Configurable retries (default: 3)
  - Customizable start period (default: 60s)
- Target group health check configuration:
  - Configurable interval (default: 15s)
  - Adjustable timeout (default: 10s)
  - Custom healthy threshold (default: 2)
  - Custom unhealthy threshold (default: 5)
  - Deregistration delay: 30 seconds

## Parameters Reference

### Infrastructure Stack Parameters

#### General Configuration
| Parameter Name | Type | Default | Mandatory | Sample Value | Description |
|---------------|------|----------|-----------|--------------|-------------|
| AppShortName | String | - | Yes | hxis | Application name |
| EnvName | String | - | Yes | nprd-dev | Environment name (nprd/prod variants) |
| EnableADOT | String | false | No | true | Enable ADOT collector deployment |
| ECSClusterName | String | - | Yes | hxis-nprd-dev-ecs-cluster | Name for the ECS cluster |
| AdditionalS3BucketArns | String | "" | No | arn:aws:s3:::*.hcc.sg,arn:aws:s3:::*.hcc.sg/* | Extra S3 bucket ARNs for buckets not following `${AppShortName}*` (e.g. domain-named). Wildcards allowed in prefix/suffix/middle; bare `arn:aws:s3:::*` rejected. Provide both bucket and object ARNs, comma-separated. |
| RDSProxyIAMDbUserArns | String | "" | No | arn:aws:rds-db:ap-southeast-1:123456789012:dbuser:prx-abcdefghijklm/app_user | RDS Proxy IAM database user ARN(s) for `rds-db:connect`. Supports multiple comma-separated `dbuser` ARNs. Leave empty to grant no RDS IAM auth permission. |

#### Network Configuration
| Parameter Name | Type | Default | Mandatory | Sample Value | Description |
|---------------|------|----------|-----------|--------------|-------------|
| VpcId | String | - | Yes | vpc-09528f37a12368b13 | VPC ID for deployment |
| AppSubnetIds | List | - | Yes | subnet-0e3f828d570c58f11,subnet-0d1706693a418f5a3 | Subnet IDs for ECS services |
| VPCSubnetCidrAZ1 | String | - | Yes | 10.53.144.128/26 | CIDR for AZ1 subnet |
| VPCSubnetCidrAZ2 | String | - | Yes | 10.53.144.192/26 | CIDR for AZ2 subnet |
| VPCSubnetCidrAZ3 | String | "" | No | 10.53.144.0/26 | CIDR for AZ3 subnet |
| VPCSubnetCidrInternetIngressAlbAZ1 | String | "" | No | 10.53.200.0/26 | Internet Ingress ALB Subnet CIDR for AZ1 |
| VPCSubnetCidrInternetIngressAlbAZ2 | String | "" | No | 10.53.200.64/26 | Internet Ingress ALB Subnet CIDR for AZ2 |
| VPCSubnetCidrInternetIngressAlbAZ3 | String | "" | No | 10.53.200.128/26 | Internet Ingress ALB Subnet CIDR for AZ3 |

#### ALB Configuration
| Parameter Name | Type | Default | Mandatory | Sample Value | Description |
|---------------|------|----------|-----------|--------------|-------------|
| ALBName | String | - | Yes | hxis-nprd-dev-alb-ecs | Name for the new Application Load Balancer to be created |
| DefaultCertificateArn | String | - | Yes | arn:aws:acm:ap-southeast-1:533267434948:certificate/xxx | ARN of default SSL certificate |
| AdditionalCertificateArn | String | "" | No | arn:aws:acm:ap-southeast-1:533267434948:certificate/yyy | ARN of additional SSL certificate |
| ALBSslPolicy | String | ELBSecurityPolicy-TLS13-1-2-2021-06 | No | ELBSecurityPolicy-TLS13-1-2-Res-PQ-2025-09 | ELB Security Policy for the HTTPS listener (TLS 1.2+ only) |
| NLBSecurityGroupId | String | "" | No | sg-0abc123def456789 | Security Group ID of the NLB to allow inbound traffic |
| ServiceContainerPort | Number | 8080 | No | 8080 | The port on which the container listens for HTTP |
| ServiceContainerSSLPort | Number | 8443 | No | 8443 | The port on which the container listens for HTTPS |
| PrefixListId | String | "" | No | pl-12345abcdef | ID of a prefix list to allow inbound HTTPS traffic |

#### ADOT Configuration (if EnableADOT = true)
| Parameter Name | Type | Default | Mandatory if ADOT enabled | Sample Value | Description |
|---------------|------|----------|--------------------------|--------------|-------------|
| ADOTContainerImage | String | - | Yes | 533267434948.dkr.ecr.ap-southeast-1.amazonaws.com/utility-images/aws-observability/aws-otel-collector:v0.104.0 | ADOT collector container image URI |
| ADOTTaskCpu | String | 256 | No | 256 | CPU units for ADOT collector |
| ADOTTaskMemory | String | 512 | No | 512 | Memory for ADOT collector in MiB |
| PrivateHostedZoneId | String | "" | No | Z095034935AWUIQP1FGLO | Route53 private hosted zone ID |
| ADOTCustomDomainName | String | - | Yes | adot.healthx.sg | Custom domain for ADOT endpoint |
| ADOTInternalCertificateArn | String | - | Yes | arn:aws:acm:ap-southeast-1:533267434948:certificate/xxx | SSL certificate ARN for ADOT ALB |
| VpcCidr1 | String | "" | No | 10.193.0.0/16 | VPC CIDR 1 IP Range |
| VpcCidr2 | String | "" | No | 172.16.0.0/16 | VPC CIDR 2 IP Range |
| VpcCidr3 | String | "" | No | 192.168.0.0/16 | VPC CIDR 3 IP Range |
| VpcCidr4 | String | "" | No | 10.194.0.0/16 | VPC CIDR 4 IP Range |
| VpcCidr5 | String | "" | No | 10.195.0.0/16 | VPC CIDR 5 IP Range |
| S3PrefixListId | String | "" | No | pl-12345678 | S3 PrefixList ID for VPC endpoint access |
| HCCVpceCidr | String | "" | No | 10.48.42.0/24 | HCC VPC Endpoint Subnet CIDR Range |
| EnableStackNotifications | String | no | No | yes | Enable CloudFormation stack event notifications on nested stacks (ALB, Cluster, ADOT). **Recommended `yes` for NEW stack creation only** — see [Stack Notifications](#stack-notifications-new-in-v8) for limitations on existing stacks. |
| StackNotificationSNSTopicArn | String | "" | Required when `EnableStackNotifications=yes` | arn:aws:sns:ap-southeast-1:123456789012:my-cfn-events | ARN of an existing SNS topic (project team must provision the topic separately). Empty when notifications are disabled. |

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
| ECRImage | String | - | Yes | 533267434948.dkr.ecr.ap-southeast-1.amazonaws.com/hxis-fhir-ecr-repo:v5.2.1 | ECR image URI |
| CPUUnits | String | - | Yes | 2048 | CPU units for the task |
| Memory | String | - | Yes | 4096 | Memory for the task in MiB |
| ServiceContainerPort | Number | - | Yes | 8080 | Container port |
| ECSCpuArchitecture | String | - | Yes | ARM64 | CPU architecture (X86_64/ARM64) |
| ECSOperatingSystemFamily | String | LINUX | No | LINUX | Operating system family |
| ContainerUser | String | 1000 | No | 1000 | Non-root UID (or UID:GID) for Linux containers — ECS.20 Security Hub compliance. Ignored for Windows containers. |
| ECSServiceProtocol | String | - | Yes | HTTP | Protocol for target group (HTTP/HTTPS) |
| ContainerProtocol | String | tcp | No | tcp | Container protocol (tcp/udp) |

#### Task Definition
| Parameter Name | Type | Default | Mandatory | Sample Value | Description |
|---------------|------|----------|-----------|--------------|-------------|
| CreateNewTaskDefinition | String | true | No | true | Create new task definition family |
| ExistingTaskFamily | String | "" | No | hxis-nprd-dev-api-service | Existing task family name (if CreateNewTaskDefinition = false) |
| ECSDesiredTaskCount | Number | - | Yes | 2 | Number of desired tasks |

#### Container Health Check Configuration
| Parameter Name | Type | Default | Mandatory | Sample Value | Description |
|---------------|------|----------|-----------|--------------|-------------|
| EnableContainerHealthCheck | String | false | No | true | Enable or disable container health checks |
| ContainerHealthCheckCommand | String | "" | No | CMD-SHELL,curl -f http://localhost:443/health | Health check command |
| ContainerHealthCheckInterval | Number | 30 | No | 30 | Time between checks (seconds) |
| ContainerHealthCheckTimeout | Number | 5 | No | 5 | Check timeout (seconds) |
| ContainerHealthCheckStartPeriod | Number | 60 | No | 60 | Grace period before checks start |
| ContainerHealthCheckRetries | Number | 3 | No | 3 | Failed attempts before unhealthy |

#### Network & Routing
| Parameter Name | Type | Default | Mandatory | Sample Value | Description |
|---------------|------|----------|-----------|--------------|-------------|
| VPCSubnetCidrAZ1 | String | - | Yes | 10.53.144.128/26 | CIDR for AZ1 subnet |
| VPCSubnetCidrAZ2 | String | - | Yes | 10.53.144.192/26 | CIDR for AZ2 subnet |
| VPCSubnetCidrAZ3 | String | - | Yes | 10.53.144.0/26 | CIDR for AZ3 subnet |
| ElasticacheSubnetAZ1 | String | "" | No | 10.0.51.0/24 | ElastiCache subnet CIDR for AZ1 (optional) |
| ElasticacheSubnetAZ2 | String | "" | No | 10.0.52.0/24 | ElastiCache subnet CIDR for AZ2 (optional) |
| ElasticacheSubnetAZ3 | String | "" | No | 10.0.53.0/24 | ElastiCache subnet CIDR for AZ3 (optional) |
| PathPattern | String | - | Yes | /api/* | Primary ALB path pattern |
| PathPattern2 | String | "" | No | /v2/api/* | Secondary ALB path pattern (optional) |
| PathPattern3 | String | "" | No | /legacy/* | Tertiary ALB path pattern (optional) |
| ALBRulePriorityForService | String | 2 | No | 100 | ALB listener rule priority |
| TGHealthCheckPath | String | - | Yes | /health | Health check endpoint |
| TGHealthCheckIntervalSeconds | Number | 15 | No | 15 | Time period in seconds between target group health checks |
| TGHealthCheckTimeoutSeconds | Number | 10 | No | 10 | Time period in seconds to wait for a target group health check response |
| TGHealthyThresholdCount | Number | 2 | No | 2 | Number of consecutive successful health checks before considering target healthy |
| TGUnhealthyThresholdCount | Number | 5 | No | 5 | Number of consecutive failed health checks before considering target unhealthy |

#### Environment Variables
| Parameter Name | Type | Default | Mandatory | Sample Value | Description |
|---------------|------|----------|-----------|--------------|-------------|
| EnvVarConnectionStringSecretName | String | "" | No | hxis-nprd-dev-api-service | Name of the secret in Secrets Manager |
| EnvVar1Name | String | "" | No | Logging__LogLevel | Environment variable 1 name |
| EnvVar1Value | String | "" | No | Information | Environment variable 1 value |
| EnvVar2Name | String | "" | No | ApiVersion | Environment variable 2 name |
| EnvVar2Value | String | "" | No | v1 | Environment variable 2 value |
| EnvVar3Name | String | "" | No | FeatureFlag | Environment variable 3 name |
| EnvVar3Value | String | "" | No | true | Environment variable 3 value |
| LogsRetentionInDays | String | 7 | No | 30 | Number of days to retain CloudWatch logs |

#### Auto-Scaling Configuration
| Parameter Name | Type | Default | Mandatory | Sample Value | Description |
|---------------|------|----------|-----------|--------------|-------------|
| EnableAutoScaling | String | false | No | true | Enable auto-scaling |
| MinContainers | Number | - | No | 1 | Minimum container count |
| MaxContainers | Number | - | No | 4 | Maximum container count |
| CPUUtilizationThreshold | String | - | No | 70 | CPU threshold percentage |
| MemoryUtilizationThreshold | String | - | No | 70 | Memory threshold percentage |

#### ADOT Configuration
| Parameter Name | Type | Default | Mandatory | Sample Value | Description |
|---------------|------|----------|-----------|--------------|-------------|
| EnableADOT | String | false | No | true | Enable ADOT integration |
| ADOTEndpoint | String | "" | No | https://adot.healthx.sg | ADOT collector endpoint |

#### VPC and Security Configuration
| Parameter Name | Type | Default | Mandatory | Sample Value | Description |
|---------------|------|----------|-----------|--------------|-------------|
| VpcCidr1 | String | "" | No | 10.0.0.0/16 | VPC CIDR 1 IP Range |
| VpcCidr2 | String | "" | No | 172.16.0.0/16 | VPC CIDR 2 IP Range |
| VpcCidr3 | String | "" | No | 192.168.0.0/16 | VPC CIDR 3 IP Range |
| VpcCidr4 | String | "" | No | 10.194.0.0/16 | VPC CIDR 4 IP Range |
| VpcCidr5 | String | "" | No | 10.195.0.0/16 | VPC CIDR 5 IP Range |
| VPCSubnetCidrDBAZ1 | String | - | Yes | 10.0.10.0/24 | AZ1 Database Subnet CIDR |
| VPCSubnetCidrDBAZ2 | String | - | Yes | 10.0.11.0/24 | AZ2 Database Subnet CIDR |
| VPCSubnetCidrDBAZ3 | String | - | Yes | 10.0.12.0/24 | AZ3 Database Subnet CIDR |
| ProdDBPort | String | 53341 | No | 53341 | Database port for production environments |
| NProdDBPort | String | 53331 | No | 53331 | Database port for non-production environments |
| S3PrefixListId | String | "" | No | pl-12345678 | S3 PrefixList ID for VPC endpoint egress access |
| DynamoDBPrefixListId | String | "" | No | pl-12345679 | DynamoDB PrefixList ID for VPC endpoint egress access |
| ExternalServicesPrefixListId | String | "" | No | pl-1234567a | Customer-managed prefix list covering external services (CAG, ESB, etc.) reachable over HTTPS 443. Single list (not per-service) to conserve SG rule quota. |
| HCCVpceCidr | String | "" | No | 10.100.0.0/16 | HCC VPC Endpoint Subnet CIDR Range |
| HCCSubnetCidrBCSAZ1 | String | "" | No | 10.200.0.0/24 | BCS Proxy CIDR block for outbound internet traffic. If specified, allows ECS service to route traffic through the proxy |
| HCCSubnetCidrBCSAZ2 | String | "" | No | 10.200.0.0/24 | BCS Proxy CIDR block for outbound internet traffic. If specified, allows ECS service to route traffic through the proxy |
| BCSProxyPort | String | "4000" | No | 4000 | BCS Proxy port for outbound internet traffic. Required if HCCSubnetCidrBCSAZ1 or HCCSubnetCidrBCSAZ2 is specified |
| UseRDSProxy | String | "no" | No | yes / no | Set to `yes` if app connects via RDS Proxy. Adds egress rules to existing DB subnet CIDRs (`VPCSubnetCidrDBAZ1/2/3`) on `RDSProxyPort`. RDS Proxy ENIs live in the DB subnets — no separate CIDR parameter needed. |
| RDSProxyPort | String | "1433" | No | 1433 / 5432 | RDS Proxy listener port (default 1433 for SQL Server). Used only when `UseRDSProxy=yes`. |

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

## What's New in v5

### Enhanced Network Security
- **ElastiCache Subnet Support**: Added conditional ElastiCache subnet parameters for dedicated ElastiCache network access
- **Additional Application Networks**: Support for prefix list-based additional application network access
- **Dual ElastiCache Configuration**: Support for both VPC-wide and ElastiCache-specific subnet access patterns
- **Dynamic Database Port Selection**: Environment-based port selection (prod: 53341, non-prod: 53331)

### New Parameters in v5
- `ElasticacheSubnetAZ1`: Optional dedicated ElastiCache subnet for AZ1
- `ElasticacheSubnetAZ2`: Optional dedicated ElastiCache subnet for AZ2  
- `ElasticacheSubnetAZ3`: Optional dedicated ElastiCache subnet for AZ3

### Conditional Security Rules
- ElastiCache egress rules are created only when ElastiCache subnet parameters are provided
- Backward compatibility maintained with existing VPC subnet-based ElastiCache access

## Deployment Strategy

### 1. Infrastructure Deployment
Deploy core infrastructure first using the main stack:
```
v8/
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
     - ALB Listener Rule (supports up to 3 path patterns)
     - Security Groups
     - Empty Secrets Manager Secret (format: `${AppShortName}-${EnvName}-${ServiceName}`)
   - Note: CloudWatch Log Group, ECS Task Definition, ECS Service, and Auto Scaling resources will **NOT** be created in this phase
   - This conditional deployment prevents failures from missing secrets

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
   - Update the service parameters YAML file (`env/parameters-ecs-service.yaml`)
   - Set `EnvVarConnectionStringSecretName` to the secret name:
     ```yaml
     EnvVarConnectionStringSecretName: "hxis-nprd-stg-ccdp"
     ```

2. **Final Service Deployment**
   - Run service pipeline again with updated parameters
   - CloudFormation will now:
     - Create CloudWatch Log Group
     - Create ECS Task Definition
     - Deploy ECS Service
     - Register targets with ALB
     - Configure auto-scaling (if enabled with `EnableAutoScaling: true`)
   - All resources are created in this phase once the secret name is provided

## Conditional Resource Creation

The template uses smart conditional logic to ensure proper deployment order:

### Resources Created in Phase 1 (Without Secret Name)
- ✅ Secrets Manager Secret (empty)
- ✅ Target Group
- ✅ ALB Listener Rule
- ✅ Security Group
- ❌ CloudWatch Log Group (skipped - **currently not implemented, needs fix**)
- ❌ ECS Task Definition (skipped)
- ❌ ECS Service (skipped)
- ❌ Auto Scaling resources (skipped)

### Resources Created in Phase 2 (With Secret Name)
- ✅ CloudWatch Log Group (**currently created in Phase 1, needs fix**)
- ✅ ECS Task Definition
- ✅ ECS Service
- ✅ Auto Scaling Target (if `EnableAutoScaling: true`)
- ✅ Auto Scaling Policies (if `EnableAutoScaling: true`)

### Key Benefits
- **Prevents Dependency Errors**: Auto scaling won't try to reference non-existent ECS service
- **Ensures Secret Availability**: ECS service only deploys when secrets are ready
- **Clean Resource Management**: Avoids orphaned resources from failed deployments

### Known Issue
⚠️ **CloudWatch Log Group Condition Missing**: The template currently creates the CloudWatch Log Group in Phase 1, but it should only be created in Phase 2. This needs to be fixed by adding `Condition: HasEnvVarConnectionStringSecretName` to the CloudWatchLogGroup resource.

## Example Deployment Flow

```
┌─────────────────────────┐
│  Infrastructure Stack   │
│  Deployment            │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│  Service Stack Phase 1  │
│  Initial Deployment     │
│  (Empty Secret Name)    │
│  Creates: Secret, TG,   │
│  ALB Rules, SG, Logs*   │
│  *Log should be Phase 2 │
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
│  Service Stack Phase 2  │
│  Final Deployment       │
│  (With Secret Name)     │
│  Creates: Task Def,     │
│  ECS Service,           │
│  Auto Scaling           │
└─────────────────────────┘
```

## Monitoring & Logging

### CloudWatch Logs
- All ECS services log to CloudWatch Logs
- Log groups follow pattern: `/ecs/${AppShortName}/${EnvName}/${ServiceName}`
- Configurable retention period via `LogsRetentionInDays` parameter (default: 7 days)
- Container Insights enabled by default on ECS cluster
- **Note**: Log group currently created in Phase 1, but should be Phase 2

### ADOT Integration
When ADOT is enabled:
- Traces exported to AWS X-Ray
- Metrics available in CloudWatch
- OTLP endpoint available at custom domain (HTTPS on port 443)
- Supports both OTLP/gRPC (port 4317) and OTLP/HTTP (port 4318)
- Environment variables automatically configured for OTLP endpoints:
  - `OTEL_EXPORTER_OTLP_ENDPOINT`: ADOT collector endpoint
  - `OTEL_EXPORTER_OTLP_PROTOCOL`: "grpc"
  - `OTEL_EXPORTER_OTLP_INSECURE`: "false"
- ADOT collector logs to: `${AppShortName}-${EnvName}-adot-collector-service`

### Health Checks
- Dual health check system:
  1. **ALB Target Group Health Checks**:
     - Configurable path via `TGHealthCheckPath`
     - Configurable interval via `TGHealthCheckIntervalSeconds` (default: 15s)
     - Adjustable timeout via `TGHealthCheckTimeoutSeconds` (default: 10s)
     - Customizable healthy threshold via `TGHealthyThresholdCount` (default: 2)
     - Customizable unhealthy threshold via `TGUnhealthyThresholdCount` (default: 5)
     - HTTP/HTTPS protocol support
     - HTTP 200 matcher
     - Deregistration delay: 30 seconds
  2. **Container-Level Health Checks** (Optional):
     - Enable via `EnableContainerHealthCheck: true`
     - Configurable command via `ContainerHealthCheckCommand` (e.g., CMD-SHELL,curl -f http://localhost/health)
     - Adjustable interval via `ContainerHealthCheckInterval` (default: 30s)
     - Adjustable timeout via `ContainerHealthCheckTimeout` (default: 5s)
     - Customizable start period via `ContainerHealthCheckStartPeriod` (default: 60s)
     - Configurable retry attempts via `ContainerHealthCheckRetries` (default: 3)
- ALB health check endpoint: `/ALBhealth` returns 200 OK
- ECS service health check grace period: 60 seconds
- Default application health check path: `/health`

## ALB Path Routing

The template supports up to **3 path patterns** per service for flexible routing:

### Configuration
```yaml
PathPattern: "/api/*"
PathPattern2: "/v2/api/*"
PathPattern3: "/legacy/*"
```

### Use Cases
- **API Versioning**: Route `/api/v1/*` and `/api/v2/*` to the same service
- **Legacy Support**: Handle both `/new-path/*` and `/old-path/*` routes
- **Multiple Endpoints**: Service responding to different base paths

## Security Considerations

### Network Security
- All ECS services run in private subnets
- Security groups limit access to required ports only
- ALB Security Group Ingress:
  - HTTPS (443) from app subnet CIDRs (AZ1, AZ2, optional AZ3)
  - HTTPS (443) from Internet Ingress ALB subnets (optional)
  - HTTPS (443) from NLB security group (optional)
  - HTTPS (443) from prefix list (optional)
- ALB Security Group Egress:
  - To container ports (HTTP and HTTPS) in app subnets
- ECS Service Security Group Ingress:
  - Container port from app subnet CIDRs
  - Container port from ALB security group
- ECS Service Security Group Egress:
  - HTTPS (443) to up to 5 VPC CIDR ranges
  - ElastiCache ports (6379-6380) to app subnets (always enabled)
  - ElastiCache ports (6379-6380) to ElastiCache subnets (conditional, when ElastiCache subnet parameters provided)
  - Database port (production: 53341, non-prod: 53331) to DB subnets
  - Database port (production: 53341, non-prod: 53331) to additional application networks via prefix list (conditional)
  - HTTPS (443) to S3 endpoint via prefix list (optional)
  - HTTPS (443) to DynamoDB endpoint via prefix list (optional)
  - HTTPS (443) to external services (CAG, ESB, etc.) via single customer-managed prefix list (optional)
  - HTTPS (443) to HCC VPC endpoint (optional)
- ALB terminates SSL/TLS traffic with configurable TLS policy via `ALBSslPolicy` parameter (default: `ELBSecurityPolicy-TLS13-1-2-2021-06`, TLS 1.2+ only)
- Optional prefix list support for granular network access control
- Deletion protection enabled on ALBs

### IAM Security
- Least privilege principle applied to all roles
- Single role used for both task execution and task runtime
- Secrets Manager access scoped to: `${AppShortName}*`
- SNS publish permissions for audit logging
- Comprehensive IAM policies for:
  - ECR (image pull)
  - CloudWatch (logs and metrics)
  - SSM (parameter store and session manager)
  - SQS (message queue operations)
  - S3 (object operations, scoped to `${AppShortName}*` by default; extendable via `AdditionalS3BucketArns` parameter for domain-named or non-conforming buckets)
  - RDS Proxy IAM authentication (`rds-db:connect`, optional and scoped to `RDSProxyIAMDbUserArns`)
  - SNS (publish notifications)
  - DynamoDB (read/write operations)
  - SES (email sending)
  - X-Ray (tracing)
  - **AWS Batch (job submission and management)** - Enables ECS services to programmatically submit and manage batch jobs
  - **Lambda (function invocation)** - Enables ECS services to invoke Lambda functions

### Secrets Management
- Secrets stored in AWS Secrets Manager
- Automatic secret creation during Phase 1 with empty values
- ECS service only deploys after secrets are populated
- Secret values never exposed in CloudFormation templates
- Secrets encrypted with AWS managed KMS key (`alias/aws/secretsmanager`)
- Secret format:
  ```json
  {
    "ConnectionStrings__Local": "",
    "ConnectionStrings__FhirMetadata": ""
  }
  ```

## Production Considerations

The templates include special handling for production environments:
- DeletionPolicy and UpdateReplacePolicy set to Retain for critical resources in production
- Production environment detection for env names: prod, prod-a, prod-b, prod-c
- Enhanced retention policies for logs and backups in production
- Additional security measures:
  - ALB deletion protection enabled
  - Dynamic database port selection (53341 for prod, 53331 for non-prod)
  - Retained resources on stack deletion

## Important Notes

### Two-Phase Deployment Process
- The two-phase deployment is **by design** to ensure secure secret management
- **Phase 1**: Creates infrastructure without ECS service
  - Creates Secrets Manager secret, Target Group, ALB rules, Security Groups
  - Prevents deployment failures from missing secrets
  - **Note**: Currently also creates CloudWatch Log Group (should be Phase 2)
- **Phase 2**: Deploys complete service stack
  - Creates Task Definition, ECS Service, Auto Scaling
  - Only proceeds when secrets are properly configured

### Conditional Deployment Logic
- Template uses `HasEnvVarConnectionStringSecretName` condition to control resource creation
- Auto scaling resources use combined condition `HasECSServiceAndAutoScaling`
- This prevents dependency errors where auto scaling tries to reference non-existent ECS service
- **Known Issue**: CloudWatch Log Group should use `HasEnvVarConnectionStringSecretName` condition but currently doesn't

### Secret Name Parameter
- First deployment: Leave `EnvVarConnectionStringSecretName` empty
- Second deployment: Provide the secret name (e.g., `hxis-nprd-stg-ccdp`)
- The secret must be populated with valid connection strings between deployments
- This approach ensures services never start with missing or empty secrets

### Container Configuration
- Read-only root filesystem enabled for security
- Tmpfs volume mounted at `/tmp/` for writable temporary storage
- Container stop timeout: 120 seconds (maximum for Fargate)
- Port mappings use `AppProtocol: http` for proper health checks

### Best Practices
- Always test in non-production environments first
- Verify secret format matches application requirements
- Monitor CloudWatch Logs during initial service startup
- Use descriptive service names for easier troubleshooting
- Configure appropriate health check parameters for your application
- Set realistic auto-scaling thresholds based on load testing
- Use multiple path patterns for API versioning and backward compatibility
- Configure container health checks for applications with critical dependencies

#### v5 Configuration Examples

#### Version Tagging Best Practices
**Container Image Versioning for v5:**
- **ADOT Collector**: Use specific versions instead of `:latest` (e.g., `:v0.104.0`)
- **Application Images**: Use semantic versioning aligned with v5 (e.g., `:v5.2.1`, `:v5.1.0`)
- **Avoid `:latest` tags** in production to ensure deployment consistency

**Recommended Image Tag Formats:**
```yaml
ECRImage: "533267434948.dkr.ecr.ap-southeast-1.amazonaws.com/my-app:v5.2.1"
ADOTContainerImage: "533267434948.dkr.ecr.ap-southeast-1.amazonaws.com/utility-images/aws-observability/aws-otel-collector:v0.104.0"
```

#### ElastiCache Network Configuration
```yaml
ElasticacheSubnetAZ1: "10.0.51.0/24"
ElasticacheSubnetAZ2: "10.0.52.0/24"
ElasticacheSubnetAZ3: "10.0.53.0/24"
```

#### Port Configuration Fix for Health Checks
**Critical**: Ensure port consistency between container and health check:
```yaml
ServiceContainerPort: "80"
ContainerHealthCheckCommand: "CMD-SHELL,curl -f http://localhost:80/health"
```

## Troubleshooting

### Common Issues

1. **Stack Creation Failures**:
   - **Issue**: Stack fails during initial deployment
   - **Solution**: 
     - Check CloudWatch Logs for service deployment issues
     - Verify subnet and CIDR configurations
     - Ensure certificate ARNs are valid
     - Check IAM Role permissions
     - Confirm VPC endpoints are properly configured
     - Verify S3 bucket for templates is accessible

2. **Service Health Issues**:
   - **Issue**: Service marked as unhealthy in target group
   - **Solution**:
     - Verify health check endpoint responds correctly (check path and port)
     - Check security group rules allow traffic from ALB
     - Validate container port configurations match `ServiceContainerPort`
     - Review task definition environment variables
     - Check if application is listening on correct port
     - Increase `ContainerHealthCheckStartPeriod` for slow-starting apps
     - Verify health check returns HTTP 200

3. **Auto Scaling Not Working**:
   - **Issue**: Service doesn't scale despite high CPU/memory
   - **Solution**:
     - Verify `EnableAutoScaling` is set to `true`
     - Ensure `EnvVarConnectionStringSecretName` is provided (required for auto scaling)
     - Check CloudWatch metrics for CPU/memory utilization
     - Verify thresholds are appropriate for your workload
     - Confirm ECS service is running properly
     - Check auto-scaling target and policies are created

4. **Secret Access Errors**:
   - **Issue**: Container fails to start with secret access errors
   - **Solution**:
     - Verify secret exists in AWS Secrets Manager
     - Check secret name matches `EnvVarConnectionStringSecretName` parameter
     - Confirm IAM role has Secrets Manager permissions
     - Ensure secret is in the same region as ECS service
     - Validate secret JSON format
     - Check secret follows naming pattern: `${AppShortName}*`

5. **ADOT Issues**:
   - **Issue**: Tracing not working with ADOT
   - **Solution**:
     - Check SSL certificate validity for ADOT ALB
     - Review collector logs in CloudWatch: `${AppShortName}-${EnvName}-adot-collector-service`
     - Verify ADOT endpoint is accessible from ECS tasks
     - Confirm `EnableADOT` is set to `true`
     - Check security group allows outbound HTTPS to ADOT endpoint
     - Validate `ADOTEndpoint` parameter format (should be https://domain)
     - Verify X-Ray daemon is running in ADOT collector
     - Check OTLP ports (4317 for gRPC, 4318 for HTTP) are accessible

6. **Multiple Path Patterns Not Working**:
   - **Issue**: Only first path pattern routes correctly
   - **Solution**:
     - Verify `PathPattern2` and `PathPattern3` are properly formatted
     - Check ALB listener rule priority doesn't conflict with other services
     - Confirm all path patterns are valid ALB patterns (use /* wildcards correctly)
     - Review ALB listener rules in AWS Console
     - Ensure priority values are unique across all services

7. **Container Health Check Failures**:
   - **Issue**: Container marked unhealthy even when application is running
   - **Solution**:
     - Verify `ContainerHealthCheckCommand` is correct
     - Check if curl or health check tool is available in container
     - Increase `ContainerHealthCheckTimeout` for slow responses
     - Adjust `ContainerHealthCheckStartPeriod` for applications with long startup time
     - Review container logs for health check execution errors
     - Ensure health check endpoint is accessible from within container
     - Test health check command manually using ECS Exec

8. **Phase 2 Deployment Fails**:
   - **Issue**: Second deployment fails after adding secret name
   - **Solution**:
     - Verify secret contains all required connection strings
     - Check secret JSON format is valid
     - Ensure secret name in parameter matches actual secret name (case-sensitive)
     - Confirm no typos in `EnvVarConnectionStringSecretName`
     - Review CloudFormation stack events for specific error
     - Check IAM permissions for Secrets Manager access

9. **ALB 404 Errors**:
   - **Issue**: ALB returns 404 for all requests
   - **Solution**:
     - Verify path patterns match incoming requests
     - Check ALB listener rules are created with correct priority
     - Confirm target group has healthy targets
     - Review ALB access logs for request routing
     - Verify service is registered with correct target group

10. **Container Cannot Write to Filesystem**:
    - **Issue**: Application fails with write permission errors
    - **Solution**:
      - Remember root filesystem is read-only by design
      - Use `/tmp/` directory for temporary writes (Tmpfs volume mounted)
      - Modify application to write only to `/tmp/`
      - Consider external storage (S3, EFS) for persistent data

11. **ECS Deployment Circuit Breaker Triggered**:
    - **Issue**: "ECS Deployment Circuit Breaker was triggered" error
    - **Solution**:
      - **Port Mismatch**: Ensure ServiceContainerPort matches health check port
      - **Health Check Path**: Verify application serves health endpoint at configured path
      - **Application Startup Time**: Increase ContainerHealthCheckStartPeriod for slow-starting apps
      - **Resource Constraints**: Check if CPU/Memory allocation is sufficient
      - **Network Connectivity**: Verify security groups allow required outbound connections
      - **Container Image**: Confirm ECR image exists and architecture matches (ARM64/X86_64)
      - **Secret Dependencies**: Ensure all required secrets are populated before deployment

12. **ElastiCache Egress Rules Missing**:
    - **Issue**: ElastiCache subnet egress rules not appearing in security group
    - **Solution**:
      - Verify ElastiCache subnet parameters have values (not empty strings)
      - Ensure CloudFormation stack has been updated with latest template
      - Check conditions: HasElasticacheSubnetAZ1/AZ2/AZ3 are evaluating correctly
      - Redeploy/update the stack to apply new conditional rules
      - Verify parameter values match expected CIDR format (e.g., 10.0.51.0/24)

## Stack Notifications (new in v8)

v8 introduces optional CloudFormation stack event notifications via SNS, addressing the Checkmarx finding on disabled stack notifications.

### How it works
- Set `EnableStackNotifications: yes` and provide `StackNotificationSNSTopicArn`.
- Nested stacks (`PrivateALBStack`, `BackendECSClusterStack`, `BackendECSADOTServiceStack`) are configured with the SNS topic via the `NotificationARNs` property.
- The SNS topic is **not provisioned by this template** — project teams must create the topic separately and pass its ARN.

### Recommendation
- **Turn ON for NEW stack creation.** Notifications will apply to all newly created nested stacks.
- **Existing stacks**: see limitations below before flipping the toggle on.

### ⚠️ Limitations

**1. Existing nested stacks will NOT be updated automatically**
The `NotificationARNs` property on a nested stack resource is honored by CloudFormation only at **child stack creation time**. If you upgrade an existing v7 deployment to v8 and set `EnableStackNotifications=yes`, the parent stack will accept the change, but the already-created nested stacks (ALB, Cluster, ADOT) will NOT pick up the new SNS topic.

**Workaround for existing stacks** — update each nested stack manually:
- **CloudFormation Console**: select the nested stack → *Update* → *Use current template* → on the next page, edit *Notification options* → add the SNS topic ARN. Alternatively use *Stack actions* → *Create change set* with current template and add the notification ARN there.
- **AWS CLI**:
  ```bash
  aws cloudformation update-stack \
    --stack-name <nested-stack-name> \
    --use-previous-template \
    --notification-arns <sns-topic-arn> \
    --capabilities CAPABILITY_NAMED_IAM
  ```

**2. Parent stack is not configured by this template**
CloudFormation does not allow a stack to self-configure its own notification target via the template — this is an AWS design constraint (the `NotificationARNs` property only exists on the `AWS::CloudFormation::Stack` resource type for nested/child stacks).

To enable notifications on the **parent stack**, configure it at deploy time:
- **CloudFormation Console**: when creating/updating the parent stack, expand *Notification options* and add the SNS topic ARN.
- **AWS CLI**: pass `--notification-arns <sns-topic-arn>` on `aws cloudformation create-stack` or `update-stack`.

### Backward compatibility
The toggle defaults to `no`, so existing v7 deployments upgrading to v8 are not forced to provide an SNS topic. Notifications can be added incrementally (see Workaround above).

## Known Issues and Limitations

### Limitation 1: Maximum Path Patterns
**Description**: Services support maximum of 3 path patterns
**Workaround**: Deploy multiple services or use wildcard patterns more effectively

### Limitation 2: Auto Scaling Metrics
**Description**: Only CPU and Memory-based auto-scaling supported
**Workaround**: Use custom CloudWatch metrics and alarms for advanced scaling

### Limitation 3: Container Stop Timeout
**Description**: Maximum container stop timeout is 120 seconds (Fargate limit)
**Workaround**: Ensure application handles SIGTERM gracefully within 120 seconds
