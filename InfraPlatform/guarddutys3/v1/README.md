# GUARDDUTY MALWARE PROTECTION FOR S3

**Amazon GuardDuty Malware Protection for S3 is a feature of GuardDuty that scans newly uploaded objects for malware, enhancing AWS security. 
 For more information please visit this https://docs.aws.amazon.com/guardduty/latest/ug/gdu-malware-protection-s3.html

This template provisions the following resources:
* Lambda Function
* GuardDuty Malware Protection Plan
* IAM Role for GuardDuty Malware Protection Plan
* IAM Policy GuardDuty Malware Protection Plan
* IAM Policy Lambda Function
* EventBridge Rule
* IaC version tagging


Provisioning of this template is straight forward. see this [instruction](#how-to-provision-template)
## GUARDDUTY MALWARE PROTECTION FOR S3 (cf-s3malwareprotection.yaml)

| ParameterKey | Value Type | Allowed Values | Mandatory | Description |
|--------------|------------|-----------------|-----------|-------------|
| AppShortName | String | e.g., myapp | Yes | Application short name for resource naming |
| EnvName | String | nprd, nprd-dev, nprd-dev1, nprd-dev2, nprd-sit1, nprd-sit2, nprd-sit3, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-sit-c, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-uat-c, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b, nprd-pp-c, prod, prod-a, prod-b, prod-c | Yes | Environment designation |
| MalwareProtectedBucketName | String | e.g sourcebucket | Yes | Source S3 bucket to enable malware scanning |
| MalwareCleanBucketName | String | e.g destbucket | Yes | Destination S3 bucket for clean files |
| MalwareQuarantineBucketName | String | e.g quarantinebucket | No | Optional S3 bucket for quarantining infected files (default: empty) |

## Architecture Flow

```
S3 Upload → GuardDuty Scan → EventBridge Rule → Lambda Function
                                                    ├── NO_THREATS_FOUND  → Copy to Clean Bucket → Delete from Source
                                                    ├── THREATS_FOUND     → Copy to Quarantine Bucket (if configured) → Delete from Source
                                                    ├── THREATS_FOUND     → Delete from Source (if no quarantine bucket)
                                                    └── UNSUPPORTED/FAILED → Delete from Source
```

## Quarantine Bucket (Optional)

When `MalwareQuarantineBucketName` is provided:
- Infected files are **copied to the quarantine bucket** with tags (`QuarantineReason`, `SourceBucket`) before being deleted from the source
- IAM policy automatically adds `s3:PutObject` and `s3:PutObjectTagging` permissions for the quarantine bucket
- Lambda environment variable `QUARANTINE_BUCKET` is set conditionally

When `MalwareQuarantineBucketName` is empty (default):
- Infected files are **deleted directly** from the source bucket (original v1 behavior)
- No additional IAM permissions or environment variables are created

## Notes

1.  This CF template does not create new S3 buckets; it applies malware protection to existing ones.

2.  The MalwareProtectedBucketName is the S3 bucket where malware protection will be enabled.

3.  When files are uploaded to this bucket, GuardDuty scans them for threats.

4.  If a file is clean (NO_THREATS_FOUND), it is moved to the MalwareCleanBucketName.

5.  If a file is infected (THREATS_FOUND) and a quarantine bucket is configured, it is moved to the MalwareQuarantineBucketName with quarantine tags for forensic review.

6.  If a file is infected and no quarantine bucket is configured, it is deleted from the MalwareProtectedBucketName to prevent potential risks.

7.  After deployment, check CloudWatch Logs for monitoring and troubleshooting.

## Resources Created

| Resource | Name Pattern | Description |
|----------|-------------|-------------|
| IAM Policy (GuardDuty) | `{AppShortName}-{EnvName}-IAMS3MalwareBucketPolicy` | S3 + EventBridge permissions for GuardDuty |
| IAM Role (GuardDuty) | `{AppShortName}-{EnvName}-IAMS3MalwareBucketRole` | Role assumed by GuardDuty for scanning |
| GuardDuty Plan | - | Malware Protection Plan for source bucket |
| EventBridge Rule | `{AppShortName}-{EnvName}-GuardDutyCopyS3ObjectRule` | Triggers Lambda on scan completion |
| IAM Policy (Lambda) | `{AppShortName}-{EnvName}-IAMLambdaS3CopyObjectPolicy` | S3 copy/delete + logging permissions |
| IAM Role (Lambda) | `{AppShortName}-{EnvName}-IAMLambdaS3CopyObjectRole` | Role for Lambda function |
| Lambda Function | `{AppShortName}-{EnvName}-LambdaGurdduty` | Processes scan results (copy/quarantine/delete) |
| Log Group | `/aws/lambda/{AppShortName}-{EnvName}-LambdaGurdduty` | Lambda function logs (30 days retention) |

* **HIP Team** will copy the parameters.json to the project's IAC Repository. The project team will update the parameters JSON based on the available parameters in their own project repository.