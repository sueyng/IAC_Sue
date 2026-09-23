# AWS Secrets Manager Template Guide

## 📋 Overview

The AWS Secrets Manager template (`cf-secretmanager.yaml`) is a reusable CloudFormation template for creating and managing up to 10 secrets in a single deployment across any AWS project. It provides a standardized approach to storing sensitive information like API keys, database credentials, and service tokens.

## 🗂️ Template Files

| File | Purpose |
|------|---------|
| `cf-secretmanager.yaml` | CloudFormation template supporting up to 10 secrets |
| `parameters-secretmanager.json` | Parameter configuration file |

## 🎯 Use Cases

This template can be used for any project requiring secure storage of:
- **API Keys** - Third-party service credentials (Twilio, SendGrid, Stripe, etc.)
- **Database Credentials** - Username/password combinations
- **Webhook Secrets** - Verification tokens for webhooks
- **OAuth Tokens** - Authentication tokens and refresh tokens
- **Multi-Service Integration** - Complete secret sets per environment

## 📋 Template Parameters

### Core Parameters

| Parameter | Example Value | Description |
|-----------|---------------|-------------|
| `AppShortName` | `myapp` | Application or project identifier |
| `EnvName` | `nprd`, `prod` | Environment name (restricted list) |

### Security Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `EnableCustomKmsKey` | `false` | Use custom KMS key for encryption |
| `CustomKmsKeyId` | `""` | Custom KMS key ID or ARN |
| `DeletionWindowInDays` | `7` | Recovery window before permanent deletion (0-30 days) |

### Secret Configuration (1-10)

| Parameter Pattern | Default | Description |
|-------------------|---------|-------------|
| `Secret[N]Name` | `""` | Name of the secret (leave empty to skip creation) |
| `Secret[N]Description` | `"Secret for application integration"` | Description of the secret |

## 🔧 Parameter File Examples

### Single Secret Deployment

```json
[
  {
    "ParameterKey": "AppShortName",
    "ParameterValue": "myapp"
  },
  {
    "ParameterKey": "EnvName",
    "ParameterValue": "nprd"
  },
  {
    "ParameterKey": "Secret1Name",
    "ParameterValue": "twilio"
  },
  {
    "ParameterKey": "Secret1Description",
    "ParameterValue": "Twilio API credentials for SMS and WhatsApp messaging"
  }
]
```

### Multiple Secrets Deployment

```json
[
  {
    "ParameterKey": "AppShortName",
    "ParameterValue": "webapp"
  },
  {
    "ParameterKey": "EnvName",
    "ParameterValue": "prod"
  },
  {
    "ParameterKey": "EnableCustomKmsKey",
    "ParameterValue": "true"
  },
  {
    "ParameterKey": "CustomKmsKeyId",
    "ParameterValue": "arn:aws:kms:ap-southeast-1:123456789012:key/12345678-1234-1234-1234-123456789012"
  },
  {
    "ParameterKey": "DeletionWindowInDays",
    "ParameterValue": "30"
  },
  {
    "ParameterKey": "Secret1Name",
    "ParameterValue": "database"
  },
  {
    "ParameterKey": "Secret1Description",
    "ParameterValue": "Primary database connection credentials"
  },
  {
    "ParameterKey": "Secret2Name",
    "ParameterValue": "twilio"
  },
  {
    "ParameterKey": "Secret2Description",
    "ParameterValue": "Twilio API credentials for SMS notifications"
  },
  {
    "ParameterKey": "Secret3Name",
    "ParameterValue": "sendgrid"
  },
  {
    "ParameterKey": "Secret3Description",
    "ParameterValue": "SendGrid API key for email services"
  }
]
```

## 🔐 Security Configuration

### Development Environment
```json
[
  {
    "ParameterKey": "EnableCustomKmsKey",
    "ParameterValue": "false"
  },
  {
    "ParameterKey": "DeletionWindowInDays",
    "ParameterValue": "7"
  }
]
```

### Production Environment
```json
[
  {
    "ParameterKey": "EnableCustomKmsKey",
    "ParameterValue": "true"
  },
  {
    "ParameterKey": "CustomKmsKeyId",
    "ParameterValue": "arn:aws:kms:ap-southeast-1:123456789012:key/12345678-1234-1234-1234-123456789012"
  },
  {
    "ParameterKey": "DeletionWindowInDays",
    "ParameterValue": "30"
  }
]
```

## 📝 Post-Deployment Management

### Update Secret Values

After deployment, the secrets contain placeholder values. Update them via AWS Console:

1. **Navigate to AWS Secrets Manager Console**
2. **Find the deployed secret** (e.g., `myapp-nprd-secret-twilio`)
3. **Click "Retrieve secret value"**
4. **Click "Edit"**
5. **Replace placeholder values with actual credentials**
6. **Save the updated secret**

#### Example Secret Updates:

**Twilio Secret:**
```json
{
  "account_sid": "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "auth_token": "your-actual-auth-token",
  "api_key": "your-actual-api-key"
}
```

**Database Secret:**
```json
{
  "username": "db_user",
  "password": "secure_password_here",
  "host": "database.cluster-xyz.region.rds.amazonaws.com",
  "port": "3306",
  "dbname": "production_db"
}
```

## 🗂️ Naming Conventions

### Secret Names
- **Pattern**: `{AppShortName}-{EnvName}-secret-{SecretName}`
- **Examples**: `myapp-prod-secret-twilio`, `billing-nprd-secret-stripe`

## 🔍 Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Secret already exists | Duplicate secret name | Use unique SecretName or delete existing secret |
| KMS access denied | Insufficient KMS permissions | Verify CloudFormation role has KMS permissions |
| No resources created | All secret names are empty | Provide at least one non-empty SecretName |
| Invalid environment | Using unsupported environment name | Use only values from allowed EnvName list |

## 📊 Best Practices

### 1. **Environment-Specific Configuration**
- Use separate parameter files for each environment
- Apply stricter security settings for production (custom KMS, longer deletion windows)
- Never share secrets between environments

### 2. **Secret Organization**
- Group related secrets in a single stack deployment
- Use descriptive secret names that indicate their purpose
- Deploy separate stacks for different applications

### 3. **Security Management**
- Use custom KMS keys for production environments
- Set appropriate deletion windows (longer for production)
- Update placeholder values immediately after deployment
- Implement regular secret rotation schedules

### 4. **Pipeline Integration**
- Use CI/CD pipelines for consistent deployments
- Implement approval gates for production secret deployments
- Test deployments in non-production first

This template provides a flexible, secure foundation for managing multiple secrets across any AWS project through standardized CloudFormation deployments.