# AMAZON ELASTICACHE

Amazon ElastiCache is a serverless, Redis-, Valkey- and Memcached-compatible caching service delivering real-time, cost-optimized performance for modern applications. ElastiCache scales to hundreds of millions of operations per second with microsecond response times, and offers enterprise-grade security and reliability. Provisioning of this template is straightforward. See this [instruction](#how-to-provision-template).

This template provisions the following resources:
* ElastiCache Subnet Group
* IAM Managed Policy
* Security Group
* ElastiCache User
* ElastiCache User Group
* ElastiCache Serverless Redis cache
* ElastiCache Serverless Valkey cache
* Redis cluster
* Valkey cluster

## Parameters and its valid values

## Redis Serverless Cache
Parameter values for `cf-elasticache-serverless.yaml` template.
| ParameterKey            | ValueType                           | Allowed Values / Example         |
|-------------------------|-------------------------------------|----------------------------------|
| AWSRegion               | <i>String</i>                       | ap-southeast-1                  |
| AppShortName            | <i>String</i>                       | e.g. my-application             |
| EnvName                 | <i>String</i>                       | nprd, nprd-dev, nprd-dev-b, nprd-sit1, nprd-sit2, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b, prod, prod-a, prod-b |
| VpcId                   | <i>AWS::EC2::VPC::Id</i>            | e.g. vpc-120324                  |
| AppSubnetIds            | <i>List<AWS::EC2::Subnet::Id></i>   | e.g. subnet-123232,subnet-2345123,subnet-323122 |
| VPCSubnetCidrAppAZ1     | <i>String</i>                       | e.g. 10.0.1.0/24                 |
| VPCSubnetCidrAppAZ2     | <i>String</i>                       | e.g. 10.0.2.0/24                 |
| VPCSubnetCidrAppAZ3     | <i>String</i>                       | e.g. 10.0.3.0/24                 |
| MaxCacheDataStorage     | <i>Number</i>                       | e.g. 10                          |
| MaxCacheECPUPerSecond   | <i>Number</i>                       | e.g. 100                         |
| Engine                  | <i>String</i>                       | redis                            |
| SnapshotRetentionLimit  | <i>Number</i>                       | e.g. 5                           |
| DailySnapshotTime       | <i>String</i>                       | e.g. 14:00                       |
| CreateCacheUserAndGroup | <i>String</i>                       | yes, no                          |
| VpcCidr1                | <i>String</i>                       | e.g. 10.0.0.0/16                 |
| VpcCidr2                | <i>String</i>                       | e.g. 10.1.0.0/16                 |
| VpcCidr3                | <i>String</i>                       | e.g. 10.2.0.0/16                 |
| VpcCidr4                | <i>String</i>                       | e.g. 10.3.0.0/16                 |
| VpcCidr5                | <i>String</i>                       | e.g. 10.4.0.0/16                 |
| S3PrefixListId          | <i>String</i>                       | e.g. pl-123456                   |
| HCCVpceCidr             | <i>String</i>                       | e.g. 192.168.0.0/24              |

## Valkey Serverless Cache
Parameter values for `cf-elasticache-serverless-valkey.yaml` template.
| ParameterKey            | ValueType                           | Allowed Values / Example         |
|-------------------------|-------------------------------------|----------------------------------|
| AWSRegion               | <i>String</i>                       | ap-southeast-1                  |
| AppShortName            | <i>String</i>                       | e.g. my-application             |
| EnvName                 | <i>String</i>                       | nprd, nprd-dev, nprd-dev-b, nprd-sit1, nprd-sit2, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b, prod, prod-a, prod-b |
| VpcId                   | <i>AWS::EC2::VPC::Id</i>            | e.g. vpc-120324                  |
| AppSubnetIds            | <i>List<AWS::EC2::Subnet::Id></i>   | e.g. subnet-123232,subnet-2345123,subnet-323122 |
| VPCSubnetCidrAppAZ1     | <i>String</i>                       | e.g. 10.0.1.0/24                 |
| VPCSubnetCidrAppAZ2     | <i>String</i>                       | e.g. 10.0.2.0/24                 |
| VPCSubnetCidrAppAZ3     | <i>String</i>                       | e.g. 10.0.3.0/24                 |
| MaxCacheDataStorage     | <i>Number</i>                       | e.g. 10                          |
| MaxCacheECPUPerSecond   | <i>Number</i>                       | e.g. 100                         |
| Engine                  | <i>String</i>                       | valkey                           |
| SnapshotRetentionLimit  | <i>Number</i>                       | e.g. 5                           |
| DailySnapshotTime       | <i>String</i>                       | e.g. 14:00                       |
| CreateCacheUserAndGroup | <i>String</i>                       | yes, no                          |
| VpcCidr1                | <i>String</i>                       | e.g. 10.0.0.0/16                 |
| VpcCidr2                | <i>String</i>                       | e.g. 10.1.0.0/16                 |
| VpcCidr3                | <i>String</i>                       | e.g. 10.2.0.0/16                 |
| VpcCidr4                | <i>String</i>                       | e.g. 10.3.0.0/16                 |
| VpcCidr5                | <i>String</i>                       | e.g. 10.4.0.0/16                 |
| S3PrefixListId          | <i>String</i>                       | e.g. pl-123456                   |
| HCCVpceCidr             | <i>String</i>                       | e.g. 192.168.0.0/24              |

## Redis Cluster
Parameter values for `cf-elasticache.yaml` template.
| ParameterKey            | ValueType                           | Allowed Values / Example         |
|-------------------------|-------------------------------------|----------------------------------|
| AppShortName            | <i>String</i>                       | e.g. my-application             |
| EnvName                 | <i>String</i>                       | nprd, nprd-dev, nprd-dev-b, nprd-sit1, nprd-sit2, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b, prod, prod-a, prod-b |
| VpcId                   | <i>AWS::EC2::VPC::Id</i>            | e.g. vpc-120324                  |
| AppSubnetIds            | <i>List<AWS::EC2::Subnet::Id></i>   | e.g. subnet-123232,subnet-2345123,subnet-323122 |
| VPCSubnetCidrAppAZ1     | <i>String</i>                       | e.g. 10.0.1.0/24                 |
| VPCSubnetCidrAppAZ2     | <i>String</i>                       | e.g. 10.0.2.0/24                 |
| VPCSubnetCidrAppAZ3     | <i>String</i>                       | e.g. 10.0.3.0/24                 |
| RedisCacheInstanceType  | <i>String</i>                       | e.g. cache.m5.large              |
| RedisAuthToken          | <i>String</i>                       | e.g. This-is-a-sample-token      |
| VpcCidr1                | <i>String</i>                       | e.g. 10.0.0.0/16                 |
| VpcCidr2                | <i>String</i>                       | e.g. 10.1.0.0/16                 |
| VpcCidr3                | <i>String</i>                       | e.g. 10.2.0.0/16                 |
| VpcCidr4                | <i>String</i>                       | e.g. 10.3.0.0/16                 |
| VpcCidr5                | <i>String</i>                       | e.g. 10.4.0.0/16                 |
| S3PrefixListId          | <i>String</i>                       | e.g. pl-123456                   |
| HCCVpceCidr             | <i>String</i>                       | e.g. 192.168.0.0/24              |

## Valkey Cluster
Parameter values for `cf-elasticache-valkey.yaml` template.
| ParameterKey            | ValueType                           | Allowed Values / Example         |
|-------------------------|-------------------------------------|----------------------------------|
| AppShortName            | <i>String</i>                       | e.g. my-application             |
| EnvName                 | <i>String</i>                       | nprd, nprd-dev, nprd-dev-b, nprd-sit1, nprd-sit2, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b, prod, prod-a, prod-b |
| VpcId                   | <i>AWS::EC2::VPC::Id</i>            | e.g. vpc-120324                  |
| AppSubnetIds            | <i>List<AWS::EC2::Subnet::Id></i>   | e.g. subnet-123232,subnet-2345123,subnet-323122 |
| VPCSubnetCidrAppAZ1     | <i>String</i>                       | e.g. 10.0.1.0/24                 |
| VPCSubnetCidrAppAZ2     | <i>String</i>                       | e.g. 10.0.2.0/24                 |
| VPCSubnetCidrAppAZ3     | <i>String</i>                       | e.g. 10.0.3.0/24                 |
| ValKeyCacheInstanceType | <i>String</i>                       | e.g. cache.m5.large              |
| ValKeyAuthToken         | <i>String</i>                       | e.g. This-is-a-sample-token      |
| VpcCidr1                | <i>String</i>                       | e.g. 10.0.0.0/16                 |
| VpcCidr2                | <i>String</i>                       | e.g. 10.1.0.0/16                 |
| VpcCidr3                | <i>String</i>                       | e.g. 10.2.0.0/16                 |
| VpcCidr4                | <i>String</i>                       | e.g. 10.3.0.0/16                 |
| VpcCidr5                | <i>String</i>                       | e.g. 10.4.0.0/16                 |
| S3PrefixListId          | <i>String</i>                       | e.g. pl-123456                   |
| HCCVpceCidr             | <i>String</i>                       | e.g. 192.168.0.0/24              |

## How to provision template

HIP Team will copy the parameters.json to the project's IAC Repository. Project team will update the parameters json based on the available [parameters](#parameters-and-its-valid-values) in their own project repository.

### Template and Parameter File Mapping

Each CloudFormation template has a corresponding parameter file:

| Template File                        | Parameter File                        |
|--------------------------------------|---------------------------------------|
| cf-elasticache.yaml                  | parameters-elasticache.json           |
| cf-elasticache-valkey.yaml           | parameters-elasticache-valkey.json    |
| cf-elasticache-serverless.yaml       | parameters-elasticache-serverless.json|
| cf-elasticache-serverless-valkey.yaml| parameters-elasticache-serverless-valkey.json |