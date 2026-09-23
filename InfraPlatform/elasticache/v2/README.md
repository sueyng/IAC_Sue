# AMAZON ELASTICACHE

Amazon ElastiCache is a serverless, Redis- and Memcached-compatible caching service delivering real-time, cost-optimized performance for modern applications. ElastiCache scales to hundreds of millions of operations per second with microsecond response times, and offers enterprise-grade security and reliability. Provisioning of this template is straight forward. see this [instruction](#how-to-provision-template)

This template provisions the following resources:
* Elasticache Subnet Group
* IAM Managed Policy
* Security Group
* Elasticache User
* Elasticache User Group
* Elasticache Serverless cache
* Redis cluster

## Parameters and its valid values

## Serverless Cache
Parameter values for `cf-elasticache serverkess` template.
|ParameterKey  | ValueType | Allowed Values  | 
|---|---|---|
| AppShortName  |   <i>String</i>               |   e.g my-application  |
|   EnvName     |   <i>String</i>               |  nprd, nprd-dev, nprd-dev-b, nprd-sit1, nprd-sit2, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b, prod, prod-a, prod-b |
|   VpcId           | <i>AWS::EC2::VPC::Id</i>  | e.g vpc-120324                |
|  AppSubnetIds |  <i>List<AWS::EC2::Subnet::Id></i>   | e.g subnet-123232,subnet-2345123,subnet-323122 |
|   VPCSubnetCidrAppAZ1     |   <i>String</i>   |   e.g 10.0.1.0/24     |
|   VPCSubnetCidrAppAZ2     |   <i>String</i>   |   e.g 10.0.2.0/24     |
|   VPCSubnetCidrAppAZ3     |   <i>String</i>   |   e.g 10.0.3.0/24     |
|   VPCSubnetCidrAppAZ3     |   <i>List<AWS::EC2::Subnet::Id></i>   |   e.g subnet-12321,subnet-23123,subnet-12321     |
|  MaxCacheDataStorage |<i>Number</i>| e.g 10 |
|  MultiMaxCacheECPUPerSecond |<i>String</i>| e.g 10 |
|   Engine  | <i>String</i> | e.g redis |
|   SnapshotRetentionLimit  | <i>Number</i> | e.g 5 |
|   DailySnapshotTime  | <i>String</i> | e.g 14:00 |

## Elasticache
Parameter values for `cf-elasticache serverkess` template.
|ParameterKey  | ValueType | Allowed Values  | 
|---|---|---|
| AppShortName  |   <i>String</i>               |   e.g my-application  |
|   EnvName     |   <i>String</i>               |  nprd, nprd-dev, nprd-dev-b, nprd-sit1, nprd-sit2, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b, prod, prod-a, prod-b |
|   VpcId           | <i>AWS::EC2::VPC::Id</i>  | e.g vpc-120324                |
|  AppSubnetIds |  <i>List<AWS::EC2::Subnet::Id></i>   | e.g subnet-123232,subnet-2345123,subnet-323122 |
|   VPCSubnetCidrAppAZ1     |   <i>String</i>   |   e.g 10.0.1.0/24     |
|   VPCSubnetCidrAppAZ2     |   <i>String</i>   |   e.g 10.0.2.0/24     |
|   VPCSubnetCidrAppAZ3     |   <i>String</i>   |   e.g 10.0.3.0/24     |
|   VPCSubnetCidrAppAZ3     |   <i>List<AWS::EC2::Subnet::Id></i>   |   e.g subnet-12321,subnet-23123,subnet-12321     |
|  RedisCacheInstanceType |<i>String</i>| e.g cache.m7g.large |
|  RedisAuthToken |<i>String</i>| e.g This-is-a-sample-token |

## How to provision template

HIP Team will copy the parameters.json to the project's IAC Repository. Project team will update the parameters json base on the available [parameters](#parameters-and-its-valid-values) in their own project repository.