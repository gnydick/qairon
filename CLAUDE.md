# Claude Code Preferences

## Git Commits
- Never include Claude/AI references in commit messages (no Co-Authored-By, no mentions of AI assistance)

---

# Project Context: Qairon

Qairon is a deployment/release management system with a hierarchical ID structure for tracking infrastructure and services.

## ID Format

All IDs are colon-delimited composites that build hierarchically:

```
{env}:{provider}:{account}:{region}:{partition}:{target_type}:{target}:{app}:{stack}:{service}:{tag}:{release_num}
```

Example: `prod:aws:111111111111:us-east-1:platform:eks:main:social:user:identity:default:100`

### ID Hierarchy
- `provider_id`: `{env}:{provider}:{account}`
- `region_id`: `{env}:{provider}:{account}:{region}`
- `partition_id`: `{env}:{provider}:{account}:{region}:{partition}`
- `target_id`: `{env}:{provider}:{account}:{region}:{partition}:{target_type}:{target}`
- `service_id`: `{app}:{stack}:{service}` (service definition is environment-agnostic)
- `deployment_id`: full path without release_num
- `release_id`: full path including release_num

### Single-Word Filter Tags
For metrics/logs, extract these for easy filtering:
- `environment`: prod, stg, dev
- `provider`: aws, gcp, azure
- `account`: AWS account ID
- `region`: us-east-1, us-west-2, etc.

---

# Monitoring Data Generator

## Location
`fixtures/social_network/generate_monitoring_data.py`

## Purpose
Generates synthetic but realistic logs and metrics for a social network platform over 1 year. Logs and metrics share `request_id` for correlation.

## Usage
```bash
python generate_monitoring_data.py <total_events> <total_users> [--output <dir>] [--seed <int>]

# Example: 1M events, 10K users
python generate_monitoring_data.py 1000000 10000 --output fixtures/test_data
```

## Output Files
- `logs.jsonl` - Log entries (one JSON object per line)
- `metrics.jsonl` - Metric entries (one JSON object per line)
- `summary.json` - Generation metadata

## Key Features

### 100 User Personas
Distributed across archetypes with distinct behavior patterns:

| Category | Count | % Users | % Activity | Characteristics |
|----------|-------|---------|------------|-----------------|
| Influencers | 5 | ~2% | ~15% | High posting, content-focused |
| Content Creators | 10 | ~5% | ~12% | Photo/video/writer variants |
| Active Engagers | 15 | ~10% | ~18% | Commenters, reactors, messengers |
| Regular Users | 25 | ~25% | ~25% | Various age group patterns |
| Casual Browsers | 20 | ~25% | ~15% | Time-of-day variants |
| Lurkers | 15 | ~20% | ~8% | Consumers, rarely post |
| New Users | 5 | ~3% | ~3% | Onboarding patterns |
| Business Accounts | 3 | ~2% | ~3% | Scheduled posting |
| Advertisers | 2 | ~1% | ~1% | Campaign management |

Each persona has:
- `activity_multiplier` - Relative event volume
- `action_weights` - Likelihood per action category
- `hourly_weights` - 24-hour activity pattern
- `daily_weights` - Day-of-week pattern
- `success_rate` - Error probability
- `latency_multiplier` - Network quality simulation

### ~90 Service Actions
Organized by stack:
- **user**: identity, profile, privacy, account
- **social**: connections, blocks, suggestions, contacts
- **content**: posts, media, stories, comments, reactions, shares, hashtags
- **feed**: timeline, ranking, fanout, aggregation
- **messaging**: dm, groups, realtime, presence
- **notifications**: push, email, sms, inapp, preferences
- **search**: users, content, hashtags, indexer
- **discovery**: trending, explore, recommendations, interests
- **moderation**: content-review, auto-mod, reports, spam
- **ads**: campaigns, targeting, bidding, delivery, analytics
- **payments**: processor, subscriptions, wallet, payouts
- **creator**: studio, analytics, monetization, shop
- **live**: streaming, chat, gifts, vod

### Service Dependencies
Two types for error propagation:

1. **Documented Dependencies** (`SERVICE_DEPENDENCIES`)
   - Explicit service-to-service calls
   - Example: `feed:timeline` depends on `content:posts`, `social:connections`

2. **Hidden Dependencies** (`HIDDEN_DEPENDENCIES`)
   - Shared infrastructure (databases, caches, queues)
   - Discoverable through correlated failures
   - Examples: Aurora clusters, Redis clusters, Kinesis streams

### Metrics Format
```json
{
  "metric": "request_duration_ms",
  "ts": 1746691431.349506,
  "value": 163.88,
  "tags": {
    "service": "media",
    "stack": "content",
    "action": "get_media",
    "success": "true",
    "is_write": "false",
    "persona": "lurker_15",
    "release_id": "prod:aws:111111111111:us-west-2:platform:eks:main:social:content:media:default:113",
    "object_type": "media"
  }
}
```

Metrics generated per event:
- `request_duration_ms` - Response latency
- `request_size_bytes` - Request payload size
- `response_size_bytes` - Response payload size
- `db_query_count` - Database queries executed
- `cache_hit` - Cache hit indicator (reads only)

### Log Format
```json
{
  "timestamp": "2025-05-08T01:03:51.349506Z",
  "level": "INFO",
  "service": "media",
  "stack": "content",
  "action": "get_media",
  "user_id": "user_abc123",
  "request_id": "req_xyz789",
  "success": true,
  "message": "get_media returned data",
  "release_id": "prod:aws:111111111111:us-west-2:platform:eks:main:social:content:media:default:113",
  "target_user_id": null,
  "object_type": "media",
  "object_id": "media_def456",
  "error_code": null,
  "error_message": null
}
```

---

# VictoriaMetrics Importer

## Location
`fixtures/social_network/import_to_victoriametrics.py`

## Purpose
Parallel batch import of metrics.jsonl to VictoriaMetrics with tag extraction.

## Usage
```bash
# Start VictoriaMetrics with 2-year retention
docker run -d --name victoria --cpus=12 -p 8428:8428 \
  -v vm-data-2y:/victoria-metrics-data \
  victoriametrics/victoria-metrics -retentionPeriod=2y

# Start Grafana
docker run -d --name grafana -p 3000:3000 grafana/grafana

# Import metrics (parallel)
python import_to_victoriametrics.py metrics.jsonl --workers 12
```

## Tag Extraction
The importer splits `release_id` into queryable tags:

**Single-word tags** (for global filtering):
- `environment`, `provider`, `account`, `region`

**Composite IDs** (all include environment):
- `provider_id`, `region_id`, `partition_id`, `target_id`
- `service_id` (app:stack:service, environment-agnostic)
- `deployment_id` (release_id without release_num)

## Grafana Queries
```promql
# By environment
request_duration_ms{environment="prod"}

# By region
request_duration_ms{region="us-east-1"}

# By service
request_duration_ms{service="posts", stack="content"}

# Error rate by deployment
sum(rate(request_duration_ms{success="false"}[5m])) by (deployment_id)
  / sum(rate(request_duration_ms[5m])) by (deployment_id)

# P99 latency by service
histogram_quantile(0.99, request_duration_ms{service="timeline"})
```

---

# Docker Management

## Start Services
```bash
docker run -d --name victoria --cpus=12 -p 8428:8428 \
  -v vm-data-2y:/victoria-metrics-data \
  victoriametrics/victoria-metrics -retentionPeriod=2y

docker run -d --name grafana -p 3000:3000 grafana/grafana
```

## Stop (preserve data)
```bash
docker stop victoria grafana
```

## Restart
```bash
docker start victoria grafana
```

## Wipe and restart
```bash
docker stop victoria && docker rm victoria && docker volume rm vm-data-2y
# Then run the start command again
```

## Grafana Setup
- URL: http://localhost:3000
- Login: admin / admin
- Add Prometheus data source with URL: `http://172.17.0.2:8428` (or check `docker inspect victoria --format '{{.NetworkSettings.IPAddress}}'`)

---

# Fixture Files

## Location
`fixtures/social_network/txt/` - Qairon entity definitions

## Key Files
- `20_services.txt` - Service definitions with stack relationships
- `24_deployments.txt` - Deployment configurations
- `26_releases.txt` - Release records with deployment_id and build_num

## Format
Tab-separated values with JSON defaults column:
```
{parent_id}	{name}	{artifact_name}	{defaults_json}
```
