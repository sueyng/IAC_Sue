# AWS KMS Key Template Guide

## 📋 Overview

The KMS template (`cf-kms.yaml`) creates one customer managed KMS key and its alias. Key type, key usage, rotation, and every statement of the key policy (root, key administrators, key users) are set through parameters.

The multi-key template (`cf-kms-multi.yaml`) takes the same parameters, but `KeyNames` (a list) replaces `KeyName` and creates one key and alias per name. All keys in the stack share the same key type, usage and key policy. See [Multi-Key Template](#-multi-key-template-cf-kms-multiyaml).

## 🗂️ Template Files

| File | Purpose |
|------|---------|
| `cf-kms.yaml` | CloudFormation template for one KMS key and alias |
| `cf-kms-multi.yaml` | CloudFormation template for several KMS keys sharing one policy |
| `env/parameters-kms.yaml` | Parameter configuration file for `cf-kms.yaml` |
| `env/parameters-kms-multi.yaml` | Parameter configuration file for `cf-kms-multi.yaml` |

### Which template to use

| Use `cf-kms.yaml` (one key per stack) | Use `cf-kms-multi.yaml` (many keys per stack) |
|---|---|
| Key needs its own policy, users or admins | Keys share the same owner, users and policy |
| Signing / HMAC / cross-account keys | Several data keys for one app in one environment |
| Key lifecycle independent from other keys | Keys created, changed and retired together |

## 📋 Template Parameters

### Core Parameters

| Parameter | Example Value | Description |
|-----------|---------------|-------------|
| `AppShortName` | `myapp` | Application or project identifier |
| `EnvName` | `nprd`, `prod` | Environment name (restricted list) |
| `KeyName` | `ec2` | Alias suffix: `alias/{AppShortName}-{EnvName}-kms-{KeyName}` |
| `KeyDescription` | `KMS key for EC2` | Key description |

### Key Type and Usage

| Parameter | Default | Description |
|-----------|---------|-------------|
| `KeySpec` | `SYMMETRIC_DEFAULT` | Key type |
| `KeyUsage` | `ENCRYPT_DECRYPT` | Cryptographic operations of the key |
| `EnableKeyRotation` | `true` | Automatic rotation (symmetric keys only) |
| `RotationPeriodInDays` | `365` | Rotation period (90-2560) |
| `PendingWindowInDays` | `30` | Deletion waiting period (7-30) |

Valid `KeySpec` / `KeyUsage` combinations (checked by the template `Rules`, so a wrong combination fails before any resource is created):

| KeyUsage | KeySpec |
|----------|---------|
| `ENCRYPT_DECRYPT` | `SYMMETRIC_DEFAULT`, `RSA_2048`, `RSA_3072`, `RSA_4096`, `SM2` |
| `SIGN_VERIFY` | `RSA_2048`, `RSA_3072`, `RSA_4096`, `ECC_NIST_P256`, `ECC_NIST_P384`, `ECC_NIST_P521`, `ECC_SECG_P256K1`, `SM2` |
| `GENERATE_VERIFY_MAC` | `HMAC_224`, `HMAC_256`, `HMAC_384`, `HMAC_512` |
| `KEY_AGREEMENT` | `ECC_NIST_P256`, `ECC_NIST_P384`, `ECC_NIST_P521`, `SM2` |

### Key Policy

| Parameter | Default | Description |
|-----------|---------|-------------|
| `RootPrincipalArn` | `""` (this account root) | Principal of the root statement |
| `RootActions` | `kms:*` | Actions of the root statement |
| `KeyAdminPrincipals` | `""` (skip) | Comma separated ARNs of key administrators |
| `KeyAdminActions` | `""` (standard admin actions) | Actions of the administrators statement |
| `KeyUserPrincipals` | `""` (skip) | Comma separated ARNs of key users |
| `KeyUserActions` | `""` (by KeyUsage) | Actions of the key users statement |
| `KeyUserResource` | `*` | Resource of the key users statement |
| `KeyUserViaServices` | `""` (no restriction) | `kms:ViaService` condition values |
| `EnableGrantForAwsResources` | `false` | Grant statement for AWS services (EBS, RDS, ...) |

Default key user actions when `KeyUserActions` is empty:

| KeyUsage | Actions |
|----------|---------|
| `ENCRYPT_DECRYPT` | `kms:Encrypt`, `kms:Decrypt`, `kms:ReEncrypt*`, `kms:DescribeKey`, `kms:GenerateDataKey*` |
| `SIGN_VERIFY` | `kms:Sign`, `kms:Verify`, `kms:GetPublicKey`, `kms:DescribeKey` |
| `GENERATE_VERIFY_MAC` | `kms:GenerateMac`, `kms:VerifyMac`, `kms:DescribeKey` |
| `KEY_AGREEMENT` | `kms:DeriveSharedSecret`, `kms:GetPublicKey`, `kms:DescribeKey` |

## 🔧 Parameter File Examples

### Symmetric encryption key for an EC2 role (default)

```yaml
AppShortName: "abc"
EnvName: "nprd"
KeyName: "ec2"
KeyUserPrincipals: "arn:aws:iam::123456789012:role/abc-ec2-role"
```

Resulting key policy:

```json
{
  "Version": "2012-10-17",
  "Id": "abc-nprd-kms-ec2-policy",
  "Statement": [
    {
      "Sid": "Enable IAM Root Permissions",
      "Effect": "Allow",
      "Principal": { "AWS": "arn:aws:iam::123456789012:root" },
      "Action": ["kms:*"],
      "Resource": "*"
    },
    {
      "Sid": "Allow use of the key",
      "Effect": "Allow",
      "Principal": { "AWS": ["arn:aws:iam::123456789012:role/abc-ec2-role"] },
      "Action": ["kms:Encrypt", "kms:Decrypt", "kms:ReEncrypt*", "kms:DescribeKey", "kms:GenerateDataKey*"],
      "Resource": "*"
    }
  ]
}
```

### Asymmetric signing key

```yaml
AppShortName: "abc"
EnvName: "nprd"
KeyName: "jwt-sign"
KeySpec: "RSA_2048"
KeyUsage: "SIGN_VERIFY"
KeyUserPrincipals: "arn:aws:iam::123456789012:role/abc-lambda-role"
```

### HMAC key with custom actions

```yaml
AppShortName: "abc"
EnvName: "prod"
KeyName: "token-mac"
KeySpec: "HMAC_256"
KeyUsage: "GENERATE_VERIFY_MAC"
KeyUserPrincipals: "arn:aws:iam::123456789012:role/abc-ecs-task-role"
KeyUserActions: "kms:GenerateMac,kms:VerifyMac"
```

### Encryption key restricted to S3, with admins

```yaml
AppShortName: "abc"
EnvName: "prod"
KeyName: "s3"
KeyAdminPrincipals: "arn:aws:iam::123456789012:role/abc-platform-admin-role"
KeyUserPrincipals: "arn:aws:iam::123456789012:role/abc-ec2-role,arn:aws:iam::123456789012:role/abc-batch-role"
KeyUserViaServices: "s3.ap-southeast-1.amazonaws.com"
```

## 🚀 Deployment

```bash
aws cloudformation deploy \
  --template-file cf-kms.yaml \
  --stack-name abc-nprd-kms-ec2 \
  --parameter-overrides AppShortName=abc EnvName=nprd KeyName=ec2 \
      KeyUserPrincipals=arn:aws:iam::123456789012:role/abc-ec2-role
```

## 📤 Outputs

| Output | Export | Description |
|--------|--------|-------------|
| `KmsKeyId` | `{StackName}-KmsKeyId` | Key ID |
| `KmsKeyArn` | `{StackName}-KmsKeyArn` | Key ARN |
| `KmsKeyAliasName` | `{StackName}-KmsKeyAliasName` | Alias name |
| `KmsKeySpec` | - | Key spec |
| `KmsKeyUsage` | - | Key usage |

## 🔑 Multi-Key Template (`cf-kms-multi.yaml`)

Uses the `AWS::LanguageExtensions` transform with `Fn::ForEach` to create one key and alias per `KeyNames` entry. All other parameters are the same as `cf-kms.yaml` and apply to every key.

```yaml
AppShortName: "abc"
EnvName: "nprd"
KeyNames: "ec2,s3,rds-data"
KeyUserPrincipals: "arn:aws:iam::123456789012:role/abc-ec2-role"
```

Creates `alias/abc-nprd-kms-ec2`, `alias/abc-nprd-kms-s3` and `alias/abc-nprd-kms-rds-data`, each with its own key and the same key policy.

```bash
aws cloudformation deploy \
  --template-file cf-kms-multi.yaml \
  --stack-name abc-nprd-kms \
  --capabilities CAPABILITY_AUTO_EXPAND \
  --parameter-overrides AppShortName=abc EnvName=nprd KeyNames=ec2,s3,rds-data \
      KeyUserPrincipals=arn:aws:iam::123456789012:role/abc-ec2-role
```

`CAPABILITY_AUTO_EXPAND` is required because of the transform.

Outputs per key (the logical ID drops `-` from the key name, the export name keeps it):

| Output | Export | Description |
|--------|--------|-------------|
| `KmsKeyId{KeyName}` | `{StackName}-{KeyName}-KmsKeyId` | Key ID |
| `KmsKeyArn{KeyName}` | `{StackName}-{KeyName}-KmsKeyArn` | Key ARN |
| `KmsKeyAliasName{KeyName}` | `{StackName}-{KeyName}-KmsKeyAliasName` | Alias name |

Behaviour when `KeyNames` changes:

| Change | Result |
|--------|--------|
| Add a name | One more key is created, existing keys are not changed |
| Remove a name | That key is **deleted** in non-prod (after `PendingWindowInDays`), kept in prod (`Retain`) |
| Reorder names | No change |
| Change the key policy parameters | Every key in the stack gets the new policy |
| Change `KeySpec` / `KeyUsage` | **Every** key in the stack is replaced |

Key names may contain letters, numbers and `-` (no `_`, because export names don't allow it). They must stay unique after `-` is removed (for example `rds-data` and `rdsdata` collide), and the stack fails before creating anything if they don't.

## ⚠️ Notes

- Only `ap-southeast-1` (Singapore) is allowed. The `SingaporeRegionOnly` rule rejects a stack in any other Region before the key is created, and keys are always single-Region (`MultiRegion: false`), so they cannot be replicated to other Regions.
- `KeySpec` and `KeyUsage` cannot be changed on an existing key. Changing them replaces the key, and data encrypted with the old key can no longer be decrypted with the new one.
- Principals must be ARNs. A unique ID such as `AIDA...` (user) or `AROA...` (role) in an existing policy means the original user or role was deleted, and KMS rejects it in a new policy.
- Every principal in the key policy must exist when the stack is deployed, or KMS rejects the policy.
- Production environments (`prod*`) use `DeletionPolicy: Retain`. Non-prod keys are scheduled for deletion after `PendingWindowInDays` when the stack is deleted.
- Keep the root statement. It lets IAM policies in the account grant key access and prevents the key from becoming unmanageable.
