# DynamoDB Table Deployment with AWS CDK

## Overview

This repository provides an AWS CDK stack for deploying DynamoDB tables using a centralized configuration file. It supports scalable, secure, and flexible table deployment with features such as TTL, point-in-time recovery, AWS-managed encryption, and IAM policies for fine-grained access.

## Template Structure

```
NoSQLDB/
└── DynamoDB/
└── v1/
├── cdk-dynamodb-stack.ts               (Main CDK stack for deploying tables)
├── env/
│   └── parameter-dynamodb.json         (Table configuration file)
└── README.md                           (Documentation for deployment)
```

## Main Components

**dynamodb_cdk_stack.ts:**  
TypeScript CDK stack that:
- Reads the table configuration from a JSON file
- Provisions DynamoDB tables with partition and optional sort keys
- Applies table settings like TTL, billing mode, encryption, and deletion policy
- Adds tags for environment, application, and backup
- Creates IAM Managed Policies with read/write access to each table

**dynamo_db_table_configuration.json:**  
Defines table deployment parameters including:
- Application short name and environment
- Table schema (partition/sort keys)
- Billing mode (on-demand or provisioned)
- TTL settings
- Deletion protection flag
- Custom tags

## Parameters and Their Valid Values

| Parameter | Description | Example Value | Required |
|----------|-------------|---------------|----------|
| appShortName | Application name prefix | "ent" | Yes |
| envName | Environment name | "nprd" | Yes |
| tableNameSuffix | Suffix for the table name | "dedup" | Yes |
| keySchema | List of keys with name, type, and attribute type | [{ "attributeName": "messageId", "keyType": "HASH", "attributeType": "S" }] | Yes |
| ttl.enabled | Enables TTL on the table | true | Optional |
| ttl.attributeName | TTL attribute used by DynamoDB | "ttlTimestamp" | Optional |
| billingMode | Billing mode | "PAY_PER_REQUEST", "PROVISIONED" | Optional |
| deletionProtection | Whether to retain table on delete | false | Optional |
| tags | Additional tags for cost, backup, etc. | { "FUNCTION": "DBS" } | Optional |

### Supported Key Types and Attribute Types
- **Key Types:** `HASH` (partition key), `RANGE` (optional sort key)
- **Attribute Types:** `S` (String), `N` (Number), `B` (Binary)

## Important Notes

1. **TTL Configuration:**
   - TTL deletes expired items automatically.
   - Must specify both `enabled` and `attributeName`.

2. **Billing Mode:**
   - Choose `PAY_PER_REQUEST` for on-demand scaling or `PROVISIONED` for fixed capacity.

3. **Deletion Protection:**
   - Set to `false` to allow table deletion (used `DESTROY` policy).
   - Set to `true` to retain table on stack deletion (used `RETAIN` policy).

4. **Encryption & Recovery:**
   - Tables are encrypted with AWS-managed keys.
   - Point-in-time recovery is always enabled.

5. **Tagging:**
   - Tags include application name, environment, and any user-defined tags.
   - Useful for backup, billing, and monitoring.

6. **IAM Policy:**
   - A managed policy with full DynamoDB read/write permissions is created for each table.

7. **Outputs:**
   - Table name, ARN, and policy ARN are exported using CloudFormation outputs.

## Deployment Steps

- **Install CDK and Dependencies:**
  ```
  npm install -g aws-cdk
  npm install
  ```

- **Edit the Configuration File:**
  Update `parameter-dynamodb.json` with your desired table details.

- **Deploy the Stack:**
  ```
  cdk deploy
  ```

- **Monitor the Stack:**
  Track stack creation via the terminal or AWS Console.

- **Validate Resources:**
  Check that DynamoDB tables are created and tagged correctly.
  Validate TTL and IAM policy via the AWS Console.
