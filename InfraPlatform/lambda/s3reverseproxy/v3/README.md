# Lambda S3 Reverse Proxy CloudFormation Template — v3

This CloudFormation template creates a VPC-attached AWS Lambda function that serves as a reverse proxy in front of S3. The Lambda is invoked by API Gateway, calls `s3:GetObject`, and returns the object as the HTTP response.

The template supports **two routing modes**. Mode is inferred from which parameter you fill — no explicit toggle:

- **Single-bucket** — fill `FrontendSPABucketName`. One Lambda → one fixed S3 bucket. Narrow IAM, managed bucket policy.
- **Multi-bucket** — fill `APIGatewayToS3BucketMapping`. One Lambda → many S3 buckets, picked by API Gateway ID. Wildcard IAM (`${AppShortName}-*/*`); bucket policies owned by the project team. Useful for multi-tenant patterns where one Lambda fronts several buckets.

Fill EITHER one and leave the other `""`. If both are empty, the Lambda deploys with no `Environment` variables block at all — it will fail at runtime when invoked.

## Purpose

Use this template when you need to serve content from a private S3 bucket through a private API Gateway, without exposing the bucket directly to the internet. Typical use case: an intranet single-page application (SPA) where the frontend assets (HTML, JS, CSS, images) live in S3, but client browsers reach them through API Gateway (which can be VPC-private, behind ALB/WAF, etc.).

This is a **standalone** template — deploy by itself for a simple "API Gateway → Lambda → S3" pipeline. (Note: `AppSubsystem/FrontendSPA-Intranet` has its own separate `cf-lambda-s3reverseproxy.yaml` template — that's a different fork, not this one.)

### How it works

```
single-bucket:  Browser → API Gateway → Lambda → S3 GetObject (FrontendSPABucketName) → Browser
multi-bucket:   Browser → API Gateway → Lambda → lookup bucket by API GW ID → S3 GetObject → Browser
```

**Single-bucket** (FrontendSPABucketName provided):
1. Client requests a path (e.g. `/index.html`)
2. API Gateway invokes Lambda (synchronous, IAM-authorized)
3. Lambda reads `S3_BUCKET_NAME` env var and calls `s3:GetObject` for the key
4. Lambda returns the object body + content-type as the HTTP response

**Multi-bucket** (APIGatewayToS3BucketMapping provided):
1. Client requests a path
2. API Gateway invokes Lambda
3. Lambda extracts API Gateway ID from `event.requestContext.apiId`, looks up the target bucket from `API_TO_S3_BUCKET_MAP` env var (JSON map)
4. Lambda calls `s3:GetObject` on the matched bucket and returns the object

The Lambda runs **inside a customer VPC** (mandatory in v3) for egress control and VPC Flow Log visibility (TISO compliance). Egress is restricted by a dedicated `LambdaSecurityGroup` (created in this template) to the AWS service endpoints the function actually needs (Logs, X-Ray, S3).

## Overview

The solution provisions:
- Lambda function with X-Ray Active tracing (functional in v3 — see [v3 Changes](#v3-changes-tiso-vpc-compliance--x-ray-iam-fix))
- IAM execution role with permissions for CloudWatch Logs, S3 GetObject (scope depends on which bucket parameter is filled), VPC ENI management, and X-Ray writes
- **Dedicated per-Lambda security group** with least-privilege inline egress (no ingress — Lambda is invoked via the API Gateway service plane)
- **Bucket policy on `FrontendSPABucketName`** — only created when `FrontendSPABucketName` is non-empty (Allow Lambda role + Deny non-TLS-1.2 + Deny non-SSL). When `FrontendSPABucketName` is empty (multi-bucket usage), this resource is skipped; project teams own bucket policies on each routed bucket.
- CloudWatch Log Group with configurable retention
- SSM parameter storing the Lambda ARN (for cross-stack reference)
- Lambda permission allowing API Gateway invocation

**IaC Version Tag:** `InfraPlatform-lambda-s3reverseproxy-v3`

## Prerequisites

1. IAM deployment role with appropriate permissions
2. S3 bucket containing the Lambda deployment package + Lambda code zip uploaded
3. Target S3 bucket for frontend content (`FrontendSPABucketName`) — must exist before deployment
4. **VPC + min 2 private subnets** in different AZs
5. **Interface VPC Endpoints reachable from those subnets**:
   - `com.amazonaws.{region}.logs` — for Lambda log writes
   - `com.amazonaws.{region}.xray` — for X-Ray traces
6. **S3 reachability path** for `FrontendSPABucketName`:
   - S3 Gateway endpoint (recommended — free; provide its prefix list ID via `S3PrefixListId`)
   - S3 Interface endpoint (covered by `VpcCidr1-5` egress rules)
   - NAT Gateway in the subnet route table

## Parameters

| Parameter | Description | Example | Default |
|---|---|---|---|
| AppShortName | Short name for the application | `myapp` | — |
| EnvName | Environment name | `nprd-dev`, `prod`, `prod-a`, `prod-b`, `prod-c` | — |
| LambdaS3bucket | S3 bucket where Lambda code is stored | `my-lambda-code-bucket` | — |
| CodeZipFileName | Zip file name for Lambda function code | `s3reverseproxy.zip` | — |
| LambdaRuntime | Runtime for Lambda | `nodejs20.x` | `nodejs20.x` |
| LambdaHandler | Handler for Lambda function | `index.handler` | `index.handler` |
| FrontendSPABucketName | Single-bucket mode — S3 bucket the Lambda reverse-proxies. Fill EITHER this OR `APIGatewayToS3BucketMapping` | `myapp-nprd-dev-frontendspa-bucket` | `""` |
| APIGatewayToS3BucketMapping | Multi-bucket mode — JSON map of API Gateway IDs to S3 bucket names. Fill EITHER this OR `FrontendSPABucketName` | `abc123:bucket1,def456:bucket2` | `""` |
| LogRetentionInDays | Number of days for Log Retention | `14` | `14` |
| **VpcId** *(NEW in v3)* | VPC where the Lambda SG will be created | `vpc-02fb2e32bbb6ff24e` | — |
| **SubnetIds** *(NEW in v3)* | Private subnet IDs for Lambda ENIs (min 2 for HA) | `subnet-abc,subnet-def` | — |
| **VpcCidr1** *(NEW in v3)* | Primary VPC CIDR for SG egress to Interface VPC Endpoints | `10.193.0.0/16` | — |
| VpcCidr2-5 *(NEW in v3, optional)* | Additional VPC CIDRs (multi-CIDR / peered VPC) | `10.194.0.0/16` | `""` |
| S3PrefixListId *(NEW in v3, optional)* | S3 Gateway Endpoint Prefix List ID for S3 egress | `pl-xxxxxxxx` | `""` |

### Routing Modes

Mode is inferred from which bucket parameter is non-empty:

| Aspect | Single-bucket (`FrontendSPABucketName` filled) | Multi-bucket (`APIGatewayToS3BucketMapping` filled) |
|---|---|---|
| Lambda env var | `S3_BUCKET_NAME` | `API_TO_S3_BUCKET_MAP` |
| IAM `s3:GetObject` scope | `${FrontendSPABucketName}/*` + `${LambdaS3bucket}/*` | `${AppShortName}-*/*` + `${LambdaS3bucket}/*` |
| Managed `S3BucketPolicy` resource | ✅ Created — TLS 1.2 enforce, deny non-SSL | ❌ Not created — project team owns each bucket's policy |
| When to use | Single-bucket use case | Multi-tenant patterns; v1 upgrade keeping multi-bucket routing without rewriting Lambda code |

Fill EITHER one and leave the other `""`. If both are empty, the template still deploys but the Lambda has **no Environment variables block at all** — it will fail at runtime when invoked. The Lambda zip (`CodeZipFileName`) must match the chosen mode — it reads a different env var and uses different routing logic.

### Important Notes

- **`FrontendSPABucketName`** (single-bucket): Must exist before deployment. Template adds a bucket policy: Allow Lambda role `s3:GetObject` + `s3:PutObject`; Deny non-TLS-1.2 + non-SSL. **If a custom bucket policy already exists, it will be overwritten** — review and merge before deploying.
- **`APIGatewayToS3BucketMapping`** (multi-bucket): All buckets in the mapping must exist before deployment. The IAM scope `${AppShortName}-*/*` is safe because project accounts are isolated per environment (one AWS account per env). Project team owns bucket policies on each routed bucket.
- **X-Ray tracing**: `TracingConfig.Mode: Active` plus the scoped IAM policy — traces appear in X-Ray service map within ~1 minute of invocation.
- **Per-Lambda security group**: The template auto-generates the SG name as `${AppShortName}-${EnvName}-s3ReverseProxy-sg` (matching v1's pattern — no parameter to fill, and v1 → v3 upgrades modify the existing SG in place rather than creating a new one). For projects deploying many s3reverseproxy Lambdas, each consumes ~2 ENIs/IPs per Lambda. If VPC IP optimization is a concern, raise that requirement separately.

## Parameter File

Edit the YAML parameter file at `env/parameters-s3reverseproxy.yaml`. The file is self-documenting — each parameter has inline guidance, examples, and `📝` markers indicate values that must be filled in before deployment.

Only edit values between the `<<< PARAMETERS_START >>>` and `<<< PARAMETERS_END >>>` markers — the appendix below those markers contains read-only reference documentation.

The pipeline reads this YAML file directly. No JSON file or `aws cloudformation` command is needed for project teams.

## Resources Created

1. **S3BucketPolicy** *(only when `FrontendSPABucketName` is provided)*: Bucket policy on `FrontendSPABucketName` (Allow Lambda role + Deny non-TLS-1.2 + Deny non-SSL). Skipped when only `APIGatewayToS3BucketMapping` is filled.
2. **LambdaLogGroup**: CloudWatch Log Group with configurable retention
3. **LambdaSecurityGroup** *(NEW in v3)*: Per-Lambda SG with least-privilege egress (HTTPS to Interface VPC Endpoints + optional S3 Gateway endpoint)
4. **LambdaS3ReverseProxy**: Lambda function (VPC-attached, X-Ray Active tracing)
5. **LambdaExecutionRole**: IAM role with policies for CloudWatch Logs, S3 access (scope depends on which bucket parameter is filled), VPC ENI management, and X-Ray write
6. **APIGatewayInvokeLambdaPolicy**: Permission allowing API Gateway to invoke Lambda
7. **ParameterLambdaArn**: SSM Parameter storing Lambda function ARN (for cross-stack reference)

## Lambda Environment Variables

The Lambda receives a different env var depending on which bucket parameter is filled:

| When this is non-empty | Env var set on Lambda |
|---|---|
| `FrontendSPABucketName` | `S3_BUCKET_NAME` = `${FrontendSPABucketName}` |
| `APIGatewayToS3BucketMapping` | `API_TO_S3_BUCKET_MAP` = `${APIGatewayToS3BucketMapping}` |

The Lambda zip code must read the env var that matches the bucket parameter you filled.

## Resource Protection

Production environments (`EnvName` matches `prod*`): resources have `DeletionPolicy: Retain` (and `UpdateReplacePolicy: Retain` on the SG).
Non-production environments: resources are deleted when the stack is deleted.

## Troubleshooting

- **Lambda fails immediately with no useful error**: both `FrontendSPABucketName` and `APIGatewayToS3BucketMapping` are empty — the Lambda has no S3 target. Fill exactly one of them.
- **API returns 504**: Most likely Lambda can't reach S3 — verify S3 reachability path (Gateway endpoint, Interface endpoint, or NAT) is configured and the SG egress permits it
- **API returns 500 / Lambda errors immediately after upgrade**: Lambda code is reading the wrong env var for the bucket parameter you filled. If `FrontendSPABucketName` is set, the Lambda gets `S3_BUCKET_NAME`; if `APIGatewayToS3BucketMapping` is set, the Lambda gets `API_TO_S3_BUCKET_MAP`. Confirm the deployed zip reads the matching env var.
- **404 from API in multi-bucket usage**: `APIGatewayToS3BucketMapping` JSON does not include the calling API Gateway's ID, or the matched bucket is empty. Check the env var and the Lambda log for the dispatch path.
- **Permission denied / `AccessDenied` on `s3:GetObject`**: in multi-bucket usage, target bucket name doesn't match the IAM scope (`${AppShortName}-*/*`). Rename the bucket to start with `${AppShortName}-`, or switch to single-bucket usage.
- **No log entries in CloudWatch**: Logs Interface Endpoint not reachable from `SubnetIds`, or `VpcCidr1-5` egress doesn't cover the endpoint subnet
- **No traces in X-Ray service map**: X-Ray Interface Endpoint not reachable from `SubnetIds`, or SG egress doesn't cover it
- **Lambda VPC ENI cleanup on stack delete takes 5–20 minutes**: well-known AWS limitation for VPC-attached Lambdas
- **S3 Bucket Not Found**: Ensure `FrontendSPABucketName` or each bucket in `APIGatewayToS3BucketMapping` exists before deployment
- **Stack creation fails on SG name conflict**: an SG with the auto-generated name `${AppShortName}-${EnvName}-s3ReverseProxy-sg` already exists in the VPC and is NOT the one this stack manages. This should be rare — the template hardcodes the same name v1 used, so v1 → v3 upgrades modify the existing SG in place. If it does happen, identify and remove the orphan SG before retrying.
- **Existing bucket policy overwritten after upgrade**: when `FrontendSPABucketName` is filled, `S3BucketPolicy` is fully owned by this template — it replaces any prior policy. Inspect and merge custom statements before deploying.
- **Lambda errors**: Check CloudWatch Logs at `/aws/lambda/{AppShortName}-{EnvName}-s3ReverseProxy`

---

## v3 Changes (TISO VPC Compliance + X-Ray IAM Fix)

v3 is built on v2 as baseline. All v2 parameters are preserved.

| # | Change | Reason |
|---|---|---|
| 1 | **NEW: VPC attachment** — `VpcConfig` block on Lambda function | TISO compliance (egress control + VPC Flow Log visibility) |
| 2 | **NEW: Per-Lambda Security Group** — `LambdaSecurityGroup` resource with least-privilege inline egress (HTTPS → `VpcCidr1-5` for Interface Endpoints, optional S3 Gateway prefix list for `FrontendSPABucket`) | Egress restriction for TISO compliance |
| 3 | **FIX: X-Ray IAM permissions** — added `s3ReverseProxy-XRayWriteAccess` inline policy | Latent bug in v2 — `TracingConfig.Mode: Active` set but no IAM permission, so traces silently dropped |
| 4 | The orphan `s3ReverseProxy-VPCAccess` IAM policy from v2 is now actually used by the new `VpcConfig` | Cleanup |
| 5 | New mandatory params: `VpcId`, `SubnetIds`, `VpcCidr1` | For VPC config + SG egress rules |
| 6 | New optional params: `VpcCidr2-5`, `S3PrefixListId` | Multi-CIDR/peered VPC + S3 Gateway endpoint egress |
| 7 | `IaCVersion` tag updated `v2` → `v3` on all tagged resources | Versioning |
| 8 | **NEW: Multi-bucket mode** — `APIGatewayToS3BucketMapping` parameter restored. Mode is inferred from which bucket parameter is non-empty (no explicit toggle). Conditional `S3BucketPolicy`, conditional Lambda env var (`S3_BUCKET_NAME` vs `API_TO_S3_BUCKET_MAP`), conditional IAM scope | Lets v1 multi-bucket users upgrade to v3 without rewriting Lambda code |
| 9 | Hygiene: `UpdateReplacePolicy` added to all stateful resources (`S3BucketPolicy`, `LambdaLogGroup`, `LambdaS3ReverseProxy`, `LambdaExecutionRole`, `APIGatewayInvokeLambdaPolicy`, `ParameterLambdaArn`) — matches `DeletionPolicy` for production retention | Resolves cfn-lint W3011 |

## Upgrading from v2 to v3

| Dimension | Verdict |
|---|---|
| Parameter contract | ⚠️ Breaking — 3 new mandatory params (`VpcId`, `SubnetIds`, `VpcCidr1`) must be added before `update-stack` |
| CFN resource lifecycle | ✅ All in-place modify, no Lambda recreation. Same `FunctionName`, same ARN. New `LambdaSecurityGroup` resource created. |
| Behavior | ⚠️ Lambda moves from non-VPC to VPC. **If Interface Endpoints / S3 reachability not pre-configured, reverse proxy returns 504 immediately on first invocation — visible production outage.** |
| Routing mode | ✅ Keep `FrontendSPABucketName` filled (as v2 had it); leave `APIGatewayToS3BucketMapping` empty. No Lambda code rewrite needed. |

> ⚠️ **Mandatory: deploy to non-prod first, smoke test end-to-end, only then promote to prod.** v2 ran the Lambda outside any VPC with direct internet access. v3 attaches the Lambda to a VPC, removing that direct internet access.

**Recommended upgrade procedure:**

1. Verify Interface VPC Endpoints (`logs`, `xray`) exist and are reachable from your subnets
2. Verify S3 reachability path (Gateway endpoint, Interface endpoint, or NAT) and ensure SG egress will cover it (provide `S3PrefixListId` for Gateway endpoint, or rely on `VpcCidr1-5` for Interface endpoint)
3. Update parameter file: add `VpcId`, `SubnetIds`, `VpcCidr1` (and optional `VpcCidr2-5`, `S3PrefixListId`). Keep `FrontendSPABucketName` as you had it; leave `APIGatewayToS3BucketMapping` empty.
4. Create CloudFormation changeset, verify `LambdaS3ReverseProxy` shows **Modify** (not Replace), and a new `LambdaSecurityGroup` shows **Add**
5. Execute changeset in **non-prod first**, smoke test (SPA loads end-to-end, CloudWatch Logs writes, X-Ray service map populated)
6. Only after non-prod passes, schedule prod upgrade in low-traffic window with rollback to v2 ready

## Upgrading from v1 to v3

v1 used multi-bucket routing via `APIGatewayToS3BucketMapping`. v3 supports both routing modes — pick by filling either `FrontendSPABucketName` (single-bucket) or `APIGatewayToS3BucketMapping` (multi-bucket). Two upgrade paths:

### Path A — keep multi-bucket routing (no Lambda code rewrite)

Best when the project team uses v1's multi-bucket pattern and wants the v3 VPC + X-Ray benefits without touching Lambda code.

| Dimension | Verdict |
|---|---|
| Parameter contract | ⚠️ Breaking — carry `APIGatewayToS3BucketMapping` value from v1, leave `FrontendSPABucketName: ""`, add `VpcId`, `SubnetIds`, `VpcCidr1` |
| Lambda code | ✅ No rewrite — v1 zip continues to work (still reads `API_TO_S3_BUCKET_MAP`) |
| CFN resource lifecycle | `SecurityGroupIngressAZ1/2/3` deleted; `LambdaSecurityGroup` modified in place (template hardcodes the same name v1 auto-generated, so no replacement) |
| IAM scope | Wildcard `${AppShortName}-*/*` (matches v1) — no managed bucket policy on routed buckets |

**Procedure:**

1. Pre-flight (same as v2 → v3): verify Interface Endpoints (`logs`, `xray`) + S3 reachability path
2. **Look up the VPC CIDR for `VpcCidr1`** — VPC Console → Your VPCs → IPv4 CIDR (e.g. `10.193.0.0/16`). **Do NOT reuse v1's `VPCSubnetCidrAZ*` values** — those are subnet CIDRs (typically `/26`/`/27`) and won't cover the Interface VPC Endpoint ENIs. If the VPC has secondary CIDRs, populate `VpcCidr2-5`.
3. Update parameter file:
   - `APIGatewayToS3BucketMapping`: copy value from v1
   - `FrontendSPABucketName: ""` (leaving this empty signals multi-bucket usage)
   - Add `VpcCidr1` (per step 2), optional `VpcCidr2-5`, `S3PrefixListId`
   - Keep existing `VpcId`, `SubnetIds`
   - **Drop** v1-only params from the file: `VPCSubnetCidrAZ1`, `VPCSubnetCidrAZ2`, `VPCSubnetCidrAZ3` (they no longer exist in v3)
4. Create changeset and verify:
   - `LambdaS3ReverseProxy` → **Modify** (ARN preserved)
   - `LambdaExecutionRole` → **Modify** (X-Ray policy added, IAM scope changes from `${AppShortName}-${EnvName}-*/*` → `${AppShortName}-*/*`)
   - `LambdaSecurityGroup` → **Modify** in place (template hardcodes the same name v1 auto-generated)
   - `SecurityGroupIngressAZ1/2/3` → **Delete** (3 separate resources)
   - `S3BucketPolicy` → not present (skipped because `FrontendSPABucketName` is empty)
5. Execute in non-prod, smoke test, then prod

### Path B — convert to single-bucket (narrower IAM)

Best when the project team only proxies to one bucket (or wants to consolidate to one). Requires a Lambda code rewrite.

| Dimension | Verdict |
|---|---|
| Parameter contract | ⚠️ Breaking — provide `FrontendSPABucketName`, leave `APIGatewayToS3BucketMapping: ""`, add `VpcId`, `SubnetIds`, `VpcCidr1` |
| Lambda code | 🔴 **Must rewrite** — env var renamed (`API_TO_S3_BUCKET_MAP` → `S3_BUCKET_NAME`), drop multi-bucket dispatch |
| CFN resource lifecycle | Same as Path A, plus `S3BucketPolicy` → **Add** on `FrontendSPABucketName` |
| IAM scope | Narrow — `${FrontendSPABucketName}/*` + `${LambdaS3bucket}/*` |

**Procedure:**

1. Pre-flight (same as Path A)
2. **Look up the VPC CIDR for `VpcCidr1`** (same as Path A step 2): VPC Console → Your VPCs → IPv4 CIDR. Do NOT reuse v1's `VPCSubnetCidrAZ*` values
3. **Rewrite Lambda code**: change env var to `S3_BUCKET_NAME`, drop the API-Gateway-ID dispatch logic, repackage zip, upload to `LambdaS3bucket`
4. **Inspect `FrontendSPABucketName`'s existing bucket policy** — v3's `S3BucketPolicy` will overwrite it. Merge any custom statements before deploying.
5. Update parameter file:
   - `FrontendSPABucketName`: target bucket
   - `APIGatewayToS3BucketMapping: ""` (leaving this empty signals single-bucket usage)
   - Update `CodeZipFileName` to the new zip
   - Add `VpcCidr1` (per step 2), optional `VpcCidr2-5`, `S3PrefixListId`
   - **Drop** v1-only params: `VPCSubnetCidrAZ1`, `VPCSubnetCidrAZ2`, `VPCSubnetCidrAZ3`
6. Create changeset and verify:
   - `LambdaS3ReverseProxy` → **Modify** (ARN preserved)
   - `S3BucketPolicy` → **Add**
   - Other resources same as Path A
7. Execute in non-prod, smoke test, then prod

### Considerations for both paths

- **Mandatory non-prod first** — same risks as v2 → v3 (504s if VPC endpoints/S3 reachability not configured)
- **Rollback**: re-deploy v1 template + v1 parameter file. Note that v3 → v1 rollback in single mode (Path B) deletes the `S3BucketPolicy` resource — re-apply any custom policy you merged in step 3
- **Skip the v2 step.** Don't try v1 → v2 → v3 thinking it's safer — v1 → v2 is itself a major breaking change (multi-bucket dropped, Lambda code rewrite required, VPC attach removed). Direct v1 → v3 with `APIGatewayToS3BucketMapping` filled (Path A) is actually the simplest path because it preserves the v1 routing pattern without any Lambda code change.
