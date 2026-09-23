# Data Loading with AWS Batch - Version 6

This CloudFormation template deploys a serverless data loading batch job using AWS Batch on Fargate, S3, EventBridge Scheduler/Rules, CloudWatch Logs, IAM roles, and optional integrations for SNS, SQS, Secrets Manager, SES SMTP, Step Functions, HCC Forward Proxy, and ElastiCache Redis.

For full version history and migration notes, see [`../release-notes.md`](../release-notes.md).

## Version 6 Highlights

v6 includes the v5 capabilities and adds:

- HCC Forward Proxy egress support with separate production and non-production proxy CIDRs.
- ElastiCache Redis egress support on ports `6379-6380`.
- SES SMTP egress support on port `587`.
- Step Functions permissions in `BatchJobPolicy`.
- Optional SQS send permissions as a post-release patch.

## Architecture

```text
Schedule or S3 Event
  -> EventBridge Scheduler / Rule
  -> AWS Batch Job Queue
  -> AWS Batch Fargate Job
  -> S3 / RDS / Secrets Manager / SNS / SQS / SES / Step Functions
  -> CloudWatch Logs
```

## Resources Created

| Resource Type | Purpose |
|---|---|
| `AWS::Logs::LogGroup` | Batch job logs |
| `AWS::S3::BucketPolicy` | Optional existing S3 bucket access policy |
| `AWS::SNS::Topic` | Optional job notification topic |
| `AWS::EC2::SecurityGroup` | Batch job network egress controls |
| `AWS::IAM::Role` | Batch job role and batch execution role |
| `AWS::IAM::ManagedPolicy` | Runtime and execution permissions |
| `AWS::Batch::ComputeEnvironment` | Fargate compute environment |
| `AWS::Batch::JobQueue` | Batch job queue |
| `AWS::Batch::JobDefinition` | Container image, resources, env vars, secrets |
| `AWS::Scheduler::Schedule` | Optional scheduled trigger |
| `AWS::Events::Rule` | Optional S3 event trigger |

## Parameters Summary

Full inline parameter guidance is available in `Env/parameters-dataloading.yaml`.

Parameters marked `Optional` have template defaults. Parameters marked `Conditional` are only required when the related feature is enabled.

### Core

| Parameter | Requirement | Description | Sample Value |
|---|---|---|---|
| `AppShortName` | Required | Application short name used in resource naming | `myapp` |
| `BatchJobName` | Required | Unique batch job identifier | `learner-master-data` |
| `EnvName` | Required | Environment name | `nprd-dev` |
| `VpcId` | Required | VPC ID | `vpc-0d99a0c727b301d67` |
| `AppSubnetIds` | Required | Private subnet IDs for the batch job | `subnet-abc123,subnet-def456` |
| `ECRImageUri` | Required | Full container image URI | `123456789012.dkr.ecr.ap-southeast-1.amazonaws.com/myapp-nprd-batch:latest` |
| `BatchJobVCPU` | Optional | Fargate vCPU | `2` |
| `BatchJobMemory` | Optional | Fargate memory in MiB | `4096` |
| `LogRetention` | Optional | CloudWatch log retention in days | `365` |

### Trigger

| Parameter | Requirement | Description | Sample Value |
|---|---|---|---|
| `TriggerType` | Optional | `Schedule` or `S3Event` | `Schedule` |
| `ScheduleExpression` | Conditional | Cron/rate expression for scheduled jobs when `TriggerType=Schedule` | `cron(0 12 * * ? *)` |
| `UseExistingS3` | Optional | Use existing S3 bucket | `true` |
| `ExistingBucketName` | Conditional | Existing bucket name when `UseExistingS3=true` | `sftpxxxxxxxxxxxx` |
| `InputPrefix` | Conditional | S3 input prefix filter when using S3 event trigger | `input/` |

### Secrets And Environment Variables

| Parameter | Requirement | Description | Sample Value |
|---|---|---|---|
| `DatabaseSecretName` | Optional | Primary database secret name or ARN | `myapp-nprd-dev-postgresql` |
| `AdditionalSecret2Name` to `AdditionalSecret5Name` | Optional | Extra secret names | `myapp-nprd-dev-api-key` |
| `AdditionalSecret2EnvVarName` to `AdditionalSecret5EnvVarName` | Conditional | Env var name for each extra secret when the related secret name is provided | `API_KEY` |
| `EnvVarConnectionStringSecretName` | Optional | Connection string secret name | `myapp-nprd-dev-conn-string` |
| `EnvVar1Name` / `EnvVar1Value` | Optional | Custom environment variable pair 1 | `LOG_LEVEL` / `INFO` |
| `EnvVar2Name` / `EnvVar2Value` | Optional | Custom environment variable pair 2 | `API_URL` / `https://api.internal/v1` |
| `EnvVar3Name` / `EnvVar3Value` | Optional | Custom environment variable pair 3 | `REGION` / `ap-southeast-1` |

### Networking And Egress

| Parameter | Requirement | Description | Sample Value |
|---|---|---|---|
| `VpcCidr1` to `VpcCidr5` | Optional | VPC CIDR ranges for HTTPS/SES/Redis egress | `10.55.53.0/24` |
| `VPCSubnetCidrDBAZ1` to `VPCSubnetCidrDBAZ3` | Optional | Database subnet CIDRs | `10.55.53.128/27` |
| `S3PrefixListId` | Optional | S3 prefix list ID for VPC endpoint egress | `pl-0f8e90357f89b3f45` |
| `HCCVpceCidr` | Optional | HCC VPC endpoint CIDR | `10.48.42.0/24` |
| `EnableBCSProxy` | Optional | Enable HCC Forward Proxy egress | `true` |
| `HCCProxyPort` | Optional | HCC Forward Proxy port | `4000` |
| `ProdHCCProxyCidr1/2` | Conditional | Production HCC proxy subnet CIDRs when BCS proxy is enabled for production | `10.48.40.0/27` |
| `NprdHCCProxyCidr1/2` | Conditional | Non-production HCC proxy subnet CIDRs when BCS proxy is enabled for non-production | `10.48.41.0/27` |
| `ElastiCacheSubnetAZ1/2/3` | Optional | Dedicated ElastiCache subnet CIDRs | `10.55.54.0/27` |

### Notifications And Downstream Triggers

| Parameter | Requirement | Description | Sample Value |
|---|---|---|---|
| `SNSTopicName` | Optional | SNS topic name for job notifications | `myapp-nprd-dev-notifications` |
| `SQSQueueArns` | Optional | SQS queue ARN(s) for downstream notifications | `arn:aws:sqs:ap-southeast-1:123456789012:myapp-nprd-sqs-notifications` |
| `SQSCustomerManagedKmsKeyArns` | Conditional | Customer-managed KMS key ARN(s) for encrypted SQS queues when using customer-managed KMS | `arn:aws:kms:ap-southeast-1:123456789012:key/abcd-...` |
| `EnableInputTransformation` | Optional | EventBridge input transformation for S3 events | `false` |

## Optional SQS Send Permission

The template can grant the running batch container permission to send messages to SQS.

Leave both parameters empty to keep existing behavior unchanged:

```yaml
SQSQueueArns: ""
SQSCustomerManagedKmsKeyArns: ""
```

When `SQSQueueArns` is provided, `BatchJobPolicy` grants:

```text
sqs:SendMessage
sqs:GetQueueUrl
sqs:GetQueueAttributes
```

When `SQSCustomerManagedKmsKeyArns` is provided, `BatchJobPolicy` grants:

```text
kms:GenerateDataKey
kms:Decrypt
```

`SQSCustomerManagedKmsKeyArns` is only for customer-managed KMS key ARN(s). Leave it empty when the SQS queue uses AWS managed key `alias/aws/sqs`. Do not enter `alias/aws/sqs` or an alias ARN.

## IAM Role Usage

| Role | Used By | Purpose |
|---|---|---|
| `BatchJobRole` | Running batch container through `JobRoleArn` | Application runtime access to S3, Secrets Manager, SNS, SQS, SES, Step Functions |
| `BatchExecutionRole` | AWS Batch / ECS platform through `ExecutionRoleArn` | Pull image, write logs, retrieve startup secrets |

SQS send permissions are added to `BatchJobPolicy` only, because the application code runs under `BatchJobRole`.

## Network Requirements

For private subnet deployments, ensure the batch job has network reachability to required AWS services through VPC endpoints or approved routing:

- ECR API and Docker endpoints
- S3 endpoint
- Secrets Manager endpoint
- CloudWatch Logs endpoint
- SNS endpoint if using SNS notifications
- SQS endpoint if using SQS downstream triggers
- SES SMTP endpoint if using SES email

IAM permission alone is not enough if the job cannot reach the SQS service endpoint.

## Upgrade Impact

The optional SQS patch is backward compatible:

- No new resources are created.
- No security group rules are changed.
- `BatchExecutionPolicy` is unchanged.
- Empty `SQSQueueArns` means no SQS permissions are added.
- Empty `SQSCustomerManagedKmsKeyArns` means no KMS permissions are added.

Existing v6 deployments can be updated in place. Providing SQS/KMS values updates the existing IAM managed policy attached to `BatchJobRole`.
