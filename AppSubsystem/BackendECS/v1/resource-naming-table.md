# AWS Resources Naming Convention - Backend ECS Template

## 1. cf-backend-ecs-main.yaml
| Resource Type | Resource Name Pattern |
|--------------|----------------------|
| CloudFormation Stack | `PrivateALBStack` |
| CloudFormation Stack | `BackendECSClusterStack` |
| CloudFormation Stack | `BackendECSADOTServiceStack` |
| CloudFormation Stack | `BackendECSServiceStack1` |
| CloudFormation Stack | `BackendECSServiceStack2` |
| CloudFormation Stack | `BackendECSServiceStack3` |
| CloudFormation Stack | `BackendECSServiceStack4` |

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
| Security Group | `{AppShortName}-{EnvName}-sg-alb-ecs` |
| ALB | `{AppShortName}-{EnvName}-alb-ecs` |
| SSM Parameter | `/{AppShortName}/{EnvName}/ecs-alb-security-group-id` |
| SSM Parameter | `/{AppShortName}/{EnvName}/alb-https-listener-arn` |

## 4. cf-ecs-cluster.yaml
| Resource Type | Resource Name Pattern |
|--------------|----------------------|
| ECS Cluster | `{AppShortName}-{EnvName}-ecs` |
| IAM Policy | `{AppShortName}-{EnvName}-ECSTaskECR` |
| IAM Policy | `{AppShortName}-{EnvName}-ECSTaskCloudWatch` |
| IAM Policy | `{AppShortName}-{EnvName}-ECSTaskSSM` |
| IAM Policy | `{AppShortName}-{EnvName}-ECSTaskSQS` |
| IAM Policy | `{AppShortName}-{EnvName}-secretsmanageraccess` |
| IAM Role | `{AppShortName}-{EnvName}-ecsTaskExecutionRole` |
| SSM Parameter | `/{AppShortName}/{EnvName}/ECSTaskExecutionRoleArn` |
| SSM Parameter | `/{AppShortName}/{EnvName}/ecs-cluster-name` |
| SSM Parameter | `/{AppShortName}/{EnvName}/secrets-manager-policy-arn` |

## 5. cf-ecs-service.yaml
| Resource Type | Resource Name Pattern |
|--------------|----------------------|
| Secrets Manager Secret | `{AppShortName}-{EnvName}-{ServiceName}` |
| Target Group | `{AppShortName}-{EnvName}-tg-ecs-{ServiceName}` |
| Log Group | `/ecs/{AppShortName}/{EnvName}/{ServiceName}` |
| ECS Task Definition | `{AppShortName}-{EnvName}-{ServiceName}` |
| Security Group | `{AppShortName}-{EnvName}-sg-ecs-{ServiceName}` |
| ECS Service | `{ServiceName}` |
| Auto Scaling Policy | `{ServiceName}-cpu-autoscaling` |
| Auto Scaling Policy | `{ServiceName}-memory-autoscaling` |

### Variable Definitions:
- `{AppShortName}`: Application short name (lowercase)
- `{EnvName}`: Environment name (e.g., prod, nprd, nprd-dev, etc.)
- `{ServiceName}`: Name of the specific ECS service
- `{ADOTCustomDomainName}`: Custom domain name for ADOT collector
