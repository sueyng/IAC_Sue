# Network Load Balancer to Application Load Balancer v5.0

This template provisions an internal Network Load Balancer (NLB) that forwards TCP port 443 traffic to a target Application Load Balancer (ALB) on port 443.

## Traffic Flow

```text
Approved client or API Gateway VPC endpoint
	-> NLB TCP/443 (TCP Pass-Through)
	-> ECS ALB HTTPS/443 (TLS Termination with ACM Certificate)
	-> ECS service container port
```

> **Important (AWS Elastic Load Balancing Requirement):**
> When an NLB targets an ALB (`TargetType: alb`), AWS requires the NLB listener protocol and target group protocol to be **`TCP`**. AWS does **not** support a `TLS` listener protocol on an NLB when forwarding to a target group of type `alb`.
>
> Therefore, the NLB operates in TCP pass-through mode on port 443. The ACM SSL/TLS certificate and SSL policy must be associated with the downstream **ECS Application Load Balancer (ALB) HTTPS listener**, where TLS is terminated.

## Security Groups

Configure these rules for least-privilege access:

| Source | Destination | Protocol and port | Rule |
| --- | --- | --- | --- |
| Approved client or API Gateway VPC endpoint | NLB security group | TCP 443 | NLB ingress, using `PrefixListNLBIngress` or an allowed source security group |
| NLB security group | ECS ALB security group | TCP 443 | NLB egress, using `TargetALBSecurityGroupId` |
| NLB security group | ECS ALB security group | TCP 443 | ECS ALB ingress, with the NLB security group as source |
| ECS ALB security group | ECS task security group | Container listener port | ECS ALB egress and task ingress |

Security groups are stateful; return traffic does not require separate rules.

## Parameters

Set values only between `PARAMETERS_START` and `PARAMETERS_END` in [env/parameters-nlb-tg-alb.yaml](env/parameters-nlb-tg-alb.yaml).

`TargetALBArn` and `TargetALBSecurityGroupId` must both be set when the NLB forwards traffic to an ECS ALB. The target ALB must be in the same VPC as the NLB and must have an HTTPS listener on port 443.

## Deployment Order

1. Deploy the ECS ALB (with its HTTPS listener and ACM certificate attached) and capture its ARN and security group ID.
2. Configure the NLB parameter file with `TargetALBArn`, `TargetALBSecurityGroupId`, subnets, and allowed ingress source.
3. Deploy this NLB template.
4. Verify that the NLB target group health check path returns an HTTP status from 200 through 399.