# Claude Code Preferences

## Git Commits
- Never include Claude/AI references in commit messages (no Co-Authored-By, no mentions of AI assistance)

## Development Environment
- Native hardware with 64 threads available
- Use `--workers 32-48` for parallel operations (leave headroom for system)

## Grafana Dashboards
- **Never hand-write dashboard JSON from scratch.** Always export from Grafana after editing in the UI, then save the exported JSON. Grafana expects the full panel schema (`pluginVersion`, `mappings`, full `options`/`fieldConfig` structure) to render correctly. Minimal hand-written JSON causes panels to fail to load.
- VictoriaLogs datasource plugin query types:
  - `"queryType": "stats"` — single aggregate value (`/select/logsql/stats_query`). Use for **stat** and **gauge** panels that show a single number.
  - `"queryType": "statsRange"` — time-bucketed values (`/select/logsql/stats_query_range`). Use for **time series**, **piechart**, **bar gauge**, and **table** panels.
  - `"queryType": "instant"` — raw log query (`/select/logsql/query`). Use for **logs** and **table** panels showing raw log lines.
  - Using the wrong query type causes stat panels to show incorrect values (e.g., `statsRange` in a stat panel shows only the last time bucket's count instead of the total).
- Dashboard JSON files use hardcoded datasource UIDs from the local Grafana instance (e.g., `"uid": "ffb8kdooypz40e"`). These are not portable across instances.

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
python generate_monitoring_data.py <total_events> <total_users> [--output <dir>] [--seed <int>] [--deployment-schedule <path>]

# Example: 1M events, 10K users
python generate_monitoring_data.py 1000000 10000 --output fixtures/test_data

# With deployment schedule (real release IDs and deployment dips)
python generate_monitoring_data.py 1000000 10000 \
  --deployment-schedule fixtures/social_network/deployment_schedule.json \
  --output fixtures/test_data
```

## Recommended Data Generation

Full pipeline: generate fixtures → generate monitoring data → import to backends.

```bash
# Step 1: Generate fixtures (DB + TSV files + deployment schedule)
SQLALCHEMY_DATABASE_URI=postgresql+psycopg2://qairon:qairon@localhost:5432/qairon \
  python fixtures/social_network/generate_fixtures.py \
  --txt-output /opt/qairon/fixtures/social_network/txt

# Step 2: Convert TSV → JSON:API format
python fixtures/social_network/convert_to_json.py \
  --input-dir /opt/qairon/fixtures/social_network/txt \
  --output-dir /opt/qairon/fixtures/social_network/json

# Step 3: Generate 50M events, 50K users (~135M logs with child spans)
python fixtures/social_network/generate_monitoring_data.py 50000000 50000 \
  --deployment-schedule fixtures/social_network/deployment_schedule.json \
  --output /opt/qairon/test_data --workers 48

# Step 4: Start all services
docker compose up -d

# Step 5: Import metrics (all 48 files in parallel, ~18k/sec)
for f in /opt/qairon/test_data/metrics_*.jsonl; do
  python fixtures/social_network/import_to_victoriametrics.py "$f" --workers 8 &
done
wait

# Step 6: Import logs (8 files at a time, 500K batch size for fewer IOPS)
ls /opt/qairon/test_data/logs_*.jsonl | xargs -P 8 -I {} \
  python fixtures/social_network/import_to_victorialogs.py {} --workers 4 --batch-size 500000

# Step 7: Export traces to Tempo (4 files at a time)
ls /opt/qairon/test_data/logs_*.jsonl | xargs -P 4 -I {} \
  python fixtures/social_network/export_traces_to_tempo.py {} --batch-size 2000
```

**Note:** Use `:z` flag on bind mounts for SELinux systems to relabel volumes for container access.

### Data Density Guide
With child spans (~2.8x multiplier), actual output is larger than base events:

| Base Events | Users | Logs (with spans) | Metrics | Raw Size | Granularity/Deployment |
|-------------|-------|-------------------|---------|----------|------------------------|
| 1M          | 10K   | ~2.8M             | ~12.3M  | ~6GB     | ~1 per 10 minutes      |
| 10M         | 20K   | ~28M              | ~123M   | ~60GB    | ~1 per minute          |
| 50M         | 50K   | ~135M             | ~613M   | ~280GB   | ~1 per 10-15 seconds   |
| 100M        | 100K  | ~280M             | ~1.2B   | ~560GB   | ~1 per 5-7 seconds     |

## Output Files

For large datasets, the generator outputs per-worker files to enable streaming without RAM constraints:
- `logs_0.jsonl`, `logs_1.jsonl`, ... - Log entries split by worker
- `metrics_0.jsonl`, `metrics_1.jsonl`, ... - Metric entries split by worker
- `summary.json` - Generation metadata

## Key Features

### 100 User Personas
Distributed across archetypes with distinct behavior patterns:

| Category          | Count | % Users | % Activity | Characteristics                  |
|-------------------|-------|---------|------------|----------------------------------|
| Influencers       | 5     | ~2%     | ~15%       | High posting, content-focused    |
| Content Creators  | 10    | ~5%     | ~12%       | Photo/video/writer variants      |
| Active Engagers   | 15    | ~10%    | ~18%       | Commenters, reactors, messengers |
| Regular Users     | 25    | ~25%    | ~25%       | Various age group patterns       |
| Casual Browsers   | 20    | ~25%    | ~15%       | Time-of-day variants             |
| Lurkers           | 15    | ~20%    | ~8%        | Consumers, rarely post           |
| New Users         | 5     | ~3%     | ~3%        | Onboarding patterns              |
| Business Accounts | 3     | ~2%     | ~3%        | Scheduled posting                |
| Advertisers       | 2     | ~1%     | ~1%        | Campaign management              |

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

| Value                        | Meaning                       | Example                        |
|------------------------------|-------------------------------|--------------------------------|
| `infrastructure:<component>` | Direct infrastructure failure | `infrastructure:redis_content` |
| `dependency:<service>`       | Cascade from upstream service | `dependency:content:posts`     |
| `deployment:<release_id>`    | Rolling restart during deploy | `deployment:...:posts:default:152` |
| `self`                       | Random error (client/server)  | Client 400, Server 500         |

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

| Component          | Description                       | Affected Services                 |
|--------------------|-----------------------------------|-----------------------------------|
| dynamodb_throttle  | DynamoDB capacity exceeded        | dm, stories, presence, timeline   |
| redis_content      | Redis content cache failure       | posts, media, comments, reactions |
| aurora_primary     | Aurora primary failover           | identity, profile, privacy        |
| neptune_timeout    | Neptune graph DB timeout          | connections, suggestions, blocks  |
| media_processing   | Media processing pipeline failure | media, stories                    |
| redis_feed         | Redis feed cache failure          | timeline, ranking                 |
| redis_messaging    | Redis messaging cache failure     | dm, groups, presence              |
| kinesis_feed       | Kinesis stream backpressure       | fanout, aggregation               |
| serialization_bug  | Hidden serialization bug          | various                           |
| opensearch_cluster | OpenSearch cluster issue          | search services                   |
| auth_library       | Auth library edge case            | identity, privacy                 |

**Dependency Cascade Errors (downstream effects):**

| Failed Dependency  | Typical Cascade Count                |
|--------------------|--------------------------------------|
| content:posts      | High (most services depend on posts) |
| content:hashtags   | Medium                               |
| content:stories    | Medium                               |
| feed:fanout        | Medium                               |
| social:connections | Medium                               |

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

# All deployment-related errors
error_source:deployment*

# Deployment events (start/complete)
action:deployment_start OR action:deployment_complete
```

### Deployment-Aware Monitoring (`--deployment-schedule`)

When a `deployment_schedule.json` is provided (generated by `generate_fixtures.py`), the monitoring data generator:

1. **Uses real release IDs** from the fixture database instead of synthetic ones
2. **Creates deployment dip effects** during rolling restarts:
   - **Throughput dip**: 15-30% reduction in requests/sec (events skipped)
   - **Error rate boost**: 2-5% additional server errors (500/502/503)
   - **Latency increase**: 20-50% higher response times
3. **Multi-region stagger**: Same-stack services deploy to region A first, then region B after 30-60 minutes
4. **Deployment log events**: `deployment_start` and `deployment_complete` actions with `user_id: "system"`

**Timing Model:**
```
release.created_at → +3-10min CI/CD delay → deployment_start → +5-15min rolling restart → deployment_complete
```

**Deployment Log Event Format:**
```json
{
  "timestamp": "2025-06-15T14:30:00Z",
  "level": "INFO",
  "service": "posts",
  "stack": "content",
  "action": "deployment_start",
  "user_id": "system",
  "request_id": "deploy_<uuid>",
  "success": true,
  "message": "Deployment started: rolling restart for release ...:152",
  "release_id": "prod:aws:...:social:content:posts:default:152",
  "object_type": "deployment",
  "object_id": "<deployment_id>"
}
```

**Generating the schedule:**
```bash
# generate_fixtures.py automatically exports deployment_schedule.json
SQLALCHEMY_DATABASE_URI=postgresql+psycopg2://qairon:qairon@localhost:5432/qairon \
  python fixtures/social_network/generate_fixtures.py \
  --txt-output /opt/qairon/fixtures/social_network/txt

# Then use it with monitoring data generation
python fixtures/social_network/generate_monitoring_data.py 50000000 50000 \
  --deployment-schedule fixtures/social_network/deployment_schedule.json \
  --output /opt/qairon/test_data --workers 48
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

# VictoriaLogs Importer

## Location
`fixtures/social_network/import_to_victorialogs.py`

## Purpose
Streaming import of logs.jsonl to VictoriaLogs with composite ID extraction. Extracts all tags from `release_id` to enable filtering by any hierarchy level.

## Usage
```bash
# Import logs (8 files in parallel, large batch size for fewer IOPS)
ls /opt/qairon/test_data/logs_*.jsonl | xargs -P 8 -I {} \
  python fixtures/social_network/import_to_victorialogs.py {} --workers 4 --batch-size 500000
```

## Performance Notes
- Use `--batch-size 500000` (not 50000) to reduce IOPS pressure from VictoriaLogs merge operations
- 8 files in parallel (`-P 8`) with 4 internal workers each is the sweet spot
- Smaller batch sizes cause thousands of tiny 3-4KB writes from storage merges, saturating NVMe IOPS even though throughput is low
- For 134M logs across 48 files, import completes in ~6 minutes with optimized settings

## Monitoring Import Errors
```bash
# Watch for insert errors during import
watch -n5 'curl -s "http://localhost:9428/metrics" | grep "vl_http.*jsonline"'
```

Key metrics:
- `vl_http_errors_total{path="/insert/jsonline"}` - Insert errors (should be 0)
- `vl_http_requests_total{path="/insert/jsonline"}` - Total batches inserted

## Tag Extraction
Same as VictoriaMetrics importer - splits `release_id` into 12 single-word tags plus 8 composite IDs.

---

# Grafana Tempo (Trace Backend)

## Purpose
Tempo stores distributed traces for visualization in Grafana (flamegraphs, waterfall views). VictoriaLogs stores trace fields (`trace_id`, `span_id`, `parent_span_id`) but can't visualize traces - Tempo provides the trace-specific UI.

## Location
`fixtures/social_network/export_traces_to_tempo.py`

## Setup

Tempo is configured inline in `docker-compose.yml` using docker configs.

```bash
# Start Tempo (and other services)
docker compose up -d tempo
```

**Note:** Uses Tempo v2.10.0 with `ingestion_time_range_slack: 8760h` to support historical trace data. Earlier versions (<2.6.0) had a bug where block metadata used ingestion time instead of trace timestamps, making historical traces unqueryable.

**Ports:**
- 3200: Tempo HTTP API (query, health)
- 4317: OTLP gRPC receiver
- 4318: OTLP HTTP receiver

## Export Traces from Logs
```bash
# Export traces (4 files in parallel, batch-size 2000)
ls /opt/qairon/test_data/logs_*.jsonl | xargs -P 4 -I {} \
  python fixtures/social_network/export_traces_to_tempo.py {} --batch-size 2000
```

**Performance:** ~33k logs/sec per file × 4 parallel = ~132k logs/sec total

**Note:** Using `-P 4` and `--batch-size 2000` prevents Tempo from getting overwhelmed. Higher parallelism causes 500 errors.

## Grafana Tempo Data Source
1. Add data source: Type = Tempo
2. URL: `http://tempo:3200`
3. Save & Test

## Querying Traces
```bash
# Search traces via API
curl -s "http://localhost:3200/api/search?limit=10"

# Get specific trace by ID
curl -s "http://localhost:3200/api/traces/<trace_id>"
```

## Correlating Logs and Traces
In Grafana, configure "Trace to logs" in Tempo data source settings:
- Data source: VictoriaLogs
- Query: `trace_id:"${__trace.traceId}"`

This enables clicking from a trace span directly to the corresponding logs.

---

# Docker Management

All services are defined in `docker-compose.yml` (Tempo config is embedded inline using docker configs).

## Start All Services
```bash
docker compose up -d
```

## Stop (preserve data)
```bash
docker compose stop
```

## Restart
```bash
docker compose restart
```

## View Logs
```bash
docker compose logs -f              # All services
docker compose logs -f victoria     # Single service
```

## Wipe and Restart
```bash
# Stop and remove containers
docker compose down

# Wipe data (choose which to wipe)
rm -rf /mnt/qairon/victoria-metrics-data/*
rm -rf /mnt/qairon/victoria-logs-data/*
rm -rf /mnt/qairon/tempo-data/*
rm -rf /mnt/qairon/grafana/*

# Start fresh
docker compose up -d
```

**Note:** The `:z` flag in volume mounts is required on SELinux systems to relabel bind mounts for container access.

## VictoriaLogs Performance Tuning

VictoriaLogs auto-tunes based on available CPU/RAM but benefits from explicit tuning for bulk ingestion.

**Current docker-compose flags:**
```
-maxConcurrentInserts=240      # Max concurrent insert requests (default: 60)
-fs.maxConcurrency=1000        # Max parallel file I/O goroutines (default: 265)
-inmemoryDataFlushInterval=15s # Flush interval to disk (default: 5s)
-memory.allowedPercent=60      # Cache memory limit as % of system RAM (default: 60)
```

**Key performance flags:**

| Flag | Default | Effect |
|------|---------|--------|
| `-maxConcurrentInserts` | 60 | Limits parallel insert HTTP requests |
| `-fs.maxConcurrency` | 265 | Limits parallel file I/O goroutines |
| `-inmemoryDataFlushInterval` | 5s | How often data is flushed to disk; higher = fewer IOPS, more RAM |
| `-memory.allowedPercent` | 60 | % of system RAM for caches; too high causes GC pressure |

**Bottleneck: Storage Merge IOPS**

VictoriaLogs compacts data via background "small merges." During bulk ingestion, these merges generate thousands of tiny 3-4KB writes that saturate NVMe IOPS even though throughput (MB/s) is low. Mitigations:
- Increase `--batch-size` on the importer (500000 vs 50000) — fewer HTTP requests, bigger in-memory batches
- Increase `-inmemoryDataFlushInterval` (15s vs 5s) — fewer fsync operations
- Reduce import parallelism if merge queue (`vl_active_merges{type="storage/small"}`) is saturated

**Monitoring VictoriaLogs during import:**
```bash
# Check active merges (main bottleneck indicator)
curl -s http://localhost:9428/metrics | grep vl_active_merges

# Check insert errors
curl -s http://localhost:9428/metrics | grep 'vl_http_errors_total.*jsonline'

# Check ingested row count
curl -s http://localhost:9428/metrics | grep vl_rows_ingested_total
```

## Storage: md RAID10 Tuning

The data volumes live on md RAID10 across 4 NVMe drives.

**Write bitmap:** md RAID10 maintains an integrity bitmap that adds I/O overhead on every write. For bulk import, temporarily disabling it dramatically improves write IOPS:
```bash
# Disable bitmap (bulk import)
sudo mdadm --grow /dev/md127 --bitmap=none

# Re-enable bitmap (normal operation)
sudo mdadm --grow /dev/md127 --bitmap=internal
```

**Risk:** Without the bitmap, an unclean shutdown (power loss, kernel panic) requires a full array resync instead of partial resync. On 4 NVMe drives this takes ~10-20 minutes. Clean shutdowns are unaffected.

**Read-ahead:** Bump for sequential read performance:
```bash
for d in nvme4n1 nvme5n1 nvme6n1 nvme7n1; do
  echo 4096 | sudo tee /sys/block/$d/queue/read_ahead_kb
done
```

## Grafana Setup
- URL: http://localhost:3000
- Login: admin / admin

**Data Sources (use service names for internal resolution):**
- Prometheus (VictoriaMetrics): `http://victoria:8428`
- VictoriaLogs: `http://victorialogs:9428`
- Tempo: `http://tempo:3200`

---

# Fixture Generator

## Location
`fixtures/social_network/generate_fixtures.py`

## Purpose
Generates all Qairon entity data in dependency order, writing to both the database (via bulk insert) and optionally to TSV fixture files.

## Usage
```bash
SQLALCHEMY_DATABASE_URI=postgresql+psycopg2://qairon:qairon@localhost:5432/qairon \
  python fixtures/social_network/generate_fixtures.py [--txt-output <dir>]
```

## What It Generates
Data is created in 8 tiers plus associations:

| Tier | Tables | Typical Count |
|------|--------|---------------|
| 0: Reference | environments, provider_types, deployment_target_types, allocation_types, repo_types, languages | ~40 |
| 1: Infrastructure | providers, regions, zones, partitions, networks, subnets, fleet_types, deployment_targets, fleets, capacities | ~360K |
| 2: Application | applications, stacks, services, procs | ~720 |
| 3: Repos & Config | repos, config_templates | ~165 |
| 4: Deployments | deployments, deployment_procs | ~260K |
| 5: Temporal | builds, releases | ~184K |
| 6: Artifacts | build_artifacts, release_artifacts | ~1.1M |
| 7: Configs | deployment_configs, service_configs, stack_configs | ~218K |
| 8: Allocations | allocations | ~2.7M |
| M2M | services_repos, deployments_zones, subnets_fleets, target_fleets, deployment_current_release | ~540K |

Total: ~5.3M rows across 36 TSV files.

## Key Design Decisions
- **Deterministic**: Uses `random.seed(42)` for reproducible output
- **Bulk insert**: Batches of 5000 rows via SQLAlchemy `executemany` for performance
- **Gap-fill**: Ensures every deployment has at least 5 releases
- **Primary deployment targets**: 6 targets (2 prod regions, 1 each for stg/dev/int/infra) get full service deployments; all others get only core services
- **Deployment schedule export**: Automatically writes `deployment_schedule.json` for use by the monitoring data generator

## TSV Fixture Files

### Location
`fixtures/social_network/txt/` (source tree) or `--txt-output <dir>` (configurable)

### Format
Tab-separated values with header comments. Column order matches `convert_to_json.py` MAPPINGS:
```
# Table Name
# Format: col1	col2	col3
# Generated by generate_fixtures.py

value1	value2	value3
```

### 36 Files (numbered by dependency order)
01-06: Reference tables (environments, provider_types, etc.)
07-16: Infrastructure (providers → capacities)
17: Repos
18-22: Application (applications → config_templates)
23-26: Temporal (builds → releases)
27: Allocations
28-29: Artifacts
30-32: Configs
33-36: M2M associations

### Pipeline: TSV → JSON:API → REST API
```bash
# Convert TSV to JSON:API
python fixtures/social_network/convert_to_json.py \
  --input-dir /opt/qairon/fixtures/social_network/txt \
  --output-dir /opt/qairon/fixtures/social_network/json

# Load JSON via REST API
python fixtures/social_network/load_json.py
```

### Data Integrity Rules
- Every deployment must have at least 5 releases (gap-filled automatically)
- Composite IDs are colon-delimited and build hierarchically
- `_` prefix columns in MAPPINGS (e.g., `_artifact_name`) are written to TSV but skipped by the JSON converter

---

# TODO

## Monitoring Data Generator

- [x] **Add distributed tracing support** - Implemented OpenTelemetry-style tracing:
  - `trace_id` (32 hex chars) - Consistent across a call chain
  - `span_id` (16 hex chars) - Unique per operation
  - `parent_span_id` - Links to parent (null for root spans)
  - Error-biased exemplar sampling for metrics (100% errors, 100% slow, 1% random)

- [x] **Generate child span events** - Full distributed tracing with parent-child span relationships:
  - For each root event, generates child spans for all `SERVICE_DEPENDENCIES`
  - Child spans share `trace_id` with parent, have unique `span_id`, link via `parent_span_id`
  - Timing: children start after parent, complete before parent (staggered offsets)
  - ~2.8x event multiplier (100 root events → ~280 total events)
  - Error propagation: infrastructure incidents affect child spans appropriately

- [x] **Streaming to disk** - Large datasets write directly to per-worker files to avoid OOM:
  - Workers write directly to `logs_N.jsonl` and `metrics_N.jsonl`
  - No RAM accumulation, enables 50M+ event generation
  - Import each file separately to VictoriaMetrics/VictoriaLogs

- [x] **Deployment-aware monitoring** - Logs/metrics align with actual deployment events:
  - `generate_fixtures.py` exports `deployment_schedule.json` with release timelines
  - `generate_monitoring_data.py --deployment-schedule` uses real release IDs and creates deployment dips
  - Deployment windows: throughput reduction (15-30%), error rate boost (2-5%), latency increase (20-50%)
  - Multi-region stagger: same-stack services deploy to region A first, region B 30-60min later
  - Deployment log events: `deployment_start` and `deployment_complete` with `user_id: "system"`

- [x] **Fixture generator with TSV export** - `generate_fixtures.py` generates all Qairon entities:
  - Bulk inserts to database (5000 rows/batch via SQLAlchemy executemany)
  - Optional `--txt-output` exports 36 TSV fixture files (5.3M rows)
  - Pipeline: TSV → `convert_to_json.py` → JSON:API → `load_json.py` → REST API
  - `convert_to_json.py` now accepts `--input-dir` and `--output-dir` CLI args
