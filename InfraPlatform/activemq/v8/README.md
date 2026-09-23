# AMAZON MQ ACTIVEMQ SETUP (v8)

Amazon MQ ActiveMQ is a fully managed message broker service for Apache ActiveMQ. This template provisions a highly available ActiveMQ broker with flexible deployment options, including all necessary security, networking, and encryption configurations.

## What's New in v8

* **KMS Encryption at Rest**: Broker data is encrypted using a customer-managed KMS key (`EncryptionOptions` with `UseAwsOwnedKey: false`)
* **KMS Key with Auto-Rotation**: Dedicated KMS key with automatic annual rotation enabled
* **KMS Key Alias**: Key alias for easy identification (`alias/{AppShortName}-{EnvName}-activemq`)
* **Checkmarx Compliance**: Addresses Checkmarx high severity finding `AmazonMQ Broker Encryption Disabled`

> **Important:** Encryption is an **immutable day-one setting** for Amazon MQ. It cannot be enabled on existing brokers — not via CloudFormation, Console, or API. Existing unencrypted brokers must be recreated using this template with a migration plan. See [Migration from v7](#migration-from-v7) below.

## Resources Provisioned

| Resource | Type | Description |
|----------|------|-------------|
| ActiveMQKMSKey | AWS::KMS::Key | Customer-managed KMS key for broker encryption |
| ActiveMQKMSKeyAlias | AWS::KMS::Alias | Key alias: `alias/{app}-{env}-activemq` |
| ActiveMQSecurityGroup | AWS::EC2::SecurityGroup | Broker security group with ingress/egress rules |
| BasicBroker | AWS::AmazonMQ::Broker | ActiveMQ broker with KMS encryption enabled |
| AmazonMQLogResourcePolicy | AWS::Logs::ResourcePolicy | CloudWatch Logs policy (conditional, first deployment only) |
| ActiveMQConfiguration | AWS::AmazonMQ::Configuration | Custom broker config with scheduler support (conditional) |

## Key Features

* **KMS Encryption at Rest**: All broker data encrypted with customer-managed KMS key (new in v8)
* **Deployment Modes**: Support for both `SINGLE_INSTANCE` and `ACTIVE_STANDBY_MULTI_AZ` deployments
* **Flexible Networking**: Configurable VPC CIDR ranges for granular network access control
* **Scheduler Support**: Option to enable ActiveMQ scheduler functionality using the `EnableScheduler` parameter
* **Enhanced Security**: Improved security group rules with conditional logic for different network topologies
* **Production-Ready**: DeletionPolicy and UpdateReplacePolicy for production environments

## Parameters and Valid Values

| ParameterKey | ValueType | Description | Required |
|-------------|-----------|-------------|----------|
| AppShortName | *String* | Application short name identifier | Yes |
| EnvName | *String* | Environment name (nprd, nprd-dev, nprd-sit, prod, etc.) | Yes |
| VpcId | *AWS::EC2::VPC::Id* | VPC ID for the deployment | Yes |
| VPCSubnetCidrAppAZ1 | *String* | VPC Subnet CIDR for App AZ1 (e.g., 10.0.1.0/24) | Yes |
| VPCSubnetCidrAppAZ2 | *String* | VPC Subnet CIDR for App AZ2 (e.g., 10.0.2.0/24) | Yes |
| VPCSubnetCidrAppAZ3 | *String* | VPC Subnet CIDR for App AZ3 (e.g., 10.0.3.0/24) | No |
| VPCSubnetIdappAZ1 | *String* | VPC Subnet ID for App AZ1 | Yes |
| VPCSubnetIdappAZ2 | *String* | VPC Subnet ID for App AZ2 | Yes |
| DeploymentServer01 | *String* | IP address of the deployment server (e.g., 10.53.29.200/32) | Yes |
| InstanceType | *String* | ActiveMQ broker instance type (e.g., mq.t3.micro, mq.m5.large) | Yes |
| MQPassword | *String* | Password for ActiveMQ (min 12 chars, NoEcho) | Yes |
| DeploymentMode | *String* | SINGLE_INSTANCE or ACTIVE_STANDBY_MULTI_AZ | Yes |
| EngineVersion | *String* | ActiveMQ engine version (e.g., 5.18) | Yes |
| FirstMQDeployment | *String* | "true" or "false" (default). Set to "true" for the first ActiveMQ deployment in the AWS account | Yes |
| EnableScheduler | *String* | Enable/disable ActiveMQ scheduler support (true/false) | Yes |
| VpcCidr1 | *String* | Primary VPC CIDR IP range | Yes |
| VpcCidr2 | *String* | Secondary VPC CIDR IP range | No |
| VpcCidr3 | *String* | Tertiary VPC CIDR IP range | No |
| VpcCidr4 | *String* | Quaternary VPC CIDR IP range | No |
| VpcCidr5 | *String* | Quinary VPC CIDR IP range | No |
| HCCVpceCidr | *String* | HCC VPC Endpoint Subnet CIDR | No |

> **Note:** No new parameters introduced in v8. The KMS key is created within the template — existing v7 parameter files are fully compatible.

## Encryption Details

### KMS Key Configuration
- **Key Type**: Symmetric, customer-managed
- **Key Rotation**: Enabled (automatic annual rotation)
- **Key Policy**:
  - Root account access (AWS recommended baseline)
  - Amazon MQ service access (`mq.amazonaws.com`) for Decrypt, GenerateDataKey, DescribeKey operations
- **Deletion Policy**: Retain for production, Delete for non-production
- **Key Alias**: `alias/{AppShortName}-{EnvName}-activemq`

### Verifying Encryption
Encryption is **not visible** in the Amazon MQ Console. Verify via CLI:
```bash
aws mq describe-broker --broker-id <broker-id> --region ap-southeast-1 \
  --query '{BrokerName:BrokerName,EncryptionOptions:EncryptionOptions}'
```

Expected output for encrypted broker:
```json
{
    "BrokerName": "myapp-nprd-dev-ActiveMQ",
    "EncryptionOptions": {
        "KmsKeyId": "arn:aws:kms:ap-southeast-1:123456789012:key/xxxx-xxxx",
        "UseAwsOwnedKey": false
    }
}
```

## ⚠️ Important: FirstMQDeployment Parameter

**Critical Decision Required**: When deploying ActiveMQ, you must decide whether this is the **first** ActiveMQ deployment in your AWS account.

| Scenario | FirstMQDeployment Setting | Result |
|----------|---------------------------|---------|
| First MQ in account | `"true"` | Creates policy + MQ broker |
| Subsequent MQ in account | `"false"` | Creates MQ broker only |
| First MQ but set to false | `"false"` | Deployment may fail (no log policy) |
| Subsequent MQ but set to true | `"true"` | Deployment fails (policy conflict) |

**Tip**: Check existing log policies with: `aws logs describe-resource-policies`

## Deployment Instructions

### Prepare the parameter file

1. Copy `parameters-activemq.json` or `parameters-activemq.yaml` from the `env` directory
2. Update parameter values for your environment:
   - Set `FirstMQDeployment` appropriately (see decision matrix above)
   - Set `DeploymentMode` according to HA requirements
   - Configure VPC and subnet details
   - Set `InstanceType` (note: `mq.t2.micro` is deprecated, use `mq.t3.micro` or higher)
   - Set `DeploymentServer01` — this is required, empty value will fail deployment

### Deploy using Azure DevOps Pipeline

1. Run the CloudFormation Stack deployment
2. Monitor stack creation in pipeline logs

### Post-Deployment Verification

1. Verify resources in AWS Management Console
2. Confirm broker is running
3. **Verify encryption** via CLI (see [Verifying Encryption](#verifying-encryption))
4. Validate security group rules
5. Test connectivity from authorized CIDR ranges

## Migration from v7

Amazon MQ encryption is an **immutable day-one setting**. It cannot be added to existing brokers.

### For New Projects
Use v8 template directly — encryption enabled from day one. No additional steps needed.

### For Existing Projects (v7 or earlier)
Encryption cannot be enabled on existing brokers. Migration requires:

1. **Deploy new broker** using v8 template (new stack name)
2. **Migrate client connections** to the new broker endpoint
3. **Drain messages** from old broker
4. **Decommission old broker** (delete old stack)

> **Note:** This is a breaking change requiring planned downtime and client reconfiguration. Coordinate with application teams before migration.

## Logging Configuration and Troubleshooting

### Logging Setup
* Broker logging is enabled with `General: true` and `Audit: true`
* Log groups in CloudWatch Logs:
   - `/aws/amazonmq/broker/<broker-name>/General`
   - `/aws/amazonmq/broker/<broker-name>/Audit`

### Troubleshooting

**Error: "Resource policy already exists"**
- **Cause**: `FirstMQDeployment=true` but the `AmazonMQ-logs` policy already exists
- **Solution**: Change `FirstMQDeployment` to `"false"`

**Error: "MQ logging failed" or empty log groups**
- **Cause**: `FirstMQDeployment=false` but no log resource policy exists
- **Solution**: Set `FirstMQDeployment=true` and redeploy, or create policy manually:
  ```bash
  aws logs put-resource-policy \
    --policy-name AmazonMQ-logs \
    --policy-document '{
      "Version": "2012-10-17",
      "Statement": [{
        "Effect": "Allow",
        "Principal": { "Service": "mq.amazonaws.com" },
        "Action": ["logs:CreateLogStream", "logs:PutLogEvents"],
        "Resource": "arn:aws:logs:*:*:log-group:/aws/amazonmq/*"
      }]
    }'
  ```

**Error: "CIDR block is malformed"**
- **Cause**: Required CIDR parameter (e.g., `DeploymentServer01`) is empty
- **Solution**: Ensure all required parameters have valid values

**Error: "Broker engine type does not support host instance type"**
- **Cause**: Instance type `mq.t2.micro` has been deprecated
- **Solution**: Use `mq.t3.micro` or higher

## Version Notes

v8 enhances v7 with:
* KMS encryption at rest (customer-managed key)
* Addresses Checkmarx `AmazonMQ Broker Encryption Disabled` finding
* All v7 features retained (flexible VPC CIDRs, scheduler support, production readiness)
* No new parameters — backward compatible with v7 parameter files

For detailed version history, refer to `release-notes.md`.
