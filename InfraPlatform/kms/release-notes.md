# Release Notes: KMS Templates

## Version History

### General Updates
- **IaC Version Tag**:
  - Updated from `InfraPlatform-kms-v1` through `InfraPlatform-kms-v1.1`.

### Templates Evolution
- **v1**:
  - Added `cf-kms.yaml`: customer managed KMS key with alias `alias/{AppShortName}-{EnvName}-kms-{KeyName}`
  - Key type (`KeySpec`) and key usage (`KeyUsage`) as parameters, default `SYMMETRIC_DEFAULT` / `ENCRYPT_DECRYPT`
  - Template `Rules` reject invalid `KeySpec` / `KeyUsage` combinations before deployment
  - Automatic rotation with configurable period (symmetric keys only), deletion window
  - Singapore only: `SingaporeRegionOnly` rule rejects any Region other than `ap-southeast-1`, keys are single-Region (no cross-Region replication)
  - Key policy built from parameters:
    - Root statement with configurable principal and actions
    - Optional key administrators statement
    - Optional key users statement with configurable principals, actions, resource and `kms:ViaService` condition; default actions follow `KeyUsage`
    - Optional grant statement for AWS resources (`kms:GrantIsForAWSResource`)
  - `DeletionPolicy: Retain` for production environments

- **v1.1**:
  - Added `cf-kms-multi.yaml`: several customer managed KMS keys in one stack, one key and alias per `KeyNames` entry
    - Uses `AWS::LanguageExtensions` transform with `Fn::ForEach` (deploy with `CAPABILITY_AUTO_EXPAND`)
    - All keys share the same key spec, key usage, rotation and key policy parameters as `cf-kms.yaml`
    - Per-key outputs and exports: `{StackName}-{KeyName}-KmsKeyId`, `-KmsKeyArn`, `-KmsKeyAliasName`
    - Key names allow letters, numbers and `-` only (no `_`), and must stay unique after `-` is removed
    - Key policy is built as a JSON string (`Fn::ToJsonString`) because optional statements inside `Fn::ForEach` cannot be dropped with `AWS::NoValue`
  - Added `env/parameters-kms-multi.yaml`
  - `cf-kms.yaml` unchanged from v1 except the IaC version tag
