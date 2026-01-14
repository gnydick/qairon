# Qairon

**A Single Source of Truth (SSoT) for Infrastructure and Operations**

Qairon is a centralized platform for modeling, managing, and querying your entire infrastructure topology. It provides a unified relational model that captures applications, deployments, infrastructure, and their relationships—enabling full traceability from code to production and back.

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

Critically, artifacts track **where they are published**—container registries, artifact repositories, S3 buckets, etc. You never lose sight of where your binaries live.

#### Infrastructure Topology
```
Provider (AWS, GCP, Azure, on-prem)
    └── Region
        └── Partition (availability zone, data center)
            └── Fleet (group of compute resources)
                └── Deployment Target
```

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

Qairon is the **source of intent** for infrastructure—it defines what should exist. The git repository contains the IaC that implements that intent.

What gets recorded **into** Qairon:
- **Build & artifact lifecycle**: Builds, build artifacts, releases, release artifacts—including where artifacts are published (registries, repos, buckets)
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

The `qcli` command-line tool provides full CRUD operations:

```bash
# Set the endpoint
export QAIRON_ENDPOINT=http://localhost:5000

# Query infrastructure
qcli get services --stack payments
qcli get deployments --region us-east-1

# Create resources
qcli create service --name order-processor --stack checkout

# Traverse relationships
qcli get deployment-path --service order-service
```

### As a Python Module

```python
from qairon.qcli import CLIController as qcli

# Programmatic access to Qairon
services = qcli.get_services(stack="payments")
deployments = qcli.get_deployments(region="us-east-1")
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
- **Build Artifacts** track what was produced and where it was published (container registry, artifact repo, S3, etc.)
- **Releases** bundle artifacts into deployable units
- **Release Artifacts** track the final published packages and their locations

This means you **never lose sight of where your binaries are**. Given any deployment, you can trace back to the exact artifact, where it's stored, what build produced it, and what commit it came from.

```yaml
# Example GitHub Actions integration
- name: Record Build
  run: |
    BUILD_ID=$(qcli create build --service $SERVICE --commit $GITHUB_SHA --branch $GITHUB_REF)
    echo "BUILD_ID=$BUILD_ID" >> $GITHUB_ENV

- name: Build & Push
  run: |
    docker build -t $IMAGE:$TAG .
    docker push $IMAGE:$TAG
    # Record where the artifact lives
    qcli create build-artifact --build-id $BUILD_ID \
      --type docker-image \
      --location $REGISTRY/$IMAGE:$TAG

- name: Get Deployment Config
  run: |
    CONFIG=$(qcli get deployment-config --service $SERVICE --env prod)
    TARGET=$(qcli get deployment-target --env prod --region us-east-1)

- name: Deploy
  run: |
    deploy --target $TARGET --config $CONFIG

- name: Record Native ID (optional)
  run: |
    qcli update deployment --id $DEPLOYMENT_ID --native-id $AWS_RESOURCE_ARN
```

## Why Qairon?

### vs. Terraform State

Terraform state tracks what Terraform manages. Qairon tracks your complete infrastructure topology including things Terraform doesn't touch—service relationships, deployment history, capacity allocations.

### vs. CMDB

Traditional CMDBs try to track actual infrastructure state and become stale because they're updated after the fact. Qairon is the **source of intent** for infrastructure—configuration is generated *from* Qairon. The build/artifact lifecycle flows *into* Qairon, giving you complete provenance without manual updates.

### vs. Artifact Registries Alone

Container registries and artifact repos store your binaries but don't track relationships. Qairon connects artifacts to builds, builds to commits, releases to deployments, and deployments to infrastructure—so you can answer "what's running where and how did it get there?"

### vs. Spreadsheets / Wikis

These can't be queried, don't enforce relationships, and drift from reality. Qairon provides relational integrity and programmatic access.

### vs. Service Mesh Observability

Observability tools show you what *is* running. Qairon tracks what *should* be running and the full lifecycle of how it got there.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Migrations

Some migrations require multiple steps. See `migrations/README.md` for details.