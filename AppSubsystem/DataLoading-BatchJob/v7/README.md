# Data Loading with AWS Batch — Version 7

This CloudFormation template deploys a serverless data loading infrastructure using **AWS Batch (Fargate)**, **S3**, **EventBridge Scheduler/Rules**, and **CloudWatch Logs**. It supports both schedule-based and S3-event-based triggers, with optional integrations for SNS notifications, SQS downstream triggers, multi-secret access, ElastiCache Redis, SES SMTP, and Step Functions.

> **Looking for the full version history and migration notes?** See [`../release-notes.md`](../release-notes.md).

---

## Version 7 Highlights

**v7 = v6 + ECS.20 remediation (non-root container) + comprehensive `IaCVersion` tagging.**

- **`ContainerUser` parameter** (default `1000`) — UID or UID:GID for the batch container
  - `AllowedPattern` blocks root (`0` and `0:0`)
  - Injected as `User: !Ref ContainerUser` into `BatchJobDefinition.ContainerProperties`
  - Combined with the existing `ReadonlyRootFilesystem: true`, this satisfies AWS Security Hub control **ECS.20**
- **IaCVersion tag** bumped to `AppSubsystem-BatchJob-v7` and applied to `DataLoadingLogGroup` and `BatchJobDefinition` (in-template). `BatchComputeEnvironment` and `BatchJobQueue` are tagged out-of-band via `aws batch tag-resource` — their CFN `Tags` property requires resource replacement, which is blocked by the custom resource names. See the coverage table in [Resources Created](#resources-created).

> **Driver:** HCC compliance scope — Security Hub ECS.20 is no longer optional.

> **All v6 features carried forward:** HCC Forward Proxy, ElastiCache Redis egress, SES SMTP egress, Step Functions IAM, multi-secret support, custom env vars.

### Optional SQS Send Permission

The template supports optional SQS send permissions for batch jobs that publish messages to downstream queues.

| Parameter | Description | Default |
|---|---|---|
| `SQSQueueArns` | Comma-delimited SQS queue ARN(s) the batch job container can send messages to | `""` |
| `SQSCustomerManagedKmsKeyArns` | Comma-delimited customer-managed KMS key ARN(s) for encrypted SQS queues | `""` |

When `SQSQueueArns` is empty, no SQS permissions are added. When `SQSCustomerManagedKmsKeyArns` is empty, no KMS permissions are added. Leave `SQSCustomerManagedKmsKeyArns` empty for SQS queues encrypted with AWS managed key `alias/aws/sqs`.

---

## ⚠️ Pre-Upgrade Requirement: Container Image Must Run as Non-Root

Before upgrading from v6 to v7, **verify your container image works as UID 1000** (or whatever value you set `ContainerUser` to).

### Checklist
1. **Inspect Dockerfile** — does it have a `USER` directive? Default-root images may break under v7.
2. **Test locally:**
   ```bash
   docker run --user 1000:1000 --read-only <your-image-uri> <entrypoint-cmd>
   ```
   The container must start cleanly with no `Permission denied` errors.
3. **App writes to allowed paths only** — `ReadonlyRootFilesystem: true` was already in v6, so you should already be writing only to `/tmp` or volume mounts.
4. **If your image needs a different UID** (e.g. nginx-base uses `100:100`), override:
   ```yaml
   ContainerUser: "100:100"
   ```

### Common failure modes if image isn't ready
| Symptom | Cause | Fix |
|---|---|---|
| `Permission denied` writing to log path | Path owned by root | `RUN chown 1000:1000 /path` in Dockerfile |
| Container exits immediately, no logs | Entrypoint needs root | Refactor entrypoint to drop privileges before start |
| Cannot bind to port < 1024 | Non-root can't bind privileged ports | Use port ≥ 1024 (rarely applies to batch) |

---

## Architecture

```
                          ┌──────────────────┐
   Schedule ─────────────▶│   EventBridge    │
                          │ Scheduler / Rule │──┐
                          └──────────────────┘  │
                                                ▼
   ┌───────────┐    S3 PUT       ┌──────────────────────┐    submit job    ┌──────────────────────────┐
   │   S3      │────────────────▶│  EventBridge Rule    │─────────────────▶│   AWS Batch Queue        │
   │  Bucket   │                 │  (S3-event trigger)  │                  │     (Fargate)            │
   └───────────┘                 └──────────────────────┘                  │   User: 1000 (non-root)  │
                                                                           │   ReadonlyRootFilesystem │
                                                                           └──────────┬───────────────┘
                                                                                      │
                                                                                      ▼
                              ┌─────────────┐  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐
                              │   RDS DB    │  │ Secrets Mgr │  │  ElastiCache │  │   SES SMTP   │
                              │  (private)  │  │  (1+5 sec)  │  │    Redis     │  │  (port 587)  │
                              └─────────────┘  └─────────────┘  └──────────────┘  └──────────────┘
                                                       │
                                                       ▼
                                              ┌─────────────────┐  ┌──────────────┐
                                              │  Step Functions │  │     SNS      │
                                              │   (optional)    │  │ (job status) │
                                              └─────────────────┘  └──────────────┘
```

---

## Resources Created

| Resource | Purpose |
|---|---|
| `AWS::Logs::LogGroup` | Centralized log retention for batch container output |
| `AWS::S3::BucketPolicy` *(conditional)* | Enforces TLS 1.2+ on existing S3 bucket; auto-skipped when `UseExistingS3=false` |
| `AWS::EC2::SecurityGroup` | Egress-only — HTTPS to VPC CIDRs/S3-prefix-list, DB ports, SES SMTP, Redis, HCC proxy |
| `AWS::IAM::Role` ×2 | `BatchJobRole` (task) + `BatchExecutionRole` (Fargate platform) |
| `AWS::IAM::Policy` ×2 | Granular per-secret + Step Functions + S3 + SNS + optional SQS |
| `AWS::Batch::ComputeEnvironment` | Fargate compute env (max 4 vCPU) |
| `AWS::Batch::JobQueue` | Single priority-1 queue feeding the compute env |
| `AWS::Batch::JobDefinition` | Container image + vCPU/memory + env vars + secrets + **`User: !Ref ContainerUser`** (v7) |
| `AWS::Scheduler::Schedule` *(conditional)* | EventBridge Scheduler — created when `TriggerType=Schedule` |
| `AWS::Events::Rule` *(conditional)* | EventBridge Rule for S3 PUT events — created when `TriggerType=S3Event` |
| `AWS::IAM::Role` + `Policy` (EventBridge) | Cross-service role allowing the scheduler/rule to submit Batch jobs |

**`IaCVersion: AppSubsystem-BatchJob-v7` tag coverage** (expanded in v7):

| Resource | Tagged? | Notes |
|---|---|---|
| `BatchJobSecurityGroup` | ✅ | Carried from v6 |
| `BatchJobRole` | ✅ | Carried from v6 |
| `BatchExecutionRole` | ✅ | Carried from v6 |
| `EventBridgeRole` | ✅ | Carried from v6 |
| `DataLoadingLogGroup` | ✅ | **Added in v7** |
| `BatchComputeEnvironment` | ⚠️ Out-of-band | `Tags` property requires resource replacement; blocked by custom `ComputeEnvironmentName`. Apply via `aws batch tag-resource` after deploy. |
| `BatchJobQueue` | ⚠️ Out-of-band | `Tags` property requires resource replacement; blocked by custom `JobQueueName`. Apply via `aws batch tag-resource` after deploy. |
| `BatchJobDefinition` | ✅ | **Added in v7** — every CFN update creates a new JobDefinition revision (expected Batch behavior); tag applies to the new revision. |
| `BatchSchedule` | ❌ | `AWS::Scheduler::Schedule` doesn't expose `Tags` in CloudFormation (verified via cfn-lint E3002). Stack-level tag inheritance only. |
| `S3EventRule` | ❌ | `AWS::Events::Rule` doesn't expose `Tags` in CloudFormation. Stack-level tag inheritance only. |
| `*Policy` (3× IAM, 1× S3 Bucket) | n/a | IAM ManagedPolicy and S3 BucketPolicy do not support resource tags. |

---

## Parameters Summary

Full inline reference (allowed values, finding instructions) lives in `Env/parameters-dataloading.yaml`.

Parameters marked `Optional` have template defaults. Parameters marked `Conditional` are only required when the related feature is enabled.

### Core
| Parameter | Requirement | Description | Sample Value |
|---|---|---|---|
| `AppShortName` | Required | Application short name — used in resource naming | `myapp` |
| `BatchJobName` | Required | Unique batch job identifier | `learner-master-data` |
| `EnvName` | Required | Environment — controls retention, DeletionPolicy, DB ports | `nprd-dev` |
| `VpcId` | Required | VPC ID | `vpc-0d99a0c727b301d67` |
| `AppSubnetIds` | Required | **2+ private subnets** in different AZs (comma-separated, no spaces) | `subnet-abc123,subnet-def456` |
| `ECRImageUri` | Required | Full container image URI | `123456789012.dkr.ecr.ap-southeast-1.amazonaws.com/myapp-nprd-batch:latest` |
| `BatchJobVCPU` | Optional | Fargate vCPU (`0.25`, `0.5`, `1`, `2`, `4`, `8`, `16`) | `2` |
| `BatchJobMemory` | Optional | Fargate memory in MiB | `4096` |
| `LogRetention` | Optional | CloudWatch log retention in days | `365` |
| `VpcCidr1` | Required | Primary VPC CIDR used by default egress rules | `10.55.53.0/24` |

### Container Runtime (v7)
| Parameter | Requirement | Description | Sample Value |
|---|---|---|---|
| **`ContainerUser`** | Optional | **Linux UID or UID:GID for the container. Must be non-root. Remediates ECS.20.** | `1000` (recommended default) |

#### `ContainerUser` — Recommended Values

| Value | Meaning | Allowed? |
|---|---|---|
| `1000` | UID 1000, default GID — **recommended default**, matches most modern base images (Alpine, Debian-slim, Ubuntu) | ✅ |
| `1000:1000` | UID 1000 with explicit GID 1000 — use if your image has a matching group | ✅ |
| `100:100` | Common UID/GID for nginx-base or similar UBI variants | ✅ |
| `1001`, `5000`, etc. | Any non-zero UID your image supports | ✅ |
| `0` | **Root user** — blocked at parameter validation (`AllowedPattern` rejects this) | ❌ |
| `0:0` | **Root user + root group** — blocked at parameter validation | ❌ |
| (blank) | Defaults to `1000` if you omit the parameter | ✅ |

> **Why is `0` blocked?** In Linux, **UID `0` is the root user**. Running containers as root violates AWS Security Hub control ECS.20 ("ECS task definitions should configure non-root users in Linux container definitions") and is the primary security finding this v7 template remediates. The CloudFormation `AllowedPattern` enforces this at stack creation time — if you try to set `ContainerUser: "0"` or `"0:0"`, the deploy will fail with a parameter validation error before any resources are created.

> **What if my image needs root?** Then your image is non-compliant with ECS.20. Two options: (1) rebuild the image with a `USER 1000` directive and proper file permissions (recommended), or (2) stay on **v6** until you can refactor the image. Don't try to bypass — Security Hub will flag it at runtime regardless of what value you pass.

### Trigger
| Parameter | Requirement | Description | Sample Value |
|---|---|---|---|
| `TriggerType` | Optional | `Schedule` or `S3Event` | `Schedule` |
| `ScheduleExpression` | Conditional | Cron expression when `TriggerType=Schedule` | `cron(0 12 * * ? *)` |
| `UseExistingS3` | Optional | Whether to attach a bucket policy to an existing bucket | `true` |
| `ExistingBucketName` | Conditional | S3 bucket name when `UseExistingS3=true` | `sftpxxxxxxxxxxxx` |
| `InputPrefix` | Conditional | Prefix to monitor when using S3 event trigger, or `""` for entire bucket | `input/` |

### Secrets (optional, up to 6 total)
| Parameter | Requirement | Description | Sample Value |
|---|---|---|---|
| `DatabaseSecretName` | Optional | Primary DB secret name | `myapp-nprd-dev-postgresql` |
| `AdditionalSecret2Name` … `AdditionalSecret5Name` | Optional | Extra secret names | `myapp-nprd-dev-api-key` |
| `AdditionalSecret2EnvVarName` … `AdditionalSecret5EnvVarName` | Conditional | Env var name for each extra secret when the related secret name is provided | `API_KEY` |
| `EnvVarConnectionStringSecretName` | Optional | Connection-string secret mapped to `AwsSecretPrefix` env var | `myapp-nprd-dev-conn-string` |

### Custom Environment Variables (optional)
| Parameter | Requirement | Description | Sample Value |
|---|---|---|---|
| `EnvVar1Name` / `EnvVar1Value` | Optional | Custom env var pair 1 | `LOG_LEVEL` / `info` |
| `EnvVar2Name` / `EnvVar2Value` | Optional | Custom env var pair 2 | `API_URL` / `https://api.internal/v1` |
| `EnvVar3Name` / `EnvVar3Value` | Optional | Custom env var pair 3 | `REGION` / `ap-southeast-1` |

### Networking & Egress
| Parameter | Requirement | Description | Sample Value |
|---|---|---|---|
| `VpcCidr2` … `VpcCidr5` | Optional | Additional VPC CIDRs | `10.55.55.0/25` |
| `VPCSubnetCidrDBAZ1` | Required | Database subnet CIDR AZ1 used by DB egress rules | `10.55.53.128/27` |
| `VPCSubnetCidrDBAZ2` | Required | Database subnet CIDR AZ2 used by DB egress rules | `10.55.53.160/27` |
| `VPCSubnetCidrDBAZ3` | Optional | Database subnet CIDR AZ3 | `10.55.53.192/27` |
| `S3PrefixListId` | Optional | S3 prefix list ID for VPC endpoint egress | `pl-0f8e90357f89b3f45` |
| `HCCVpceCidr` | Optional | HCC VPC endpoint CIDR | `10.48.42.0/24` |
| `EnableBCSProxy` | Optional | `true`/`false` — enables HCC Forward Proxy egress | `true` |
| `HCCProxyPort` | Optional | HCC Forward Proxy port | `4000` |
| `ProdHCCProxyCidr1/2` | Conditional | Prod HCC proxy subnet CIDRs when BCS proxy is enabled and `EnvName` matches `prod*` | `10.48.40.0/27` |
| `NprdHCCProxyCidr1/2` | Conditional | Non-prod HCC proxy subnet CIDRs when BCS proxy is enabled and `EnvName` matches `nprd*` | `10.48.41.0/27` |
| `ElastiCacheSubnetAZ1/2/3` | Optional | Dedicated cache subnet CIDRs | `10.55.54.0/27` |

### Notifications & Misc
| Parameter | Requirement | Description | Sample Value |
|---|---|---|---|
| `SNSTopicName` | Optional | SNS topic for job success/failure notifications without ARN | `myapp-nprd-dev-notifications` |
| `SQSQueueArns` | Optional | SQS queue ARN(s) for downstream notifications | `arn:aws:sqs:ap-southeast-1:123456789012:myapp-nprd-sqs-notifications` |
| `SQSCustomerManagedKmsKeyArns` | Conditional | Customer-managed KMS key ARN(s) for encrypted SQS queues. Leave empty for `alias/aws/sqs` | `arn:aws:kms:ap-southeast-1:123456789012:key/abcd-...` |
| `EnableInputTransformation` | Optional | EventBridge input transformation for S3 events | `false` |

---

## Security Group Egress

| Port(s) | Protocol | Destination | Condition |
|---|---|---|---|
| 443 | TCP | `VpcCidr1-5` | `VpcCidr1` always; 2-5 conditional |
| Auto DB port | TCP | `VPCSubnetCidrDBAZ1-3` | AZ1/AZ2 always; AZ3 conditional |
| 443 | TCP | `S3PrefixListId` | When provided |
| 443 | TCP | `HCCVpceCidr` | When provided |
| `HCCProxyPort` | TCP | Prod or Nprd HCC proxy CIDRs | `EnableBCSProxy=true` + matching env + CIDR provided |
| 587 | TCP | `VpcCidr1-5` | `VpcCidr1` always; 2-5 conditional |
| 6379–6380 | TCP | `VpcCidr1-5` | `VpcCidr1` always; 2-5 conditional |
| 6379–6380 | TCP | `ElastiCacheSubnetAZ1-3` | When provided |

**DB port auto-selection:** prod = `53341`, nprd = `53331`.

**No inbound rules** — batch tasks initiate all connections.

---

## Security Baseline (Enforced)

- **Non-root container** (v7) — `ContainerUser` defaults to `1000`; root (`0`, `0:0`) blocked at parameter validation. Satisfies **ECS.20**.
- **Read-only root filesystem** — carried from v6
- **TLS 1.2+** required on all S3 access (bucket policy)
- **VPC-private** — Batch tasks run in private subnets, no public IP
- **CIDR-scoped egress** — no `0.0.0.0/0` rules
- **IAM least-privilege** — secrets and Step Functions ARNs scoped to account/region
- **CloudWatch logs encrypted** at rest (AWS-managed KMS)
- **DeletionPolicy** — `Retain` for prod, `Delete` for nprd

---

## Migration from v6

**Drop-in upgrade if your container image runs cleanly as UID 1000.**

CloudFormation-side:
- ✅ `ContainerUser` has `Default: "1000"` — existing parameter files don't need to change
- ✅ No resource replacement (Batch creates a new JobDefinition revision; in-flight jobs unaffected)
- ✅ No new resources or security group rules. New optional SQS/KMS IAM statements are inactive unless `SQSQueueArns` or `SQSCustomerManagedKmsKeyArns` is provided.

Runtime-side (the only real risk):
- ⚠️ **First job submission after upgrade** uses the new revision with `User: 1000`
- ⚠️ Container image must support running as UID 1000 — see [Pre-Upgrade Requirement](#️-pre-upgrade-requirement-container-image-must-run-as-non-root) above

Full migration guide: [`../release-notes.md`](../release-notes.md#migration-from-v6-to-v7).

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| First job fails with `Permission denied` after v7 upgrade | Container image needs root or specific UID | Update Dockerfile to run as UID 1000, or override `ContainerUser` |
| Stack creation: `Parameter ContainerUser failed pattern validation` | Tried to set `0` or `0:0` | Use any non-root UID (e.g. `1000`) |
| Job stuck in `RUNNABLE` | Compute env `MaxvCpus=4` exhausted | Wait or raise compute env limit |
| Job times out connecting to RDS | Missing `VPCSubnetCidrDBAZx` for the AZ where DB lives | Add the AZ's CIDR to params |
| HCC proxy egress denied | `EnableBCSProxy=true` but matching CIDRs blank | Provide CIDRs for prod or nprd as appropriate |
| Job can't reach Redis | `ElastiCacheSubnetAZx` not set + cache in non-VPC-CIDR subnet | Add dedicated subnet CIDR |
