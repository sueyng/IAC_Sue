# AWS App Runner CloudFormation Template

This repository contains an AWS CloudFormation template to deploy an [AWS App Runner](https://docs.aws.amazon.com/apprunner/latest/dg/what-is-apprunner.html) service using a container image from Amazon ECR. The stack provisions all necessary resources, including IAM roles, VPC connectors, security groups, secrets, and auto scaling configuration.

## Features

- **App Runner Service**: Deploys a containerized application from ECR.
- **VPC Integration**: Uses a VPC connector for secure networking.
- **IAM Roles**: Grants least-privilege access for App Runner and ECR.
- **Secrets Management**: Integrates with AWS Secrets Manager for secure environment variable injection.
- **Auto Scaling**: Configurable min/max instances and concurrency.
- **Custom Tags**: All resources are tagged for traceability.

## Upgrade Note

This v1 template has been patched with the v3 functional updates while retaining the existing v1 `IaCVersion` tags. This avoids App Runner resource replacement caused by changing App Runner resource tags during in-place updates from existing v1 stacks.

## Parameters

### Core Configuration
| Parameter            | Description                                      | Example/Default                                  |
|----------------------|--------------------------------------------------|--------------------------------------------------|
| `AppShortName`       | Application short name                           | `gms`                                            |
| `EnvName`            | Environment name                                 | `nprd`, `prod`, etc.                             |
| `ServiceName`        | App Runner service name                          | `my-app-runner-service`                          |

### Secret Management (AWS Secrets Manager Integration)
| Parameter            | Description                                      | Example/Default                                  |
|----------------------|--------------------------------------------------|--------------------------------------------------|
| `EnvVar1Name`        | Environment variable name for secret 1           | `DATABASE_PASSWORD`                              |
| `EnvVar1Value`       | AWS Secrets Manager ARN for secret 1             | `arn:aws:secretsmanager:region:account:secret:name` |
| `EnvVar2-7Name`      | Additional environment variable names            | `API_KEY`, `JWT_SECRET`, etc.                    |
| `EnvVar2-7Value`     | Additional Secrets Manager ARNs                  |                                                  |
| `AdditionalSecretsManagerSecretArns` | Optional comma-separated extra secret ARNs or ARN patterns for secrets not prefixed with `AppShortName` | `arn:aws:secretsmanager:region:account:secret:shared-*` |

### Application Configuration
| Parameter            | Description                                      | Example/Default                                  |
|----------------------|--------------------------------------------------|--------------------------------------------------|
| `EcrImageUri`        | ECR image URI                                    | `123456789012.dkr.ecr.region.amazonaws.com/app:tag` |
| `ContainerPort`      | Container port                                   | `80`                                             |
| `AppRunnerCpu`       | CPU units                                        | `1024`                                           |
| `AppRunnerMemory`    | Memory (MB)                                      | `2048`                                           |
| `MaxConcurrency`     | Max concurrent requests per instance             | `100`                                            |
| `MinInstances`       | Minimum number of instances                      | `1`                                              |
| `MaxInstances`       | Maximum number of instances                      | `2`                                              |

### Health Check Configuration
| Parameter            | Description                                      | Example/Default                                  |
|----------------------|--------------------------------------------------|--------------------------------------------------|
| `HealthCheckPath`    | Health check endpoint path                       | `/health`                                        |
| `HealthyThreshold`   | Consecutive successful checks for healthy        | `2`                                              |
| `UnhealthyThreshold` | Consecutive failed checks for unhealthy          | `2`                                              |
| `HealthCheckInterval`| Interval between health checks (seconds)         | `30`                                             |
| `Timeout`            | Health check timeout (seconds)                   | `5`                                              |

### Networking Configuration
| Parameter            | Description                                      | Example/Default                                  |
|----------------------|--------------------------------------------------|--------------------------------------------------|
| `VpcId`              | VPC ID                                           | `vpc-xxxxxxxx`                                   |
| `SubnetIds`          | Comma-separated subnet IDs                       | `subnet-xxxx,subnet-yyyy`                        |
| `VpcCidr1/2/3/4/5`   | VPC CIDR IP ranges for egress                    |                                                  |
| `S3PrefixListId`     | S3 Prefix List ID for egress                     |                                                  |
| `HCCVpceCidr`        | HCC VPC Endpoint CIDR                            |                                                  |
| `HCCSubnetCidrBCSAZ1`| HCC BCS Proxy Subnet CIDR for AZ1 (optional)          |                                                  |
| `HCCSubnetCidrBCSAZ2`| HCC BCS Proxy Subnet CIDR for AZ2 (optional)          |                                                  |
| `BCSProxyPort`       | BCS Proxy port number                            | `4000`                                           |
| `AppRunnerVPCEndpoint`| VPC Endpoint ID for App Runner                   |                                                  |
| `WAFWebACLArn`       | WAF Web ACL ARN (optional)                       |                                                  |

### Database Configuration
| Parameter            | Description                                      | Example/Default                                  |
|----------------------|--------------------------------------------------|--------------------------------------------------|
| `ProdDBPort`         | Production database port                         | `53341`                                          |
| `NProdDBPort`        | Non-production database port                     | `53331`                                          |
| `VPCSubnetCidrDBAZ1-3` | Database subnet CIDR blocks                    |                                                  |
| `VPCSubnetCidrAppAZ1-3`| Application subnet CIDR blocks                 |                                                  |

## Deployment

1. **Clone the repository**  
   ```sh
   git clone <repo-url>
   cd IaC-Templates-5-apprunner/AppSubsystem/AppRunner
   ```

2. **Validate the template**  
   ```sh
   aws cloudformation validate-template --template-body file://cf-apprunner-service.yaml
   ```

3. **Deploy the stack**  
   ```sh
   aws cloudformation deploy \
     --template-file cf-apprunner-service.yaml \
     --stack-name <your-stack-name> \
     --capabilities CAPABILITY_NAMED_IAM \
     --parameter-overrides \
       AppShortName=gms \
       EnvName=nprd \
       ServiceName=my-app-runner-service \
       EcrImageUri=961341547198.dkr.ecr.ap-southeast-1.amazonaws.com/my-nginx-custom:1.27-bookworm \
       ContainerPort=80 \
       VpcId=vpc-02fb2e32bbb6ff24e \
       SubnetIds='subnet-0fe7a1d34484c75cf,subnet-0610b1fee398eb38b,subnet-0e36eb3efe04524a6' \
       AppRunnerCpu=1024 \
       AppRunnerMemory=2048 \
       SecretKeyEnvVar1=DATABASE_PASSWORD \
       SecretArn1='arn:aws:secretsmanager:ap-southeast-1:123456789012:secret:db-password-AbCdEf'
   ```

   Adjust parameter values as needed.

## Secret Management

The template supports up to 7 secrets from AWS Secrets Manager. For each secret:
1. Set `EnvVarNName` to the environment variable name your application expects
2. Set `EnvVarNValue` to the ARN of the secret in AWS Secrets Manager
3. If the secret name does not start with `AppShortName`, add the full secret ARN or ARN pattern to `AdditionalSecretsManagerSecretArns`

Example:
- `EnvVar1Name=DATABASE_PASSWORD` will create an environment variable named `DATABASE_PASSWORD`
- `EnvVar1Value=arn:aws:secretsmanager:region:account:secret:db-password-AbCdEf` will source the value from this secret
- `AdditionalSecretsManagerSecretArns=arn:aws:secretsmanager:region:account:secret:shared-*` will extend the App Runner instance role permission for non-`AppShortName` secret names

## Notes

- Ensure your AWS CLI user/role has permissions to create all resources, including Secrets Manager access.
- The template is designed for private (internal) App Runner services with VPC connectivity.
- All resources are tagged with `IaCVersion` and `Name` for traceability.
- The App Runner instance role includes permissions to access Secrets Manager.
- Environment variables from secrets are automatically injected at container startup.
- HCC BCS subnet CIDR parameters are optional - when left empty, no security group rules will be created for those subnets.
- The BCS proxy port is fixed at 4000 and used for HCC BCS subnet access when CIDR ranges are provided.

## Cleanup

To delete the stack and all associated resources:

```sh
aws cloudformation delete-stack --stack-name <your-stack-name>
```

---

**Version:** v1
