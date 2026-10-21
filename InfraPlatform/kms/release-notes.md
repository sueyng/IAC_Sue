# Release Notes: KMS Templates

## Version History

### General Updates
- **IaC Version Tag**: `InfraPlatform-kms-v1`

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
