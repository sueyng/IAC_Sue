import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Tags } from 'aws-cdk-lib';
import * as fs from 'fs';
import * as path from 'path';

interface KeySchemaEntry {
  attributeName: string;
  keyType: 'HASH' | 'RANGE';
  attributeType: 'S' | 'N' | 'B';
}

interface TableConfig {
  tableNameSuffix: string;
  keySchema: KeySchemaEntry[];
  ttl?: {
    enabled: boolean;
    attributeName: string;
  };
  billingMode?: 'PAY_PER_REQUEST' | 'PROVISIONED';
  deletionProtection?: boolean;
  tags?: Record<string, string>;
}

interface StackProps extends cdk.StackProps {
  appShortName: string;
  envName: string;
}

export class DynamodbCdkStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: StackProps) {
    super(scope, id, props);

    const { appShortName, envName } = props;
    const parameterFile = `${appShortName}-${envName}-parameter-dynamodb.json`;
    const configPath = path.join(__dirname, '..', 'parameters', parameterFile);

    if (!fs.existsSync(configPath)) {
      throw new Error(`Missing parameter file: ${configPath}`);
    }

    const config: { tables: TableConfig[] } = JSON.parse(fs.readFileSync(configPath, 'utf8'));

    const typeMap: Record<'S' | 'N' | 'B', dynamodb.AttributeType> = {
      S: dynamodb.AttributeType.STRING,
      N: dynamodb.AttributeType.NUMBER,
      B: dynamodb.AttributeType.BINARY,
    };

    for (const tableConfig of config.tables) {
      const fullTableName = `${appShortName}-${envName}-${tableConfig.tableNameSuffix}`;

      const partitionKey = tableConfig.keySchema.find(k => k.keyType === 'HASH');
      if (!partitionKey) {
        throw new Error(`Missing HASH (partition) key for table ${fullTableName}`);
      }

      const sortKey = tableConfig.keySchema.find(k => k.keyType === 'RANGE');

      const tableProps: dynamodb.TableProps = {
        tableName: fullTableName,
        partitionKey: {
          name: partitionKey.attributeName,
          type: typeMap[partitionKey.attributeType],
        },
        ...(sortKey && {
          sortKey: {
            name: sortKey.attributeName,
            type: typeMap[sortKey.attributeType],
          }
        }),
        billingMode: tableConfig.billingMode === 'PROVISIONED'
          ? dynamodb.BillingMode.PROVISIONED
          : dynamodb.BillingMode.PAY_PER_REQUEST,
        removalPolicy: tableConfig.deletionProtection === false
          ? cdk.RemovalPolicy.DESTROY
          : cdk.RemovalPolicy.RETAIN,
        pointInTimeRecovery: true,
        encryption: dynamodb.TableEncryption.AWS_MANAGED,
        timeToLiveAttribute: tableConfig.ttl?.enabled ? tableConfig.ttl.attributeName : undefined,
      };

      const dynamoTable = new dynamodb.Table(this, `${fullTableName}-Table`, tableProps);

      const baseTags: Record<string, string> = {
        Name: fullTableName,
        APPSHORTNAME: appShortName,
        ENVIRONMENT: envName,
        ...(tableConfig.tags || {}),
      };

      for (const [key, value] of Object.entries(baseTags)) {
        Tags.of(dynamoTable).add(key, value);
      }

      const policy = new iam.ManagedPolicy(this, `${fullTableName}-RWPolicy`, {
        managedPolicyName: `${fullTableName}-iam-readwritetablepolicy`,
        statements: [
          new iam.PolicyStatement({
            effect: iam.Effect.ALLOW,
            actions: [
              "dynamodb:BatchGetItem",
              "dynamodb:BatchWriteItem",
              "dynamodb:ConditionCheckItem",
              "dynamodb:PutItem",
              "dynamodb:DescribeTable",
              "dynamodb:DeleteItem",
              "dynamodb:GetItem",
              "dynamodb:Scan",
              "dynamodb:Query",
              "dynamodb:UpdateItem"
            ],
            resources: [dynamoTable.tableArn],
          }),
        ],
      });

      new cdk.CfnOutput(this, `${fullTableName}-TableArn`, {
        value: dynamoTable.tableArn,
        exportName: `${fullTableName}-arn`,
      });

      new cdk.CfnOutput(this, `${fullTableName}-TableName`, {
        value: dynamoTable.tableName,
        exportName: `${fullTableName}-name`,
      });

      new cdk.CfnOutput(this, `${fullTableName}-PolicyArn`, {
        value: policy.managedPolicyArn,
        exportName: `${fullTableName}-policy-arn`,
      });
    }
     // ✅ Prevent CDKMetadata from being added
    this.node.tryRemoveChild('CDKMetadata');
  }
}
