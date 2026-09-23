# 📊 AWS Monitoring Dashboards - Grafana JSON Toolkit

This repository contains pre-built Grafana dashboards for monitoring key AWS services. Each JSON file is a self-contained dashboard that can be imported into Grafana. These dashboards use CloudWatch metrics and are compatible with AWS Managed Grafana or any Grafana instance with AWS CloudWatch as a data source.

---

## 🔧 Prerequisites

- Grafana with CloudWatch data source configured
- Required IAM permissions to access CloudWatch metrics
- Optional: AWS Observability (AMP + ADOT) for ECS metrics

---

## 📁 Dashboard Overview

| File Name       | Service        | Description                                                                 |
|----------------|----------------|-----------------------------------------------------------------------------|
| `alb.json`      | ALB             | Monitors ALB 4XX/5XX errors, target health, request counts, and latency    |
| `apigw.json`    | API Gateway     | Tracks API Gateway metrics like latency, error rates, and integration failures |
| `ecs.json`      | ECS (Fargate)   | Visualizes CPU, memory, task count, and service health (via ADOT/AMP)      |
| `elasticache.json` | ElastiCache (Redis) | Provides memory usage, CPU, connections, eviction count, and engine stats |
| `glue.json`     | AWS Glue        | Displays job duration, DPU usage, failures, and trigger executions         |
| `lambda.json`   | AWS Lambda      | Monitors invocations, errors, duration, throttles, and concurrent executions |
| `rds.json`      | RDS             | Includes CPU, memory, disk space, DB connections, and agent job failures   |
| `sqs.json`      | SQS             | Tracks sent/received/deleted messages, queue size, and age of oldest msg   |

---

## 📥 Importing a Dashboard

1. Open Grafana and go to **Dashboards > Import**
2. Upload the respective JSON file
3. Select your **CloudWatch datasource**
4. Set template variables (like `$region`, `$dbinstanceidentifier`, etc.) if prompted

---

## 📌 Notes

- You may need to customize variable values like `$queue`, `$region`, `$dbinstanceidentifier` based on your environment.
- For ECS dashboards, ADOT collector should be configured to scrape Prometheus metrics from containers and push to AMP (Amazon Managed Prometheus).

---

## 🛡️ License

MIT License. Feel free to use and modify for internal or production use.

---

## 👩‍💻 Maintainer

Created and maintained by your cloud engineering team for platform monitoring needs.
