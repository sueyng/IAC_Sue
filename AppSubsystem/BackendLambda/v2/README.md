# Lambda Infrastructure Deployment Guide

This guide provides instructions for deploying AWS Lambda infrastructure using CloudFormation templates.

## 📋 Overview

Four CloudFormation templates work together to provision Lambda infrastructure:

1. **Prefix List Template** - Managed prefix lists for network access control
2. **Security Group Template** - VPC security groups for Lambda functions
3. **Lambda Layers Template** - Reusable Lambda layers for dependencies  
4. **Lambda Function Template** - Lambda functions with IAM roles and integrations

## 🗂️ Template Files

| Template | File | Purpose |
|----------|------|---------|
| Prefix List | `cf-lambda-prefixlist.yaml` | Managed prefix lists for CIDR groups |
| Security Group | `cf-lambda-securitygroup.yaml` | VPC security groups |
| Lambda Layers | `cf-lambda-layers.yaml` | Reusable layers |
| Lambda Function | `cf-lambda-app.yaml` | Functions with IAM & integrations |

## 🚀 Deployment Sequence

Deploy in this order:

```
1. Prefix Lists (cf-lambda-prefixlist.yaml) [Optional - for network control]
   ↓
2. Security Group (cf-lambda-securitygroup.yaml) [Optional - VPC only]
   ↓
3. Lambda Layers (cf-lambda-layers.yaml) [Optional]
   ↓  
4. Lambda Function (cf-lambda-app.yaml)
```

## 📋 Template 1: Prefix List Configuration

### Required Parameters
| Parameter | Example | Description |
|-----------|---------|-------------|
| `AppShortName` | `myapp` | Application identifier |
| `EnvName` | `nprd` | Environment (nprd/prod) |
| `PrefixListPurpose` | `dynamodb` | Purpose/name suffix (dynamodb, s3, external-api) |
| `NumberOfEntries` | `4` | Number of CIDR entries to create (1-20) |

### CIDR Entry Configuration
```json
{
  "ParameterKey": "CidrEntry01",
  "ParameterValue": "52.94.0.0/16"
},
{
  "ParameterKey": "EntryDescription01",
  "ParameterValue": "DynamoDB Global Tables"
}
```

### Common Use Cases
| Purpose | Example CIDRs | Description |
|---------|---------------|-------------|
| `dynamodb` | `52.94.0.0/16`, `52.119.161.0/24` | DynamoDB service endpoints |
| `s3` | `54.231.0.0/16`, `52.216.0.0/16` | S3 and CloudFront endpoints |
| `external-api` | `208.43.0.0/16` | Twilio, FormSG services |

### Key Features
- **MaxEntries**: 50 (configurable)
- **Conditional Creation**: Only creates filled CIDR entries
- **Environment Protection**: Retain policy for production environments

## 📋 Template 2: Security Group Configuration

### Required Parameters
| Parameter | Example | Description |
|-----------|---------|-------------|
| `AppShortName` | `myapp` | Application identifier |
| `EnvName` | `nprd` | Environment (nprd/prod) |
| `VpcId` | `vpc-0d99a0c727b301d67` | Target VPC |

### Prefix List Integration (Manual Entry Required)
```json
{
  "ParameterKey": "DynamoDBPrefixListId",
  "ParameterValue": "pl-0dynamodb123"
},
{
  "ParameterKey": "S3PrefixListId",
  "ParameterValue": "pl-0s3456"
},
{
  "ParameterKey": "AdditionalPrefixListId",
  "ParameterValue": "pl-0external789"
}
```

### Database Integration

#### CIDR-Only Method (Most Common)
```json
{
  "ParameterKey": "DatabaseSubnetCidrs",
  "ParameterValue": "10.53.70.96/28,10.53.70.112/28"
},
{
  "ParameterKey": "DatabasePort",
  "ParameterValue": "3306"
}
```

#### Security Group Method
```json
{
  "ParameterKey": "DatabaseSecurityGroupId", 
  "ParameterValue": "sg-0database123"
},
{
  "ParameterKey": "DatabasePort",
  "ParameterValue": "3306"
}
```

#### Combined Method (Both)
```json
{
  "ParameterKey": "DatabaseSubnetCidrs",
  "ParameterValue": "10.53.70.96/28,10.53.70.112/28"
},
{
  "ParameterKey": "DatabaseSecurityGroupId", 
  "ParameterValue": "sg-0database123"
},
{
  "ParameterKey": "DatabasePort",
  "ParameterValue": "3306"
}
```

### Key Configuration
- **HCC Proxy**: Different CIDRs for prod vs non-prod environments
- **Database Access**: 
  - **Via Security Group**: Use `DatabaseSecurityGroupId` for security group-to-security group rules
  - **Via Subnet CIDRs**: Use `DatabaseSubnetCidrs` for direct CIDR-based rules (supports up to 2 CIDRs)
  - **Database Port**: Configurable port (default: 3306 for MySQL/Aurora)
- **Service Access**: Configurable egress rules for AWS services
- **Prefix List Support**: Uses prefix lists for scalable CIDR management

## 🔧 Database Configuration Options

### Option 1: CIDR-Only Method (Most Common)
```json
{
  "ParameterKey": "DatabaseSubnetCidrs",
  "ParameterValue": "10.53.70.96/28,10.53.70.112/28"
}
```
**Use when**: 
- Well-defined database subnets 
- Self-managed databases on EC2
- Cross-account database access
- Explicit CIDR-based network control preferred
- Multi-AZ deployments with known subnet ranges

**Supports**: Up to 2 database subnet CIDRs

### Option 2: Security Group Reference
```json
{
  "ParameterKey": "DatabaseSecurityGroupId",
  "ParameterValue": "sg-0database123"
}
```
**Use when**: 
- Managed databases (RDS, Aurora) with security groups
- Dynamic security group management preferred
- Database security group rules change frequently

### Option 3: Combined Approach
```json
{
  "ParameterKey": "DatabaseSubnetCidrs",
  "ParameterValue": "10.53.70.96/28,10.53.70.112/28"
},
{
  "ParameterKey": "DatabaseSecurityGroupId", 
  "ParameterValue": "sg-0database123"
}
```
**Use when**: Both security group and subnet-specific access required

## 📋 Template 3: Lambda Layers Configuration

### Required Parameters
| Parameter | Example | Description |
|-----------|---------|-------------|
| `AppShortName` | `myapp` | Application identifier |
| `EnvName` | `nprd` | Environment |
| `LayerDeploymentBucketName` | `myapp-nprd-deployment` | S3 bucket for layers |

### Layer Configuration (1-5 layers supported)
```json
{
  "ParameterKey": "Layer1Name",
  "ParameterValue": "requests"
},
{
  "ParameterKey": "Layer1S3Key", 
  "ParameterValue": "layers/requests/requests-layer.zip"
}
```

## 📋 Template 4: Lambda Function Configuration

### Core Required Parameters
| Parameter | Example | Description |
|-----------|---------|-------------|
| `AppShortName` | `myapp` | Application identifier |
| `EnvName` | `nprd` | Environment |
| `LambdaFunctionName` | `hello-world` | Function name |
| `LambdaS3BucketName` | `myapp-nprd-bucket` | Deployment S3 bucket |
| `LambdaS3KeyPath` | `lambda/hello-world.zip` | S3 path to code |

### Service Access Configuration
| Parameter | Default | Description |
|-----------|---------|-------------|
| `EnableS3Access` | `true` | S3 permissions |
| `EnableDynamoDBAccess` | `true` | DynamoDB permissions |
| `EnableSecretsManagerAccess` | `true` | Secrets Manager permissions |
| `EnableSQSAccess` | `true` | SQS permissions |
| `EnableSSMAccess` | `true` | Parameter Store permissions |
| `EnableSESAccess` | `false` | Email service permissions |
| `EnableSNSAccess` | `false` | Notification permissions |
| `EnableEventBridgeAccess` | `false` | EventBridge permissions |
| `EnableLambdaInvokeAccess` | `false` | Lambda invoke permissions |

### S3 Access Configuration

#### Default Pattern-Based Access (Backward Compatible)
```json
{
  "ParameterKey": "EnableS3Access",
  "ParameterValue": "true"
}
```
**Grants access to:**
- `{AppShortName}-{EnvName}-*` buckets
- `{AppShortName}-*` buckets

#### Specific Bucket Access (Enhanced Security) 🆕
```json
{
  "ParameterKey": "EnableS3Access",
  "ParameterValue": "true"
},
{
  "ParameterKey": "S3SpecificBucketNames",
  "ParameterValue": "my-app-data,my-app-logs,my-app-config"
}
```
**Grants access to:**
- Only the specified buckets
- Both bucket-level and object-level permissions automatically
- Overrides pattern-based access when provided

#### S3 Configuration Options

| Configuration | Use Case | Security Level |
|---------------|----------|----------------|
| **Pattern-based** (default) | General applications, multiple buckets | Standard |
| **Specific buckets** | Production workloads, compliance requirements | Enhanced |

### VPC Configuration (Optional)
```json
{
  "ParameterKey": "EnableVpcConfiguration",
  "ParameterValue": "true"
},
{
  "ParameterKey": "SubnetIds",
  "ParameterValue": "subnet-123,subnet-456"
},
{
  "ParameterKey": "LambdaSecurityGroupId",
  "ParameterValue": "sg-0lambda123"
}
```

### Event Sources
| Type | Parameters Required |
|------|-------------------|
| `none` | None |
| `sqs` | `SqsQueueArn` |
| `eventbridge` | `ScheduleExpression` |
| `apigateway` | `ApiGatewayId` |

## 🚨 CloudWatch Alarms Configuration (Optional)

### Overview
The Lambda template now includes optional CloudWatch alarms for production monitoring. This feature provides automated alerting for Lambda function health and performance issues.

### Alarm Configuration Parameters
| Parameter | Default | Description |
|-----------|---------|-------------|
| `EnableAlarms` | `false` | Enable CloudWatch alarms for Lambda monitoring |
| `AdminAlertsTopicArn` | `""` | **REQUIRED if EnableAlarms='true'**: SNS topic ARN for notifications |
| `ErrorRateThreshold` | `5` | Error rate threshold percentage (0-100) |
| `ThrottlesThreshold` | `1` | Throttles threshold count per minute |
| `DurationThresholdMs` | `30000` | Duration threshold in milliseconds |

### Alarms Created
When `EnableAlarms=true`, three CloudWatch alarms are automatically created:

#### 1. Error Rate Alarm
- **Metric**: (Errors / Invocations) * 100
- **Threshold**: Configurable percentage (default: 5%)
- **Description**: Monitors high error rates indicating system issues
- **Action Required**: Review Lambda function logs for errors

#### 2. Throttles Alarm  
- **Metric**: Lambda throttles count
- **Threshold**: Configurable count per minute (default: 1)
- **Description**: Monitors Lambda concurrency throttling
- **Action Required**: Review invocation patterns and concurrency limits

#### 3. Duration Alarm
- **Metric**: Average function duration
- **Threshold**: Configurable milliseconds (default: 30,000ms)
- **Description**: Monitors high execution duration
- **Action Required**: Investigate performance issues or increase timeout

### Basic Alarm Configuration
```json
{
  "ParameterKey": "EnableAlarms",
  "ParameterValue": "true"
},
{
  "ParameterKey": "AdminAlertsTopicArn",
  "ParameterValue": "arn:aws:sns:ap-southeast-1:123456789012:admin-alerts"
}
```

### Advanced Alarm Configuration
```json
{
  "ParameterKey": "EnableAlarms",
  "ParameterValue": "true"
},
{
  "ParameterKey": "AdminAlertsTopicArn",
  "ParameterValue": "arn:aws:sns:ap-southeast-1:123456789012:admin-alerts"
},
{
  "ParameterKey": "ErrorRateThreshold",
  "ParameterValue": "2"
},
{
  "ParameterKey": "ThrottlesThreshold",
  "ParameterValue": "5"
},
{
  "ParameterKey": "DurationThresholdMs",
  "ParameterValue": "15000"
}
```

### Alarm Naming Convention
Alarms are named using the pattern:
- `{AppShortName}-{EnvName}-alarm-{LambdaFunctionName}-{alarm-type}`

Examples:
- `myapp-prod-alarm-processor-errorrate`
- `myapp-prod-alarm-processor-throttles`
- `myapp-prod-alarm-processor-duration`

### Prerequisites for Alarms
1. **SNS Topic**: Create an SNS topic for alarm notifications
2. **Subscriptions**: Configure email/SMS subscriptions to the SNS topic
3. **IAM Permissions**: Ensure CloudWatch has permission to publish to SNS topic

### Production Recommendations
- **Always enable alarms** for production workloads
- **Set appropriate thresholds** based on function requirements:
  - **Error Rate**: 1-5% for production functions
  - **Throttles**: 0-1 for critical functions
  - **Duration**: 50-80% of function timeout value
- **Test alarm notifications** before production deployment
- **Document alarm response procedures** in runbooks

### Alarm Outputs
When alarms are enabled, the template provides these outputs:
- `ErrorRateAlarmArn`: ARN of the error rate alarm
- `ThrottlesAlarmArn`: ARN of the throttles alarm  
- `DurationAlarmArn`: ARN of the duration alarm

## 🔧 Environment Variables

### Database Configuration
```json
{
  "ParameterKey": "DbSecretArn",
  "ParameterValue": "arn:aws:secretsmanager:region:account:secret:db-creds"
},
{
  "ParameterKey": "DbHost", 
  "ParameterValue": "db.cluster-xyz.rds.amazonaws.com"
}
```

### External Service Configuration
```json
{
  "ParameterKey": "FormSgSecretArn",
  "ParameterValue": "arn:aws:secretsmanager:region:account:secret:formsg-webhook"
},
{
  "ParameterKey": "FormId",
  "ParameterValue": "64f8b9a2e1234567890abcdef"
},
{
  "ParameterKey": "EnableFormSg",
  "ParameterValue": "true"
},
{
  "ParameterKey": "TwilioSecretArn",
  "ParameterValue": "arn:aws:secretsmanager:region:account:secret:twilio-creds"
},
{
  "ParameterKey": "TwilioAccountSid",
  "ParameterValue": "AC1234567890abcdef1234567890abcdef"
},
{
  "ParameterKey": "ProxyUrl",
  "ParameterValue": "http://proxy.internal.gov.sg:8080"
}
```

## 📊 Parameter Dependencies

| Source Template | Output | Target Parameter | Method |
|-----------------|--------|------------------|---------|
| Prefix Lists | `PrefixListId` | `DynamoDBPrefixListId`, `S3PrefixListId`, `AdditionalPrefixListId` | **Manual Copy** |
| Security Group | `LambdaSecurityGroupId` | `LambdaSecurityGroupId` | Cross-stack reference |
| Layers | `Layer1Arn,Layer2Arn...` | `LambdaLayerArns` | Cross-stack reference |

## 🚨 Key Configuration Notes

### Prefix Lists
- **Single purpose per list** - Create separate stacks for DynamoDB, S3, external APIs
- **20 CIDR entries maximum** per template (can extend MaxEntries to 50+ for future growth)
- **Environment protection** - Production prefix lists use Retain deletion policy

### Database Connectivity
- **CIDR-Only Method**: Most common approach for well-defined database subnets
- **Security Group Method**: Alternative for managed databases with dynamic security groups  
- **Combined Method**: Use both when multiple access patterns are required
- **Port Configuration**: Default MySQL/Aurora (3306), configurable for other databases
- **Multi-AZ Support**: Comma-separated CIDRs support multi-availability zone deployments
- **No Security Group Required**: CIDR method works independently without database security group references

### S3 Access Control 🆕
- **Pattern-based (default)**: Uses `{AppShortName}-{EnvName}-*` and `{AppShortName}-*` patterns
- **Specific buckets**: Specify exact bucket names for enhanced security
- **Automatic permissions**: Both bucket and object-level permissions granted automatically
- **Backward compatible**: Existing deployments continue working without changes
- **Security benefit**: Follows principle of least privilege when specific buckets used
- **Production recommended**: Use specific buckets for production workloads and compliance requirements

### IAM Roles
- **Automatically created** per Lambda function - no separate role template needed
- Service permissions controlled via `Enable*Access` parameters

### VPC Configuration  
- Set `EnableVpcConfiguration=true` for VPC deployment
- Requires both `SubnetIds` and `LambdaSecurityGroupId`
- Use private subnets with NAT Gateway or HCC Proxy

### Event Sources
- **SQS**: Standard queues only (no FIFO support)
- **EventBridge**: Use `cron(0 1 * * ? *)` or `rate(5 minutes)`
- **API Gateway**: Requires existing API Gateway resource

### Security
- HCC Proxy CIDRs automatically selected based on environment (prod vs nprd)
- Service access can be enabled/disabled per function
- All secrets accessed via ARN parameters

### CloudWatch Alarms
- **Optional feature** - disabled by default to avoid additional costs
- **SNS topic required** - must exist before enabling alarms
- **Production recommended** - enable for all production workloads
- **Environment protection** - Production alarms use Retain deletion policy
- **Actionable descriptions** - Each alarm includes specific troubleshooting guidance

## 🔍 Sample Parameter Files

### Prefix List - DynamoDB
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
    "ParameterKey": "PrefixListPurpose",
    "ParameterValue": "dynamodb"
  },
  {
    "ParameterKey": "PrefixListDescription",
    "ParameterValue": "DynamoDB service endpoints for Lambda access"
  },
  {
    "ParameterKey": "NumberOfEntries",
    "ParameterValue": "4"
  },
  {
    "ParameterKey": "CidrEntry01",
    "ParameterValue": "52.94.0.0/16"
  },
  {
    "ParameterKey": "EntryDescription01",
    "ParameterValue": "DynamoDB Global Tables"
  },
  {
    "ParameterKey": "CidrEntry02",
    "ParameterValue": "52.119.161.0/24"
  },
  {
    "ParameterKey": "EntryDescription02",
    "ParameterValue": "DynamoDB Streams"
  }
]
```

### External API prefix list example to focus on remaining services
```json
[
  {
    "ParameterKey": "PrefixListPurpose",
    "ParameterValue": "external-api"
  },
  {
    "ParameterKey": "PrefixListDescription",
    "ParameterValue": "External API services (Twilio, FormSG)"
  },
  {
    "ParameterKey": "NumberOfEntries",
    "ParameterValue": "2"
  },
  {
    "ParameterKey": "CidrEntry01",
    "ParameterValue": "208.43.0.0/16"
  },
  {
    "ParameterKey": "EntryDescription01",
    "ParameterValue": "Twilio Voice/SMS"
  }
]
```

### Security Group with Database Access (Security Group Method)
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
    "ParameterKey": "VpcId",
    "ParameterValue": "vpc-0d99a0c727b301d67"
  },
  {
    "ParameterKey": "DatabaseSecurityGroupId",
    "ParameterValue": "sg-0database123"
  },
  {
    "ParameterKey": "DatabasePort",
    "ParameterValue": "3306"
  }
]
```

### Security Group with Database Subnet CIDRs
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
    "ParameterKey": "VpcId",
    "ParameterValue": "vpc-0d99a0c727b301d67"
  },
  {
    "ParameterKey": "DatabaseSubnetCidrs",
    "ParameterValue": "10.53.70.96/28,10.53.70.112/28"
  },
  {
    "ParameterKey": "DatabasePort",
    "ParameterValue": "3306"
  }
]
```

### Basic Function
```json
[
  {
    "ParameterKey": "AppShortName",
    "ParameterValue": "myapp"
  },
  {
    "ParameterKey": "LambdaFunctionName", 
    "ParameterValue": "hello-world"
  },
  {
    "ParameterKey": "LambdaS3BucketName",
    "ParameterValue": "myapp-nprd-deployment"
  },
  {
    "ParameterKey": "EnableVpcConfiguration",
    "ParameterValue": "false"
  }
]
```

### Function with Specific S3 Buckets (Enhanced Security) 🆕
```json
[
  {
    "ParameterKey": "AppShortName",
    "ParameterValue": "myapp"
  },
  {
    "ParameterKey": "EnvName",
    "ParameterValue": "prod"
  },
  {
    "ParameterKey": "LambdaFunctionName",
    "ParameterValue": "data-processor"
  },
  {
    "ParameterKey": "LambdaS3BucketName",
    "ParameterValue": "myapp-prod-deployment"
  },
  {
    "ParameterKey": "EnableS3Access",
    "ParameterValue": "true"
  },
  {
    "ParameterKey": "S3SpecificBucketNames",
    "ParameterValue": "myapp-prod-data,myapp-prod-logs,myapp-prod-config"
  },
  {
    "ParameterKey": "EnableVpcConfiguration",
    "ParameterValue": "true"
  },
  {
    "ParameterKey": "LambdaSecurityGroupId",
    "ParameterValue": "sg-0lambda123"
  },
  {
    "ParameterKey": "SubnetIds",
    "ParameterValue": "subnet-123,subnet-456"
  }
]
```

### Production Function with Monitoring
```json
[
  {
    "ParameterKey": "AppShortName",
    "ParameterValue": "myapp"
  },
  {
    "ParameterKey": "EnvName",
    "ParameterValue": "prod"
  },
  {
    "ParameterKey": "LambdaFunctionName",
    "ParameterValue": "processor"
  },
  {
    "ParameterKey": "LambdaS3BucketName",
    "ParameterValue": "myapp-prod-deployment"
  },
  {
    "ParameterKey": "EnableVpcConfiguration", 
    "ParameterValue": "true"
  },
  {
    "ParameterKey": "LambdaSecurityGroupId",
    "ParameterValue": "sg-0lambda123"
  },
  {
    "ParameterKey": "SubnetIds",
    "ParameterValue": "subnet-123,subnet-456"
  },
  {
    "ParameterKey": "EnableS3Access",
    "ParameterValue": "true"
  },
  {
    "ParameterKey": "EnableDynamoDBAccess",
    "ParameterValue": "true"
  },
  {
    "ParameterKey": "EnableAlarms",
    "ParameterValue": "true"
  },
  {
    "ParameterKey": "AdminAlertsTopicArn",
    "ParameterValue": "arn:aws:sns:ap-southeast-1:123456789012:prod-admin-alerts"
  },
  {
    "ParameterKey": "ErrorRateThreshold",
    "ParameterValue": "2"
  },
  {
    "ParameterKey": "DurationThresholdMs",
    "ParameterValue": "25000"
  }
]
```

### Full-Featured Function with External Services
```json
[
  {
    "ParameterKey": "AppShortName",
    "ParameterValue": "myapp"
  },
  {
    "ParameterKey": "LambdaFunctionName",
    "ParameterValue": "processor"
  },
  {
    "ParameterKey": "EnableVpcConfiguration", 
    "ParameterValue": "true"
  },
  {
    "ParameterKey": "LambdaSecurityGroupId",
    "ParameterValue": "sg-0lambda123"
  },
  {
    "ParameterKey": "EnableS3Access",
    "ParameterValue": "true"
  },
  {
    "ParameterKey": "EnableDynamoDBAccess",
    "ParameterValue": "true"
  },
  {
    "ParameterKey": "FormId",
    "ParameterValue": "64f8b9a2e1234567890abcdef"
  },
  {
    "ParameterKey": "EnableFormSg",
    "ParameterValue": "true"
  },
  {
    "ParameterKey": "TwilioAccountSid",
    "ParameterValue": "AC1234567890abcdef1234567890abcdef"
  },
  {
    "ParameterKey": "ProxyUrl",
    "ParameterValue": "http://proxy.internal.gov.sg:8080"
  },
  {
    "ParameterKey": "EventSourceType",
    "ParameterValue": "sqs"
  },
  {
    "ParameterKey": "SqsQueueArn",
    "ParameterValue": "arn:aws:sqs:region:account:queue-name"
  },
  {
    "ParameterKey": "EnableAlarms",
    "ParameterValue": "true"
  },
  {
    "ParameterKey": "AdminAlertsTopicArn",
    "ParameterValue": "arn:aws:sns:ap-southeast-1:123456789012:admin-alerts"
  }
]
```

## 🔧 Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Prefix list creation fails | Invalid CIDR format | Validate CIDR notation (e.g., 10.0.0.0/16) |
| Security group prefix list error | Wrong prefix list ID | Use exact prefix list ID from stack outputs |
| Can't find prefix list ID | Stack outputs not checked | Use `aws cloudformation describe-stacks` to get outputs |
| Wrong prefix list referenced | Copy-paste error | Double-check prefix list purpose matches parameter |
| Prefix list not found | Stack name incorrect | Verify exact stack naming convention |
| Database connection fails | Missing database config | Set either `DatabaseSecurityGroupId` or `DatabaseSubnetCidrs` |
| Second database CIDR ignored | Using old template version | Update to latest template with multi-CIDR support |
| Database port error | Wrong port configured | Verify database port (3306=MySQL, 5432=PostgreSQL, etc.) |
| Mixed database access needed | Single method limitation | Use both security group ID and subnet CIDRs parameters |
| VPC config error | Missing SubnetIds/SecurityGroupId | Provide both when VPC enabled |
| Service access denied | Missing Enable*Access=true | Enable required service access |
| **S3 specific bucket access denied** 🆕 | **Wrong bucket names in parameter** | **Verify exact bucket names in S3SpecificBucketNames parameter** |
| **S3 pattern access not working** 🆕 | **Specific buckets parameter provided** | **Remove S3SpecificBucketNames to use pattern-based access** |
| **S3 bucket policy conflict** 🆕 | **Mixed access methods** | **Use either pattern-based OR specific buckets, not both** |
| Layer ARN error | Wrong layer ARN format | Use exact ARN from layer stack outputs |
| JSON syntax error | Invalid parameter JSON | Validate JSON before deployment |
| **Alarm creation fails** | **Missing SNS topic ARN** | **Create SNS topic and provide valid ARN** |
| **Alarms not triggering** | **Wrong threshold values** | **Adjust thresholds based on function behavior** |
| **No alarm notifications** | **SNS topic not subscribed** | **Add email/SMS subscriptions to SNS topic** |
| **Alarm permission error** | **CloudWatch cannot publish to SNS** | **Verify SNS topic policy allows CloudWatch access** |

## 💡 Best Practices

### Prefix List Management
- **Create separate stacks** for each purpose (DynamoDB, S3, external APIs)
- **Use descriptive names** - `myapp-nprd-pl-dynamodb` not `myapp-nprd-pl-1`
- **Document prefix list IDs** - Keep a team-shared spreadsheet/wiki with prefix list mappings
- **Always use stack outputs** - Get IDs from CloudFormation console
- **Start small** - Begin with known CIDRs, expand as needed using MaxEntries buffer

### Database Connectivity
- **Prefer security group references** for managed databases (RDS, Aurora)
- **Use CIDR method** for self-managed or cross-account database access
- **Document database connection method** in deployment notes
- **Test connectivity** after deployment using VPC endpoints or test Lambda
- **Consider both methods** when database spans multiple security contexts

### S3 Access Control 
- **Use specific buckets for production** - Enhanced security for production workloads
- **Pattern-based for development** - Convenient for development environments
- **Document bucket requirements** - Clearly specify which buckets each function needs
- **Regular access reviews** - Periodically review and tighten S3 permissions
- **Test both access methods** - Verify permissions work as expected after deployment
- **Consider compliance requirements** - Use specific buckets when audit trails require exact resource access

### CloudWatch Alarms
- **Enable for production** - Always enable alarms for production workloads
- **Set environment-specific thresholds** - Different values for dev vs prod
- **Create SNS topics per environment** - Separate notification channels
- **Test alarm notifications** - Trigger test alarms to verify notifications work
- **Document response procedures** - Create runbooks for alarm responses
- **Monitor alarm costs** - Each alarm has a small monthly cost (~$0.10/month)
- **Review alarm history** - Regular review to tune thresholds and reduce false positives