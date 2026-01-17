# Social Network Platform Fixtures

This directory contains a comprehensive set of fixtures to populate Qairon with a complete
social networking platform infrastructure model.

## Quick Start

```bash
# Preview what will be loaded (dry run)
./load_fixtures.sh --dry-run

# Load all fixtures
./load_fixtures.sh
```

## Contents Summary

### Platform Services (77 microservices across 18 stacks)

| Stack | Services | Description |
|-------|----------|-------------|
| user | 4 | Identity, profile, privacy, account management |
| social | 4 | Connections, blocks, suggestions, contacts |
| content | 7 | Posts, media, stories, comments, reactions, shares, hashtags |
| feed | 4 | Timeline, ranking, fanout, aggregation |
| messaging | 4 | DM, groups, realtime, presence |
| notifications | 5 | Push, email, SMS, in-app, preferences |
| search | 4 | Users, content, hashtags, indexer |
| discovery | 4 | Trending, explore, recommendations, interests |
| moderation | 5 | Content review, auto-mod, reports, spam, trust & safety |
| ads | 5 | Campaigns, targeting, bidding, delivery, analytics |
| payments | 4 | Processor, subscriptions, wallet, payouts |
| creator | 4 | Studio, analytics, monetization, shop |
| live | 4 | Streaming, chat, gifts, VOD |
| analytics | 5 | Events, warehouse, pipeline, reporting, ML features |
| platform | 5 | API gateway, rate limiter, feature flags, A/B testing, config |
| observability | 5 | Logging, metrics, tracing, alerting, dashboards |
| cicd | 4 | Pipelines, artifacts, deployments, testing |
| security | 3 | Vault, scanner, compliance |

### AWS Infrastructure

| Resource | Count | Description |
|----------|-------|-------------|
| Environments | 6 | prod, stg, dev, int, infra, local |
| AWS Accounts | 10 | Multi-account architecture |
| Regions | 4 | us-east-1, us-west-2, eu-west-1, ap-southeast-1 |
| VPCs | 40+ | Platform, data, DMZ, transit per region |
| Subnets | 100+ | Public, app, data, lambda, endpoints |
| EKS Clusters | 15+ | Main, realtime, batch clusters |
| Node Groups | 50+ | Various instance types |

### AWS Services Used

**Compute:** EKS, Lambda, Fargate, EC2
**Networking:** VPC, ALB, NLB, CloudFront, Route 53, API Gateway, PrivateLink
**Databases:** Aurora, DynamoDB, ElastiCache, Neptune, OpenSearch, Redshift
**Storage:** S3, EBS, EFS
**Messaging:** SQS, SNS, Kinesis, MSK, EventBridge
**Security:** IAM, KMS, Secrets Manager, WAF, Shield, Cognito, GuardDuty
**ML/AI:** SageMaker, Rekognition, Comprehend, Personalize
**Media:** MediaConvert, IVS, MediaLive
**DevOps:** CodePipeline, CodeBuild, ECR, CloudWatch, X-Ray

## File Structure

```
01_environments.txt          # Environment definitions
02_provider_types.txt        # Cloud provider types
03_deployment_target_types.txt # Target types (EKS, Lambda, etc.)
04_allocation_types.txt      # Resource types (CPU, memory, etc.)
05_repo_types.txt            # Repository types
06_languages.txt             # Config languages
07_providers.txt             # AWS accounts
08_regions.txt               # AWS regions
09_zones.txt                 # Availability zones
10_partitions.txt            # VPCs
11_networks.txt              # VPC CIDRs
12_subnets.txt               # Subnet CIDRs
13_fleet_types.txt           # Fleet/node group types
14_deployment_targets.txt    # EKS clusters, Lambda, etc.
15_fleets.txt                # Node groups
16_capacities.txt            # Fleet capacities
17_repos.txt                 # Git, ECR, Helm, S3 repos
18_applications.txt          # Applications
19_stacks.txt                # Service domains
20_services.txt              # Microservices
21_procs.txt                 # Process definitions
22_config_templates.txt      # Configuration templates
23_builds.txt                # Sample builds
24_deployments.txt           # Service deployments
```

## File Format

Each fixture file uses tab-separated values:
- Lines starting with `#` are comments
- Empty lines are ignored
- First comment line describes the format
- Second comment line shows the qcli command

Example:
```
# Environments
# Format: id
# Command: environment create {id}

prod
stg
dev
```

## Architecture Highlights

### Multi-Region Active-Active
- Primary: us-east-1
- Secondary: us-west-2
- Europe: eu-west-1
- Asia Pacific: ap-southeast-1

### Multi-Account Structure
- Production Platform (111111111111)
- Production Data (111111111112)
- Production ML (111111111113)
- Staging (222222222222)
- Development (333333333333)
- Integration (444444444444)
- Infrastructure Shared (555555555555)
- Security (555555555556)
- Logging (555555555557)
- Network Transit (555555555558)

### Security Best Practices
- VPC isolation between environments
- Private subnets for databases
- WAF and Shield for DDoS protection
- KMS encryption at rest
- Secrets Manager for credentials
- IAM roles with least privilege

### High Availability
- 3 AZs per region
- Multi-AZ database deployments
- Cross-region replication
- Auto-scaling groups
- Health checks and failover

## Customization

To customize these fixtures for your environment:

1. Update AWS account IDs in `07_providers.txt`
2. Adjust CIDR ranges in `11_networks.txt` and `12_subnets.txt`
3. Modify service configurations in `20_services.txt`
4. Adjust replica counts in `21_procs.txt`
5. Update ECR URLs in `17_repos.txt`

## Dependencies

Fixtures must be loaded in order due to foreign key relationships:
1. Base types (environments, provider types, etc.)
2. Infrastructure (providers, regions, partitions)
3. Networking (networks, subnets)
4. Deployment targets (clusters, fleets)
5. Applications (services, procs)
6. Deployments

The `load_fixtures.sh` script handles this automatically.
