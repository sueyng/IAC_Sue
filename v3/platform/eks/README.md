# ELASTIC KUBERNETES SERVICE (EKS)

**Amazon Elastic Kubernetes Service** (Amazon EKS) is a managed service that eliminates the need to install, operate, and maintain your own Kubernetes control plane on Amazon Web Services (AWS). Kubernetes is an open-source system that automates the management, scaling, and deployment of containerized applications. For more information visit this [site](https://docs.aws.amazon.com/eks/latest/userguide/what-is-eks.html).

## Resources Provisioned

These templates provision the following resources:
* EKS Cluster
* Fargate Profiles
* Network Load Balancer (NLB)
* Application Load Balancer (ALB) Target Group
* KMS Key and Alias
* Secret Manager Secrets
* IAM Managed Policies and Roles
* Security Groups
* EKS Add-ons

## Template Overview

1. **cf-eks.yaml**: Main template for EKS cluster creation and associated resources.
2. **cf-eks-fp.yaml**: Template for creating Fargate profiles for custom application namespaces.
3. **cf-eks-secrets.yaml**: Template for creating AWS Secrets Manager secrets.
4. **cf-nlb-tg-alb.yaml**: Template for creating an NLB with ALB as the target.

## Dependencies and Conditions

### cf-eks.yaml
- Creates SSM Parameters that are used by other templates.
- Conditions based on production environment and subnet configurations.
- Creates default Fargate profiles for 'default', 'kube-system', and monitoring namespaces.

### cf-eks-fp.yaml
- Depends on the EKS cluster created by cf-eks.yaml.
- Uses SSM Parameters created by cf-eks.yaml for cluster name, pod execution role, and OIDC provider.
- Allows creation of up to 5 custom namespaces.

### cf-eks-secrets.yaml
- Depends on the KMS key created in cf-eks.yaml.
- Uses environment mapping for sub-environments (e.g., sit-a, sit-b).

### cf-nlb-tg-alb.yaml
- Can use the Ingress ALB ARN created by the EKS cluster (if provided).
- Creates security group rules based on provided subnet CIDRs.

## Parameters and Their Valid Values

### EKS Cluster (cf-eks.yaml)

| ParameterKey | ValueType | Allowed Values | Mandatory |
|--------------|-----------|----------------|-----------|
| AppShortName | String | e.g., my-application | Yes |
| EnvName | String | nprd, nprd-dev, nprd-sit1, nprd-sit2, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b, prod, prod-a, prod-b | Yes |
| AppSubnetIds | List<AWS::EC2::Subnet::Id> | e.g., subnet-123232,subnet-2345123,subnet-323122 | Yes |
| AWSRegion | String | ap-southeast-1 | Yes |
| VpcId | AWS::EC2::VPC::Id | e.g., vpc-120324 | Yes |
| VPCSubnetCidrAppAZ1 | String | e.g., 10.0.1.0/24 | Yes |
| VPCSubnetCidrAppAZ2 | String | e.g., 10.0.2.0/24 | Yes |
| VPCSubnetCidrAppAZ3 | String | e.g., 10.0.3.0/24 | No |
| AppIngressNodePort | String | e.g., 8080 | Yes |
| InternalIngressNodePort | String | e.g., 8081 | Yes |
| HIPDeploymentServer01 | String | e.g., 10.0.2.4 | Yes |
| HIPDeploymentServer02 | String | e.g., 10.0.2.5 | Yes |
| DeploymentServerUTL01 | String | e.g., 10.0.2.8 | Yes |
| NLBIngressSecurityGroupId | String | e.g., sg-0123456789abcdef0 | No |

### EKS Fargate Profile (cf-eks-fp.yaml)

| ParameterKey | ValueType | Allowed Values | Mandatory |
|--------------|-----------|----------------|-----------|
| AppShortName | String | e.g., my-application | Yes |
| EnvName | String | nprd, nprd-dev, nprd-sit1, nprd-sit2, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b, prod, prod-a, prod-b | Yes |
| FargateProfileName | String | e.g., my-app-fp | Yes |
| Namespace1 | String | e.g., namespace1 | Yes |
| Namespace2 | String | e.g., namespace2 | Yes |
| Namespace3 | String | e.g., namespace3 | No |
| Namespace4 | String | e.g., namespace4 | No |
| Namespace5 | String | e.g., namespace5 | No |
| AppSubnetIds | List<AWS::EC2::Subnet::Id> | e.g., subnet-123232,subnet-2345123,subnet-323122 | Yes |

### NLB, Target Group, and ALB (cf-nlb-tg-alb.yaml)

| ParameterKey | ValueType | Allowed Values | Mandatory |
|--------------|-----------|----------------|-----------|
| AppShortName | String | e.g., my-application | Yes |
| EnvName | String | nprd, nprd-dev, nprd-sit1, nprd-sit2, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b, prod, prod-a, prod-b | Yes |
| AppSubnetIds | List<AWS::EC2::Subnet::Id> | e.g., subnet-123232,subnet-2345123,subnet-323122 | Yes |
| VpcId | AWS::EC2::VPC::Id | e.g., vpc-120324 | Yes |
| Function | String | APP, WEB | Yes |
| IngressALBArn | String | e.g., arn:aws:elasticloadbalancing:us-west-2:123456789012:loadbalancer/app/example-lb/1 | Yes |
| HealthCheckPath | String | e.g., /healthz | Yes |
| InternetALBSubnetAZ1 | String | e.g., 10.0.1.0/24 | No |
| InternetALBSubnetAZ2 | String | e.g., 10.0.2.0/24 | No |
| InternetALBSubnetAZ3 | String | e.g., 10.0.3.0/24 | No |
| HSGWSubnet1 | String | e.g., 10.0.4.0/24 | No |
| HSGWSubnet2 | String | e.g., 10.0.5.0/24 | No |

### EKS Secrets (cf-eks-secrets.yaml)

| ParameterKey | ValueType | Allowed Values | Mandatory |
|--------------|-----------|----------------|-----------|
| AppShortName | String | e.g., my-application | Yes |
| EnvName | String | nprd, nprd-dev, nprd-sit1, nprd-sit2, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b, prod, prod-a, prod-b | Yes |

## How to Provision Templates

1. HIP Team will copy the parameters.json files to the project's IAC Repository. 
2. Project team will update the parameters json based on the available parameters in their own project repository.
3. Below is an example of how your directory would look like:
```
nprd-dev
|_ parameters-eks.json
|_ parameters-eks-fp.json
|_ parameters-nlb-tg-alb.json
|_ parameters-eks-secrets.json
```
4. Provision the templates in the following order:
   a. EKS Cluster (`cf-eks.yaml`)
   b. EKS Fargate Profile (`cf-eks-fp.yaml`)
   c. Network Load Balancer, Target Group, and Application Load Balancer (`cf-nlb-tg-alb.yaml`)
   d. EKS Secrets (`cf-eks-secrets.yaml`)

## Important Notes

1. The EKS Cluster stack (`cf-eks.yaml`) must be fully created before provisioning other stacks.
2. The KMS key SSM parameter created by the EKS Cluster stack is required for the EKS Secrets stack.
3. The Fargate Profile stack uses SSM parameters created by the EKS Cluster stack.
4. The NLB stack can use the Ingress ALB ARN as a target. This ALB is typically created by the development team using the AWS Load Balancer Controller, which deploys the ALB based on Kubernetes Ingress resources.
5. For production environments (prod, prod-a, prod-b), resources have a DeletionPolicy and UpdateReplacePolicy set to 'Retain'.
6. The EKS Secrets stack uses a mapping for sub-environments (e.g., sit-a, sit-b) to determine the parent environment for KMS key lookup.
7. The NLB stack creates conditional security group rules based on provided subnet CIDRs and HSGW subnets.

Always ensure you have the necessary permissions and have configured your AWS CLI or deployment tool correctly before running these templates.