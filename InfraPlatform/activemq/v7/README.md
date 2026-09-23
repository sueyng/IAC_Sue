# AMAZON MQ ACTIVEMQ SETUP (v6)

Amazon MQ ActiveMQ is a fully managed message broker service for Apache ActiveMQ. This template provisions a highly available ActiveMQ broker with flexible deployment options, including all necessary security and networking configurations.

## Resources Provisioned

This template provisions the following resources:

* **Amazon MQ Broker**: ActiveMQ broker in either SINGLE_INSTANCE or ACTIVE_STANDBY_MULTI_AZ configuration
* **Security Group**: Configures access to the broker with flexible CIDR configurations and enhanced security rules

## Key Features in v6

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
| DeploymentServer01 | *String* | IP address of the deployment server (e.g., 192.168.1.10/32) | Yes |
| InstanceType | *String* | ActiveMQ broker instance type (e.g., mq.m5.large) | Yes |
| MQPassword | *String* | Password for ActiveMQ | Yes |
| DeploymentMode | *String* | SINGLE_INSTANCE or ACTIVE_STANDBY_MULTI_AZ | Yes |
| EngineVersion | *String* | ActiveMQ engine version (e.g., 5.18.2) | Yes |
| **FirstMQDeployment** | *String* | **"true"** or **"false"** (default). Set to **"true"** for the first ActiveMQ deployment in the AWS account to create the AmazonMQ Log Resource Policy. Set to **"false"** for subsequent deployments. | **Yes** |
| EnableScheduler | *String* | Enable/disable ActiveMQ scheduler support (true/false) | Yes |
| VpcCidr1 | *String* | Primary VPC CIDR IP range (e.g., 10.0.1.0/24) | Yes |
| VpcCidr2 | *String* | Secondary VPC CIDR IP range (e.g., 10.0.2.0/24) | No |
| VpcCidr3 | *String* | Tertiary VPC CIDR IP range (e.g., 10.0.3.0/24) | No |
| VpcCidr4 | *String* | Quaternary VPC CIDR IP range (e.g., 10.0.4.0/24) | No |
| VpcCidr5 | *String* | Quinary VPC CIDR IP range (e.g., 10.0.5.0/24) | No |

## ⚠️ Important: FirstMQDeployment Parameter

**Critical Decision Required**: When deploying ActiveMQ, you must decide whether this is the **first** ActiveMQ deployment in your AWS account.

### When to set FirstMQDeployment=true:
- This is the **very first** ActiveMQ broker being deployed in the AWS account
- Creates the required `AmazonMQ-logs` CloudWatch resource policy
- **Only use this for ONE deployment per AWS account**

### When to set FirstMQDeployment=false (default):
- This is a **subsequent** ActiveMQ deployment in an account that already has ActiveMQ
- Skips creating the log resource policy (assumes it already exists)
- **Use this for ALL other deployments after the first one**

### Decision Matrix:
| Scenario | FirstMQDeployment Setting | Result |
|----------|---------------------------|---------|
| First MQ in account | `"true"` | ✅ Creates policy + MQ broker |
| Subsequent MQ in account | `"false"` | ✅ Creates MQ broker only |
| First MQ but set to false | `"false"` | ❌ Deployment may fail (no log policy) |
| Subsequent MQ but set to true | `"true"` | ❌ Deployment fails (policy conflict) |

💡 **Tip**: When in doubt, check existing log policies with: `aws logs describe-resource-policies`

## Deployment Instructions

### Prepare the parameters-activemq.json file

1. Copy the `parameters-activemq.json` template from the `env` directory to your project's IAC repository
2. Update the parameter values in `parameters-activemq.json` based on your environment requirements:
   - **Set `FirstMQDeployment` appropriately** (see decision matrix above)
   - Set `DeploymentMode` according to your high availability needs
   - Configure VPC and subnet IDs for your network
   - Set appropriate CIDR ranges for security group rules
   - Configure the instance type based on your performance requirements
   - Set the engine version as needed
   - Set `EnableScheduler` to "true" if you need scheduler support

### Deploy using Azure DevOps Pipeline

1. Run the CloudFormation Stack deployment using the Azure DevOps Pipeline
2. Monitor the stack creation process in the Azure DevOps Pipeline logs

### Post-Deployment Verification


1. Verify successful resource creation in the AWS Management Console
2. Check that the ActiveMQ broker is up and running
3. Validate that the security group rules are properly configured
4. Test connectivity to the broker from authorized CIDR ranges

## Logging Configuration and Troubleshooting

### Logging Setup
* The CloudFormation template enables AmazonMQ broker logging with:
   - `General: true`
   - `Audit: true`
* Log groups are automatically created in CloudWatch Logs, typically named:
   - `/aws/amazonmq/broker/<broker-name>/General`
   - `/aws/amazonmq/broker/<broker-name>/Audit`

### Troubleshooting Log Delivery
If log groups are created but remain empty:
1. Confirm the broker is running and healthy in the AWS Console.
2. Generate broker activity (connect a client, send messages).
3. Check for restrictive Service Control Policies (SCPs) or IAM policies that may block CloudWatch Logs actions (`logs:CreateLogGroup`, `logs:CreateLogStream`, `logs:PutLogEvents`).
4. Review the broker's monitoring tab for errors or warnings.
5. Wait a few minutes for log delivery, then refresh CloudWatch Logs.

### Troubleshooting Deployment Issues

**Error: "Resource policy already exists"**
- **Cause**: `FirstMQDeployment=true` but the `AmazonMQ-logs` policy already exists
- **Solution**: Change `FirstMQDeployment` to `"false"`

**Error: "MQ logging failed" or empty log groups**
- **Cause**: `FirstMQDeployment=false` but no log resource policy exists
- **Solutions**: 
  1. Set `FirstMQDeployment=true` and redeploy, OR
  2. Create the policy manually:
     ```bash
     aws logs put-resource-policy \
       --policy-name AmazonMQ-logs \
       --policy-document '{
         "Version": "2012-10-17",
         "Statement": [
           {
             "Effect": "Allow",
             "Principal": { "Service": "mq.amazonaws.com" },
             "Action": [
               "logs:CreateLogStream",
               "logs:PutLogEvents"
             ],
             "Resource": "arn:aws:logs:*:*:log-group:/aws/amazonmq/*"
           }
         ]
       }'
     ```

**Verify existing log policies**:
```bash
aws logs describe-resource-policies --region your-region
```

## Troubleshooting

* If deployment fails due to subnet issues, check that the provided subnets exist and are in the correct VPC
* For permission errors, verify that the deployment role has the necessary IAM permissions
* For connectivity issues, check security group rules and network ACLs

## Version Notes

This is version 6 of the ActiveMQ template, which enhances the v5 version with:
* Flexible VPC CIDR configuration
* Enhanced security group rules
* ActiveMQ scheduler support via the `EnableScheduler` parameter
* Improved production readiness features

For a detailed comparison with previous versions, refer to the `release-notes.md` file.
