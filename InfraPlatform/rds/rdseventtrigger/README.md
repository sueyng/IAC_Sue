# RDS Event Trigger with AWS CloudFormation v1

## Overview

This repository provides an AWS CloudFormation template for deploying automated RDS event monitoring and alerting system. The solution captures critical RDS database events (downtime, maintenance, failover) and sends formatted SMS alerts via SNS with timezone conversion to UTC+8. This setup ensures proactive monitoring and immediate notification of RDS issues across environments.

## Template Structure

```
RDS-Event-Trigger-CF/
├── cf-rds-event-trigger.yaml              (Main CloudFormation template)
├── parameter-rds-event-trigger.json       (Parameter file for deployment)
└── README.md                              (Documentation for deployment)
```

## Main Components
**cf-rds-event-trigger.yaml:**
CloudFormation template to provision the RDS event monitoring setup, including:
- EventBridge rule for RDS event filtering
- Lambda function for event processing and timezone conversion
- SNS integration for alert delivery
- IAM roles and permissions
- CloudWatch log groups
Fully parameterized for flexible deployment across environments.

**parameter-rds-event-trigger.json:**
Defines the environment-specific parameters such as application name, SNS topic ARN, KMS key ARN, and RDS instance identifiers to monitor.

## Parameters and its valid values

| ParameterKey | Description | Example Value | Required |
|--------------|-------------|---------------|----------|
| AppShortName | Short name of the application | "billing", "orders", "myapp" | Yes |
| Environment | Environment name | "dev", "qa", "prod" | Yes |
| SnsTopicArn | ARN of existing SNS topic for SMS alerts | "arn:aws:sns:us-east-1:123456789012:rds-alerts" | Yes |
| SnsKmsKeyArn | KMS key ARN for SNS topic encryption | "arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012" | Yes |
| RdsInstanceIds | Comma-separated list of RDS DB identifiers to monitor | "mydb-prod-1,mydb-prod-2" | Yes |

### Supported Environment Names
- **Development:** dev, development, test
- **Quality Assurance:** qa, uat, staging, sit
- **Production:** prod, production

### Monitored RDS Events
The template monitors the following critical RDS events:

#### Reboot/Restart Events
- **RDS-EVENT-0004:** DB instance shutdown
- **RDS-EVENT-0006:** DB instance restarted

#### Failover Events
- **RDS-EVENT-0013:** Multi-AZ failover started
- **RDS-EVENT-0015:** Multi-AZ failover completed

#### Instance Failure Events
- **RDS-EVENT-0031:** DB instance failure
- **RDS-EVENT-0035:** Bad parameter state
- **RDS-EVENT-0036:** Incompatible network/not available

#### KMS/Encryption Issues
- **RDS-EVENT-0418:** KMS access problem (may become inaccessible)
- **RDS-EVENT-0419:** KMS access problem, DB made inaccessible

#### Maintenance/Patching Events
- **RDS-EVENT-0026:** Applying offline patches (DB unavailable)
- **RDS-EVENT-0027:** Offline patches complete (DB available)
- **RDS-EVENT-0266:** Downtime started for engine upgrade
- **RDS-EVENT-0267:** Engine upgrade started
- **RDS-EVENT-0268:** Engine upgrade finished
- **RDS-EVENT-0270:** Engine upgrade failed, rollback succeeded
- **RDS-EVENT-0422:** Host replacement due to maintenance
- **RDS-EVENT-0396:** Reboot scheduled for replica

## Important Notes

1. **SNS Topic Prerequisites:**
   - Ensure the SNS topic exists before deploying the stack and is configured for SMS delivery.
   - The SNS topic should have appropriate subscription(s) configured for receiving alerts.

2. **KMS Key Configuration:**
   - The KMS key specified in SnsKmsKeyArn must exist and be accessible by the Lambda function.
   - Ensure the KMS key policy allows Lambda service to use GenerateDataKey, Decrypt, and Encrypt operations.
   - Verify the key is in the same region as your deployment.

3. **RDS Instance Identifiers:**
   - The RDS instance identifiers in RdsInstanceIds must exactly match the DB instance identifiers in RDS console.
   - Use the actual DB identifier, not the DB name or endpoint.
   - Multiple instances should be separated by commas without spaces.

4. **Event Filtering:**
   - The EventBridge rule is configured to monitor only critical downtime and maintenance events.
   - Events are filtered by both source identifier (RDS instances) and specific event IDs to reduce noise.
   - All monitored events are documented in the "Monitored RDS Events" section.

5. **Timezone Conversion:**
   - Lambda function converts UTC timestamps to UTC+8 (Singapore/Malaysia timezone) by default.
   - The timezone offset can be modified by changing the TIME_OFFSET_HOURS environment variable.
   - Conversion handles both standard and microsecond timestamp formats.

6. **Alert Message Format:**
   - SMS alerts include: Instance name, Event ID, Description, and converted timestamp.
   - Messages are formatted for readability on mobile devices.
   - Each alert contains sufficient context for immediate understanding of the issue.

7. **Lambda Function Configuration:**
   - Function timeout is set to 10 seconds to handle timestamp conversion and SNS publishing.
   - Runtime is Python 3.12 with boto3 for AWS service interactions.
   - Function logs are stored in CloudWatch with 30-day retention for cost optimization.

8. **EventBridge Rule:**
   - Rule is enabled by default and triggers immediately when matching events occur.
   - Pattern matching is case-sensitive and requires exact instance identifier matches.
   - Rule processes events in real-time with minimal latency.

9. **IAM Permissions:**
   - Lambda execution role follows least-privilege principle with only necessary permissions.
   - Role can publish to specified SNS topic and use the provided KMS key.
   - No additional AWS service permissions are granted beyond requirements.

10. **Multi-Region Deployment:**
    - Template can be deployed in any AWS region where RDS instances are located.
    - Ensure SNS topic and KMS key are in the same region as the stack deployment.
    - EventBridge rules automatically monitor RDS events in the deployment region.

11. **Resource Naming:**
    - All resources are named with AppShortName and Environment prefixes for easy identification.
    - Resource names follow consistent pattern: {AppShortName}-{Environment}-{ResourceType}.
    - Tags are applied to all resources for cost tracking and management.

12. **Error Handling:**
    - Lambda function includes error handling for timestamp parsing failures.
    - Function will still send alerts even if timezone conversion fails (using original UTC time).
    - All errors are logged to CloudWatch for troubleshooting.

15. **Monitoring and Troubleshooting:**
    - Lambda execution logs provide detailed information about processed events.
    - EventBridge rule metrics show event processing statistics.
    - SNS delivery status can be monitored through CloudWatch metrics.

## Deployment Steps

1. **Prepare the Prerequisites:**
   - Ensure the SNS topic exists and is configured for SMS delivery with appropriate subscriptions.
   - Verify the KMS key for SNS encryption exists and has proper permissions.
   - Collect the exact RDS DB instance identifiers you want to monitor.

2. **Edit the Parameter File:**
   - Update the parameter-rds-event-trigger.json file with environment-specific values:
   ```json
   [
     {
       "ParameterKey": "AppShortName",
       "ParameterValue": "your-app-name"
     },
     {
       "ParameterKey": "Environment", 
       "ParameterValue": "prod"
     },
     {
       "ParameterKey": "SnsTopicArn",
       "ParameterValue": "arn:aws:sns:your-region:your-account:your-topic"
     },
     {
       "ParameterKey": "SnsKmsKeyArn",
       "ParameterValue": "arn:aws:kms:your-region:your-account:key/your-key-id"
     },
     {
       "ParameterKey": "RdsInstanceIds",
       "ParameterValue": "db-instance-1,db-instance-2"
     }
   ]
   ```

3. **Deploy Using AWS CLI:**
   - Execute the following command:
   ```bash
   aws cloudformation deploy \
     --template-file cf-rds-event-trigger.yaml \
     --parameter-overrides file://parameter-rds-event-trigger.json \
     --stack-name RDS-Event-Monitoring \
     --capabilities CAPABILITY_NAMED_IAM \
     --region your-region
   ```

4. **Alternative: Deploy Using AWS Console:**
   - Navigate to CloudFormation in AWS Management Console
   - Click "Create Stack" → "With new resources"
   - Upload cf-rds-event-trigger.yaml template
   - Fill in parameters or upload parameter-rds-event-trigger.json
   - Review and create stack

5. **Monitor the Stack Creation:**
   - Track the stack creation process in the AWS Management Console.
   - Verify all resources are created successfully without errors.

6. **Validate Resources:**
   - Confirm the Lambda function is created: `{AppShortName}-{Environment}-rds-alert-lambda`
   - Verify the EventBridge rule is enabled: `{AppShortName}-{Environment}-rds-downtime-rule`
   - Check the IAM role exists: `{AppShortName}-{Environment}-rds-alert-lambda-role`
   - Confirm CloudWatch log group is created: `/aws/lambda/{AppShortName}-{Environment}-rds-alert-lambda`

7. **Test the Setup (Optional):**
   - You can test by triggering a manual RDS event (like restarting an RDS instance)
   - Monitor CloudWatch logs to see event processing
   - Verify SMS alert is received through SNS

## Recent Updates (v1)

### RDS Event Monitoring System
- **Automated Event Detection**: EventBridge rule automatically captures critical RDS events for specified instances
- **Intelligent Event Filtering**: Monitors only downtime and maintenance-related events to reduce alert noise
- **Real-time Alerting**: Lambda function processes events immediately and sends formatted SMS alerts
- **Timezone Conversion**: Automatic UTC to UTC+8 time conversion for regional teams

### Event Coverage
The system monitors 15 critical RDS event types across four categories:
- **Reboot/Restart Events**: Instance shutdowns and restarts
- **Failover Events**: Multi-AZ failover start and completion
- **Instance Failures**: Database failures and parameter issues  
- **Maintenance Events**: Patching, upgrades, and host replacements

### Key Benefits
- **Proactive Monitoring**: Immediate notification of RDS issues before user impact
- **Regional Time Display**: UTC+8 conversion for Singapore/Malaysia teams
- **Selective Monitoring**: Only specified RDS instances trigger alerts
- **Secure Communication**: KMS-encrypted SNS messaging for alert delivery
