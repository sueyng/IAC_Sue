# AWS Resources Naming Convention - Backend ECS Template v5

## 1. cf-backend-ecs-main.yaml
| Resource Type | Resource Name Pattern |
|--------------|----------------------|
| CloudFormation Stack | `PrivateALBStack` |
| CloudFormation Stack | `BackendECSClusterStack` |
| CloudFormation Stack | `BackendECSADOTServiceStack` (conditional) |

## 2. cf-ecs-adot-service.yaml
| Resource Type | Resource Name Pattern |
|--------------|----------------------|
| Route53 Record | `{ADOTCustomDomainName}` |
| ALB | `{AppShortName}-{EnvName}-adot-alb` |
| Security Group | `{AppShortName}-{EnvName}-sg-adot-alb` |
| Target Group | `{AppShortName}-{EnvName}-adot-tg` |
| Log Group | `{AppShortName}-{EnvName}-adot-collector-service` |
| ECS Task Definition | `adot-collector` |
| Security Group | `{AppShortName}-{EnvName}-sg-ecs-adot` |
| ECS Service | `adot-collector` |

## 3. cf-ecs-alb.yaml
| Resource Type | Resource Name Pattern |
|--------------|----------------------|
| Security Group | `${ALBName}-sg` |
| ALB | `{ALBName}` |
| SSM Parameter | `/{ALBName}/ecs-alb-security-group-id` |
| SSM Parameter | `/{ALBName}/alb-https-listener-arn` |

## 4. cf-ecs-cluster.yaml
| Resource Type | Resource Name Pattern |
|--------------|----------------------|
| ECS Cluster | `{ECSClusterName}` |
| IAM Policy | `{ECSClusterName}-ECRPolicy` |
| IAM Policy | `{ECSClusterName}-CloudWatchPolicy` |
| IAM Policy | `{ECSClusterName}-SSMPolicy` |
| IAM Policy | `{ECSClusterName}-SQSPolicy` |
| IAM Policy | `{ECSClusterName}-SNSPolicy` |
| IAM Policy | `{ECSClusterName}-SecretsManagerAccessPolicy` |
| IAM Role | `{ECSClusterName}-TaskExecutionRole` |
| SSM Parameter | `/{ECSClusterName}/ECSTaskExecutionRoleArn` |
| SSM Parameter | `/{ECSClusterName}/secrets-manager-policy-arn` |

## 5. cf-ecs-service.yaml
| Resource Type | Resource Name Pattern |
|--------------|----------------------|
| Secrets Manager Secret | `{AppShortName}-{EnvName}-{ServiceName}` |
| Target Group | `{AppShortName}-{EnvName}-tg-ecs-{ServiceName}` |
| ALB Listener Rule | `{AppShortName}-{EnvName}-alb-rule-{ServiceName}` |
| Log Group | `/ecs/{AppShortName}/{EnvName}/{ServiceName}` |
| ECS Task Definition | `{AppShortName}-{EnvName}-{ServiceName}` or `{ExistingTaskFamily}` |
| Security Group | `{AppShortName}-{EnvName}-sg-ecs-{ServiceName}` |
| ECS Service | `{ServiceName}` |
| Auto Scaling Target | `{ServiceName}-autoscaling-target` |
| Auto Scaling Policy | `{ServiceName}-cpu-autoscaling` |
| Auto Scaling Policy | `{ServiceName}-memory-autoscaling` |

## New in v5

### Enhanced Network Security Configuration
| Parameter | Description | Default |
|-----------|-------------|---------|
| `ElasticacheSubnetAZ1` | ElastiCache subnet CIDR for AZ1 (optional) | "" |
| `ElasticacheSubnetAZ2` | ElastiCache subnet CIDR for AZ2 (optional) | "" |
| `ElasticacheSubnetAZ3` | ElastiCache subnet CIDR for AZ3 (optional) | "" |

### Enhanced Security Group Rules (v5)
| Rule Type | Description | Condition |
|-----------|-------------|-----------|
| Egress | ElastiCache access to VPC subnets (6379-6380) | Always enabled |
| Egress | ElastiCache access to dedicated subnets (6379-6380) | When ElastiCache subnet parameters provided |
| Egress | Environment-specific database ports (53341/53331) | Production vs Non-production detection |

### Resource Tagging (v5)
All resources are tagged with:
- `Name`: Resource-specific naming pattern
- `Application`: `{AppShortName}`
- `Environment`: `{EnvName}`
- `Service`: `{ServiceName}`
- `Component`: Resource type identifier
- `Version`: "v5"
- `ManagedBy`: "CloudFormation"
- `CreatedBy`: "ECS-Service-Template"

### Variable Definitions:
- `{AppShortName}`: Application short name (lowercase)
- `{EnvName}`: Environment name (e.g., prod, nprd, nprd-dev, etc.)
- `{ServiceName}`: Name of the specific ECS service (used to make resources unique)
- `{ADOTCustomDomainName}`: Custom domain name for ADOT collector
- `{ALBName}`: Name for the Application Load Balancer (used as unique identifier for ALB resources and SSM parameters)
- `{ECSClusterName}`: Name for the ECS cluster (used as unique identifier for cluster resources and SSM parameters)
- `{ExistingTaskFamily}`: Existing task definition family name (when CreateNewTaskDefinition is false)

