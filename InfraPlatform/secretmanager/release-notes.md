# AWS Secrets Manager Template - Release Notes

## Version 1.1.0 - Multi-Secret Support Enhancement
**Release Date:** June 20, 2025

### 🎉 New Features

#### Multi-Secret Template Support
- **Enhanced Template**: `cf-secretmanager.yaml` now supports up to 10 secrets in a single deployment
- **Conditional Creation**: Only creates secrets when names are provided (empty names are skipped)
- **Batch Deployment**: Deploy multiple related secrets together for complete application configurations
- **Individual Configuration**: Each secret has its own name and description parameters

#### New Parameter Structure
- **Secret Parameters**: `Secret1Name` through `Secret10Name` for flexible secret naming
- **Description Support**: `Secret1Description` through `Secret10Description` for individual secret documentation
- **Simplified Configuration**: Removed `SecretType` and `SecretJsonTemplate` for streamlined setup

#### Enhanced Stack Management
- **Single Stack Deployment**: Manage all application secrets in one CloudFormation stack
- **Simplified Outputs**: Individual ARN and name outputs for each created secret
- **Consistent Tagging**: Automatic tagging across all secrets with application and environment metadata

### 🔧 Technical Improvements

#### Template Logic
- **Advanced Conditions**: Smart conditional logic for creating only specified secrets
- **Environment-Aware Policies**: Production environments automatically get `Retain` deletion policy
- **Resource Optimization**: No unused resources created when secret names are empty

#### Security Enhancements
- **Unified KMS**: Single KMS configuration applies to all secrets in the stack
- **Production Protection**: Enhanced deletion policies for production environments (`prod`, `prod-a`, `prod-b`)
- **Consistent Encryption**: All secrets use the same encryption configuration

### 🚀 Use Cases

#### Complete Application Secret Suite
Deploy all secrets needed for a web application in one stack:
- Database credentials
- External API keys (Twilio, SendGrid, Stripe)
- OAuth tokens
- Webhook verification secrets
- Custom application secrets

#### Environment Consistency
Maintain identical secret structures across development, staging, and production environments with different parameter files.

---

## Version 1.0.0 - Initial Release
**Release Date:** June 11, 2025

### 🎉 Initial Features

#### Generic Secrets Manager Template
- **New CloudFormation Template**: `cf-secretmanager.yaml` - Generic, reusable template for creating AWS Secrets Manager secrets
- **Flexible Secret Types**: Support for multiple secret categories including API keys, database credentials, webhook secrets, OAuth tokens, and custom formats
- **JSON Template Structure**: Configurable JSON templates with placeholder values for consistent secret initialization

#### Core Functionality
- **Standardized Naming**: Consistent naming convention `{AppShortName}-{EnvName}-secret-{SecretName}`
- **Environment Support**: Full environment lifecycle support (nprd, nprd-dev, nprd-sit, nprd-uat, nprd-pt, nprd-pp, prod variants)
- **Security Options**: Optional custom KMS key encryption for enhanced security
- **Configurable Deletion Window**: Flexible recovery window (0-30 days) before permanent deletion

#### Template Parameters
- **Core Parameters**: AppShortName, EnvName, SecretName, SecretDescription
- **Secret Configuration**: SecretType categorization and customizable JSON templates
- **Security Configuration**: Custom KMS key support with conditional logic
- **Deletion Management**: Configurable deletion window for different environments

#### Security Features
- **AWS Managed Encryption**: Default encryption using AWS managed keys
- **Custom KMS Support**: Optional custom KMS key encryption for production environments
- **Conditional Logic**: Smart KMS key application based on configuration
- **IAM Integration**: Compatible with existing IAM roles and policies

#### Documentation
- **Comprehensive Guide**: Complete deployment and configuration guide
- **Common Templates**: Pre-configured examples for popular services
- **Security Best Practices**: Production and development configuration guidelines
- **Pipeline Integration**: Azure DevOps integration examples

---

## Compatibility Notes

- **AWS Regions**: Compatible with all AWS regions supporting Secrets Manager
- **CloudFormation**: Requires CloudFormation capabilities for secret creation
- **Dependencies**: No external dependencies or custom resources required

## Known Limitations

- **Secret Size**: Limited by AWS Secrets Manager secret size limits (64KB)
- **JSON Format**: Secrets must be in JSON format for template compatibility

## Future Considerations

- Potential support for automatic secret rotation configurations
- Enhanced integration templates for specific AWS services
- Extended security configuration options

---

**Template Version**: 1.1.0  
**Documentation Version**: 1.1.0  
**Compatibility**: AWS CloudFormation, Azure DevOps Pipelines