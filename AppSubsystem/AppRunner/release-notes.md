# Release Notes - App Runner CloudFormation Template

## Version: v1 Post-release Patch
## Release Date: 2026-06-24

### App Runner Additional Secrets Manager ARN Support
- Added optional `AdditionalSecretsManagerSecretArns` parameter to extend the App Runner instance role Secrets Manager permission for secret names that do not follow the `${AppShortName}*` naming prefix.
- Existing behavior is unchanged when the parameter is left empty.
- Updated v1 README and sample parameter files to document the optional parameter.
- Consolidated prior App Runner template updates into the maintained `v1` template path while preserving v1 upgrade compatibility.

### Migration Notes
- Existing v1 stacks can update without providing the new parameter.
- Use comma-separated full secret ARNs or ARN patterns only when App Runner needs to inject secrets outside the default application-prefixed naming scope.
- Project pipelines should reference `AppSubsystem/AppRunner/v1` for App Runner deployments.

---

## Version: v1 Post-release Patch
## Release Date: 2026-06-19

### App Runner Tag Replacement Mitigation
- Patched `v1` with the latest functional updates while retaining existing `AppSubsystem-AppRunner-v1` IaCVersion tags for in-place v1 stack updates.

### Included v1 Functional Updates
- Added optional `VpcCidr4` and `VpcCidr5` egress support.
- Scoped `AppRunnerInstanceRole` Secrets Manager access from `Resource: "*"` to application-prefixed secret ARNs.

### Migration Notes
- Existing `v1` stacks can apply the patched v1 template first to avoid App Runner resource replacement from IaCVersion tag changes.
- For new deployments, use the maintained `v1` template path.
- Always review the change set and confirm `AppRunnerService` does not show replacement before execution.

---

## Version: v1.2
## Release Date: 2025-09-16

### Enhancements
- **Expanded Secrets Capacity**: Increased AWS Secrets Manager integration support from 5 to 7 secrets
- **Additional Secret Parameters**: Added `SecretKeyEnvVar6`, `SecretArn6`, `SecretKeyEnvVar7`, and `SecretArn7` parameters
- **Enhanced Documentation**: Updated README and parameter documentation to reflect expanded secret management capabilities

### Technical Changes
- Added conditions `HasSecretKeyEnvVar6` and `HasSecretKeyEnvVar7` for new secret parameters
- Extended App Runner service Secrets property to support 2 additional conditional secret entries
- Updated parameter file template with new secret parameter placeholders

---

## Version: v1.1
## Release Date: 2025-09-16

### New Features
- **Enhanced Secrets Management**: Support for up to 7 AWS Secrets Manager integrations with configurable environment variable names and ARNs
- **Improved Parameter Organization**: Parameters reorganized into logical groups (Core, Secrets, Application, Health Check, Networking, Database)
- **Runtime Environment Variables**: Direct injection of secrets into environment variables using App Runner's Secrets property
- **Conditional Secret Loading**: Secrets are only loaded when both environment variable name and ARN are provided

### Features
- **App Runner Service**: Deploys a containerized application from Amazon ECR using AWS App Runner.
- **VPC Integration**: Supports private networking with VPC connector and security group configuration.
- **IAM Roles**: Creates dedicated IAM roles for App Runner instance and ECR access with Secrets Manager permissions.
- **Advanced Secrets Management**: Integrates with AWS Secrets Manager for secure environment variable injection (up to 7 secrets).
- **Auto Scaling**: Configurable minimum and maximum instances, and concurrency settings.
- **Health Check Configuration**: Comprehensive health check settings including path, thresholds, intervals, and timeouts.
- **Ingress/Egress Control**: Supports VPC endpoint and ingress connection for secure access.
- **WAF Integration**: Optional Web Application Firewall (WAF) association for enhanced security.
- **Database Connectivity**: Environment-specific database port configuration and subnet access.
- **Parameterization**: All key settings are parameterized for flexible deployments.
- **Resource Tagging**: All resources include `IaCVersion` and `Name` tags for traceability.

### Improvements
- **Parameter Structure**: Reorganized parameters into logical categories for better usability
- **Secrets Integration**: Replaced basic secret provisioning with comprehensive Secrets Manager integration
- **Parameter Naming**: Updated parameter names for clarity (`SecretKeyName` → `SecretArn`)
- **Conditional Logic**: Enhanced condition checking for secret parameters
- **Documentation**: Updated README with comprehensive parameter documentation and examples
- **Template Organization**: Improved parameter ordering and grouping within the template

### Breaking Changes
- **Parameter Names**: `SecretKeyName1-5` parameters renamed to `SecretArn1-5`
- **Secrets Structure**: Changed from basic secret creation to Secrets Manager ARN references
- **Template File**: Template filename updated to `cf-apprunner-service.yaml`

### Bug Fixes
- Fixed duplicate parameter definitions
- Corrected condition references for secret parameters
- Improved YAML structure and validation

### Migration Guide
For existing deployments using v1.0:
1. **Update Parameter Names**: Change `SecretKeyName1-5` to `SecretArn1-5` in your parameter files
2. **Provide Secret ARNs**: Update parameter values to use actual Secrets Manager ARNs instead of secret names
3. **Review Parameter Structure**: Check new parameter organization and update deployment scripts
4. **Test Secret Integration**: Verify that secrets are properly injected as environment variables

### Usage Examples
```yaml
# New parameter structure
SecretKeyEnvVar1: "DATABASE_PASSWORD"
SecretArn1: "arn:aws:secretsmanager:ap-southeast-1:123456789012:secret:db-password-AbCdEf"
SecretKeyEnvVar2: "API_KEY" 
SecretArn2: "arn:aws:secretsmanager:ap-southeast-1:123456789012:secret:api-key-GhIjKl"
```

### Notes
- Designed for internal/private App Runner deployments with VPC connectivity.
- Requires AWS CLI or CloudFormation Console for deployment.
- Ensure IAM permissions for stack creation, resource management, and Secrets Manager access.
- App Runner instance role automatically includes Secrets Manager read permissions.
- Environment variables from secrets are available at container startup.

---

**Maintainer:** Infrastructure Team  
**Template Version:** v1.1  
**Last Updated:** September 16, 2025  
