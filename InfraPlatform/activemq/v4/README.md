### AMAZON MQ ACTIVEMQ SETUP

Amazon MQ ActiveMQ is a fully managed message broker service for Apache ActiveMQ, This template provisions a highly available ActiveMQ broker across multiple AZs, including all necessary security and networking configurations.

This template provisions the following resources:

* Amazon MQ Broker: ActiveMQ broker in multi-AZ configuration.
* Security Group: Configures access to the broker and allows traffic from specified subnets.

Provisioning of this template is straightforward. See this instruction.

### Parameters and Its Valid Values:

|ParameterKey  | ValueType | Allowed Values  | 
|---|---|---|
|AppShortName  |   <i>String</i>               |   e.g my-application  |
|EnvName     |   <i>String</i>               |  nprd, nprd-dev, nprd-sit1, nprd-sit2, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b, prod, prod-a, prod-b |
|VpcId           | <i>AWS::EC2::VPC::Id</i>  | e.g vpc-120324                |
|VPCSubnetCidrAppAZ1 |  <i>String</i>   | e.g., 10.0.1.0/24   |
|VPCSubnetCidrAppAZ2 |  <i>String</i>   | e.g., 10.0.2.0/24   |
|VPCSubnetCidrAppAZ3 |  <i>String</i>   | e.g., 10.0.3.0/24   |
|VPCSubnetIdappAZ1  |   <i>String</i>               |  e.g., subnet-1234567890abcdef1  |
|VPCSubnetIdappAZ2       |   <i>String</i>               |  e.g., subnet-0987654321fedcba1  |
|DeploymentServer01       |   <i>String</i>               |  e.g., 192.168.1.10/32 (IP address of the tooling server)|
|InstanceType |  <i>String</i>   | e.g., mq.m5.large   |
|MQPassword |  <i>String</i>   | e.g., your-password   |  


### How to Provision Template
The project team will need to create and update the parameters file based on the available parameters for their specific environment. Follow the steps below to provision the template:

### Prepare the parameters-activemq.json file:

1.  The HIP team will copy the parameters.json template into the project's IAC repository.
2.  The project team should update the values of the parameters in the parameters-activemq.json based on their environment and networking configuration.
3.  Run the CloudFormation Stack using the Azure DevOps Pipeline and Releases.

### Review the Stack Creation:

1.  Verify the successful creation of resources in the AWS Management Console.
2.  Ensure that the ActiveMQ broker is up and running across multiple availability zones.
