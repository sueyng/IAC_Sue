# Deployment Role - Release Notes

## Version 1.0.0 - Initial Release

**Release Date:** 2026-08-05

### Overview
Comprehensive CloudFormation template for IAM deployment roles used by EC2 instances to deploy infrastructure. The template provides one consolidated role per account (PROD/NPRD) with extensive AWS service permissions and fixed, environment-specific EC2 instance trust relationships.

### Features

#### 1. Single Consolidated Template
- **File:** `v1/cf-deployment-role.yaml`
- **Single Stack Deployment:** Role and policy created together in one CloudFormation stack
- **No Dependencies:** Standalone template with no external dependencies

#### 2. Environment-Specific Trust Relationships
- **Automatic Selection:** Trust principals selected based on `EnvName` parameter
- **Fixed EC2 Instances:** Hardcoded instance ARNs per environment (no parameterization required)
  
  **PROD Environment (028485325974)**
  - 4 EC2 instances from HIP-ec2-role
  - i-0120280f586ce0dba, i-0ea761be26edc86d2, i-07f913f3f02a78d23, i-0cb778bccea61a275

  **NPRD Environment (899035119154)**
  - 3 EC2 instances from HIP-ec2-role
  - 1 EC2 instance from AmazonSSMRoleForInstancesMDCSetup
  - i-05637073d644167ef, i-05a891f27a7134874, i-0d568c38e8f0e99fb, i-0721167e37d3ce455

#### 3. Comprehensive AWS Service Coverage
- **34+ AWS Services** with wildcard permissions (service:*)
- **Infrastructure Services:**
  - cloudformation, ec2, ecs, eks, rds, s3, lambda, iam
- **Deployment Services:**
  - codedeploy, ecr, batch, glue, states
- **Networking Services:**
  - elasticloadbalancing, apigateway, route53, cloudfront
- **Data Services:**
  - dynamodb (via s3 nosqldb), sqs, sns, mq, events
- **Security & Secrets:**
  - secretsmanager, kms, ssm, sso, identitystore, sso-oidc, guardduty
- **Observability:**
  - cloudwatch, logs, grafana, aps
- **Additional Services:**
  - elasticache, scheduler, application-autoscaling, s3-object-lambda

#### 4. Environment-Aware Policies
- **DeletionPolicy:**
  - PROD: Retain (role preserved on stack deletion)
  - NPRD: Delete (role removed on stack deletion)
- **UpdateReplacePolicy:**
  - Conditional based on environment (Retain for PROD, Delete for NPRD)
- **Session Duration:** 3600 seconds (1 hour) for all environments

#### 5. Comprehensive Tagging
All resources include tags for tracking and organization:
- **IaCVersion:** InfraPlatform-deploymentrole-v1
- **Environment:** EnvName value (nprd or prod)
- **Application:** AppShortName value

#### 6. Parameter-Driven Naming
- **Role Name Pattern:** `{AppShortName}-{EnvName}-depl-role`
- **Policy Name Pattern:** `{AppShortName}-{EnvName}-depl-policy`
- **Example (AppShortName=myapp, EnvName=nprd):**
  - Role: `myapp-nprd-depl-role`
  - Policy: `myapp-nprd-depl-policy`

#### 7. Parameter File Structure
- **Format:** YAML for easy editing
- **Location:** `v1/env/parameters-cf-deployment-role.yaml`
- **Documentation:** Quick start guide with detailed parameter reference
- **Validation:** Parameter key/value structure with constraints

### Technical Specifications

#### Template Metadata
- **Format:** YAML (AWS CloudFormation 2010-09-09)
- **Size:** ~600 lines
- **Type:** IaC Template for IAM resource creation

#### Parameters
| Parameter | Type | Values | Default |
|-----------|------|--------|---------|
| AppShortName | String | Any alphanumeric | app |
| EnvName | String | nprd, prod | nprd |

#### Resources Created
1. **AWS::IAM::Role (DeploymentRole)**
   - Configurable role name
   - Environment-specific deletion policy
   - Conditional trust relationships
   - Tagged with environment and application info

2. **AWS::IAM::Policy (DeploymentPolicy)**
   - Inline policy (not standalone managed policy)
   - 35 Sid-based statement groups
   - Service-level wildcard permissions
   - Attached directly to role

### Deployment Options

#### Method 1: With Parameter File
```bash
aws cloudformation create-stack \
  --stack-name app-nprd-depl-role-stack \
  --template-body file://v1/cf-deployment-role.yaml \
  --parameters file://v1/env/parameters-cf-deployment-role.yaml \
  --capabilities CAPABILITY_NAMED_IAM
```

#### Method 2: Inline Parameters
```bash
aws cloudformation create-stack \
  --stack-name app-nprd-depl-role-stack \
  --template-body file://v1/cf-deployment-role.yaml \
  --parameters \
    ParameterKey=AppShortName,ParameterValue=myapp \
    ParameterKey=EnvName,ParameterValue=nprd \
  --capabilities CAPABILITY_NAMED_IAM
```

### Required Capabilities
- `CAPABILITY_NAMED_IAM` - Required for creating IAM resources with specific names

### Permissions Required (for deployment)
- `iam:CreateRole`
- `iam:PutRolePolicy`
- `iam:TagRole`
- `cloudformation:CreateStack`

### Validation Checklist
- ✅ All 34+ AWS services included with wildcard permissions
- ✅ PROD and NPRD EC2 instance ARNs verified
- ✅ Environment-specific trust relationships implemented
- ✅ Parameter file format matches workspace standards
- ✅ Deletion policies correctly configured per environment
- ✅ All CloudFormation syntax validated
- ✅ Resource naming convention implemented

### Security Considerations

#### Wildcard Permissions
The template uses `service:*` format for permissions. This grants all actions within each AWS service. For production use, consider:
- Restricting to specific actions if more granular control needed
- Implementing service control policies (SCPs) for additional boundaries
- Regular audits of actual service usage vs. granted permissions

#### Trust Relationship Security
- Fixed EC2 instance ARNs (no parameter-based flexibility)
- Environment isolation (separate PROD/NPRD trust relationships)
- Assumed role ARNs used (requires proper EC2 instance role configuration)

#### Session Duration
- 1 hour (3600 seconds) maximum session time
- Balances convenience with security

### Known Limitations

1. **Fixed Instance ARNs:** EC2 instance trust relationships are hardcoded and cannot be easily modified without template update
2. **Wildcard Permissions:** All services receive full wildcard permissions
3. **Inline Policy:** Policy is inline (not standalone managed policy)

### File Manifest

```
deploymentrole/
├── release-notes.md                     # This file (version history)
├── v1/
│   ├── cf-deployment-role.yaml          # Main CloudFormation template
│   ├── env/
│   │   └── parameters-cf-deployment-role.yaml  # Parameter configuration file
│   └── README.md                        # Detailed documentation
```

### Version Information

- **Current Version:** 1.0.0
- **CloudFormation Version:** 2010-09-09
- **Region:** ap-southeast-1 (Singapore)
- **AWS Account Types:** PROD (028485325974) and NPRD (899035119154)
- **Created:** 2026-08-05
- **Status:** Production Ready

---

**Document Version:** 1.0.0  
**Last Updated:** 2026-08-05  
**Maintained By:** Infrastructure Platform Team

## Deployment Approaches

### Single-Stack Approach (Recommended)
Deploy `cf-deployment-role.yaml` for a complete, self-contained deployment role with all permissions.

**Advantages**:
- Single stack to manage
- All related resources in one place
- Simpler for most use cases

### Modular Approach
Deploy `cf-deployment-role.yaml` for role, then `cf-deployment-policy.yaml` for policy.

**Advantages**:
- Separate policy lifecycle
- Attach to multiple roles
- Policy version management
- Better for complex environments

## Permissions Matrix

### CloudFormation Permissions (14 actions)
`CreateStack`, `UpdateStack`, `DeleteStack`, `DescribeStacks`, `GetTemplate`, `GetTemplateSummary`, `ListStacks`, `CreateChangeSet`, `DescribeChangeSet`, `ExecuteChangeSet`, `DeleteChangeSet`, `ValidateTemplate`

### S3 Permissions (7 actions)
`GetObject`, `GetObjectVersion`, `PutObject`, `DeleteObject`, `ListBucket`, `GetBucketVersioning`, `GetBucketLocation`

### ECR Permissions (9 actions)
`GetAuthorizationToken`, `BatchGetImage`, `GetDownloadUrlForLayer`, `PutImage`, `InitiateLayerUpload`, `UploadLayerPart`, `CompleteLayerUpload`, `DescribeImages`, `ListImages`

### ECS Permissions (10 actions)
`UpdateService`, `DescribeServices`, `DescribeTaskDefinition`, `ListTasks`, `RegisterTaskDefinition`, `StartTask`, `StopTask`, `CreateService`, `DeleteService`, `UpdateTaskSet`

### Lambda Permissions (15 actions)
`CreateFunction`, `DeleteFunction`, `GetFunction`, `GetFunctionConfiguration`, `UpdateFunctionCode`, `UpdateFunctionConfiguration`, `AddPermission`, `RemovePermission`, `PublishVersion`, `CreateAlias`, `UpdateAlias`

### IAM Permissions (20 actions)
`CreateRole`, `DeleteRole`, `GetRole`, `PassRole`, `AttachRolePolicy`, `DetachRolePolicy`, `CreatePolicy`, `DeletePolicy`, `PutRolePolicy`, `DeleteRolePolicy`, `TagRole`, `UntagRole`

### RDS Permissions (11 actions)
`DescribeDBInstances`, `DescribeDBClusters`, `ModifyDBInstance`, `ModifyDBCluster`, `StartDBInstance`, `StopDBInstance`, `RebootDBInstance`, `CreateDBSnapshot`, `DescribeDBSnapshots`, `DescribeDBParameterGroups`, `ModifyDBParameterGroup`

### CodeDeploy Permissions (7 actions)
`CreateDeployment`, `GetDeployment`, `GetDeploymentConfig`, `GetApplication`, `GetApplicationRevision`, `ListDeployments`, `ListApplications`

### EC2 Permissions (13 actions)
`DescribeInstances`, `DescribeInstanceStatus`, `DescribeTags`, `DescribeSecurityGroups`, `DescribeNetworkInterfaces`, `StartInstances`, `StopInstances`, `RebootInstances`, `DescribeImages`, `DescribeSnapshots`, `CreateSnapshot`, `CreateSecurityGroup`, `AuthorizeSecurityGroupIngress`

### Additional Services
- **Secrets Manager**: 8 actions
- **CloudWatch/Logs**: 7 actions
- **ElastiCache**: 6 actions
- **SNS**: 5 actions
- **SQS**: 8 actions
- **CloudFront**: 7 actions

## Version Details

- **Version**: v1
- **Release Date**: 2026-08-05
- **Status**: Initial Release
- **IaC Framework**: AWS CloudFormation (2010-09-09)
- **Compatibility**: AWS accounts with IAM permissions

## Outputs Provided

### cf-deployment-role.yaml Outputs
- `DeploymentRoleArn`: Full ARN of the created role
- `DeploymentRoleName`: Name of the created role
- `DeploymentRoleId`: AWS-generated role ID

### cf-deployment-policy.yaml Outputs
- `ManagedPolicyArn`: ARN of the managed policy
- `ManagedPolicyName`: Name of the managed policy

## Stack Naming Conventions

**Role Stack Example**:
```
app-nprd-deployment-role-stack
```

**Policy Stack Example**:
```
app-nprd-deployment-policy-stack
```

## Next Steps

### 1. Customize for Your Environment
- Update `AppShortName` and `EnvName` parameters
- Adjust `AssumeRolePrincipal` based on your CI/CD service
- Review and restrict permissions as needed

### 2. Deploy Stack
```bash
aws cloudformation create-stack \
  --stack-name app-nprd-deployment-role-stack \
  --template-body file://cf-deployment-role.yaml \
  --parameters ParameterKey=AppShortName,ParameterValue=myapp \
               ParameterKey=EnvName,ParameterValue=nprd \
  --capabilities CAPABILITY_NAMED_IAM
```

### 3. Retrieve Role Information
```bash
aws cloudformation describe-stacks --stack-name app-nprd-deployment-role-stack
```

### 4. Integrate with CI/CD
- Use the role ARN in CodeBuild project configuration
- Reference role name in deployment specifications
- Ensure CI/CD service has permission to assume the role

## Known Limitations

1. **Broad Resource Scope**: Permissions use wildcard `*` for resource ARNs. For production, consider restricting to specific resources.

2. **Cross-Account**: Current template assumes single-account deployment. For cross-account, additional trust policies needed.

3. **Service Control Policies (SCPs)**: Stack respects SCPs but does not verify them. Ensure SCPs permit all actions.

## Recommendations

### Security Best Practices
1. **Production**: Review permissions and restrict resource ARNs
2. **Audit**: Enable CloudTrail logging for all deployment actions
3. **Approval**: Implement manual approval gates for production deployments
4. **Monitoring**: Set up alerts for deployment role usage

### Operational Best Practices
1. Use separate roles per environment
2. Document custom parameter values
3. Version track stack parameter files
4. Periodically audit role permissions
5. Use Stack Sets for multi-region deployments

## Migration Guide

### From Manual IAM Setup
1. Backup existing role policies
2. Deploy new stack with identical parameters
3. Update CI/CD to use new role ARN
4. Validate deployments work correctly
5. Archive old role (don't delete immediately)

### Adding to Existing Stacks
1. Deploy policy template with existing role name
2. Verify policy attachment
3. Test permissions with test deployment
4. Update documentation

## Troubleshooting Checklist

- [ ] IAM permissions to create roles/policies
- [ ] Stack name is unique in region
- [ ] Parameters are valid and environment names match
- [ ] CloudFormation service has assumed role trust
- [ ] No naming conflicts with existing roles
- [ ] Account limits not exceeded (roles, policies)

## Support & Documentation

- Full parameter reference in README.md
- Deployment examples in README.md
- Permission matrix in release notes
- Best practices in README.md

## Future Enhancements (Potential v2)

- [ ] Cross-account assume role support
- [ ] Restricted resource ARNs per environment
- [ ] Service Control Policy (SCP) guidance
- [ ] Cost allocation tags support
- [ ] Compliance-specific permission sets
- [ ] Automated permission audit reports
- [ ] Multi-region Stack Set support

## Feedback & Issues

Please refer to project guidelines for:
- Template improvements
- New service support requests
- Bug reports
- Documentation updates
