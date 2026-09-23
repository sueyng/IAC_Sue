# Deployment Role CloudFormation Template

## Overview

This directory contains a CloudFormation template for creating IAM deployment roles used by EC2 instances to deploy infrastructure using AWS services. The role is designed for infrastructure-as-code (IaC) deployments across PROD and NPRD environments.

## Template

### `cf-deployment-role.yaml`
**Single consolidated template for IAM Deployment Role with integrated policies**

This template creates:
- **IAM Deployment Role** with environment-specific trust relationships
  - PROD: Trusts 4 EC2 instances from account 028485325974 (HIP-ec2-role)
  - NPRD: Trusts 4 EC2 instances from account 899035119154 (HIP-ec2-role + AmazonSSMRoleForInstancesMDCSetup)
- **Inline IAM Policy** with comprehensive permissions across 34+ AWS services
  - All permissions use wildcard format (service:*)
  - Covers infrastructure deployment, database, networking, and observability services

**Key Features:**
- One role per account (NPRD or PROD)
- Fixed, hardcoded EC2 instance trust relationships per environment
- Automatic deletion policy based on environment (Retain for PROD, Delete for NPRD)
- Session duration: 3600 seconds (1 hour)
- Comprehensive resource tagging

## Parameters

| Parameter | Type | Allowed Values | Default | Description |
|-----------|------|---|---------|-------------|
| `AppShortName` | String | Any | app | Application short name for resource naming |
| `EnvName` | String | nprd, prod | nprd | Environment designation (one role per account) |

### Environment-Specific Behavior

**Production (prod)**
- **Account:** 028485325974 (HIP AWS Account)
- **Trusted EC2 Instances:** 4 instances from HIP-ec2-role
  - i-0120280f586ce0dba
  - i-0ea761be26edc86d2
  - i-07f913f3f02a78d23
  - i-0cb778bccea61a275
- **DeletionPolicy:** Retain (resources preserved on stack deletion)
- **Termination Protection:** Enabled

**Non-Production (nprd)**
- **Account:** 899035119154 (NPRD AWS Account)
- **Trusted EC2 Instances:** 4 instances
  - 3 from HIP-ec2-role: i-05637073d644167ef, i-0d568c38e8f0e99fb, i-0721167e37d3ce455
  - 1 from AmazonSSMRoleForInstancesMDCSetup: i-05a891f27a7134874
- **DeletionPolicy:** Delete (resources removed on stack deletion)
- **Termination Protection:** Disabled

## Resource Naming Convention

Generated resource names follow the pattern: `{AppShortName}-{EnvName}-{resource-type}`

**Example (AppShortName=myapp, EnvName=nprd):**
- **Role Name:** `myapp-nprd-depl-role`
- **Policy Name:** `myapp-nprd-depl-policy`

## Included AWS Service Permissions

The role includes wildcard permissions (`service:*`) for 34+ AWS services:

| Service | Purpose |
|---------|---------|
| cloudformation | Infrastructure stack management |
| s3 | Artifact and state storage |
| ecr | Container image management |
| ecs | Container orchestration |
| lambda | Serverless function deployment |
| iam | Role and policy management |
| rds | Database provisioning and management |
| codedeploy | Application deployment |
| ec2 | Compute instance management |
| secretsmanager | Secrets management |
| logs, cloudwatch | Monitoring and logging |
| elasticache | In-memory cache deployment |
| sns, sqs | Message services |
| cloudfront | Content delivery |
| sso, identitystore, sso-oidc | Identity management |
| kms, ssm | Key and parameter management |
| eks | Kubernetes cluster management |
| glue, states, events | Data and workflow services |
| grafana, aps | Observability |
| mq | Message queue |
| elasticloadbalancing | Load balancer management |
| apigateway | API management |
| route53 | DNS management |
| batch, scheduler | Job scheduling |
| application-autoscaling | Auto-scaling |
| guardduty | Security threat detection |
| s3-object-lambda | S3 object processing |

## Deployment Instructions

### Prerequisites
- AWS CLI configured with appropriate credentials
- Permissions to create CloudFormation stacks and IAM roles
- Correct AWS account (PROD or NPRD)

### NPRD Deployment

```bash
# Using parameter file
aws cloudformation create-stack \
  --stack-name app-nprd-depl-role-stack \
  --template-body file://cf-deployment-role.yaml \
  --parameters file://env/parameters-cf-deployment-role.yaml \
  --capabilities CAPABILITY_NAMED_IAM \
  --region ap-southeast-1

# Or inline parameters
aws cloudformation create-stack \
  --stack-name app-nprd-depl-role-stack \
  --template-body file://cf-deployment-role.yaml \
  --parameters \
    ParameterKey=AppShortName,ParameterValue=myapp \
    ParameterKey=EnvName,ParameterValue=nprd \
  --capabilities CAPABILITY_NAMED_IAM \
  --region ap-southeast-1

# Wait for completion
aws cloudformation wait stack-create-complete \
  --stack-name app-nprd-depl-role-stack \
  --region ap-southeast-1
```

### PROD Deployment

```bash
# Update parameter file: change EnvName from nprd to prod

aws cloudformation create-stack \
  --stack-name app-prod-depl-role-stack \
  --template-body file://cf-deployment-role.yaml \
  --parameters file://env/parameters-cf-deployment-role.yaml \
  --capabilities CAPABILITY_NAMED_IAM \
  --region ap-southeast-1
```

### Stack Updates

```bash
# Update existing stack (e.g., to change AppShortName)
aws cloudformation update-stack \
  --stack-name app-nprd-depl-role-stack \
  --template-body file://cf-deployment-role.yaml \
  --parameters file://env/parameters-cf-deployment-role.yaml \
  --capabilities CAPABILITY_NAMED_IAM \
  --region ap-southeast-1
```

### Verify Deployment

```bash
# Check stack status
aws cloudformation describe-stacks \
  --stack-name app-nprd-depl-role-stack \
  --region ap-southeast-1

# List stack resources
aws cloudformation describe-stack-resources \
  --stack-name app-nprd-depl-role-stack \
  --region ap-southeast-1

# Get role details
aws iam get-role --role-name app-nprd-depl-role

# Get role trust policy
aws iam get-role --role-name app-nprd-depl-role \
  --query 'Role.AssumeRolePolicyDocument' \
  --output json | jq .
```

## Parameter Configuration

### Quick Start

1. **Edit parameter file:** `env/parameters-cf-deployment-role.yaml`
2. **Set AppShortName:** Your application identifier (e.g., myapp)
3. **Set EnvName:** nprd or prod (based on target account)
4. **Deploy:** Use deployment commands above

### Parameter File Format

```yaml
# <<< PARAMETERS_START >>>
AppShortName: "<edit_here>"  # 📝 Application identifier
EnvName: "<edit_here>"       # 📝 nprd | prod
# <<< PARAMETERS_END >>>
```

## Troubleshooting

### Issue: "User is not authorized to perform: iam:CreateRole"
**Cause:** Insufficient IAM permissions
**Solution:** Ensure your AWS user/role has `iam:CreateRole`, `iam:PutRolePolicy`, and `iam:TagRole` permissions

### Issue: "CAPABILITY_NAMED_IAM is required for this operation"
**Cause:** Missing CloudFormation capability flag
**Solution:** Add `--capabilities CAPABILITY_NAMED_IAM` to aws cloudformation command

### Issue: Role already exists
**Cause:** Attempting to create stack with same name
**Solution:** Use different stack name or delete existing stack first

### Issue: Stack creation failed with trust relationship error
**Cause:** EC2 instance ARNs don't match environment
**Solution:** Verify EnvName parameter is correct (nprd or prod) before deployment

## Related Files

- `cf-deployment-role.yaml` - CloudFormation template
- `env/parameters-cf-deployment-role.yaml` - Parameter configuration file
- `README.md` - This documentation
- `release-notes.md` - Version history and features

### Secrets Manager
- Secret retrieval
- Secret creation/update/delete
- Tagging

### CloudWatch & Logs
- Log group and stream management
- Metric alarms
- Log data retrieval

### ElastiCache (In-Memory Cache)
- Cluster and replication group management
- Parameter group modifications

### SNS & SQS (Messaging)
- Topic and queue management
- Message publishing/sending

### CloudFront (CDN)
- Distribution management
- Cache invalidation

## Output Values

After stack creation, you can retrieve the following values:

```bash
# Get the role ARN
aws cloudformation describe-stacks \
  --stack-name app-nprd-deployment-role-stack \
  --query 'Stacks[0].Outputs[?OutputKey==`DeploymentRoleArn`].OutputValue' \
  --output text

# Get the role name
aws cloudformation describe-stacks \
  --stack-name app-nprd-deployment-role-stack \
  --query 'Stacks[0].Outputs[?OutputKey==`DeploymentRoleName`].OutputValue' \
  --output text

# Get the role ID
aws cloudformation describe-stacks \
  --stack-name app-nprd-deployment-role-stack \
  --query 'Stacks[0].Outputs[?OutputKey==`DeploymentRoleId`].OutputValue' \
  --output text
```

## Environment-Specific Settings

The templates automatically adjust for environment:

- **Production Environments** (prod, prod-a, prod-b, prod-c):
  - DeletionPolicy: Retain
  - UpdateReplacePolicy: Retain
  - Prevents accidental deletion

- **Non-Production Environments** (nprd, dev, stg, sit, uat):
  - DeletionPolicy: Delete
  - UpdateReplacePolicy: Delete
  - Allows easier cleanup

## Security Considerations

1. **Least Privilege**: The policy includes broad permissions. Consider restricting resource ARNs based on your specific needs.

2. **Production Access**: For production deployments, consider:
   - Using separate roles per environment
   - Implementing additional approval workflows
   - Enabling CloudTrail logging
   - Using session policies with temporary credentials

3. **Cross-Account Deployments**: If you need cross-account deployments:
   - Create the role in the target account
   - Configure trust relationships appropriately
   - Document the cross-account access patterns

## Version History

### v1 (Current)
- Initial release
- Support for CodeBuild, CodeDeploy, CloudFormation
- Comprehensive AWS service permissions
- Environment-based deletion policies
- Modular and monolithic template options

## Troubleshooting

### Stack Creation Fails
```bash
# Check stack events
aws cloudformation describe-stack-events \
  --stack-name app-nprd-deployment-role-stack

# Validate template
aws cloudformation validate-template \
  --template-body file://cf-deployment-role.yaml
```

### Role Not Found After Creation
```bash
# Verify role exists
aws iam get-role --role-name myapp-nprd-deployment-role
```

### Missing Permissions
Review the "Included AWS Service Permissions" section and verify the policy includes all required actions for your deployment pipeline.

## Related Resources

- [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [CloudFormation User Guide](https://docs.aws.amazon.com/cloudformation/latest/userguide/)
- [CodeBuild User Guide](https://docs.aws.amazon.com/codebuild/latest/userguide/)
- [CodeDeploy User Guide](https://docs.aws.amazon.com/codedeploy/latest/userguide/)

## Support

For issues or questions:
1. Review the CloudFormation events in AWS Console
2. Check CloudTrail logs for detailed error messages
3. Verify parameter values and stack names
4. Ensure IAM permissions to create roles and policies
