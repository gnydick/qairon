# Qairon — Onboarding Guide

> Generated from the Understand-Anything knowledge graph (commit `dda8d00`).
>
> **Scope:** this guide covers the **core Qairon platform**. The synthetic-monitoring / observability toolchain — data generators, VictoriaMetrics/VictoriaLogs/Tempo importers, Grafana dashboards, the observability Docker Compose stack, and the monitoring-focused BDD features — is being extracted to a separate project and is intentionally **excluded** here.

## 1. Project Overview

**Qairon** is a centralized **Single Source of Truth (SSoT)** platform for modeling, managing, and querying an entire infrastructure & operations topology in one relational model — enabling full traceability from code to production and back.

It is delivered as three cooperating interfaces over one PostgreSQL-backed model:
- a **relational data model** (SQLAlchemy ORM),
- a **REST API + Flask-Admin UI** (the `app.py` Flask app),
- and a **pluggable Click CLI**, `qcli` (also embeddable as a Python module).

| | |
|---|---|
| **Primary language** | Python 3.9+ (target 3.13 in CI/Docker) |
| **Other languages** | YAML, Dockerfile, Gherkin (`.feature`), HTML/CSS, TOML |
| **Frameworks** | Flask, SQLAlchemy, Alembic, Click, flask-restless-ng, Flask-Admin, behave, Docker |
| **Packaging** | setuptools distribution `qairon_qcli` exposing the `qcli` console script |

### The one idea that unlocks the codebase: canonical composite IDs

Every entity's identity is a **colon-delimited composite ID** built hierarchically, and each model derives its own ID in a SQLAlchemy `before_insert`/`before_update` listener. Learn this shape and the whole system reads cleanly:

```
{env}:{provider}:{account}:{region}:{partition}:{target_type}:{target}:{app}:{stack}:{service}:{tag}:{release_num}
```

- Infrastructure path (*where code runs*): `provider_id` → `region_id` → `partition_id` → `target_id`
- Application path (*what runs*): `stack_id` (`app:stack`) → `service_id` (`app:stack:service`)
- **Environment sits at the top of the infrastructure hierarchy on purpose** — it enforces multi-account isolation; resources cannot be shared across environments.

---

## 2. Architecture Layers

The core platform sorts into 6 layers. Dependency direction generally flows **top → down** (models are foundational; everything else builds on them).

| Layer | What lives here |
|---|---|
| **Domain & ORM Models** | SQLAlchemy entities for the whole topology (providers → allocations, builds/releases/deployments), the shared `db` instance, and the dependencies-plugin models. |
| **REST API & Admin UI** | `app.py` app factory / REST host, Flask-Admin `ModelView`s, serializers, CIDR converter, Jinja2 admin templates, static assets. |
| **qcli Client & Plugins** | The Click/argparse CLI: controller stack, REST client, schema, tab-completion, and the `aws`/`bake`/`dependencies` plugins; plus `qcli_as_module` embedding examples. |
| **Infrastructure & Deployment** | `Dockerfile` (packages the app image) and the GitHub Actions CI pipeline. |
| **Testing (behave BDD)** | Gherkin feature specs, step definitions, and the harness that bootstraps a fresh DB per feature. |
| **Documentation & Project Config** | README/setup/audit docs, requirements, setuptools packaging, coverage, IDE descriptors. |

---

## 3. Key Concepts & Design Decisions

- **Single Source of Truth (intent, not actual state).** Qairon records *what should exist*; IaC (Terraform, K8s manifests) and deployment artifacts are generated *from* Qairon. Reconciliation = comparing actual against Qairon's intent (see the `defaults`-field `recon` patterns in the README).
- **Self-deriving composite IDs.** Models never accept a hand-built ID for their identity — `before_insert` listeners compose it from component parts. This discipline is what makes the platform trustworthy as an SSoT.
- **Layered CLI controller stack.** `qcli.py` → `QCLIController` (facade) → `OperationsController` (verbs) → `RestController` (HTTP). The CLI talks to the *same* REST API the Admin UI exposes — it is a client, not a second data path.
- **Dynamic, schema-driven CLI.** `args.py` + `schema.py` generate per-model `create/list/get/set-field` subparsers with `argcomplete` tab-completion wired to the REST client — adding a model surfaces CLI commands with little bespoke code.
- **Pluggability.** Both the server model (`plugins/dependencies/` — polymorphic `Relatable`/`Related` relationships) and the CLI (`qairon_qcli/plugins/` — `aws`, `bake`, `dependencies`, discovered at runtime via `lib/dynamic.py`) extend without touching the core.
- **Bake = generation in action.** The `bake` plugin renders a deployment's stored configs into Helm-style files (env/attribute substitution, Jinja2, AWS secret resolution) — a concrete demonstration of Qairon as the authoritative generation source.
- **BDD-first correctness.** Behavior is specified in Gherkin and executed end-to-end (CLI, REST) against a freshly bootstrapped DB, run in CI on every change.

---

## 4. Guided Tour (recommended reading order)

1. **What Qairon Is** — `README.md`, `DEVSETUP.md`. Absorb the mission and the composite-ID conventions before touching code.
2. **Application Entry Point** — `app.py`. The Flask app factory that wires models + views together and adds custom REST endpoints (health, on-the-fly Terraform/config generation). Root of the dependency graph.
3. **Shared DB & Model Registry** — `db.py` (the single shared SQLAlchemy instance — most depended-upon file in the repo), `models/__init__.py` (barrel that registers every mapper on import).
4. **The Domain Model** — `models/application.py`, `stack.py`, `service.py`, `environment.py`. The `application:stack:service` hierarchy and environment-anchored isolation; study the `before_insert` ID derivation.
5. **Deployments, Builds & Releases** — `models/deployment.py`, `build.py`, `release.py`. Closes the loop from code to production; where forward/backward traceability lives.
6. **Exposing the Model** — `views/__init__.py`, `views/default_view.py`, `serializers/default.py`, `templates/base_list.html`. How ORM entities become a browsable Admin UI + queryable REST surface.
7. **Extending the Model — Dependencies Plugin** — `plugins/dependencies/models/*`. Polymorphic `DependencyCase` / `Relatable` / `Related` relationship layer that plugs into the admin UI.
8. **The qcli Client** — `qcli.py`, `args.py`, `rest_controller.py`, `qcli_controller.py`. The controller stack, dynamic subparser generation, and the HTTP client that talks to the REST API.
9. **qcli Plugins — aws & bake** — `aws/cli/aws.py`, `bake/cli/bake.py`, `bake/.../file.py`, `dependencies/.../dependencies.py`. Secrets Manager integration and config baking.
10. **Behave BDD Tests & CI** — `features/environment.py`, `cli_controller.feature`, `features/steps/cli.py`, `.github/workflows/test.yml`. Where correctness is enforced.

---

## 5. File Map (by layer)

### Domain & ORM Models
- `db.py` — shared SQLAlchemy `db` instance (ORM session + declarative base) used by every model. **Most depended-upon file in the project.**
- `models/__init__.py` — barrel importing every model so all mappers/relationships register on package load.
- **Application path:** `application.py` (top of hierarchy), `stack.py` (`app:stack`), `service.py` (`app:stack:service`), `proc.py`.
- **Infrastructure path:** `environment.py`, `provider.py`/`provider_type.py`, `region.py`, `partition.py`, `zone.py`, `deployment_target.py`/`deployment_target_type.py`, `fleet.py`/`fleet_type.py`, `capacity.py`, `network.py`, `subnet.py` (IPv4 computed props + `SubnetUnavailableError`), `allocation.py`/`allocation_type.py`.
- **Lifecycle:** `build.py` (derived `git_tag`), `artifact.py` (BuildArtifact + ReleaseArtifact), `release.py` (full 12-part release ID), `deployment.py` (links target↔service; relationships to configs/zones/procs/releases), `deployment_proc.py`, `config.py` (three-level DeploymentConfig/ServiceConfig/StackConfig), `config_template.py`.
- **Support:** `repo.py`/`repo_type.py`, `language.py`, `associations.py` (M2M join tables).
- **Dependencies plugin models:** `plugins/dependencies/models/{dependency,dependency_case,relatable,related}.py`.

### REST API & Admin UI
- `app.py` **(complex)** — Flask app factory / REST host; wires models + views, adds health + Terraform/config-generation endpoints.
- `base.py` — bootstraps the Flask app, SQLAlchemy engine options, Talisman CSP, HTTPS URL normalization.
- `views/__init__.py` (barrel), `views/default_view.py` (base `ModelView` all entities inherit — shared search/sort/export/templates), `views/with_id_view.py`, `views/sti_view.py`, plus per-entity views (`service_view.py`, `deployment_view.py`, `network_view.py`, `subnet_view.py`, `config_view.py`, …).
- `converters/cidr.py` — maps the Postgres CIDR column type to a WTForms field; used by network/subnet views.
- `serializers/default.py` — bridges API output into the CLI's row formatter.
- `templates/base_{create,edit,list}.html` + `templates/admin/master.html` + `static/css/main.css` — Admin UI shell.
- Dependencies-plugin admin views: `plugins/dependencies/views/*`.

### qcli Client & Plugins
- `qcli.py` — CLI entry point; assembles the controller stack, parses argv, dispatches to command or plugin.
- `controllers/args.py` **(complex)** — dynamic argparse tree with argcomplete completers.
- `controllers/operations_controller.py` **(complex)** — verb layer (get/list/query/CRUD, clone, promote, allocate-subnet).
- `controllers/rest_controller.py` **(complex)** — HTTP client (search/CRUD, M2M membership, pagination, subnet allocation, completer backends).
- `controllers/qcli_controller.py` (facade), `output_controller.py` (pluggable output formatting), `schema.py` (create-field declarations), `functions.py` (shared helpers), `subnets.py`, `lib/dynamic.py` (plugin discovery).
- **Plugins:** `plugins/aws/` (Secrets Manager via boto3), `plugins/bake/` (config baking → `controllers/baking/file.py` **(complex)**), `plugins/dependencies/` (get_related).
- **Embedding examples:** `qcli_as_module/{main,helm_to_files_bake_engine,generate_dt_inventory_by_acount}.py`.

### Infrastructure & Deployment
- `Dockerfile` — builds the Qairon Flask application image on `python:3.13`, copying controllers, models, views, migrations, and app entry points.
- `.github/workflows/test.yml` — CI: spins up Postgres 17, installs deps, starts the app, and runs the behave suite against the running endpoint.

### Testing (behave BDD)
- `features/environment.py` — harness that bootstraps a fresh DB + qcli stack per feature and tears it down afterward.
- Feature specs: `cli_controller.feature` (CLI create/get/delete across the entity hierarchy), `rest_controller.feature` (REST entity creation + M2M links), `tab_complete.feature` (dynamic shell tab-completion).
- Step defs: `features/steps/{cli,rest_api,tab_complete}.py`.

### Documentation & Project Config
- `README.md` **(complex)** — project overview + reconciliation patterns + tool comparisons (Terraform state, CMDB, artifact registries).
- `DEVSETUP.md` — local dev setup (Postgres, pip, SQLAlchemy config, running the server, building/publishing the qcli package).
- `SCALAR_OUTPUT_AUDIT.md` — design audit of the qcli output pipeline (simplify_row / simplify_rows / handle / _output_ separation).
- `requirements.txt` / `dev_requirements.txt`, `setup.py` / `setup.cfg` / `pyproject.toml`, `.coveragerc`, `.python-version`, `.iml` descriptors.
- `CLAUDE.md` — repo developer guide. *Note: much of it documents the separate observability toolchain; treat those sections as belonging to the extracted project.*

---

## 6. Complexity Hotspots — approach with care

The core-platform files that carry the most complexity. Read them slowly and lean on the tests before changing them.

**Core runtime & CLI**
- `app.py` — the app factory wiring *everything*; custom Terraform/config-generation endpoints. A change here can affect the whole app.
- `qairon_qcli/controllers/rest_controller.py` — the REST client every CLI verb funnels through (pagination, M2M, subnet allocation, completers).
- `qairon_qcli/controllers/operations_controller.py` — verb translation layer (clone/promote/allocate-subnet).
- `qairon_qcli/controllers/args.py` — dynamic subparser generation; subtle interactions with argcomplete + schema.
- `qairon_qcli/plugins/bake/controllers/baking/file.py` — env/attribute substitution + Jinja2 + AWS secret resolution.

**Tests**
- `features/steps/cli.py` — drives the qcli client and captures stdout to assert created entity IDs.
- `features/steps/rest_api.py` — exercises the REST client for entity creation and M2M links.

**Reference docs**
- `README.md` — dense but authoritative; read before large changes.

---

## Getting started checklist

1. Read the tour docs (step 1) — internalize the composite-ID format.
2. `pip install -r requirements.txt`; set `SQLALCHEMY_DATABASE_URI`; `flask db upgrade`.
3. Run the app (`flask run` / gunicorn) and browse the Flask-Admin UI.
4. Try the CLI: `export QAIRON_ENDPOINT=http://localhost:5000` then `qcli service list`.
5. Create a few entities via the CLI (or your own fixtures) to explore the model hierarchy.
6. Run the tests: `behave`.
