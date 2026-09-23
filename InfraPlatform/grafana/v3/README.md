# AMAZON MANAGED GRAFANA

**Amazon Managed Grafana** is a fully managed service for Grafana, a popular open-source analytics platform that enables you to query, visualize, and alert on your metrics, logs, and traces. For more information please visit this [site](https://aws.amazon.com/grafana/).

This template provisions the following resources:
* EC2: Prefix List
* Security Group
* IAM Role
* IAM Policy
* Grafana Workspace


Provisioning of this template is straight forward. see this [instruction](#how-to-provision-template)
## Grafana (cf-grafana.yaml)

| ParameterKey | Value Type | Allowed Values | Mandatory |
|--------------|------------|-----------------|-----------|
| AppShortName | String | e.g., myapp | Yes |
| EnvName | String | nprd, nprd-dev, nprd-sit1, nprd-sit2, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b, prod, prod-a, prod-b | Yes |
| VpcId | AWS::EC2::VPC::Id | e.g., vpc-0123456789abcdef0 | Yes |
| AppSubnetIds | AWS::EC2::Subnet::Id | e.g subnet-123232,subnet-2345123,subnet-323122 | Yes |
| AuthProvider | String | AWS_SSO, SAML | Yes |
| VpcCidr1 | String | e.g., 10.54.0.0/24 | Yes |
| VpcCidr2 | String | e.g., 10.54.1.0/24 | Optional |
| HCCVpceCidr      |   <i>String</i>               |  e.g 10.48.42.0/24  |  Yes |

## Notes

1.  Prefix Lists: Used to define external IP ranges (e.g., office IPs) that can access the Grafana workspace.

2.  The Grafana workspace assumes an IAM role with predefined permissions to access AWS services (CloudWatch, EC2, Tags).

3.  Serverices retention is conditional on whether the environment is production.

4.  Security Group: Controls ingress and egress to ensure that only authorized traffic can reach the Grafana workspace.

5.  Grafana workspace is secured by restricting access based on prefix lists and subnet configurations.

* **HIP Team** will copy the parameters.json to the project's IAC Repository. The project team will update the parameters JSON based on the available parameters in their own project repository.