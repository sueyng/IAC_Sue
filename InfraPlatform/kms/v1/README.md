# AWS KMS Key Template Guide

## 📋 Overview

The KMS template (`cf-kms-multi.yaml`) creates one or more customer managed KMS keys, one key and alias per entry in `KeyNames`. All keys in a stack share the same key type, key usage, rotation and key policy (root, key administrators, key users), which are set through parameters.

For a single key, give one name (`KeyNames: "ec2"`). For keys that need different settings or policies, deploy separate stacks.

## 🗂️ Template Files

| File | Purpose |
|------|---------|
| `cf-kms-multi.yaml` | CloudFormation template for one or more KMS keys and aliases sharing one policy |
| `env/parameters-kms-multi.yaml` | Parameter configuration file |

### One stack or several

| Put keys in the same stack when… | Use a separate stack when… |
|---|---|
| They share the same owner, users and policy | A key needs its own policy, users or admins |
| They are data keys for one app in one environment | It is a signing, HMAC or cross-account key |
| They are created, changed and retired together | Its lifecycle is independent from other keys |

## 📋 Template Parameters

### Core Parameters

| Parameter | Example Value | Description |
|-----------|---------------|-------------|
| `AppShortName` | `myapp` | Application or project identifier |
| `EnvName` | `nprd`, `prod` | Environment name (restricted list) |
| `KeyNames` | `ec2,s3,rds-data` | One key per name, alias `alias/{AppShortName}-{EnvName}-kms-{KeyName}` |
| `KeyDescription` | `KMS key for app data` | Key description, the key name is appended per key |

Key names may contain letters, numbers and `-` (no `_`, because export names don't allow it). They must stay unique after `-` is removed (for example `rds-data` and `rdsdata` collide), and the stack fails before creating anything if they don't.

### Key Type and Usage

| Parameter | Default | Description |
|-----------|---------|-------------|
| `KeySpec` | `SYMMETRIC_DEFAULT` | Key type |
| `KeyUsage` | `ENCRYPT_DECRYPT` | Cryptographic operations of the keys |
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

### Key Policy (applied to every key in the stack)

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

### Encryption keys for an app (default type and usage)

```yaml
AppShortName: "abc"
EnvName: "nprd"
KeyNames: "ec2,s3,rds-data"
KeyUserPrincipals: "arn:aws:iam::123456789012:role/abc-ec2-role"
```

Creates `alias/abc-nprd-kms-ec2`, `alias/abc-nprd-kms-s3` and `alias/abc-nprd-kms-rds-data`. Each key gets this policy, with its own `Id`:

```json
{
  "Version": "2012-10-17",
  "Id": "abc-nprd-kms-ec2-policy",
  "Statement": [
    {
      "Sid": "Enable IAM Root Permissions",
      "Effect": "Allow",
      "Principal": { "AWS": "arn:aws:iam::123456789012:root" },
      "Action": "kms:*",
      "Resource": "*"
    },
    {
      "Sid": "Allow use of the key",
      "Effect": "Allow",
      "Principal": { "AWS": "arn:aws:iam::123456789012:role/abc-ec2-role" },
      "Action": ["kms:Encrypt", "kms:Decrypt", "kms:ReEncrypt*", "kms:DescribeKey", "kms:GenerateDataKey*"],
      "Resource": "*"
    }
  ]
}
```

### Single asymmetric signing key

```yaml
AppShortName: "abc"
EnvName: "nprd"
KeyNames: "jwt-sign"
KeySpec: "RSA_2048"
KeyUsage: "SIGN_VERIFY"
KeyUserPrincipals: "arn:aws:iam::123456789012:role/abc-lambda-role"
```

### HMAC key with custom actions

```yaml
AppShortName: "abc"
EnvName: "prod"
KeyNames: "token-mac"
KeySpec: "HMAC_256"
KeyUsage: "GENERATE_VERIFY_MAC"
KeyUserPrincipals: "arn:aws:iam::123456789012:role/abc-ecs-task-role"
KeyUserActions: "kms:GenerateMac,kms:VerifyMac"
```

### Encryption keys restricted to S3, with admins and grants

```yaml
AppShortName: "abc"
EnvName: "prod"
KeyNames: "s3-data,s3-logs"
KeyAdminPrincipals: "arn:aws:iam::123456789012:role/abc-platform-admin-role"
KeyUserPrincipals: "arn:aws:iam::123456789012:role/abc-ec2-role,arn:aws:iam::123456789012:role/abc-batch-role"
KeyUserViaServices: "s3.ap-southeast-1.amazonaws.com"
EnableGrantForAwsResources: "true"
```

## 🚀 Deployment

```bash
aws cloudformation deploy \
  --template-file cf-kms-multi.yaml \
  --stack-name abc-nprd-kms \
  --capabilities CAPABILITY_AUTO_EXPAND \
  --parameter-overrides AppShortName=abc EnvName=nprd KeyNames=ec2,s3,rds-data \
      KeyUserPrincipals=arn:aws:iam::123456789012:role/abc-ec2-role
```

`CAPABILITY_AUTO_EXPAND` is required because the template uses the `AWS::LanguageExtensions` transform (`Fn::ForEach`).

## 📤 Outputs

Per key (the output key drops `-` from the key name, the export name keeps it):

| Output | Export | Description |
|--------|--------|-------------|
| `KmsKeyId{KeyName}` | `{StackName}-{KeyName}-KmsKeyId` | Key ID |
| `KmsKeyArn{KeyName}` | `{StackName}-{KeyName}-KmsKeyArn` | Key ARN |
| `KmsKeyAliasName{KeyName}` | `{StackName}-{KeyName}-KmsKeyAliasName` | Alias name |

Per stack: `KmsKeySpec` and `KmsKeyUsage`.

Example reference from another stack: `!ImportValue abc-nprd-kms-rds-data-KmsKeyArn`.

## 🔄 Changing `KeyNames` and Other Parameters

| Change | Result |
|--------|--------|
| Add a name | One more key is created, existing keys are not changed |
| Remove a name | That key is **deleted** in non-prod (after `PendingWindowInDays`), kept in prod (`Retain`) |
| Reorder names | No change |
| Change the key policy parameters | Every key in the stack gets the new policy |
| Change `KeySpec` / `KeyUsage` | **Every** key in the stack is replaced |

## ⚠️ Notes

- Only `ap-southeast-1` (Singapore) is allowed. The `SingaporeRegionOnly` rule rejects a stack in any other Region before a key is created, and keys are always single-Region (`MultiRegion: false`), so they cannot be replicated to other Regions.
- `KeySpec` and `KeyUsage` cannot be changed on an existing key. Changing them replaces every key in the stack, and data encrypted with the old keys can no longer be decrypted with the new ones.
- Principals must be ARNs. A unique ID such as `AIDA...` (user) or `AROA...` (role) in an existing policy means the original user or role was deleted, and KMS rejects it in a new policy.
- Every principal in the key policy must exist when the stack is deployed, or KMS rejects the policy.
- Production environments (`prod*`) use `DeletionPolicy: Retain`. Non-prod keys are scheduled for deletion after `PendingWindowInDays` when they are removed from `KeyNames` or the stack is deleted.
- Keep the root statement. It lets IAM policies in the account grant key access and prevents the keys from becoming unmanageable.
- The key policy is built as a JSON string (`Fn::ToJsonString`) because, inside `Fn::ForEach`, an optional statement removed with `AWS::NoValue` becomes `null` instead of being dropped. The resulting policy is a normal key policy.
