# Claude Code Preferences

## Git Commits
- Never include Claude/AI references in commit messages (no Co-Authored-By, no mentions of AI assistance)

## Development Environment
- Native hardware with 64 threads available
- Use `--workers 32-48` for parallel operations (leave headroom for system)

---

# Project Context: Qairon

Qairon is a deployment/release management system with a hierarchical ID structure for tracking infrastructure and services.

## ID Format

All IDs are colon-delimited composites that build hierarchically:

```
{env}:{provider}:{account}:{region}:{partition}:{target_type}:{target}:{app}:{stack}:{service}:{tag}:{release_num}
```

Example: `prod:aws:111111111111:us-east-1:platform:eks:main:social:user:identity:default:100`

### ID Hierarchy (Composite IDs)
Infrastructure path (where code runs):
- `provider_id`: `{environment}:{provider}:{account}`
- `region_id`: `{environment}:{provider}:{account}:{region}`
- `partition_id`: `{environment}:{provider}:{account}:{region}:{partition}`
- `target_id`: `{environment}:{provider}:{account}:{region}:{partition}:{target_type}:{target}`

Application path (what code runs):
- `stack_id`: `{application}:{stack}`
- `service_id`: `{application}:{stack}:{service}`

Combined:
- `deployment_id`: full path without release (target + service)
- `release_id`: full path including release number

### Single-Word Filter Tags
All 12 components of the release_id are extracted as individual tags:

**Infrastructure (where):**
- `environment`: prod, stg, dev
- `provider`: aws, gcp, azure
- `account`: cloud account ID
- `region`: us-east-1, us-west-2, etc.
- `partition`: platform, tenant isolation
- `target_type`: eks, ecs, lambda, etc.
- `target`: cluster/resource name

**Application (what):**
- `application`: social, payments, etc.
- `stack`: user, content, feed, etc.
- `service`: identity, posts, timeline, etc.
- `tag`: deployment variant (default, canary, etc.)
- `release`: release number

---

# Monitoring Data Generator

## Location
`fixtures/social_network/generate_monitoring_data.py`

## Purpose
Generates synthetic but realistic logs and metrics for a social network platform over 1 year. Logs and metrics share `request_id` for correlation.

## Usage
```bash
python generate_monitoring_data.py <total_events> <total_users> [--output <dir>] [--seed <int>] [--format {jsonl,otlp}]

# Example: 1M events, 10K users (default JSONL format)
python generate_monitoring_data.py 1000000 10000 --output fixtures/test_data

# Example: OTLP format for ClickStack/OpenTelemetry backends
python generate_monitoring_data.py 1000000 10000 --output fixtures/test_data --format otlp
```

## Recommended Data Generation

For smooth time series data with visible outliers at 10-15 second granularity per deployment:

```bash
# Generate 50M events, 50K users (~225M metrics, ~50GB)
# Takes 20-30 minutes to generate, gives ~1 event/minute/deployment
python fixtures/social_network/generate_monitoring_data.py 50000000 50000 --output fixtures/test_data

# Start VictoriaMetrics with 2-year retention (use ~75% of available cores)
docker run -d --name victoria --cpus=48 -p 8428:8428 \
  -v vm-data-2y:/victoria-metrics-data \
  victoriametrics/victoria-metrics -retentionPeriod=2y

# Start Grafana
docker run -d --name grafana -p 3000:3000 grafana/grafana

# Import with parallel workers (use ~50-75% of threads)
python fixtures/social_network/import_to_victoriametrics.py fixtures/test_data/metrics.jsonl --workers 32
```

### Data Density Guide
| Events | Users | Metrics | Approx Size | Granularity per Deployment |
|--------|-------|---------|-------------|---------------------------|
| 1M | 10K | 4.5M | ~1.5GB | ~1 per 10 minutes |
| 10M | 20K | 45M | ~15GB | ~1 per minute |
| 50M | 50K | 225M | ~50GB | ~1 per 10-15 seconds |
| 100M | 100K | 450M | ~100GB | ~1 per 5-7 seconds |

## Output Files

**JSONL format (default):**
- `logs.jsonl` - Log entries (one JSON object per line)
- `metrics.jsonl` - Metric entries (one JSON object per line)
- `summary.json` - Generation metadata

**OTLP format (`--format otlp`):**
- `logs.otlp.json` - OpenTelemetry OTLP JSON format (resourceLogs structure)
- `metrics.otlp.json` - OpenTelemetry OTLP JSON format (resourceMetrics structure)
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

### Infrastructure-Aware Error Simulation

The generator creates realistic correlated failures through a three-tier error system:

**Error Priority (checked in order):**
1. **Infrastructure incidents** - Hidden dependency failures (databases, caches, queues)
2. **Dependency cascades** - Failures propagated from upstream services
3. **Self errors** - Random errors based on persona success rate

**Infrastructure Incidents:**
- Generated at startup: 2-8 incidents per hidden dependency per year
- Duration: 5 minutes to 4 hours each
- Low failure rate during incident (0.1%-0.4% of requests)
- Dependency cascades have 10x amplified failure rate

**Error Source Types (`error_source` field):**
| Value | Meaning | Example |
|-------|---------|---------|
| `infrastructure:<component>` | Direct infrastructure failure | `infrastructure:redis_content` |
| `dependency:<service>` | Cascade from upstream service | `dependency:content:posts` |
| `self` | Random error (client/server) | Client 400, Server 500 |

**Log Levels:**
- `ERROR` - Server/infrastructure errors (500, 502, 503, 504, database, cache, queue)
- `WARN` - Client errors (400, 401, 403, 404, 422, 429)
- `INFO` - Successful requests

**Correlation Analysis:**
Use `error_source` and `upstream_request_id` to trace failures:
```bash
# Find all errors from a specific infrastructure incident
grep "infrastructure:redis_content" logs.jsonl

# Find cascade effects from a service failure
grep "dependency:content:posts" logs.jsonl
```

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
  "trace_id": "0af7651916cd43dd8448eb211c80319c",
  "span_id": "b7ad6b7169203331",
  "parent_span_id": null,
  "target_user_id": null,
  "object_type": "media",
  "object_id": "media_def456",
  "error_code": null,
  "error_message": null,
  "error_source": null,
  "error_type": null,
  "upstream_request_id": null
}
```

**Tracing fields (OpenTelemetry format):**
- `trace_id` - 32 hex chars identifying the entire request chain
- `span_id` - 16 hex chars identifying this specific operation
- `parent_span_id` - Links to parent span (null for root spans)

**Error fields (populated on failure):**
- `error_code` - HTTP status code (400, 500, 503, etc.)
- `error_message` - Human-readable error description
- `error_source` - Origin of failure (`self`, `dependency:*`, `infrastructure:*`)
- `error_type` - Category (`client`, `server`, `database`, `cache`, `queue`, `internal`)
- `upstream_request_id` - Request ID of failed dependency call (for tracing)

### Generated Anomalies

**Infrastructure Incidents (root causes):**
| Component | Description | Affected Services |
|-----------|-------------|-------------------|
| dynamodb_throttle | DynamoDB capacity exceeded | dm, stories, presence, timeline |
| redis_content | Redis content cache failure | posts, media, comments, reactions |
| aurora_primary | Aurora primary failover | identity, profile, privacy |
| neptune_timeout | Neptune graph DB timeout | connections, suggestions, blocks |
| media_processing | Media processing pipeline failure | media, stories |
| redis_feed | Redis feed cache failure | timeline, ranking |
| redis_messaging | Redis messaging cache failure | dm, groups, presence |
| kinesis_feed | Kinesis stream backpressure | fanout, aggregation |
| serialization_bug | Hidden serialization bug | various |
| opensearch_cluster | OpenSearch cluster issue | search services |
| auth_library | Auth library edge case | identity, privacy |

**Dependency Cascade Errors (downstream effects):**
| Failed Dependency | Typical Cascade Count |
|-------------------|----------------------|
| content:posts | High (most services depend on posts) |
| content:hashtags | Medium |
| content:stories | Medium |
| feed:fanout | Medium |
| social:connections | Medium |

**Querying Anomalies in VictoriaLogs:**
```logsql
# All infrastructure failures
error_source:infrastructure*

# Specific infrastructure component
error_source:infrastructure:dynamodb_throttle

# All dependency cascade failures
error_source:dependency*

# Specific dependency cascade
error_source:dependency:content:posts

# Find incident time windows
error_source:infrastructure:redis_content | stats by(_time:1h) count()
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

**Single-word tags (12 total):**
- Infrastructure: `environment`, `provider`, `account`, `region`, `partition`, `target_type`, `target`
- Application: `application`, `stack`, `service`, `tag`, `release`

**Composite IDs (8 total):**
- Infrastructure: `provider_id`, `region_id`, `partition_id`, `target_id`
- Application: `stack_id`, `service_id`
- Combined: `deployment_id`, `release_id`

## Grafana Queries
```promql
# By environment
request_duration_ms{environment="prod"}

# By region
request_duration_ms{region="us-east-1"}

# By application and stack
request_duration_ms{application="social", stack="content"}

# By service
request_duration_ms{service="posts", stack="content"}

# By target (specific cluster)
request_duration_ms{target_type="eks", target="main"}

# By release number
request_duration_ms{release="100"}

# Error rate by deployment
sum(rate(request_duration_ms{success="false"}[5m])) by (deployment_id)
  / sum(rate(request_duration_ms[5m])) by (deployment_id)

# Error rate by stack
sum(rate(request_duration_ms{success="false"}[5m])) by (stack_id)
  / sum(rate(request_duration_ms[5m])) by (stack_id)

# P99 latency by service_id
histogram_quantile(0.99, request_duration_ms) by (service_id)
```

---

# ClickStack (Alternative Backend)

ClickStack is a ClickHouse-based observability stack with HyperDX UI and built-in OpenTelemetry collector. Recommended for high-volume data with better query performance than VictoriaMetrics/VictoriaLogs.

## Start ClickStack
```bash
docker run -d --name clickstack \
  -p 8080:8080 -p 4317:4317 -p 4318:4318 \
  -v clickstack-data:/var/lib/clickhouse \
  docker.io/hyperdx/hyperdx-local
```

**Ports:**
- 8080: HyperDX UI (http://localhost:8080)
- 4317: OTLP gRPC receiver
- 4318: OTLP HTTP receiver

## Get API Key
1. Open http://localhost:8080
2. Create account / log in
3. Go to Team Settings → API Keys
4. Copy the API key

## Ingest OTLP Data
```bash
# Generate OTLP data
python fixtures/social_network/generate_monitoring_data.py 1000000 10000 --format otlp --output fixtures/test_data

# Send logs
curl -X POST -H "Content-Type: application/json" \
  -H "Authorization: <API_KEY>" \
  -d @fixtures/test_data/logs.otlp.json \
  http://localhost:4318/v1/logs

# Send metrics
curl -X POST -H "Content-Type: application/json" \
  -H "Authorization: <API_KEY>" \
  -d @fixtures/test_data/metrics.otlp.json \
  http://localhost:4318/v1/metrics
```

## Wipe and Restart
```bash
docker stop clickstack && docker rm clickstack && docker volume rm clickstack-data
# Then run the start command again
```

---

# Docker Management

## Start Services
```bash
# VictoriaMetrics (metrics)
docker run -d --name victoria --cpus=24 -p 8428:8428 \
  -v vm-data-2y:/victoria-metrics-data \
  victoriametrics/victoria-metrics -retentionPeriod=2y -search.cacheTimestampOffset=8760h

# VictoriaLogs (logs)
docker run -d --name victorialogs --cpus=30 -p 9428:9428 \
  -v vl-data-2y:/victoria-logs-data \
  victoriametrics/victoria-logs -retentionPeriod=2y

# Grafana (with VictoriaLogs plugin and persistent storage)
docker run -d --name grafana -p 3000:3000 \
  -v grafana-data:/var/lib/grafana \
  -e GF_INSTALL_PLUGINS=victoriametrics-logs-datasource \
  grafana/grafana
```

## Stop (preserve data)
```bash
docker stop victoria victorialogs grafana
```

## Restart
```bash
docker start victoria victorialogs grafana
```

## Wipe and restart
```bash
# Wipe VictoriaMetrics
docker stop victoria && docker rm victoria && docker volume rm vm-data-2y

# Wipe VictoriaLogs
docker stop victorialogs && docker rm victorialogs && docker volume rm vl-data-2y

# Wipe Grafana
docker stop grafana && docker rm grafana && docker volume rm grafana-data

# Then run the start commands again
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

---

# TODO

## Monitoring Data Generator

- [x] **Add distributed tracing support** - Implemented OpenTelemetry-style tracing:
  - `trace_id` (32 hex chars) - Consistent across a call chain
  - `span_id` (16 hex chars) - Unique per operation
  - `parent_span_id` - Links to parent (null for root spans)
  - Error-biased exemplar sampling for metrics (100% errors, 100% slow, 1% random)

- [x] **Add OTLP output format** - `--format otlp` option outputs OpenTelemetry OTLP JSON:
  - `logs.otlp.json` with resourceLogs/scopeLogs/logRecords structure
  - `metrics.otlp.json` with resourceMetrics/scopeMetrics/metrics structure
  - Compatible with ClickStack, Jaeger, Tempo, and other OTLP receivers

### Future Enhancements

- [ ] **Generate child span events** - Currently only root spans are generated. To enable full trace visualization:
  - Generate explicit child events for dependency calls
  - Link child spans with parent_span_id
  - Proper timing (child starts after parent, completes before)

- [ ] **Streaming OTLP sender** - Send OTLP data directly to collectors without intermediate files
