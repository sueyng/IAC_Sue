# AMAZON MANAGED PROMETHEUS

**Amazon Managed Service for Prometheus** is a Prometheus-compatible service that monitors and provides alerts on containerized applications and infrastructure at scale. The service is integrated with Amazon Elastic Kubernetes Service (EKS), Amazon Elastic Container Service (ECS), and AWS Distro for OpenTelemetry. visit [this](https://aws.amazon.com/prometheus/) to learn more.

This template provisions the following resources:
* Log Group
* Prometheus Workspace


Provisioning of this template is straight forward. see this [instruction](#how-to-provision-template)
## Parameters and its valid values

|ParameterKey  | ValueType | Allowed Values  | 
|---|---|---|
| AppShortName  |   <i>String</i>               |   e.g my-application  |
|   EnvName     |   <i>String</i>               |  nprd, nprd-dev, nprd-sit1, nprd-sit2, nprd-sit, nprd-sit-a, nprd-sit-b, nprd-uat, nprd-uat-a, nprd-uat-b, nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b, prod, prod-a, prod-b |

## How to provision template

HIP Team will copy the parameters.json to the project's IAC Repository. Project team will update the parameters json base on the available [parameters](#parameters-and-its-valid-values) in their own project repository.