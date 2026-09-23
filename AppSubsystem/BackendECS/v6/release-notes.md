# Backend ECS CloudFormation Templates - Release Notes

## Version 6.0 (November 6, 2025)

### 🚀 New Features

#### Extended VPC CIDR Support
- **Additional VPC CIDRs**: Added support for VpcCidr4 and VpcCidr5 parameters
- **Enhanced Multi-VPC Connectivity**: Now supports up to 5 VPC CIDR ranges (previously 3)
- **Security Group Flexibility**: Expanded security group rules to accommodate additional VPC peering and multi-VPC architectures

### 🔧 Improvements

#### Network Security Enhancements
- **Expanded VPC CIDR Rules**: ECS Service Security Group egress rules now support up to 5 VPC CIDR ranges
- **Multi-VPC Architecture Support**: Better support for complex network topologies with multiple VPC peerings

### 🛠️ Technical Details

#### New Parameters (Optional)
```yaml
VpcCidr4: ""                      # Quaternary VPC CIDR (optional)
VpcCidr5: ""                      # Quinary VPC CIDR (optional)
```

#### Updated Documentation
- **README.md**: Updated parameter tables and security considerations
- **parameters-backend-ecs.yaml**: Added VpcCidr4 and VpcCidr5 with inline documentation
- **parameters-ecs-service.yaml**: Added VpcCidr4 and VpcCidr5 with inline documentation

### 📋 Migration Notes

#### From v5 to v6
1. **Backward Compatible**: No breaking changes - existing v5 deployments will continue to work
2. **Optional Parameters**: VpcCidr4 and VpcCidr5 are optional with empty string defaults
3. **No Template Changes Required**: Existing stacks can be updated without parameter changes
4. **Incremental Adoption**: Add new VPC CIDRs only when needed for your architecture

#### Configuration Example
```json
{
  "ParameterKey": "VpcCidr4",
  "ParameterValue": "10.194.0.0/16"
},
{
  "ParameterKey": "VpcCidr5",
  "ParameterValue": "10.195.0.0/16"
}
```

### ⚠️ Important Notes

#### Use Cases for Additional VPC CIDRs
- **Multi-VPC Peering**: Connect to 4-5 different VPCs
- **Complex Network Topologies**: Enterprise architectures with multiple network segments
- **Hybrid Cloud**: Additional on-premises network ranges via VPN/Direct Connect
- **Cross-Region VPC Peering**: Additional VPC CIDRs from other AWS regions

---

## Version 5.0 (October 30, 2025)

### 🚀 New Features

#### Enhanced Network Security
- **ElastiCache Dedicated Subnets**: Added support for optional dedicated ElastiCache subnets (`ElasticacheSubnetAZ1/AZ2/AZ3`)
- **Dual Network Configuration**: Maintains backward compatibility with VPC-wide ElastiCache access while adding dedicated subnet support

#### Dynamic Port Management
- **Environment-Based DB Ports**: Automatic port selection based on environment (Production: 53341, Non-production: 53331)

#### Comprehensive Resource Tagging
- **Standardized Tagging**: All resources now include consistent tags for better resource management
- **Version Tracking**: Added "Version: v5" tag to all resources for easy identification
- **Cost Allocation**: Enhanced tagging for cost management and organizational visibility

### 🔧 Improvements

#### Security Group Enhancements
- **Conditional Egress Rules**: ElastiCache egress rules are only created when ElastiCache subnet parameters are provided
- **Flexible Network Access**: Support for both traditional VPC subnet access and dedicated ElastiCache subnet access

#### Template Documentation
- **Updated README**: Comprehensive documentation updates for v5 features
- **Configuration Examples**: Practical examples for new ElastiCache and network configurations
- **Troubleshooting Guide**: Enhanced troubleshooting section with v5-specific issues

#### Resource Management
- **Enhanced Resource Naming**: Updated naming conventions to support new v5 features
- **ALB Listener Rule Naming**: Improved naming pattern for ALB listener rules
- **Auto Scaling Target**: Explicit naming for auto scaling targets

### 🛠️ Technical Details

#### New Parameters (Optional)
```yaml
ElasticacheSubnetAZ1: ""          # ElastiCache subnet for AZ1
ElasticacheSubnetAZ2: ""          # ElastiCache subnet for AZ2  
ElasticacheSubnetAZ3: ""          # ElastiCache subnet for AZ3
```

#### New Conditions
```yaml
HasElasticacheSubnetAZ1: !Not [!Equals [!Ref ElasticacheSubnetAZ1, '']]
HasElasticacheSubnetAZ2: !Not [!Equals [!Ref ElasticacheSubnetAZ2, '']]
HasElasticacheSubnetAZ3: !Not [!Equals [!Ref ElasticacheSubnetAZ3, '']]
HasElasticacheSubnetAZ2: !Not [!Equals [!Ref ElasticacheSubnetAZ2, '']]
HasElasticacheSubnetAZ3: !Not [!Equals [!Ref ElasticacheSubnetAZ3, '']]
```

#### Enhanced Security Rules
- **ElastiCache VPC Access**: Always enabled for existing VPC subnets (backward compatibility)
- **ElastiCache Dedicated Access**: Conditional access to dedicated ElastiCache subnets
- **Database Network Access**: Dynamic port access via additional networks

### 📋 Migration Notes

#### From v4 to v5
1. **Backward Compatible**: No breaking changes - existing v4 deployments will continue to work
2. **Optional Features**: All new features are optional with empty string defaults
3. **Parameter Updates**: Update parameter files to include new optional parameters
4. **Gradual Adoption**: New features can be enabled incrementally

#### Configuration Updates
```json
{
  "ParameterKey": "ElasticacheSubnetAZ1",
  "ParameterValue": "10.0.51.0/24"
},
{
  "ParameterKey": "ElasticacheSubnetAZ2",
  "ParameterValue": "10.0.52.0/24"
},
{
  "ParameterKey": "ElasticacheSubnetAZ3",
  "ParameterValue": "10.0.53.0/24"
}
```

### 🏷️ Resource Tagging Strategy

All resources now include standardized tags:
- **Name**: Resource-specific identifier
- **Application**: Application short name
- **Environment**: Deployment environment
- **Service**: ECS service name
- **Component**: Resource type (e.g., "TargetGroup", "SecurityGroup")
- **Version**: "v5" for template version tracking
- **ManagedBy**: "CloudFormation"
- **CreatedBy**: "ECS-Service-Template"

### 🐛 Bug Fixes

#### Port Configuration Issues
- **Health Check Alignment**: Fixed documentation examples for port consistency between container and health checks
- **ECS Circuit Breaker**: Enhanced troubleshooting guide for deployment circuit breaker issues

#### Documentation Updates
- **Version References**: Updated all template references from v4 to v5
- **Sample Configurations**: Updated image tags to use semantic versioning (e.g., v5.2.1)
- **Best Practices**: Added version tagging best practices section

### 🔄 Deployment Process

#### Two-Phase Deployment (Unchanged)
1. **Phase 1**: Infrastructure creation without ECS service (empty secret name)
2. **Phase 2**: Complete service deployment (with populated secrets)

#### New Stack Updates
- **Parameter Files**: Update with new optional ElastiCache subnet parameters
- **Conditional Resources**: New egress rules created only when conditions are met
- **Tagging Application**: All resources receive v5 tags automatically

### 📊 Monitoring & Observability

#### Enhanced Logging
- **Version Identification**: Easy identification of v5 resources through tags
- **Component Tracking**: Clear component identification for troubleshooting

#### Cost Management
- **Tag-Based Allocation**: Enhanced cost allocation through comprehensive tagging
- **Service-Level Tracking**: Improved service-level cost visibility

### ⚠️ Important Notes

#### Version Tagging
- **Container Images**: Recommended to use semantic versioning aligned with v5 (e.g., v5.2.1)
- **ADOT Collector**: Updated to use specific version (v0.104.0) instead of :latest
- **Production Stability**: Avoid :latest tags for production deployments

#### Network Configuration
- **Dual Configuration Support**: Both VPC-wide and dedicated ElastiCache subnet access patterns supported
- **Conditional Rules**: Security group rules are created based on parameter availability
- **Backward Compatibility**: Existing network configurations continue to work unchanged

### 🔮 Future Considerations

#### Planned Enhancements
- Additional network security features
- Enhanced monitoring and observability integration
- Extended auto-scaling capabilities

#### Template Evolution
- Continued focus on backward compatibility
- Gradual introduction of new features
- Community feedback integration

---

## Version History

### v6.0 (November 6, 2025)
- Extended VPC CIDR support (VpcCidr4 and VpcCidr5)
- Enhanced security group rules for multi-VPC architectures
- Improved documentation for complex network topologies

### v5.0 (October 30, 2025)
- Enhanced network security with dedicated ElastiCache subnets
- Comprehensive resource tagging implementation
- Dynamic port management for different environments
- Additional application network support via prefix lists

### v4.0 (Previous Release)
- Core ECS service deployment functionality
- Auto-scaling support
- Health check configuration
- Two-phase deployment process

---

**Template Compatibility**: CloudFormation, AWS CDK
**Supported Regions**: All AWS regions with ECS Fargate support
**Minimum IAM Permissions**: ECS, ALB, CloudWatch, Secrets Manager, SSM, VPC management