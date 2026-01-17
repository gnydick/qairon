# Social Network Platform - Infrastructure Overview

## Platform Services Architecture

This document outlines all services required to operate a modern social networking platform,
organized by functional domain, along with the AWS services that support them.

---

## 1. Application Domains (Stacks)

### 1.1 User Domain (`user`)
Core user identity and account management.

| Service | Description | AWS Services |
|---------|-------------|--------------|
| `identity` | Authentication, OAuth, JWT tokens, sessions | Cognito, ElastiCache, DynamoDB |
| `profile` | User profiles, avatars, bios, settings | RDS Aurora, S3, CloudFront |
| `privacy` | Privacy settings, data controls, GDPR | RDS Aurora, Lambda |
| `account` | Account lifecycle, deactivation, deletion | RDS Aurora, SQS, Lambda |

### 1.2 Social Graph Domain (`social`)
Relationships and connections between users.

| Service | Description | AWS Services |
|---------|-------------|--------------|
| `connections` | Friends, followers, following relationships | Neptune, ElastiCache |
| `blocks` | User blocking and muting | Neptune, DynamoDB |
| `suggestions` | Friend/follow recommendations | Neptune, SageMaker, Personalize |
| `contacts` | Contact book sync and matching | DynamoDB, Lambda |

### 1.3 Content Domain (`content`)
User-generated content creation and management.

| Service | Description | AWS Services |
|---------|-------------|--------------|
| `posts` | Text posts, status updates | RDS Aurora, ElastiCache |
| `media` | Image/video upload and processing | S3, MediaConvert, Lambda, CloudFront |
| `stories` | Ephemeral 24-hour content | DynamoDB, S3, CloudFront |
| `comments` | Comments on posts | RDS Aurora, ElastiCache |
| `reactions` | Likes, reactions, emoji responses | DynamoDB, ElastiCache |
| `shares` | Sharing and reposting content | RDS Aurora, SQS |
| `hashtags` | Hashtag tracking and trending | DynamoDB, OpenSearch |

### 1.4 Feed Domain (`feed`)
Content aggregation and delivery.

| Service | Description | AWS Services |
|---------|-------------|--------------|
| `timeline` | Personal timeline assembly | ElastiCache, DynamoDB, Kinesis |
| `ranking` | Feed ranking and ML scoring | SageMaker, ElastiCache |
| `fanout` | Feed fanout to followers | Kinesis, DynamoDB, SQS |
| `aggregation` | Activity aggregation | Kinesis, Lambda |

### 1.5 Messaging Domain (`messaging`)
Direct and group communication.

| Service | Description | AWS Services |
|---------|-------------|--------------|
| `dm` | Direct messages (1:1) | DynamoDB, ElastiCache, API Gateway WebSocket |
| `groups` | Group chat conversations | DynamoDB, ElastiCache |
| `realtime` | WebSocket connection management | API Gateway WebSocket, ElastiCache |
| `presence` | Online/offline status tracking | ElastiCache, Lambda |

### 1.6 Notifications Domain (`notifications`)
User notifications and alerts.

| Service | Description | AWS Services |
|---------|-------------|--------------|
| `push` | Mobile push notifications | SNS, Pinpoint |
| `email` | Email notifications | SES, Lambda |
| `sms` | SMS notifications | SNS, Pinpoint |
| `inapp` | In-app notification center | DynamoDB, ElastiCache |
| `preferences` | Notification preferences | DynamoDB |

### 1.7 Search Domain (`search`)
Platform-wide search capabilities.

| Service | Description | AWS Services |
|---------|-------------|--------------|
| `users` | User search | OpenSearch |
| `content` | Post/content search | OpenSearch |
| `hashtags` | Hashtag search | OpenSearch, DynamoDB |
| `indexer` | Search index management | OpenSearch, Kinesis, Lambda |

### 1.8 Discovery Domain (`discovery`)
Content and user discovery.

| Service | Description | AWS Services |
|---------|-------------|--------------|
| `trending` | Trending topics and posts | DynamoDB, ElastiCache, Kinesis |
| `explore` | Explore page content curation | SageMaker, Personalize |
| `recommendations` | Content recommendations | SageMaker, Personalize |
| `interests` | User interest profiling | SageMaker, DynamoDB |

### 1.9 Moderation Domain (`moderation`)
Content and user safety.

| Service | Description | AWS Services |
|---------|-------------|--------------|
| `content-review` | Content moderation queue | RDS Aurora, SQS |
| `auto-mod` | Automated content moderation | Rekognition, Comprehend, SageMaker |
| `reports` | User reports and appeals | RDS Aurora, SQS |
| `spam` | Spam detection and prevention | SageMaker, Lambda |
| `trust-safety` | Trust and safety operations | RDS Aurora, OpenSearch |

### 1.10 Advertising Domain (`ads`)
Monetization through advertising.

| Service | Description | AWS Services |
|---------|-------------|--------------|
| `campaigns` | Ad campaign management | RDS Aurora, ElastiCache |
| `targeting` | Audience targeting | DynamoDB, SageMaker |
| `bidding` | Real-time ad bidding | ElastiCache, Lambda |
| `delivery` | Ad delivery and pacing | ElastiCache, CloudFront |
| `analytics` | Ad performance analytics | Kinesis, Redshift |

### 1.11 Payments Domain (`payments`)
Financial transactions.

| Service | Description | AWS Services |
|---------|-------------|--------------|
| `processor` | Payment processing | Lambda, Step Functions |
| `subscriptions` | Subscription management | RDS Aurora, Lambda |
| `wallet` | User wallet/credits | RDS Aurora |
| `payouts` | Creator payouts | RDS Aurora, Step Functions |

### 1.12 Creator Domain (`creator`)
Creator/business tools.

| Service | Description | AWS Services |
|---------|-------------|--------------|
| `studio` | Content creation tools | S3, MediaConvert, Lambda |
| `analytics` | Creator analytics dashboard | Redshift, QuickSight |
| `monetization` | Creator monetization tools | RDS Aurora, Lambda |
| `shop` | Creator shops/storefronts | RDS Aurora, S3 |

### 1.13 Live Domain (`live`)
Live streaming functionality.

| Service | Description | AWS Services |
|---------|-------------|--------------|
| `streaming` | Live video streaming | IVS (Interactive Video Service), MediaLive |
| `chat` | Live stream chat | API Gateway WebSocket, DynamoDB |
| `gifts` | Virtual gifts/donations | DynamoDB, Lambda |
| `vod` | Video-on-demand from streams | S3, CloudFront, MediaConvert |

### 1.14 Analytics Domain (`analytics`)
Platform analytics and insights.

| Service | Description | AWS Services |
|---------|-------------|--------------|
| `events` | Event collection | Kinesis Data Firehose |
| `warehouse` | Data warehouse | Redshift, S3 |
| `pipeline` | ETL pipelines | Glue, EMR |
| `reporting` | Business intelligence | QuickSight, Athena |
| `ml-features` | ML feature store | SageMaker Feature Store |

### 1.15 Platform Domain (`platform`)
Core platform infrastructure.

| Service | Description | AWS Services |
|---------|-------------|--------------|
| `api-gateway` | API gateway and routing | API Gateway, ALB |
| `rate-limiter` | Rate limiting | ElastiCache, Lambda@Edge |
| `feature-flags` | Feature flag management | AppConfig, DynamoDB |
| `ab-testing` | A/B testing framework | Lambda, DynamoDB |
| `config` | Configuration management | AppConfig, Parameter Store |
| `secrets` | Secrets management | Secrets Manager |

### 1.16 Infrastructure Domain (`infra`)
Platform infrastructure services.

| Service | Description | AWS Services |
|---------|-------------|--------------|
| `logging` | Centralized logging | CloudWatch Logs, OpenSearch |
| `metrics` | Metrics collection | CloudWatch, Managed Prometheus |
| `tracing` | Distributed tracing | X-Ray, Jaeger |
| `alerting` | Alert management | CloudWatch Alarms, SNS |
| `dashboards` | Observability dashboards | Managed Grafana, CloudWatch |

### 1.17 CI/CD Domain (`cicd`)
Build and deployment automation.

| Service | Description | AWS Services |
|---------|-------------|--------------|
| `pipelines` | CI/CD pipelines | CodePipeline, CodeBuild |
| `artifacts` | Artifact management | ECR, S3 |
| `deployments` | Deployment automation | CodeDeploy, EKS |
| `testing` | Automated testing | CodeBuild, Device Farm |

---

## 2. AWS Services Summary

### 2.1 Compute
| Service | Purpose | Criticality |
|---------|---------|-------------|
| EKS | Primary container orchestration | Critical |
| Lambda | Serverless compute for events | High |
| Fargate | Serverless container compute | High |
| EC2 | Specialized workloads (ML, video) | Medium |

### 2.2 Networking
| Service | Purpose | Criticality |
|---------|---------|-------------|
| VPC | Network isolation | Critical |
| ALB | Application load balancing | Critical |
| NLB | Network load balancing (gRPC) | High |
| CloudFront | Global CDN | Critical |
| Route 53 | DNS management | Critical |
| API Gateway | REST/WebSocket APIs | Critical |
| PrivateLink | Private connectivity | High |
| Global Accelerator | Global traffic acceleration | Medium |

### 2.3 Databases
| Service | Purpose | Criticality |
|---------|---------|-------------|
| Aurora PostgreSQL | Primary relational database | Critical |
| DynamoDB | High-throughput key-value | Critical |
| ElastiCache Redis | Caching and sessions | Critical |
| Neptune | Social graph database | High |
| OpenSearch | Full-text search | High |
| DocumentDB | Document storage | Medium |
| Timestream | Time-series data | Medium |

### 2.4 Storage
| Service | Purpose | Criticality |
|---------|---------|-------------|
| S3 | Object storage (media, backups) | Critical |
| EBS | Block storage for EC2 | High |
| EFS | Shared file storage | Medium |
| S3 Glacier | Long-term archival | Low |

### 2.5 Messaging & Streaming
| Service | Purpose | Criticality |
|---------|---------|-------------|
| SQS | Message queuing | Critical |
| SNS | Pub/sub messaging | Critical |
| Kinesis Data Streams | Real-time streaming | Critical |
| Kinesis Firehose | Data delivery | High |
| MSK (Kafka) | Event streaming | High |
| EventBridge | Event routing | High |

### 2.6 Security
| Service | Purpose | Criticality |
|---------|---------|-------------|
| IAM | Identity and access management | Critical |
| KMS | Key management | Critical |
| Secrets Manager | Secrets storage | Critical |
| WAF | Web application firewall | Critical |
| Shield Advanced | DDoS protection | Critical |
| Cognito | User authentication | High |
| Certificate Manager | TLS certificates | Critical |
| GuardDuty | Threat detection | High |
| Security Hub | Security posture | High |
| Macie | Data discovery | Medium |

### 2.7 Machine Learning
| Service | Purpose | Criticality |
|---------|---------|-------------|
| SageMaker | ML model training/inference | High |
| Rekognition | Image/video analysis | High |
| Comprehend | NLP and text analysis | High |
| Personalize | Recommendations | Medium |
| Fraud Detector | Fraud detection | Medium |

### 2.8 Analytics
| Service | Purpose | Criticality |
|---------|---------|-------------|
| Redshift | Data warehouse | High |
| Athena | S3 querying | Medium |
| QuickSight | Business intelligence | Medium |
| EMR | Big data processing | Medium |
| Glue | ETL and data catalog | High |

### 2.9 Media
| Service | Purpose | Criticality |
|---------|---------|-------------|
| MediaConvert | Video transcoding | High |
| IVS | Live streaming | Medium |
| MediaLive | Live video | Medium |
| Elemental MediaPackage | Video packaging | Medium |

### 2.10 DevOps & Operations
| Service | Purpose | Criticality |
|---------|---------|-------------|
| CloudWatch | Monitoring and logging | Critical |
| X-Ray | Distributed tracing | High |
| CodePipeline | CI/CD | High |
| CodeBuild | Build service | High |
| ECR | Container registry | Critical |
| Systems Manager | Operations management | High |
| Managed Grafana | Dashboards | Medium |
| Managed Prometheus | Metrics | Medium |

---

## 3. Infrastructure Topology

### 3.1 Environments
- `prod` - Production environment
- `stg` - Staging environment
- `dev` - Development environment
- `int` - Integration testing
- `infra` - Infrastructure services (shared)

### 3.2 Regions (Multi-Region for HA)
- `us-east-1` - Primary US (Virginia)
- `us-west-2` - Secondary US (Oregon)
- `eu-west-1` - Europe (Ireland)
- `ap-southeast-1` - Asia Pacific (Singapore)

### 3.3 VPCs per Region
- `platform` - Main application VPC
- `data` - Database VPC
- `security` - Security/compliance VPC
- `management` - Management/tooling VPC

### 3.4 Availability Zones
- 3 AZs per region for high availability

---

## 4. Security Best Practices

### 4.1 Network Security
- VPC isolation between environments
- Private subnets for databases and internal services
- Public subnets only for load balancers
- Security groups with least-privilege rules
- NACLs for subnet-level security
- VPC Flow Logs enabled
- PrivateLink for AWS service access

### 4.2 Data Security
- Encryption at rest (KMS) for all data stores
- Encryption in transit (TLS 1.3)
- Secrets rotation via Secrets Manager
- PII data classification and masking
- Database audit logging
- S3 bucket policies and versioning

### 4.3 Application Security
- WAF rules for OWASP Top 10
- Rate limiting at API Gateway
- JWT token validation
- OAuth 2.0 / OIDC authentication
- API key rotation
- Input validation
- Content Security Policy headers

### 4.4 Identity & Access
- IAM roles with least privilege
- Service accounts for applications
- MFA for human users
- SSO integration
- Regular access reviews
- Session management

### 4.5 Compliance & Audit
- CloudTrail enabled (all regions)
- Config Rules for compliance
- Security Hub aggregation
- GuardDuty for threat detection
- Regular penetration testing
- SOC 2 / GDPR compliance

---

## 5. High Availability & Disaster Recovery

### 5.1 Availability Targets
- Platform SLA: 99.99% uptime
- Recovery Time Objective (RTO): 15 minutes
- Recovery Point Objective (RPO): 1 minute

### 5.2 HA Patterns
- Multi-AZ deployments for all services
- Auto-scaling groups with health checks
- Database replication (synchronous within region)
- Redis cluster mode with replicas
- S3 cross-region replication
- Route 53 health checks and failover

### 5.3 DR Patterns
- Active-passive multi-region for databases
- Global tables for DynamoDB
- Aurora Global Database
- Cross-region backup replication
- Infrastructure as Code (reproducible)
- Regular DR drills

---

## 6. Fixture File Structure

The fixture files are organized in load order to handle dependencies:

```
01_environments.txt       - Environment definitions
02_provider_types.txt     - Cloud provider types (aws, gcp, etc.)
03_deployment_target_types.txt - Target types (eks, lambda, etc.)
04_allocation_types.txt   - Resource types (cpu, memory, etc.)
05_repo_types.txt         - Repository types (ecr, s3, etc.)
06_languages.txt          - Config languages (yaml, json, etc.)
07_providers.txt          - AWS accounts
08_regions.txt            - AWS regions
09_zones.txt              - Availability zones
10_partitions.txt         - VPCs
11_networks.txt           - VPC networks
12_subnets.txt            - Subnets
13_fleet_types.txt        - Fleet types
14_deployment_targets.txt - EKS clusters, Lambda, etc.
15_fleets.txt             - Node groups, capacity
16_capacities.txt         - Fleet capacities
17_repos.txt              - Container registries, S3 buckets
18_applications.txt       - Social network application
19_stacks.txt             - Service domains
20_services.txt           - Individual microservices
21_procs.txt              - Process definitions
22_config_templates.txt   - Configuration templates
23_builds.txt             - Service builds
24_build_artifacts.txt    - Build artifacts
25_releases.txt           - Releases
26_release_artifacts.txt  - Release artifacts
27_deployments.txt        - Service deployments
28_deployment_configs.txt - Deployment configurations
29_deployment_procs.txt   - Deployment processes
30_allocations.txt        - Resource allocations
```

Each file uses a simple format that can be parsed:
- One record per line
- Tab-separated values
- Comments start with #
- Empty lines are ignored