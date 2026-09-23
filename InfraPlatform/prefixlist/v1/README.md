# InfraPlatform - Managed Prefix List (v1)

## Overview

This template provisions up to 10 AWS Managed Prefix Lists as empty containers. Prefix lists are reusable sets of CIDR blocks that can be referenced in security group rules, reducing the need to duplicate CIDR entries across multiple resources. CIDR entries are managed by the project team via AWS Console after deployment.

## IaCVersion

`InfraPlatform-PrefixList-v1`

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   CloudFormation Stack                  │
│  {AppShortName}-{EnvName}-prefixlist                    │
│                                                         │
│  ┌──────────────────┐  ┌──────────────────┐             │
│  │ Prefix List 01   │  │ Prefix List 02   │  ... (x10)  │
│  │ pl-{purpose01}   │  │ pl-{purpose02}   │             │
│  │ MaxEntries: 50   │  │ MaxEntries: 50   │             │
│  │ IPv4             │  │ IPv4             │             │
│  │ Entries: managed │  │ Entries: managed │             │
│  │ via AWS Console  │  │ via AWS Console  │             │
│  └──────────────────┘  └──────────────────┘             │
└─────────────────────────────────────────────────────────┘
                    │
            ┌───────┴───────┐
            │ Referenced by │
            └───────┬───────┘
                    │
       ┌────────────┼────────────┐
       │            │            │
       ▼            ▼            ▼
  Security      Security     Security
  Group         Group        Group
  Egress        Ingress      (other stacks)
```

## Use Cases

- **Security Group Egress**: Restrict outbound traffic to specific CIDRs (e.g., DB subnets, VPC endpoint CIDRs, external API ranges)
- **Security Group Ingress**: Allow inbound traffic from known CIDR ranges (e.g., on-prem networks, trusted subnets)
- **Centralized CIDR Management**: Update CIDRs in one place — all referencing security groups automatically pick up changes
- **Reduce Security Group Rule Count**: One prefix list reference = one rule (vs. N individual CIDR rules)
- **Multiple Prefix Lists per Stack**: Create up to 10 prefix lists in a single deployment (e.g., DB subnets, VPC endpoints, external APIs)

## Parameters

### Required Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| AppShortName | Application short name | myapp, gms |
| EnvName | Environment name | nprd, nprd-dev, prod |
| NumberOfPrefixLists | Number of prefix lists to create (1-10) | 3 |
| PrefixListPurpose01 | Purpose suffix for prefix list 1 | db-subnets, vpce, external-api |

### Optional Parameters (per prefix list)

| Parameter | Default | Description |
|-----------|---------|-------------|
| MaxEntries{NN} | 50 | Maximum entries the prefix list can hold (1-1000) |
| PrefixListPurpose02-10 | "" | Purpose suffix for additional prefix lists |

## Environment Support

| Environment | DeletionPolicy | UpdateReplacePolicy |
|-------------|---------------|---------------------|
| nprd, nprd-dev, nprd-dev1, nprd-dev2 | Delete | Delete |
| nprd-sit, nprd-sit1, nprd-sit2, nprd-sit3 | Delete | Delete |
| nprd-sit-a, nprd-sit-b, nprd-sit-c | Delete | Delete |
| nprd-uat, nprd-uat-a, nprd-uat-b, nprd-uat-c | Delete | Delete |
| nprd-pt, nprd-pp, nprd-pp-a, nprd-pp-b, nprd-pp-c | Delete | Delete |
| prod, prod-a, prod-b, prod-c | Retain | Retain |

## Resources Created (per prefix list)

| Resource | Name Pattern | Description |
|----------|-------------|-------------|
| Managed Prefix List | {AppShortName}-{EnvName}-pl-{PrefixListPurpose} | Empty IPv4 prefix list (entries managed via AWS Console) |

## Outputs (per prefix list)

| Output | Description |
|--------|-------------|
| PrefixListId{NN} | Prefix List ID (pl-xxxxxxxxx) |

## Examples

### Single Prefix List — DB Subnets

```yaml
AppShortName: "myapp"
EnvName: "nprd-dev"
NumberOfPrefixLists: "1"
PrefixListPurpose01: "db-subnets"
MaxEntries01: "10"
```

### Multiple Prefix Lists — Network Segmentation

```yaml
AppShortName: "myapp"
EnvName: "nprd-dev"
NumberOfPrefixLists: "3"

# Prefix List 01 — DB Subnets
PrefixListPurpose01: "db-subnets"
MaxEntries01: "10"

# Prefix List 02 — VPC Endpoints
PrefixListPurpose02: "vpce"
MaxEntries02: "20"

# Prefix List 03 — External APIs
PrefixListPurpose03: "external-api"
MaxEntries03: "20"
```

### Post-Deployment: Adding CIDR Entries

After the stack is deployed, add entries via AWS Console:

1. Go to **AWS Console → VPC → Managed Prefix Lists**
2. Find the prefix list by name: `{AppShortName}-{EnvName}-pl-{PrefixListPurpose}`
3. Select the prefix list → **Entries** tab → **Modify**
4. Add CIDR entries with descriptions
5. Save changes

## Important Notes

1. **MaxEntries cannot be decreased** after prefix list creation (only increased). Plan for future growth.
2. **Security group rule limits**: When a prefix list is referenced in a security group, it consumes MaxEntries worth of rules (not the actual number of entries). AWS default limit is 60 inbound + 60 outbound rules per security group.
3. **Production environments** (prod, prod-a, prod-b, prod-c) have DeletionPolicy=Retain to prevent accidental deletion.
4. **Entries are NOT managed by CloudFormation** — this template creates empty prefix lists. Project teams add/modify/remove entries via AWS Console or CLI.
5. **Up to 10 prefix lists** can be created in a single stack. Set `NumberOfPrefixLists` to control how many are deployed.
6. **IPv4 only** — all prefix lists use IPv4 address family.

## Conditions

| Condition | Logic | Purpose |
|-----------|-------|---------|
| IsProduction | EnvName in (prod, prod-a, prod-b, prod-c) | Controls DeletionPolicy |
| DeployPL{NN} | NumberOfPrefixLists >= N (cascading) | Determines if prefix list N is created |

## Troubleshooting

| Issue | Cause | Resolution |
|-------|-------|------------|
| Stack fails: "MaxEntries cannot be decreased" | Attempted to lower MaxEntries on update | Increase or keep MaxEntries the same |
| Security group rule limit exceeded | Prefix list MaxEntries too high | Lower MaxEntries or request limit increase |
| Prefix list has no entries | Entries are managed outside CloudFormation | Add entries via AWS Console (see Post-Deployment section) |
