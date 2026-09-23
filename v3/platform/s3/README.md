# AMAZON S3

**Amazon S3** is an object storage service offering industry-leading scalability, data availability, security, and performance. This repository contains three CloudFormation templates for provisioning S3 resources:

1. `cf-s3bucket.yaml`: Dynamic S3 bucket creation
2. `cf-s3buckets-batchjob.yaml`: S3 buckets for batch job processing
3. `cf-s3buckets-infra.yaml`: S3 buckets and resources for infrastructure

## Templates Overview

### 1. cf-s3bucket.yaml

This template provides dynamic S3 bucket creation based on input parameters.

Resources provisioned:
* Multiple S3 Buckets (based on input)
* S3 Bucket Policies for each bucket

### 2. cf-s3buckets-batchjob.yaml

This template creates specific S3 buckets for batch job processing.

Resources provisioned:
* AppArtefact S3 Bucket
* AppRuntime S3 Bucket
* App S3 Bucket
* Dataload S3 Bucket
* DataExtraction S3 Bucket
* Corresponding S3 Bucket Policies for each bucket

### 3. cf-s3buckets-infra.yaml

This template creates S3 buckets and resources for infrastructure purposes.

Resources provisioned:
* EC2 File Repository S3 Bucket
* Inspector S3 Bucket
* KMS Key for Inspector
* KMS Key Alias
* S3 Bucket Policies

## Parameters and their valid values

### 1. cf-s3bucket.yaml (parameters-s3bucket.json)

| ParameterKey | ValueType | Allowed Values | Example | Mandatory |
|--------------|-----------|----------------|---------|-----------|
| AppShortName | String    | e.g., my-application | "xxx" | Yes |
| EnvName      | String    | nprd, nprd-dev, nprd-sit1, nprd-sit2, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b, prod, prod-a, prod-b | "nprd-sit1" | Yes |
| BucketNames  | CommaDelimitedList | e.g., bucket1,bucket2,bucket3 | "dataloading,extraction" | Yes |

### 2. cf-s3buckets-batchjob.yaml (parameters-s3-batchjob.json)

| ParameterKey | ValueType | Allowed Values | Example | Mandatory |
|--------------|-----------|----------------|---------|-----------|
| AppShortName | String    | e.g., my-application | "xxx" | Yes |
| EnvName      | String    | nprd, nprd-dev, nprd-sit1, nprd-sit2, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b, prod, prod-a, prod-b | "prod" | Yes |

### 3. cf-s3buckets-infra.yaml (parameters-s3buckets-infra.json)

| ParameterKey | ValueType | Allowed Values | Example | Mandatory |
|--------------|-----------|----------------|---------|-----------|
| AppShortName | String    | e.g., my-application | "xxx" | Yes |
| EnvName      | String    | nprd, nprd-dev, nprd-sit1, nprd-sit2, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b, prod, prod-a, prod-b | "prod" | Yes |

## S3 Bucket Naming Convention

All S3 buckets created by these templates follow a specific naming convention using the AppShortName and EnvName as prefixes. This ensures consistency and easy identification of buckets across different applications and environments.

The general format for bucket names is:
<AppShortName>-<EnvName>-<BucketPurpose>

Where:
- `<AppShortName>` is the short name or acronym for your application
- `<EnvName>` is the environment name (e.g., prod, nprd-sit1)
- `<BucketPurpose>` is a descriptor for the bucket's specific use

Examples:
1. For the dynamic S3 bucket creation (cf-s3bucket.yaml):
   If AppShortName = "xxx", EnvName = "nprd-sit1", and BucketNames = "dataloading,extraction"
   The resulting bucket names would be:
   - xxx-nprd-sit1-dataloading
   - xxx-nprd-sit1-extraction

2. For the batch job S3 buckets (cf-s3buckets-batchjob.yaml):
   If AppShortName = "xxx" and EnvName = "prod"
   The resulting bucket names would include:
   - xxx-prod-app-artefact
   - xxx-prod-app-runtime
   - xxx-prod-app
   - xxx-prod-dataload
   - xxx-prod-data-extraction

3. For the infrastructure S3 buckets (cf-s3buckets-infra.yaml):
   If AppShortName = "xxx" and EnvName = "prod"
   The resulting bucket names would include:
   - xxx-prod-s3-ec2-file-repo
   - xxx-prod-s3-inspector

When using these templates, ensure that the combination of AppShortName, EnvName, and bucket purpose creates unique and compliant S3 bucket names within your AWS account.

## How to use these templates

1. Choose the appropriate template based on your requirements.
2. Locate the corresponding parameters JSON file for the chosen template:
   - For `cf-s3bucket.yaml`, use `parameters-s3bucket.json`
   - For `cf-s3buckets-batchjob.yaml`, use `parameters-s3-batchjob.json`
   - For `cf-s3buckets-infra.yaml`, use `parameters-s3buckets-infra.json`
3. Update the parameters in the JSON file based on the available [parameters](#parameters-and-their-valid-values) for the specific template.
4. Ensure all mandatory parameters are filled with appropriate values.

## Common Features Across Templates

- All templates use conditions to determine if the environment is production.
- Production environments have different deletion and update replace policies (Retain instead of Delete).
- All S3 buckets are created with:
  - AES256 encryption
  - Private access control
  - Public access blocking
- All S3 bucket policies enforce SSL-only requests.

## Notes

- The `cf-s3bucket.yaml` template uses the `AWS::LanguageExtensions` transform to enable the `Fn::ForEach` functionality for dynamic resource creation.
- The `cf-s3buckets-infra.yaml` template includes additional resources like KMS keys for the Inspector service.
- All parameters in the provided JSON files are mandatory for their respective templates.