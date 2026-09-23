# AMAZON MANAGED GRAFANA

**Amazon Managed Grafana** is a fully managed service for Grafana, a popular open-source analytics platform that enables you to query, visualize, and alert on your metrics, logs, and traces. For more information please visit this [site](https://aws.amazon.com/grafana/).

This template provisions the following resources:
* EC2: Prefix List
* Security Group
* IAM Role
* IAM Policy
* Grafana Workspace


Provisioning of this template is straight forward. see this [instruction](#how-to-provision-template)

## Parameters for Grafana Deployment (v5)

| ParameterKey      | Example Value                                               | Description                       |
|-------------------|------------------------------------------------------------|-----------------------------------|
| VPCID             | vpc-0f5fc534c59f69a2a                                      | VPC ID for Grafana deployment     |
| AppSubnetIDs      | subnet-07be5e2da470c6503,subnet-049a0f1e8d28fb7be          | Comma-separated subnet IDs        |
| AppShortName      | grm                                                        | Application short name            |
| EnvName           | nprd-dev                                                   | Environment name                  |
| AuthProvider      | AWS_SSO                                                    | Authentication provider           |
| VpcCidr1          | 10.53.40.40/24                                             | Primary VPC CIDR                  |
| VpcCidr2          | 10.53.40.40/24                                             | Secondary VPC CIDR                |
| HCCVpceCidr       | 10.48.42.0/24                                              | VPC endpoint CIDR                 |
| GrafanaVersion    | 9.8                                                        | Grafana version                   |

## Notes

1.  Prefix Lists: Used to define external IP ranges (e.g., office IPs) that can access the Grafana workspace.

2.  The Grafana workspace assumes an IAM role with predefined permissions to access AWS services (CloudWatch, EC2, Tags).

3.  Serverices retention is conditional on whether the environment is production.

4.  Security Group: Controls ingress and egress to ensure that only authorized traffic can reach the Grafana workspace.

5.  Grafana workspace is secured by restricting access based on prefix lists and subnet configurations.

* **HIP Team** will copy the parameters.json to the project's IAC Repository. The project team will update the parameters JSON based on the available parameters in their own project repository.