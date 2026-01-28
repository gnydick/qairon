# Qairon

**A Single Source of Truth (SSoT) for Infrastructure and Operations**

Qairon is a centralized platform for modeling, managing, and querying your entire infrastructure topology. It provides a unified relational model that captures applications, deployments, infrastructure, and their relationships - enabling full traceability from code to production and back.

## What is Qairon?

Qairon solves the fundamental problem of infrastructure fragmentation: when information about your systems is scattered across terraform state files, Kubernetes manifests, CI/CD configs, spreadsheets, and tribal knowledge, you lose the ability to answer basic questions like "what depends on this?" or "what changed?"

Qairon provides:
- **A relational data model** capturing your complete infrastructure topology
- **REST API** for programmatic access and integration
- **CLI tool (`qcli`)** for command-line operations and scripting
- **Python module** for embedding in automation pipelines

## Core Concepts

### The Infrastructure Model

Qairon models infrastructure through interconnected entities that mirror how modern systems are actually built and operated:

#### Application Hierarchy
```
Application
    └── Stack
        └── Service
            └── Proc (Process definition)
```

An **Application** is a logical grouping of related functionality. **Stacks** are independently deployable units within an application. **Services** are the actual running components, and **Procs** define how they execute.

#### Deployment Lifecycle
```
Build
    └── Build Artifact
        └── Release
            └── Release Artifact
                └── Deployment
                    └── Deployment Config
```

A **Build** produces **Build Artifacts** (compiled outputs). **Releases** bundle artifacts for deployment and produce **Release Artifacts** (the actual deployable packages). **Deployments** put releases onto specific targets with associated **Configurations**.

Critically, artifacts track **where they are published** - container registries, artifact repositories, S3 buckets, etc. You never lose sight of where your binaries live.

#### Infrastructure Topology
```
Environment (prod, staging, dev)
    └── Provider (AWS, GCP, Azure, on-prem)
        └── Region
            └── Partition (availability zone, data center)
                └── Fleet (group of compute resources)
                    └── Deployment Target
```

**Environment** is intentionally at the top of the infrastructure hierarchy. This is a critical architectural decision: everything underneath an environment genuinely belongs to that environment. A provider account cannot be shared across environments - this enforces multi-account isolation by design.

All infrastructure IDs carry their environment prefix (e.g., `prod:`, `staging:`, `dev:`). This makes environment membership explicit and prevents accidental cross-environment references. Resources like fleets, clusters, networks, and deployment targets cannot be shared across environments.

If you need to connect resources across environments (e.g., a `dev:` resource to an `int:` resource), you must use your provider's peering mechanisms (VPC peering, Transit Gateway, etc.) to explicitly break the isolation boundary.

**Providers** contain **Regions**, which contain **Partitions** (availability zones, data centers). **Fleets** are logical groupings of compute within partitions, and **Deployment Targets** are where releases actually run.

#### Networking
```
Network
    └── Subnet
        └── Allocation
```

Network topology is tracked separately and cross-referenced with the infrastructure and deployment models.

### Unified Traceability

The power of Qairon is that all these entities are relationally connected. You can traverse the graph in any direction:

- **Forward**: "What infrastructure runs this service?" → Service → Deployment → Deployment Target → Fleet → Partition → Region → Provider
- **Backward**: "What services depend on this fleet?" → Fleet → Deployment Targets → Deployments → Services
- **Lateral**: "What else is deployed alongside this?" → Deployment Target → All Deployments → Services
- **Provenance**: "Where is this deployment's binary?" → Deployment → Release → Release Artifact → location (registry, S3, etc.)
- **Lineage**: "What commit produced this artifact?" → Build Artifact → Build → commit SHA

## Operational Models

### 1. Infrastructure-as-Code Generation

Qairon serves as the authoritative data source from which IaC can be generated:

```
┌─────────────────┐
│     Qairon      │
│   (Database)    │
└────────┬────────┘
         │ query via API/CLI
         ▼
┌─────────────────┐      ┌─────────────────┐
│  Your Templates │  →   │   Terraform     │
│  / Generators   │      │   K8s Manifests │
└─────────────────┘      └─────────────────┘
```

You query Qairon for the canonical data (networks, regions, services, deployment targets) and feed it into your own templating or generation logic. This ensures your IaC always reflects the single source of truth.

### 2. Configuration Management

Pair Qairon with a git repository containing your actual terraform and configuration files:

```
Qairon (SSoT)              Git Repository
┌──────────────┐           ┌──────────────┐
│ What should  │    →      │ What is      │
│ exist        │  generate │ declared     │
└──────────────┘           └──────────────┘
```

Qairon is the **source of intent** for infrastructure - it defines what should exist. The git repository contains the IaC that implements that intent.

What gets recorded **into** Qairon:
- **Build & artifact lifecycle**: Builds, build artifacts, releases, release artifacts - including where artifacts are published (registries, repos, buckets)
- **Native resource IDs**: AWS ARNs, GCP resource IDs, etc. for cross-referencing convenience

What gets generated **from** Qairon:
- Infrastructure definitions (networks, regions, partitions, fleets)
- Deployment targets and configurations
- Service topology

This enables:
- **Artifact provenance**: Always know where your binaries are and what produced them
- **Change correlation**: Link git commits to Qairon entities
- **Impact analysis**: Understand blast radius before committing changes
- **Native ID lookups**: Quick reference to actual cloud resources

### 3. Deployment Orchestration & Artifact Tracking

Use Qairon to drive deployments and maintain full artifact provenance:

```
CI/CD Pipeline
      │
      ├─► Record Build (commit, branch, metadata)
      │
      ├─► Record Build Artifact (location: registry/repo/bucket)
      │
      ├─► Query Qairon for deployment target & config
      │
      └─► Execute deployment
              │
              └─► (Optionally) Record native ID back to Qairon
```

Your pipelines record builds and artifacts as they're created, query Qairon for deployment targets, and maintain a complete chain of custody. Given any running deployment, you can trace back to the exact binary, where it's stored, what build produced it, and what source commit it came from.

### 4. Capacity Planning & Allocation

Track resource allocations against available capacity:

```
Fleet (capacity: 100 CPU)
    └── Deployment Target A (allocated: 30 CPU)
    └── Deployment Target B (allocated: 25 CPU)
    └── Available: 45 CPU
```

Query for available capacity, track utilization trends, and plan infrastructure expansion.

### 5. Disaster Recovery & Compliance

With full relationship tracking, Qairon enables:
- **Dependency mapping** for DR planning
- **Audit trails** for compliance
- **Point-in-time queries** for incident investigation

## Installation

### Prerequisites

- Python 3.9+
- PostgreSQL 10+
- pyenv (recommended)

### Setup

1. Create Python virtual environments:
```bash
pyenv virtualenv 3.9.2 qairon-3.9.2
pyenv virtualenv 3.9.2 qairon-dev-3.9.2
```

2. Install dependencies:
```bash
pyenv activate qairon-3.9.2
pip install -r requirements.txt
pyenv deactivate

pyenv activate qairon-dev-3.9.2
pip install -r dev_requirements.txt
```

3. Configure database connection:
```bash
export SQLALCHEMY_DATABASE_URI=postgresql://qairon:qairon@localhost:5432/qairon
```

4. Initialize the database:
```bash
# Create PostgreSQL role and database first, then:
flask db upgrade
```

5. Run the server:
```bash
flask app
```

## Usage

### CLI (qcli)

The `qcli` command-line tool is pluggable and provides CRUD operations plus specialized functions like subnet allocation:

```bash
# Set the endpoint
export QAIRON_ENDPOINT=http://localhost:5000

# List all resources of a type
qcli service list
qcli deployment list

# Get a specific resource
qcli service get ecommerce:checkout:order-processor

# Get related resources via get_field
qcli stack get_field ecommerce:payments services
qcli service get_field ecommerce:checkout:order-processor deployments

# Create resources (positional args)
qcli service create ecommerce:checkout order-processor

# Query with flask-restless-ng syntax
qcli deployment query '{"filters":[{"name":"service_id","op":"eq","val":"ecommerce:checkout:order-processor"}]}'

# Allocate a non-overlapping subnet (e.g., /22 from a /16 network)
# network_id = <partition_id>:<name>
qcli network allocate_subnet prod:aws:123456789012:us-east-1:us-east-1a:main-vpc 6 eks0

# Import resources from CSV files
qcli csv_import import_csv application applications.csv
qcli csv_import import_csv stack stacks.csv --dry-run
```

See [CSV_IMPORT.md](CSV_IMPORT.md) for detailed documentation on importing data from CSV files.

### As a Python Module

The same operations available via CLI can be used programmatically. Positional CLI arguments become named parameters:

```python
from qairon_qcli.controllers import QCLIController, PrintingOutputController

qcli = QCLIController(PrintingOutputController())

# CLI: qcli service get ecommerce:checkout:order-processor
qcli.get(resource='service', resource_id='ecommerce:checkout:order-processor')

# CLI: qcli service list
qcli.list(resource='service')

# CLI: qcli stack get_field ecommerce:payments services
qcli.get_field(resource='stack', resource_id='ecommerce:payments', field='services')

# CLI: qcli network allocate_subnet prod:aws:123456789012:us-east-1:us-east-1a:main-vpc 6 eks0
qcli.allocate_subnet(network_id='prod:aws:123456789012:us-east-1:us-east-1a:main-vpc', additional_mask_bits=6, name='eks0')
```

### REST API

Full REST endpoints for all entities:

```bash
# Get all services
curl http://localhost:5000/api/services

# Get specific deployment
curl http://localhost:5000/api/deployments/123

# Create a release
curl -X POST http://localhost:5000/api/releases \
  -H "Content-Type: application/json" \
  -d '{"build_artifact_id": 456, "version": "1.2.3"}'
```

## Project Structure

```
qairon/
├── models/           # SQLAlchemy ORM models
├── views/            # Flask REST API views
├── serializers/      # JSON serialization
├── migrations/       # Alembic database migrations
├── qairon_qcli/      # CLI package
├── features/         # BDD tests (Gherkin)
├── plugins/          # Extension points
├── templates/        # HTML templates (admin UI)
└── static/           # Static assets
```

## Integration Patterns

### With Terraform

1. Define infrastructure in Qairon
2. Query Qairon via API/CLI to feed your templating/generation tools
3. Store generated `.tf` files in git
4. Run `terraform apply` from CI/CD
5. (Optional) Record native resource IDs back to Qairon for reference

### With Kubernetes

1. Define services and deployments in Qairon
2. Query Qairon to feed your manifest generation tools
3. Apply via kubectl or GitOps (ArgoCD, Flux)
4. (Optional) Record native resource identifiers back to Qairon

### With CI/CD

The integration between CI/CD and Qairon is deep. The ideal workflow tracks the full artifact lifecycle:

- **Builds** are recorded with source commit, branch, and build system metadata
- **Build Artifacts** track the input repo (source code location) and output repo (where the artifact was published)
- **Releases** bundle builds into deployable units for a specific deployment
- **Release Artifacts** track the input repo (where the build artifact lives) and output repo (where the release artifact was published)

This means you **never lose sight of where your binaries are**. Given any deployment, you can trace back to the exact artifact, where it's stored, what build produced it, and what commit it came from.

```yaml
# Example GitHub Actions integration
- name: Build
  run: |
    docker build -t $IMAGE:$TAG .

- name: Record Build
  run: |
    BUILD_ID=$(qcli build create $SERVICE_ID $BUILD_NUM $GITHUB_SHA)
    echo "BUILD_ID=$BUILD_ID" >> $GITHUB_ENV

- name: Push Build Artifact
  run: |
    docker push $IMAGE:$TAG

- name: Record Build Artifact
  run: |
    qcli build_artifact create $BUILD_ID $INPUT_REPO_ID $OUTPUT_REPO_ID $NAME $UPLOAD_PATH

- name: Record Release
  run: |
    RELEASE_ID=$(qcli release create $BUILD_ID $DEPLOYMENT_ID $BUILD_NUM)
    echo "RELEASE_ID=$RELEASE_ID" >> $GITHUB_ENV

- name: Bake and Push Release Artifact
  run: |
    bake $RELEASE_ID

- name: Record Release Artifact
  run: |
    qcli release_artifact create $RELEASE_ID $INPUT_REPO_ID $OUTPUT_REPO_ID $NAME $UPLOAD_PATH

- name: Deploy
  run: |
    deploy $DEPLOYMENT_ID
```

## Why Qairon?

Each of these tools stores actual state. Qairon stores intended state. Reconciliation means comparing actual against intended to detect drift.

### Storing Reconciliation Patterns in Qairon

Every Qairon object has a `defaults` field that can store arbitrary metadata - including the reconciliation patterns themselves. Store patterns on **type** objects so all instances share the same documentation. Override on specific instances only when needed.

```bash
# Store terraform reconciliation patterns on the provider_type (applies to all AWS providers)
qcli provider_type set_field aws defaults '{
  "recon": {
    "terraform": {
      "vpc_jq": ".values.root_module.resources[] | select(.type == \"aws_vpc\") | {native_id: .values.id, cidr: .values.cidr_block}",
      "qairon_network_jq": "{native_id: .native_id, cidr: .cidr}"
    }
  }
}'

# Store k8s reconciliation patterns on the deployment_target_type (applies to all EKS clusters)
qcli deployment_target_type set_field eks defaults '{
  "recon": {
    "k8s_jq": "[.items[] | {service: .metadata.name, namespace: .metadata.namespace, image: .spec.template.spec.containers[0].image}] | sort_by(.service)",
    "qairon_jq": "[.[] | {service: (.service_id | split(\":\") | .[-1]), namespace: (.service_id | split(\":\") | .[1]), image: .current_release.release_artifacts[0].upload_path}] | sort_by(.service)"
  }
}'

# Instance-specific overrides only when needed (e.g., this cluster has a different context name)
qcli deployment_target set_field prod:aws:123456789012:us-east-1:us-east-1a:eks:main-cluster defaults '{
  "recon": {
    "k8s_context": "prod-eks-main-cluster"
  }
}'

# Retrieve type-level patterns, merge with instance overrides
TYPE_DEFAULTS=$(qcli deployment_target_type get_field eks defaults -o plain)
INSTANCE_DEFAULTS=$(qcli deployment_target get_field prod:aws:123456789012:us-east-1:us-east-1a:eks:main-cluster defaults -o plain)
K8S_JQ=$(echo $TYPE_DEFAULTS | jq -r '.recon.k8s_jq')
K8S_CTX=$(echo $INSTANCE_DEFAULTS | jq -r '.recon.k8s_context')

kubectl --context "$K8S_CTX" get deployments -A -o json | jq "$K8S_JQ" > k8s_running.json
```

### Unix-Philosophy Integration with Defaults

> **Note:** The following examples demonstrate how Qairon data can be integrated into shell pipelines and scripts. While this showcases the flexibility of the system, these patterns are inherently cumbersome, error-prone, and brittle to change. They are provided as illustrations of what's *possible*, not necessarily what's *recommended* for production automation. For robust integrations, consider wrapping these patterns in tested scripts or using the Python module directly.

**Load patterns into environment variables:**

```bash
# Load all recon patterns from a type into env vars
eval $(qcli deployment_target_type get_field eks defaults -o plain | \
  jq -r '.recon | to_entries[] | "export RECON_\(.key | ascii_upcase)=\((.value | @json))"')

# Now use them directly
kubectl get deployments -A -o json | jq "$RECON_K8S_JQ" > actual.json
qcli deployment_target get_field $DT_ID deployments -o json | jq "$RECON_QAIRON_JQ" > intended.json
diff actual.json intended.json
```

**One-liner with process substitution:**

```bash
diff <(kubectl get deployments -A -o json | \
       jq "$(qcli deployment_target_type get_field eks defaults -o plain | jq -r '.recon.k8s_jq')") \
     <(qcli deployment_target get_field $DT_ID deployments -o json | \
       jq "$(qcli deployment_target_type get_field eks defaults -o plain | jq -r '.recon.qairon_jq')")
```

**Shell function for reusable pattern fetching:**

```bash
# Add to .bashrc or source from a script
qrecon() {
  local resource_type=$1 pattern_name=$2 type_id=$3
  qcli ${resource_type}_type get_field "$type_id" defaults -o plain | jq -r ".recon.$pattern_name"
}

# Usage
diff <(kubectl get deployments -A -o json | jq "$(qrecon deployment_target k8s_jq eks)") \
     <(qcli deployment_target get_field $DT_ID deployments -o json | jq "$(qrecon deployment_target qairon_jq eks)")
```

**Merge type + instance defaults:**

```bash
# Merge type-level and instance-level defaults (instance overrides type)
merge_defaults() {
  local type_defaults=$1 instance_defaults=$2
  echo "$type_defaults" "$instance_defaults" | jq -s '.[0] * .[1]'
}

TYPE=$(qcli deployment_target_type get_field eks defaults -o plain)
INSTANCE=$(qcli deployment_target get_field $DT_ID defaults -o plain)
MERGED=$(merge_defaults "$TYPE" "$INSTANCE")

# Extract from merged
K8S_JQ=$(echo "$MERGED" | jq -r '.recon.k8s_jq')
K8S_CTX=$(echo "$MERGED" | jq -r '.recon.k8s_context')
```

**Pipe-friendly reconciliation script:**

```bash
#!/bin/bash
# recon.sh - generic reconciliation using Qairon defaults
RESOURCE_TYPE=$1  # e.g., deployment_target
TYPE_ID=$2        # e.g., eks
INSTANCE_ID=$3    # e.g., prod:aws:...:eks:main-cluster
ACTUAL_CMD=$4     # e.g., "kubectl get deployments -A -o json"

TYPE_DEFAULTS=$(qcli ${RESOURCE_TYPE}_type get_field "$TYPE_ID" defaults -o plain)
INSTANCE_DEFAULTS=$(qcli $RESOURCE_TYPE get_field "$INSTANCE_ID" defaults -o plain)

ACTUAL_JQ=$(echo "$TYPE_DEFAULTS" | jq -r '.recon.actual_jq')
QAIRON_JQ=$(echo "$TYPE_DEFAULTS" | jq -r '.recon.qairon_jq')

diff <(eval "$ACTUAL_CMD" | jq "$ACTUAL_JQ") \
     <(qcli $RESOURCE_TYPE get_field "$INSTANCE_ID" deployments -o json | jq "$QAIRON_JQ")
```

### vs. Terraform State

Terraform state tracks what Terraform manages. Qairon tracks your complete infrastructure topology including things Terraform doesn't touch - service relationships, deployment history, capacity allocations.

**Reconciliation: "Do my Terraform-managed networks match Qairon's intent?"**

```bash
# Patterns stored on provider_type (see "Storing Reconciliation Patterns" above)
# Instance-specific: store terraform state path on the network
qcli network set_field prod:aws:123456789012:us-east-1:us-east-1a:main-vpc defaults '{
  "recon": {
    "terraform_state_path": "s3://terraform-state/prod/vpc.tfstate"
  }
}'

# Retrieve type-level patterns + instance-specific config
TYPE_DEFAULTS=$(qcli provider_type get_field aws defaults -o plain)
INSTANCE_DEFAULTS=$(qcli network get_field prod:aws:123456789012:us-east-1:us-east-1a:main-vpc defaults -o plain)
TF_JQ=$(echo $TYPE_DEFAULTS | jq -r '.recon.terraform.vpc_jq')
Q_JQ=$(echo $TYPE_DEFAULTS | jq -r '.recon.terraform.qairon_network_jq')
TF_STATE=$(echo $INSTANCE_DEFAULTS | jq -r '.recon.terraform_state_path')

terraform show -json $TF_STATE | jq -r "$TF_JQ" | jq -s 'sort_by(.native_id)' > tf_vpcs.json
qcli network get prod:aws:123456789012:us-east-1:us-east-1a:main-vpc -o json | jq "$Q_JQ" > qairon_networks.json
diff tf_vpcs.json qairon_networks.json
```

### vs. CMDB

Traditional CMDBs try to track actual infrastructure state and become stale because they're updated after the fact. Qairon is the **source of intent** for infrastructure - configuration is generated *from* Qairon. The build/artifact lifecycle flows *into* Qairon, giving you complete provenance without manual updates.

**Reconciliation: "Does the CMDB reflect what Qairon says should exist?"**

```bash
# Store jq patterns on deployment_target_type
qcli deployment_target_type set_field eks defaults '{
  "recon": {
    "cmdb_jq": "[.[] | {service: .service_name, cluster: .cluster_name, env: .environment}] | sort_by(.service)",
    "qairon_jq": "[.[] | {service: (.service_id | split(\":\") | .[-1]), cluster: (.deployment_target_id | split(\":\") | .[-1]), env: (.deployment_target_id | split(\":\") | .[0])}] | sort_by(.service)"
  }
}'

# Store instance-specific CMDB endpoint on the deployment_target
qcli deployment_target set_field prod:aws:123456789012:us-east-1:us-east-1a:eks:main-cluster defaults '{
  "recon": {
    "cmdb_endpoint": "https://cmdb.internal/api/services?cluster=main-cluster"
  }
}'

# Retrieve type-level patterns + instance-specific config
TYPE_DEFAULTS=$(qcli deployment_target_type get_field eks defaults -o plain)
INSTANCE_DEFAULTS=$(qcli deployment_target get_field prod:aws:123456789012:us-east-1:us-east-1a:eks:main-cluster defaults -o plain)
CMDB_JQ=$(echo $TYPE_DEFAULTS | jq -r '.recon.cmdb_jq')
Q_JQ=$(echo $TYPE_DEFAULTS | jq -r '.recon.qairon_jq')
CMDB_URL=$(echo $INSTANCE_DEFAULTS | jq -r '.recon.cmdb_endpoint')

curl -s "$CMDB_URL" | jq "$CMDB_JQ" > cmdb_services.json
qcli deployment_target get_field prod:aws:123456789012:us-east-1:us-east-1a:eks:main-cluster deployments -o json | jq "$Q_JQ" > qairon_services.json
diff cmdb_services.json qairon_services.json
```

### vs. Artifact Registries Alone

Container registries and artifact repos store your binaries but don't track relationships. Qairon connects artifacts to builds, builds to commits, releases to deployments, and deployments to infrastructure - so you can answer "what's running where and how did it get there?"

**Reconciliation: "Do published artifacts match what Qairon recorded?"**

```bash
# Store jq patterns on repo_type
qcli repo_type set_field ecr defaults '{
  "recon": {
    "ecr_jq": "[.imageDetails[] | .imageTags[] | {image: ($repo + \":\" + .)}] | sort_by(.image)",
    "qairon_jq": "[.[] | {image: .upload_path}] | sort_by(.image)"
  }
}'

# Store instance-specific repository name on the repo
qcli repo set_field ecr:ecommerce-order-processor defaults '{
  "recon": {
    "repository": "ecommerce/order-processor"
  }
}'

# Retrieve type-level patterns + instance-specific config
TYPE_DEFAULTS=$(qcli repo_type get_field ecr defaults -o plain)
INSTANCE_DEFAULTS=$(qcli repo get_field ecr:ecommerce-order-processor defaults -o plain)
ECR_JQ=$(echo $TYPE_DEFAULTS | jq -r '.recon.ecr_jq')
Q_JQ=$(echo $TYPE_DEFAULTS | jq -r '.recon.qairon_jq')
REPO=$(echo $INSTANCE_DEFAULTS | jq -r '.recon.repository')

aws ecr describe-images --repository-name "$REPO" | jq --arg repo "$REPO" "$ECR_JQ" > ecr_images.json
qcli repo get_field ecr:ecommerce-order-processor build_artifacts -o json | jq "$Q_JQ" > qairon_artifacts.json
diff ecr_images.json qairon_artifacts.json
```

### vs. Spreadsheets / Wikis

These can't be queried, don't enforce relationships, and drift from reality. Qairon provides relational integrity and programmatic access.

**Reconciliation: "Does the spreadsheet match Qairon?"**

```bash
# Spreadsheets don't have a "type" in Qairon, so store patterns at environment level
qcli environment set_field prod defaults '{
  "recon": {
    "spreadsheet_jq": "[.[] | {service: .service, stack: .stack, app: .application}] | sort_by(.service)",
    "qairon_service_jq": "[.[] | .id | split(\":\") | {app: .[0], stack: .[1], service: .[2]}] | sort_by(.service)"
  }
}'

# Store instance-specific spreadsheet path on the application
qcli application set_field ecommerce defaults '{
  "recon": {
    "spreadsheet_path": "/shared/docs/ecommerce-deployments.csv"
  }
}'

# Retrieve environment-level patterns + application-specific config
ENV_DEFAULTS=$(qcli environment get_field prod defaults -o plain)
APP_DEFAULTS=$(qcli application get_field ecommerce defaults -o plain)
SHEET_JQ=$(echo $ENV_DEFAULTS | jq -r '.recon.spreadsheet_jq')
Q_JQ=$(echo $ENV_DEFAULTS | jq -r '.recon.qairon_service_jq')
SHEET_PATH=$(echo $APP_DEFAULTS | jq -r '.recon.spreadsheet_path')

cat "$SHEET_PATH" | csvjson | jq "$SHEET_JQ" > spreadsheet.json
qcli service query '{"filters":[{"name":"stack.application_id","op":"eq","val":"ecommerce"}]}' -o json | jq "$Q_JQ" > qairon_services.json
diff spreadsheet.json qairon_services.json
```

### vs. Service Mesh Observability

Observability tools show you what *is* running. Qairon tracks what *should* be running and the full lifecycle of how it got there.

**Reconciliation: "Is what's running what Qairon says should be running?"**

```bash
# Store jq patterns on deployment_target_type (applies to all EKS clusters)
qcli deployment_target_type set_field eks defaults '{
  "recon": {
    "k8s_jq": "[.items[] | {service: .metadata.name, namespace: .metadata.namespace, image: .spec.template.spec.containers[0].image}] | sort_by(.service)",
    "qairon_jq": "[.[] | {service: (.service_id | split(\":\") | .[-1]), namespace: (.service_id | split(\":\") | .[1]), image: .current_release.release_artifacts[0].upload_path}] | sort_by(.service)"
  }
}'

# Store instance-specific k8s context on the deployment_target
qcli deployment_target set_field prod:aws:123456789012:us-east-1:us-east-1a:eks:main-cluster defaults '{
  "recon": {
    "k8s_context": "prod-eks-main"
  }
}'

# Retrieve type-level patterns + instance-specific config
TYPE_DEFAULTS=$(qcli deployment_target_type get_field eks defaults -o plain)
INSTANCE_DEFAULTS=$(qcli deployment_target get_field prod:aws:123456789012:us-east-1:us-east-1a:eks:main-cluster defaults -o plain)
K8S_JQ=$(echo $TYPE_DEFAULTS | jq -r '.recon.k8s_jq')
Q_JQ=$(echo $TYPE_DEFAULTS | jq -r '.recon.qairon_jq')
K8S_CTX=$(echo $INSTANCE_DEFAULTS | jq -r '.recon.k8s_context')

kubectl --context "$K8S_CTX" get deployments -A -o json | jq "$K8S_JQ" > k8s_running.json
qcli deployment_target get_field prod:aws:123456789012:us-east-1:us-east-1a:eks:main-cluster deployments -o json | jq "$Q_JQ" > qairon_intended.json
diff k8s_running.json qairon_intended.json
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Migrations

Some migrations require multiple steps. See `migrations/README.md` for details.