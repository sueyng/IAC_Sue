### AMAZON MQ ACTIVEMQ SETUP

Amazon MQ ActiveMQ is a fully managed message broker service for Apache ActiveMQ, This template provisions a highly available ActiveMQ broker across multiple AZs, including all necessary security and networking configurations.

This template provisions the following resources:

* Amazon MQ Broker: ActiveMQ broker in multi-AZ configuration.
* Security Group: Configures access to the broker and allows traffic from specified subnets.

Provisioning of this template is straightforward. See this instruction.

### Parameters and Its Valid Values:

|ParameterKey  | ValueType | Allowed Values  | 
|---|---|---|
|AppShortName  |   <i>String</i>               |   e.g my-application  |
|EnvName     |   <i>String</i>               |  nprd, nprd-dev, nprd-sit1, nprd-sit2, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b, prod, prod-a, prod-b |
|VpcId           | <i>AWS::EC2::VPC::Id</i>  | e.g vpc-120324                |
|VPCSubnetCidrAppAZ1 |  <i>String</i>   | e.g., 10.0.1.0/24   |
|VPCSubnetCidrAppAZ2 |  <i>String</i>   | e.g., 10.0.2.0/24   |
|VPCSubnetCidrAppAZ3 |  <i>String</i>   | e.g., 10.0.3.0/24   |
|VPCSubnetIdappAZ1  |   <i>String</i>               |  e.g., subnet-1234567890abcdef1  |
|VPCSubnetIdappAZ2       |   <i>String</i>               |  e.g., subnet-0987654321fedcba1  |
|DeploymentServer01       |   <i>String</i>               |  e.g., 192.168.1.10/32 (IP address of the tooling server)|
|InstanceType |  <i>String</i>   | e.g., mq.m5.large   |
|MQPassword |  <i>String</i>   | e.g., your-password   |
|DeploymentMode |  <i>String</i>   | e.g., SINGLE_INSTANCE or ACTIVE_STANDBY_MULTI_AZ  |  
|EngineVersion |  <i>String</i>   | e.g., Can avail from AWS console or ActiveMQ Dcoumentation   |
|**FirstMQDeployment** |  <i>String</i>   | **"true"** or **"false"** (default). Set to **"true"** for the first ActiveMQ deployment in the AWS account to create the AmazonMQ Log Resource Policy. Set to **"false"** for subsequent deployments.   |    


### Important: FirstMQDeployment Parameter

⚠️ **Critical Decision Required**: When deploying ActiveMQ, you must decide whether this is the **first** ActiveMQ deployment in your AWS account.

#### When to set FirstMQDeployment=true:
- This is the **very first** ActiveMQ broker being deployed in the AWS account
- Creates the required `AmazonMQ-logs` CloudWatch resource policy
- **Only use this for ONE deployment per AWS account**

#### When to set FirstMQDeployment=false (default):
- This is a **subsequent** ActiveMQ deployment in an account that already has ActiveMQ
- Skips creating the log resource policy (assumes it already exists)
- **Use this for ALL other deployments after the first one**

#### Decision Matrix:
| Scenario | FirstMQDeployment Setting | Result |
|----------|---------------------------|---------|
| First MQ in account | `"true"` | ✅ Creates policy + MQ broker |
| Subsequent MQ in account | `"false"` | ✅ Creates MQ broker only |
| First MQ but set to false | `"false"` | ❌ Deployment may fail (no log policy) |
| Subsequent MQ but set to true | `"true"` | ❌ Deployment fails (policy conflict) |

💡 **Tip**: When in doubt, check existing log policies with: `aws logs describe-resource-policies`

### How to Provision Template
The project team will need to create and update the parameters file based on the available parameters for their specific environment. Follow the steps below to provision the template:

### Prepare the parameters-activemq.json file:

1.  The HIP team will copy the parameters.json template into the project's IAC repository.
2.  The project team should update the values of the parameters in the parameters-activemq.json based on their environment and networking configuration.
3.  Run the CloudFormation Stack using the Azure DevOps Pipeline and Releases.

### Review the Stack Creation:

1.  Verify the successful creation of resources in the AWS Management Console.
2.  Ensure that the ActiveMQ broker is up and running across multiple availability zones.

### Logging Configuration and Troubleshooting

#### Logging Setup
* The CloudFormation template enables AmazonMQ broker logging with:
	- `General: true`
	- `Audit: true`
* Log groups are automatically created in CloudWatch Logs, typically named:
	- `/aws/amazonmq/broker/<broker-name>/General`
	- `/aws/amazonmq/broker/<broker-name>/Audit`

#### Troubleshooting Log Delivery
If log groups are created but remain empty:
1. Confirm the broker is running and healthy in the AWS Console.
2. Generate broker activity (connect a client, send messages).
3. Check for restrictive Service Control Policies (SCPs) or IAM policies that may block CloudWatch Logs actions (`logs:CreateLogGroup`, `logs:CreateLogStream`, `logs:PutLogEvents`).
4. Review the broker's monitoring tab for errors or warnings.
5. Wait a few minutes for log delivery, then refresh CloudWatch Logs.

#### Troubleshooting Deployment Issues

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
