# Release Notes: KMS Templates

## Version History

### General Updates
- **IaC Version Tag**: `InfraPlatform-kms-v1`

### Templates Evolution
- **v1**:
  - Added `cf-kms-multi.yaml`: one or more customer managed KMS keys, one key and alias `alias/{AppShortName}-{EnvName}-kms-{KeyName}` per `KeyNames` entry
    - Uses `AWS::LanguageExtensions` transform with `Fn::ForEach` (deploy with `CAPABILITY_AUTO_EXPAND`)
    - All keys in a stack share the same key spec, key usage, rotation and key policy
    - Per-key outputs and exports: `{StackName}-{KeyName}-KmsKeyId`, `-KmsKeyArn`, `-KmsKeyAliasName`
    - Key names allow letters, numbers and `-` only (no `_`), and must stay unique after `-` is removed
  - Key type (`KeySpec`) and key usage (`KeyUsage`) as parameters, default `SYMMETRIC_DEFAULT` / `ENCRYPT_DECRYPT`
  - Template `Rules` reject invalid `KeySpec` / `KeyUsage` combinations before deployment
  - Automatic rotation with configurable period (symmetric keys only), deletion window
  - Singapore only: `SingaporeRegionOnly` rule rejects any Region other than `ap-southeast-1`, keys are single-Region (no cross-Region replication)
  - Key policy built from parameters:
    - Root statement with configurable principal and actions
    - Optional key administrators statement
    - Optional key users statement with configurable principals, actions, resource and `kms:ViaService` condition; default actions follow `KeyUsage`
    - Optional grant statement for AWS resources (`kms:GrantIsForAWSResource`)
    - Built as a JSON string (`Fn::ToJsonString`) because optional statements inside `Fn::ForEach` cannot be dropped with `AWS::NoValue`
  - `DeletionPolicy: Retain` for production environments
  - Added `env/parameters-kms-multi.yaml`
