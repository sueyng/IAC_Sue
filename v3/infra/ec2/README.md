# EC2 Instance Template

**Amazon EC2** provides a wide selection of instance types optimized to fit different use cases. Instance types comprise varying combinations of CPU, memory, storage, and networking capacity and give you the flexibility to choose the appropriate mix of resources for your applications. Each instance type includes one or more instance sizes, allowing you to scale your resources to the requirements of your target workload. This template provisions `EC2 instance` based on the parameter values that will be passed using a parameter file e.g., `params.json`.

This template provisions the following resources:
* IAM Role for EC2 instance
* EC2 Instance Profile
* EC2 Key Pair
* Launch Template
* Security Group
* EC2 Instance
* EBS Volume

## Provisioning

Resource provisioning consists of sequential steps that must be observed diligently. Since prior steps are prerequisites to another.

Provisioning steps are as follows:
1. Provision base components like launch template, SSH key pairs, roles, infra security group and instance profiles `cf-ec2-launchTemplate.yaml`
2. Provision security groups `cf-ec2-securitygroups.yaml`
3. Finally, provision servers in the form of EC2 `cf-ec2.yaml`

## Parameters and Their Valid Values

### Launch Template Provisioning (cf-ec2-launchTemplate.yaml)

| ParameterKey | Value Type | Allowed Values | Mandatory |
|--------------|------------|-----------------|-----------|
| AppShortName | String | e.g., myapp | Yes |
| EnvName | String | nprd, nprd-dev, nprd-sit1, nprd-sit2, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b, prod, prod-a, prod-b | Yes |
| VpcId | AWS::EC2::VPC::Id | e.g., vpc-0123456789abcdef0 | Yes |
| EC2IAMRoleName | String | e.g., xyz-nprd-ec2-role | Yes |
| EC2InstanceProfileName | String | e.g., xyz-nprd-ec2-profile | Yes |
| EC2KeyPairName | String | e.g., xyz-nprd-keypair | Yes |
| EC2LaunchTemplateName | String | e.g., xyz-nprd-ec2-launch-template | Yes |
| EC2InfraSecurityGroupName | String | e.g., xyz-nprd-sg-ec2-base | Yes |

### Security Groups (cf-ec2-securityGroups.yaml)

| ParameterKey | Value Type | Allowed Values | Mandatory |
|--------------|------------|-----------------|-----------|
| AppShortName | String | e.g., myapp | Yes |
| EnvName | String | nprd, nprd-dev, nprd-sit1, nprd-sit2, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b, prod, prod-a, prod-b | Yes |
| VpcId | AWS::EC2::VPC::Id | e.g., vpc-0123456789abcdef0 | Yes |
| Function | String | APP, WEB, DB, UTL, INT, RPT, SYS | Yes |
| ALBSecurityGroupId | String | e.g., sg-0123456789abcdef0 | No |
| AnsibleServerIP1 | String | IP Address of the first Ansible server in x.x.x.x/32 format | No |
| AnsibleServerIP2 | String | IP Address of the second Ansible server in x.x.x.x/32 format | No |
| EC2AppSecurityGroupName | String | e.g., xyz-nprd-sg-ec2-web | Yes if Function is Non-UTL, otherwise No |
| EC2DeploymentSecurityGroupName | String | e.g., xyz-nprd-sg-ec2-deployment-web | Yes if Function is UTL, otherwise No |

### EC2 Instance (cf-ec2.yaml)

| ParameterKey | Value Type | Allowed Values | Mandatory |
|--------------|------------|-----------------|-----------|
| AppShortName | String | e.g., myapp | Yes |
| AvailabilityZone | String | ap-southeast-1a, ap-southeast-1b, ap-southeast-1c | Yes |
| SubnetIdappAZ1 | AWS::EC2::Subnet::Id | e.g., subnet-0123456789abcdef0 | Yes |
| EnvName | String | nprd, nprd-dev, nprd-sit1, nprd-sit2, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b, prod, prod-a, prod-b | Yes |
| AMIId | AWS::EC2::Image::Id | e.g., ami-0123456789abcdef0 | Yes |
| InstanceName | String | e.g., MyAppServer | Yes |
| InstanceType | String | e.g., t2.micro | Yes |
| DataVolumeSize | String | e.g., 20 (20 GiB) | No |
| OSVolumeSize | String | e.g., 100 (in GiB) | Yes |
| Function | String | APP, UTL, DB, UTL, RPT, SYS | Yes |
| EC2InfraSecurityGroupID | String | e.g., sg-1234567890abcdef0 | Yes (Created in Launch Template) |
| EC2AppSecurityGroupID | String | e.g., sg-0987654321fedcba0 | No (Created in Security Groups if Function is Non-UTL) |
| EC2DeploymentSecurityGroupID | String | e.g., sg-1122334455aabbcc0 | No (Created in Security Groups if Function is UTL) |

## Dependencies and Important Notes

1. The EC2InfraSecurityGroupID used in the EC2 Instance template is created during the Launch Template execution. Users must provide this ID when running the EC2 Instance template.

2. The EC2AppSecurityGroupID and EC2DeploymentSecurityGroupID (if applicable) used in the EC2 Instance template are created during the Security Groups template execution. Users must provide these IDs when running the EC2 Instance template.

3. The EC2 Instance template uses SSM Parameters created by the Launch Template for LaunchTemplateId, LaunchTemplateLatestVersionNumber, and EC2InstanceProfileName. These don't need to be provided manually.

4. The DataVolumeSize parameter in the EC2 Instance template is optional. If left blank, no additional data volume will be created.

5. The EC2DeploymentSecurityGroupID is only required if the Function is set to UTL in the Security Groups template.

6. Conditional parameters in the Security Groups template:
   
   a. ALBSecurityGroupId:
      - This parameter is optional.
      - If provided, it will be added to the inbound rules of the EC2AppSecurityGroup, allowing traffic from the Application Load Balancer on port 443.
      - This is typically used for web applications that are behind a load balancer.

   b. AnsibleServerIP1 and AnsibleServerIP2:
      - These parameters are optional.
      - They are specifically used when the Function is set to 'UTL' (Utility).
      - When provided and Function is 'UTL', these IPs will be whitelisted in the EC2DeploymentSecurityGroup.
      - The EC2DeploymentSecurityGroup will allow inbound traffic on port 5986 from these Ansible server IPs.
      - This setup is typically used for deployment and management purposes, allowing Ansible servers to securely connect to the EC2 instances.

   In summary:
   - For non-UTL functions: If ALBSecurityGroupId is provided, it will be added to EC2AppSecurityGroup.
   - For UTL function: AnsibleServerIP1 and AnsibleServerIP2 (if provided) will be added to EC2DeploymentSecurityGroup. ALBSecurityGroupId is not typically used in this case.

   Always ensure you're providing the correct parameters based on your specific use case and function type.

## How to use the template

* **HIP Team** will copy the parameters.json to the project's IAC Repository. The project team will update the parameters JSON based on the available parameters in their own project repository.

* Below is an example of how your directory would look like:
```
nprd-dev
|_ parameters-ec2-launchTemplate.json
|_ parameters-ec2-securitygroups.json
|_ parameters-ec2.json
```