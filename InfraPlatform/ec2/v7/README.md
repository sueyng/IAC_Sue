# EC2 Instance Template v7

**Amazon EC2** provides a wide selection of instance types optimized to fit different use cases. Instance types comprise varying combinations of CPU, memory, storage, and networking capacity and give you the flexibility to choose the appropriate mix of resources for your applications. Each instance type includes one or more instance sizes, allowing you to scale your resources to the requirements of your target workload. This template provisions `EC2 instance` based on the parameter values that will be passed using a parameter file e.g., `params.json`.

## What's New in v7

- **Extended VPC CIDR Support**: Added support for **VpcCidr4** and **VpcCidr5** parameters, allowing up to 5 VPC CIDR ranges for infrastructure HTTPS egress rules (previously limited to 3)
- **Enhanced Network Flexibility**: Better support for complex multi-VPC and hybrid cloud architectures requiring multiple CIDR ranges
- **Version Consistency**: All template descriptions updated to v7 for proper version tracking

## Deployment Options

Version 7 now provides **TWO deployment approaches** (inherited from v6 with enhancements):

### Option 1: Original 3-Phase Deployment (Standard)
**Use this for**: Complex scenarios requiring separate security groups for different purposes (Infra, App, Deployment)

This template provisions the following resources:
* IAM Role for EC2 instance
* EC2 Instance Profile
* EC2 Key Pair
* Launch Template
* Multiple Security Groups (Infra, App, Deployment)
* EC2 Instance
* EBS Volume

**Templates**: `cf-ec2-launchTemplate.yaml`, `cf-ec2-securitygroups.yaml`, `cf-ec2.yaml`

### Option 2: Single-Template Deployment (Simplified)
**Use this for**: Deployment servers with simplified security group requirements

This template provisions ALL resources in one stack:
* Deployment Security Group (Primary - with infrastructure + Ansible + DB rules)
* IAM Role for EC2 instance (or use custom role)
* EC2 Instance Profile
* EC2 Key Pair (auto-created with SSM storage)
* Launch Template
* EC2 Instance (NO public IP by default)
* EBS Data Volume (Optional)

**Template**: `cf-ec2-deployment.yaml`

**Key Features**:
- ✅ Single-template deployment (no multi-phase orchestration)
- ✅ Integrated security group (no separate template needed)
- ✅ No public IP assignment (private deployment servers)
- ✅ EC2 Key Pair auto-creation with SSM Parameter Store integration
- ✅ Custom IAM role support
- ✅ IMDSv2 enforcement
- ✅ Console-first deployment
- ✅ **NEW in v7**: Support for up to 5 VPC CIDR ranges (VpcCidr1-5)

**When to Use Single-Template Deployment**:
- Deployment/utility servers
- Servers managed by Ansible
- Internal workload servers (no ALB required)
- Simplified security group requirements

**When to Use 3-Phase Deployment**:
- Complex multi-tier applications
- Servers requiring multiple specialized security groups
- Existing deployments already using v6/v7
- Need separate Infra, App, and Deployment security groups

---

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
| HasCustomEC2IAMRole | String | yes, no | Yes |
| CustomEC2IAMRoleName | String | e.g., custom-ec2-role-name | No (Required if HasCustomEC2IAMRole is 'yes') |
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
| CreateAppSecurityGroup | String | yes, no | Yes |
| CreateDeploymentSecurityGroup | String | yes, no | Yes |
| ALBSecurityGroupId | String | e.g., sg-0123456789abcdef0 | No |
| AnsibleServerIP1 | String | IP Address of the first Ansible server in x.x.x.x/32 format | No |
| AnsibleServerIP2 | String | IP Address of the second Ansible server in x.x.x.x/32 format | No |
| EC2AppSecurityGroupName | String | e.g., xyz-nprd-sg-ec2-web | Yes if CreateAppSecurityGroup is 'yes' |
| EC2DeploymentSecurityGroupName | String | e.g., xyz-nprd-sg-ec2-deployment-web | Yes if CreateDeploymentSecurityGroup is 'yes' |

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
| EC2InfraSecurityGroupID | String | e.g., sg-1234567890abcdef0 | Yes (Created in Launch Template) |
| EC2AppSecurityGroupID | String | e.g., sg-0987654321fedcba0 | No (Created in Security Groups if CreateAppSecurityGroup is 'yes') |
| EC2DeploymentSecurityGroupID | String | e.g., sg-1122334455aabbcc0 | No (Created in Security Groups if CreateDeploymentSecurityGroup is 'yes') |

---

### Single-Template Deployment (cf-ec2-deployment.yaml)

**Single-step deployment** - all resources in one stack!

| ParameterKey | Value Type | Allowed Values | Mandatory | Description |
|--------------|------------|----------------|-----------|-------------|
| **General** |
| AppShortName | String | e.g., myapp, xyz | Yes | Application identifier |
| EnvName | String | nprd, nprd-dev, nprd-sit, nprd-uat, nprd-pp, prod, prod-a, prod-b, prod-c | Yes | Environment designation |
| **VPC and Network** |
| VpcId | AWS::EC2::VPC::Id | e.g., vpc-0123456789abcdef0 | Yes | VPC where resources will be created |
| EC2DeploymentSecurityGroupName | String | e.g., xyz-nprd-sg-ec2-deployment | Yes | Name for primary security group |
| **Database Access** |
| VPCSubnetCidrDBAZ1 | String | e.g., 10.0.152.0/24 | Yes | Database subnet CIDR (AZ1) |
| VPCSubnetCidrDBAZ2 | String | e.g., 10.0.153.0/24 | Yes | Database subnet CIDR (AZ2) |
| VPCSubnetCidrDBAZ3 | String | e.g., 10.0.154.0/24 | No | Database subnet CIDR (AZ3 - optional) |
| ProdDBPort | String | Default: 53341 | Yes | Production database port |
| NProdDBPort | String | Default: 53331 | Yes | Non-production database port |
| **IAM Role** |
| EC2IAMRoleName | String | e.g., xyz-nprd-ec2-role | Yes | IAM role name |
| HasCustomEC2IAMRole | String | yes, no | Yes (Default: no) | Use existing custom IAM role? |
| CustomEC2IAMRoleName | String | e.g., xyz-custom-role | No | Custom IAM role name (if HasCustomEC2IAMRole=yes) |
| EC2InstanceProfileName | String | e.g., xyz-nprd-ec2-profile | Yes | Instance profile name |
| **Key Pair and Launch Template** |
| EC2KeyPairName | String | e.g., xyz-nprd-keypair | Yes | Key pair name (auto-created) |
| EC2LaunchTemplateName | String | e.g., xyz-nprd-ec2-lt | Yes | Launch template name |
| **EC2 Instance** |
| AvailabilityZone | AWS::EC2::AvailabilityZone::Name | ap-southeast-1a, ap-southeast-1b, ap-southeast-1c | Yes | AZ for EC2 placement |
| SubnetIdappAZ1 | AWS::EC2::Subnet::Id | e.g., subnet-08170d48a795103d2 | Yes | Subnet for EC2 instance |
| AMIId | AWS::EC2::Image::Id | e.g., ami-0adcf082d85f6a445 | Yes | AMI ID for EC2 instance |
| InstanceName | String | e.g., MYAPPSERVER01 | Yes | EC2 instance name tag |
| InstanceType | String | e.g., t3.medium, m5.large | Yes | EC2 instance type |
| Function | String | APP, WEB, DB, UTL, INT, RPT, SYS, DBS | Yes | Server function classification |
| OSVolumeSize | String | Default: 100 | Yes | Root volume size (GiB) |
| DataVolumeSize | String | e.g., 500 or "" | No | Data volume size (leave empty to skip) |
| **Optional Infrastructure** |
| VpcCidr1 | String | e.g., 10.0.0.0/16 | No | VPC CIDR for infrastructure HTTPS egress |
| VpcCidr2 | String | e.g., 10.1.0.0/16 | No | Additional VPC CIDR |
| VpcCidr3 | String | e.g., 10.2.0.0/16 | No | Additional VPC CIDR |
| VpcCidr4 | String | e.g., 10.3.0.0/16 | No | Additional VPC CIDR (quaternary) |
| VpcCidr5 | String | e.g., 10.4.0.0/16 | No | Additional VPC CIDR (quinary) |
| S3PrefixListId | String | e.g., pl-6ca54005 | No | S3 prefix list ID for S3 access |
| HCCVpceCidr | String | e.g., 10.1.0.0/24 | No | HCC VPC endpoint CIDR |
| AnsibleServerIP1 | String | e.g., 10.1.50.100/32 | No | First Ansible server IP (WinRM access) |
| AnsibleServerIP2 | String | e.g., 10.1.50.101/32 | No | Second Ansible server IP |

**Deployment Steps (AWS Console)**:
1. Navigate to CloudFormation Console → Create stack
2. Upload `cf-ec2-deployment.yaml`
3. Fill parameters or upload `parameters-ec2-deployment.json`
4. Acknowledge IAM capabilities
5. Create stack (~3-5 minutes)
6. Retrieve outputs: EC2DeploymentSecurityGroupID, EC2InstanceID, EC2KeyPairID

**Parameter Files**:
- JSON: `env/parameters-ec2-deployment.json` (compact, for pipelines)
- YAML: `env/parameters-ec2-deployment.yaml` (with inline documentation)

---

## Dependencies and Important Notes

1. The EC2InfraSecurityGroupID used in the EC2 Instance template is created during the Launch Template execution. Users must provide this ID when running the EC2 Instance template.

2. The EC2AppSecurityGroupID and EC2DeploymentSecurityGroupID (if applicable) used in the EC2 Instance template are created during the Security Groups template execution. Users must provide these IDs when running the EC2 Instance template.

3. The EC2 Instance template uses SSM Parameters created by the Launch Template for LaunchTemplateId, LaunchTemplateLatestVersionNumber, and EC2InstanceProfileName. These don't need to be provided manually.

4. The DataVolumeSize parameter in the EC2 Instance template is optional. If left blank, no additional data volume will be created.

5. Custom IAM Role functionality (v6):
   - HasCustomEC2IAMRole: Set to 'yes' if you have an existing custom IAM role, 'no' to create a new one.
   - CustomEC2IAMRoleName: Required only when HasCustomEC2IAMRole is 'yes'. Specify the name of your existing custom IAM role.
   - When using a custom role, the template will create an instance profile using the specified custom role name.

6. Conditional parameters in the Security Groups template:
   
   a. CreateAppSecurityGroup and CreateDeploymentSecurityGroup:
      - These parameters determine which security groups will be created.
      - Set to 'yes' to create the corresponding security group, 'no' to skip creation.
      - By default, CreateAppSecurityGroup is set to 'yes' and CreateDeploymentSecurityGroup is set to 'no'.

   b. ALBSecurityGroupId:
      - This parameter is optional.
      - If provided and CreateAppSecurityGroup is 'yes', it will be added to the inbound rules of the EC2AppSecurityGroup, allowing traffic from the Application Load Balancer on port 443.
      - This is typically used for web applications that are behind a load balancer.

   c. AnsibleServerIP1 and AnsibleServerIP2:
      - These parameters are optional.
      - They are used when CreateDeploymentSecurityGroup is set to 'yes'.
      - When provided, these IPs will be whitelisted in the EC2DeploymentSecurityGroup.
      - The EC2DeploymentSecurityGroup will allow inbound traffic on port 5986 from these Ansible server IPs.
      - This setup is typically used for deployment and management purposes, allowing Ansible servers to securely connect to the EC2 instances.

   In summary:
   - If CreateAppSecurityGroup is 'yes': EC2AppSecurityGroup will be created. If ALBSecurityGroupId is provided, it will be added to EC2AppSecurityGroup.
   - If CreateDeploymentSecurityGroup is 'yes': EC2DeploymentSecurityGroup will be created. AnsibleServerIP1 and AnsibleServerIP2 (if provided) will be added to EC2DeploymentSecurityGroup.

   Always ensure you're providing the correct parameters based on your specific use case and security requirements.

## How to use the template

* **HIP Team** will copy the parameters.json to the project's IAC Repository. The project team will update the parameters JSON based on the available parameters in their own project repository.
