# API Gateway CloudWatch Logging Infrastructure

This CloudFormation template deploys the necessary configuration to enable CloudWatch logging for API Gateways in your AWS account.

## Template Overview

The template `cf-apigw-cloudwatch.yaml` provides a one-time global setup for API Gateway logging that includes:
- IAM role for CloudWatch logging with appropriate permissions
- API Gateway account settings configuration
- Environment-based naming conventions

## Key Features

- Account-level CloudWatch configuration
- Reusable across multiple API Gateways
- Environment-specific role naming

## Deployment

This is a one-time setup required per AWS account. Once deployed, all API Gateways in the account can use this configuration for CloudWatch logging.

## Template Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| AppShortName | String | Yes | Application identifier for resource naming |
| EnvName | String | Yes | Environment name (nprd, prod) |

## Resources Created

1. **IAM Role (ApiGatewayCloudWatchRole)**:
   - Named according to pattern: `${AppShortName}-${EnvName}-apigw-cloudwatch-role`
   - Grants API Gateway service the ability to push logs to CloudWatch
   - Uses the managed policy: `arn:aws:iam::aws:policy/service-role/AmazonAPIGatewayPushToCloudWatchLogs`

2. **API Gateway Account Settings (ApiGatewayAccount)**:
   - Associates the created IAM role with the API Gateway service account
   - Enables CloudWatch logging for all API Gateways in the AWS account

## Logging Features Enabled

Once this template is deployed, API Gateways in the account can be configured with:
- Detailed CloudWatch metrics
- Request/response logging capabilities
- Method-level logging configuration


## Troubleshooting

### Missing Logs
If API Gateway logs are not appearing in CloudWatch:
   - Verify this CloudWatch setup template has been successfully deployed
   - Check that the IAM role has the correct permissions
   - Confirm that individual API Gateway stages have logging enabled
   - Verify log level configuration in API Gateway settings