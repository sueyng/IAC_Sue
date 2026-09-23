# AWS SQS Template - Release Notes
## Version 2.0.0 - SNS Subscription and Resource Retention
**Release Date:** September 07, 2026

### New Features

- Added the optional `CustomSnsTopicName` parameter to allow project team to custom their SNS topic name

## Version 1.1.0 - SNS Subscription and Resource Retention
**Release Date:** August 26, 2026

### New Features

- Added the `EnableSnsSubscription` true/false parameter, defaulting to `false` for backward-compatible deployments.
- Added conditional creation of an SNS topic named `{AppShortName}-{EnvName}-sns-{QueueName}`.
- Added an SNS-to-SQS subscription with raw message delivery.
- Added the SQS queue policy required for the SNS topic to publish messages to the queue.
- Added the `SnsTopicArn` output for publishers and cross-stack references.

### Resource Retention

- Added environment-based `DeletionPolicy` and `UpdateReplacePolicy` handling to the SNS topic, subscription, and queue policy.
- Production environments retain messaging resources during stack deletion or replacement.
- Non-production environments delete messaging resources during stack deletion or replacement.

### Documentation

- Updated the v2 README with SNS configuration, deployment, troubleshooting, and retention guidance.
- Updated the v2 parameter example with the SNS subscription toggle.

## Version 1.0.0 - Initial Release
**Release Date:** June 11, 2025

### 🎉 New Features

#### Standard SQS Queue Template
- **New CloudFormation Template**: `cf-sqs.yaml` - Comprehensive template for creating Standard SQS queues with Dead Letter Queue support
- **Optimized Defaults**: Production-ready default configurations for high-performance message processing
- **Enterprise-Ready**: Built-in security, reliability, and monitoring capabilities

#### Core Queue Functionality
- **Standard SQS Queues**: Full support for Standard SQS queues with at-least-once delivery
- **Dead Letter Queue Integration**: Automatic DLQ creation and configuration for failed message handling
- **Message Processing Control**: Configurable visibility timeouts, retention periods, and delivery attempts
- **Long Polling Support**: Built-in long polling configuration to reduce costs and improve performance

#### Advanced Configuration Options
- **Message Size Control**: Configurable maximum message size up to 256KB
- **Delivery Delay**: Optional message delay configuration for scheduled processing
- **Retry Logic**: Customizable maximum receive count before DLQ routing
- **Batch Processing Support**: Optimized settings for both real-time and batch processing scenarios

### 🔧 Technical Specifications

#### Queue Types Supported
- **Standard SQS Queues**: High-throughput, at-least-once delivery
- **Dead Letter Queues**: Automatic failure handling and message preservation
- **Note**: FIFO queues not supported in this version (by design for simplicity)

#### Performance Features
- **Long Polling**: Default 20-second long polling to minimize empty receives
- **Flexible Timeouts**: Visibility timeout range from 0 to 12 hours (43,200 seconds)
- **Message Retention**: Configurable retention from 1 minute to 14 days
- **Delivery Attempts**: 1-1000 delivery attempts before DLQ routing

#### Security Features
- **Server-Side Encryption**: AWS managed KMS encryption enabled by default
- **Custom KMS Support**: Optional custom KMS key integration for enhanced security
- **IAM Integration**: Compatible with existing IAM roles and policies
- **VPC Endpoint Support**: Works with VPC endpoints for private communication

### 📋 Template Parameters

#### Mandatory Parameters (3)
- **AppShortName**: Application identifier for consistent naming
- **EnvName**: Environment specification with 17 supported environment types
- **QueueName**: Descriptive queue identifier

#### Optional Parameters (11)
- **Queue Configuration**: 6 configurable performance parameters
- **Dead Letter Queue**: 2 DLQ-specific settings
- **Security Settings**: 2 encryption and KMS parameters
- **Metadata**: 1 description parameter

#### Environment Support
- **Non-Production**: nprd, nprd-dev, nprd-sit1, nprd-sit2, nprd-sit, nprd-sit-a, nprd-sit-b
- **User Acceptance Testing**: nprd-uat, nprd-uat-a, nprd-uat-b
- **Pre-Production**: nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b
- **Production**: prod, prod-a, prod-b

### 🚀 Deployment Capabilities

#### Single Queue Deployment
- Simple CloudFormation stack deployment with parameter file
- Immediate queue creation with optimized default settings
- Automatic DLQ creation and linking

#### Multiple Queue Deployment
- Azure DevOps pipeline integration support
- Separate parameter files for different queue types
- Batch deployment capabilities for complex architectures

#### Parameter File Support
- **Complete Parameter File**: `parameters-sqs.json` with production-ready defaults
- **Pre-configured Templates**: Optimized configurations for common use cases
- **Pipeline-Ready**: Designed for CI/CD integration

### 🎯 Use Case Templates

#### High-Throughput Processing
- Optimized for fast message processing with minimal latency
- Short visibility timeouts and aggressive retry policies
- Maximum long polling for cost efficiency

#### Batch Processing
- Extended visibility timeouts for long-running tasks
- Configurable delay seconds for scheduled processing
- Higher retry counts for fault tolerance

#### Notification Systems
- Quick processing with short retention periods
- Optimized for real-time notifications
- Lightweight configuration for cost efficiency

### 🔐 Security & Compliance

#### Encryption
- **Default Encryption**: Server-side encryption with AWS managed keys
- **Custom KMS**: Support for customer-managed encryption keys
- **Key Rotation**: Compatible with automatic key rotation policies

#### Access Control
- **IAM Integration**: Works with existing IAM roles and policies
- **Resource-Based Policies**: Support for queue-level access policies
- **Cross-Account Access**: Configurable for multi-account architectures

### 📊 Monitoring & Observability

#### CloudWatch Integration
- **Automatic Metrics**: Queue depth, message age, and processing rates
- **DLQ Monitoring**: Separate metrics for dead letter queue analysis
- **Cost Tracking**: Visibility into API calls and storage costs

#### Tagging Strategy
- **Consistent Tagging**: Automatic tagging with app, environment, and queue identifiers
- **Cost Allocation**: Tags support cost allocation and resource management
- **Compliance**: Tags facilitate compliance and governance requirements

### 🔗 Integration Support

#### AWS Service Integration
- **Lambda Functions**: Direct event source mapping support
- **SNS Integration**: Fan-out message patterns
- **EventBridge**: Event-driven architecture support
- **ECS/Fargate**: Container-based message processing

#### Application Integration
- **SDK Compatibility**: Works with all AWS SDKs
- **URL/ARN Outputs**: Ready-to-use queue identifiers
- **Cross-Stack References**: CloudFormation output integration

### 📋 Documentation

#### Comprehensive Guide
- **Parameter Documentation**: Detailed parameter descriptions with examples
- **Configuration Templates**: Pre-built configurations for common scenarios
- **Best Practices**: Performance, security, and cost optimization guidance
- **Troubleshooting**: Common issues and resolution steps

#### Integration Examples
- **Lambda Integration**: Event source mapping examples
- **Application Code**: SDK usage patterns
- **Pipeline Integration**: Azure DevOps deployment examples

### 🔄 Performance Optimizations

#### Default Settings
- **Long Polling**: 20-second long polling enabled by default
- **Visibility Timeout**: 5-minute default suitable for most workloads
- **Message Retention**: 14-day retention for reliability
- **DLQ Configuration**: 5 delivery attempts before DLQ routing

#### Cost Optimization
- **Reduced Empty Polls**: Long polling minimizes unnecessary API calls
- **Appropriate Retention**: Balanced retention periods for cost vs. reliability
- **Encryption Efficiency**: AWS managed keys for cost-effective encryption

### 🔍 Quality Assurance

#### Template Validation
- **CloudFormation Syntax**: Comprehensive syntax validation
- **Parameter Constraints**: Min/max value validation for all parameters
- **Conditional Logic**: Tested conditional resource creation

#### Documentation Quality
- **Complete Examples**: Real-world parameter configurations
- **Clear Requirements**: Mandatory vs. optional parameter identification
- **Best Practices**: Industry-standard recommendations

---

## Compatibility Notes

- **AWS Regions**: Compatible with all AWS regions supporting SQS
- **CloudFormation**: Standard CloudFormation capabilities required
- **Dependencies**: No external dependencies or custom resources
- **Queue Types**: Standard SQS queues only (FIFO queues excluded by design)

## Known Limitations

- **FIFO Queues**: FIFO queues not supported (design decision for simplicity)
- **Cross-Region**: Single region deployment (multi-region requires separate stacks)
- **Message Size**: Limited to 256KB per message (SQS standard limit)
- **Throughput**: Standard queue throughput limits apply (nearly unlimited)

## Performance Characteristics

- **Throughput**: Nearly unlimited messages per second
- **Latency**: Sub-second message delivery in most cases
- **Availability**: 99.9% availability SLA from AWS
- **Durability**: Messages stored redundantly across multiple AZs

## Future Considerations

- Potential support for FIFO queues in separate template
- Enhanced monitoring and alerting configurations
- Advanced routing and filtering capabilities
- Integration templates for specific AWS services

---

**Template Version**: 1.1.0  
**Documentation Version**: 1.1.0  
**Compatibility**: AWS CloudFormation, Azure DevOps Pipelines, Standard SQS Queues  
**AWS Services**: Amazon SQS, AWS KMS, Amazon CloudWatch