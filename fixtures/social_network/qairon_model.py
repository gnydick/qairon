"""
In-memory Qairon model: hierarchical topology loaded from fixture TSVs.

All IDs are canonical colon-delimited composites.  Walk the model to find anything.
"""

from __future__ import annotations

import random
import re
import uuid
from bisect import bisect_right
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# =============================================================================
# PRIMARY DEPLOYMENT TARGETS — shared by both generators
# =============================================================================

PRIMARY_DEPLOYMENT_TARGETS = [
    # PROD — 2 AWS accounts × 2 regions, 2 GCP accounts × 2 regions, 2 Azure accounts × 2 regions (12 targets)
    'prod:aws:111111111111:us-east-1:platform:eks:main',
    'prod:aws:111111111111:us-west-2:platform:eks:main',
    'prod:aws:111111111112:us-east-1:platform:eks:main',
    'prod:aws:111111111112:us-west-2:platform:eks:main',
    'prod:gcp:social-prod-001:us-central1:platform:gke:main',
    'prod:gcp:social-prod-001:southamerica-east1:platform:gke:main',
    'prod:gcp:social-prod-002:us-central1:platform:gke:main',
    'prod:gcp:social-prod-002:us-east4:platform:gke:main',
    'prod:azure:prod-sub-001:eastus:platform:aks:main',
    'prod:azure:prod-sub-001:westeurope:platform:aks:main',
    'prod:azure:prod-sub-002:eastus:platform:aks:main',
    'prod:azure:prod-sub-002:westus2:platform:aks:main',
    # STG — 1 each (3 targets)
    'stg:aws:222222222221:us-east-1:platform:eks:main',
    'stg:gcp:social-stg-001:us-central1:platform:gke:main',
    'stg:azure:stg-sub-001:eastus:platform:aks:main',
    # DEV — 1 each (3 targets)
    'dev:aws:333333333331:us-east-1:platform:eks:main',
    'dev:gcp:social-dev-001:us-central1:platform:gke:main',
    'dev:azure:dev-sub-001:eastus:platform:aks:main',
    # INT — 1 each (3 targets)
    'int:aws:444444444441:us-east-1:platform:eks:main',
    'int:gcp:social-int-001:us-central1:platform:gke:main',
    'int:azure:int-sub-001:eastus:platform:aks:main',
    # INFRA — AWS only (1 target)
    'infra:aws:555555555555:us-east-1:platform:eks:main',
]

# Environment traffic weights
ENV_WEIGHT_MAP = {
    "prod": 0.85,
    "stg": 0.10,
    "dev": 0.03,
    "int": 0.015,
    "infra": 0.005,
}

# Regional latency/error characteristics for geo-distributed simulation
REGION_PROFILES = {
    # AWS US regions (baseline)
    "us-east-1": {"latency_multiplier": 1.0, "error_multiplier": 1.0},
    "us-west-2": {"latency_multiplier": 1.1, "error_multiplier": 1.0},
    # AWS EU regions
    "eu-west-1": {"latency_multiplier": 1.3, "error_multiplier": 1.05},
    "eu-central-1": {"latency_multiplier": 1.35, "error_multiplier": 1.05},
    # AWS AP regions
    "ap-southeast-1": {"latency_multiplier": 1.5, "error_multiplier": 1.1},
    "ap-northeast-1": {"latency_multiplier": 1.45, "error_multiplier": 1.08},
    # AWS CA region
    "ca-central-1": {"latency_multiplier": 1.15, "error_multiplier": 1.02},
    # GCP US regions
    "us-central1": {"latency_multiplier": 1.05, "error_multiplier": 1.0},
    "us-east4": {"latency_multiplier": 1.0, "error_multiplier": 1.0},
    # GCP EU regions
    "europe-west1": {"latency_multiplier": 1.3, "error_multiplier": 1.05},
    "europe-west4": {"latency_multiplier": 1.32, "error_multiplier": 1.05},
    # GCP Asia regions
    "asia-southeast1": {"latency_multiplier": 1.5, "error_multiplier": 1.1},
    "asia-east1": {"latency_multiplier": 1.48, "error_multiplier": 1.09},
    # GCP South America
    "southamerica-east1": {"latency_multiplier": 1.6, "error_multiplier": 1.12},
    # Azure regions
    "eastus": {"latency_multiplier": 1.0, "error_multiplier": 1.0},
    "westus2": {"latency_multiplier": 1.1, "error_multiplier": 1.0},
    "northeurope": {"latency_multiplier": 1.3, "error_multiplier": 1.05},
    "westeurope": {"latency_multiplier": 1.3, "error_multiplier": 1.05},
    "southeastasia": {"latency_multiplier": 1.5, "error_multiplier": 1.1},
    "japaneast": {"latency_multiplier": 1.45, "error_multiplier": 1.08},
    "canadacentral": {"latency_multiplier": 1.15, "error_multiplier": 1.02},
}

DEFAULT_REGION_PROFILE = {"latency_multiplier": 1.2, "error_multiplier": 1.05}

HIGH_FREQUENCY_SERVICES = [
    'social:user:identity',
    'social:content:posts',
    'social:feed:timeline',
    'social:platform:api-gateway',
    'social:messaging:dm',
    'social:content:media',
]


# =============================================================================
# ENTITY DATACLASSES
# =============================================================================

@dataclass
class Environment:
    id: str
    traffic_weight: float = 0.0
    providers: Dict[str, Provider] = field(default_factory=dict)

    @property
    def targets(self) -> List[str]:
        result = []
        for provider in self.providers.values():
            for region in provider.regions.values():
                for partition in region.partitions.values():
                    for target in partition.targets.values():
                        result.append(target.id)
        return result


@dataclass
class Provider:
    id: str             # "prod:aws:111111111111"
    environment: str
    provider_type: str
    account: str
    regions: Dict[str, Region] = field(default_factory=dict)


@dataclass
class Region:
    id: str             # "prod:aws:111111111111:us-east-1"
    name: str
    provider_id: str
    partitions: Dict[str, Partition] = field(default_factory=dict)


@dataclass
class Partition:
    id: str             # "prod:aws:111111111111:us-east-1:platform"
    name: str
    region_id: str
    targets: Dict[str, DeploymentTarget] = field(default_factory=dict)


@dataclass
class DeploymentTarget:
    id: str             # full 7-component target_id
    partition_id: str
    target_type: str
    name: str
    environment: str
    provider: str
    account: str
    region: str
    partition: str
    is_primary: bool = False
    deployments: Dict[str, Deployment] = field(default_factory=dict)


@dataclass
class Application:
    id: str
    stacks: Dict[str, Stack] = field(default_factory=dict)


@dataclass
class Stack:
    id: str             # "social:content"
    name: str
    application: str
    services: Dict[str, Service] = field(default_factory=dict)


@dataclass
class Service:
    id: str             # "social:content:posts"
    name: str
    stack_id: str
    application: str
    stack: str
    high_frequency: bool = False
    builds: List[Build] = field(default_factory=list)
    incidents: List = field(default_factory=list)


@dataclass
class Deployment:
    id: str             # "target_id:service_id:tag"
    deployment_target_id: str
    service_id: str
    tag: str = "default"
    releases: List[Release] = field(default_factory=list)
    current_release: Optional[Release] = None
    release_timeline: List[Tuple[datetime, str, int]] = field(default_factory=list)
    deployment_windows: List = field(default_factory=list)


@dataclass
class Build:
    id: str             # "service_id:build_num"
    service_id: str
    build_num: int
    vcs_ref: str
    ver: str
    created_at: datetime
    artifacts: List[BuildArtifact] = field(default_factory=list)


@dataclass
class BuildArtifact:
    id: str
    build_id: str
    name: str
    input_repo_id: str
    output_repo_id: str
    upload_path: str
    created_at: datetime


@dataclass
class Release:
    id: str             # "deployment_id:build_num"
    deployment_id: str
    build_id: str
    build_num: int
    created_at: datetime
    artifacts: List[ReleaseArtifact] = field(default_factory=list)


@dataclass
class ReleaseArtifact:
    id: str
    release_id: str
    name: str
    input_repo_id: str
    output_repo_id: str
    upload_path: str
    created_at: datetime


# =============================================================================
# QAIRON MODEL CONTAINER
# =============================================================================

class QaironModel:
    """Hierarchical in-memory model loaded from fixture TSV files."""

    def __init__(self):
        self.environments: Dict[str, Environment] = {}
        self.providers: Dict[str, Provider] = {}
        self.regions: Dict[str, Region] = {}
        self.partitions: Dict[str, Partition] = {}
        self.deployment_targets: Dict[str, DeploymentTarget] = {}
        self.applications: Dict[str, Application] = {}
        self.stacks: Dict[str, Stack] = {}
        self.services: Dict[str, Service] = {}
        self.deployments: Dict[str, Deployment] = {}
        self.primary_targets: List[str] = []
        self.region_profiles: Dict[str, dict] = dict(REGION_PROFILES)
        self.default_region_profile: dict = dict(DEFAULT_REGION_PROFILE)

    @classmethod
    def from_tsv(cls, tsv_dir: Path, primary_targets: List[str]) -> QaironModel:
        """Load topology from TSV fixture files, synthesizing missing entities."""
        tsv_dir = Path(tsv_dir)
        model = cls()
        model.primary_targets = list(primary_targets)

        # Load environments
        for row in _parse_tsv(tsv_dir / "01_environments.txt", ["id"]):
            env_id = row["id"]
            model.environments[env_id] = Environment(
                id=env_id,
                traffic_weight=ENV_WEIGHT_MAP.get(env_id, 0.01),
            )

        # Load providers
        for row in _parse_tsv(tsv_dir / "07_providers.txt", ["environment_id", "provider_type_id", "native_id"]):
            env_id = row["environment_id"]
            ptype = row["provider_type_id"]
            account = row["native_id"]
            provider_id = f"{env_id}:{ptype}:{account}"
            provider = Provider(id=provider_id, environment=env_id, provider_type=ptype, account=account)
            model.providers[provider_id] = provider
            if env_id in model.environments:
                model.environments[env_id].providers[provider_id] = provider

        # Load regions
        for row in _parse_tsv(tsv_dir / "08_regions.txt", ["provider_id", "name"]):
            provider_id = row["provider_id"]
            name = row["name"]
            region_id = f"{provider_id}:{name}"
            region = Region(id=region_id, name=name, provider_id=provider_id)
            model.regions[region_id] = region
            if provider_id in model.providers:
                model.providers[provider_id].regions[region_id] = region

        # Load partitions
        for row in _parse_tsv(tsv_dir / "10_partitions.txt", ["region_id", "name"]):
            region_id = row["region_id"]
            name = row["name"]
            partition_id = f"{region_id}:{name}"
            partition = Partition(id=partition_id, name=name, region_id=region_id)
            model.partitions[partition_id] = partition
            if region_id in model.regions:
                model.regions[region_id].partitions[partition_id] = partition

        # Load deployment targets
        for row in _parse_tsv(tsv_dir / "14_deployment_targets.txt", ["partition_id", "deployment_target_type_id", "name"]):
            partition_id = row["partition_id"]
            target_type = row["deployment_target_type_id"]
            name = row["name"]
            target_id = f"{partition_id}:{target_type}:{name}"
            parts = target_id.split(":")
            target = DeploymentTarget(
                id=target_id,
                partition_id=partition_id,
                target_type=target_type,
                name=name,
                environment=parts[0],
                provider=parts[1],
                account=parts[2],
                region=parts[3],
                partition=parts[4],
                is_primary=(target_id in primary_targets),
            )
            model.deployment_targets[target_id] = target
            if partition_id in model.partitions:
                model.partitions[partition_id].targets[target_id] = target

        # Load applications
        for row in _parse_tsv(tsv_dir / "18_applications.txt", ["id", "defaults"]):
            app_id = row["id"]
            model.applications[app_id] = Application(id=app_id)

        # Load stacks
        for row in _parse_tsv(tsv_dir / "19_stacks.txt", ["application_id", "name", "defaults"]):
            app_id = row["application_id"]
            name = row["name"]
            stack_id = f"{app_id}:{name}"
            stack = Stack(id=stack_id, name=name, application=app_id)
            model.stacks[stack_id] = stack
            if app_id in model.applications:
                model.applications[app_id].stacks[stack_id] = stack

        # Load services
        for row in _parse_tsv(tsv_dir / "20_services.txt", ["stack_id", "name", "_artifact_name", "defaults"]):
            stack_id = row["stack_id"]
            name = row["name"]
            service_id = f"{stack_id}:{name}"
            parts = stack_id.split(":")
            service = Service(
                id=service_id,
                name=name,
                stack_id=stack_id,
                application=parts[0],
                stack=parts[1],
                high_frequency=(service_id in HIGH_FREQUENCY_SERVICES),
            )
            model.services[service_id] = service
            if stack_id in model.stacks:
                model.stacks[stack_id].services[service_id] = service

        # Load deployments
        dep_file = tsv_dir / "24_deployments.txt"
        if dep_file.exists():
            for row in _parse_tsv(dep_file, ["deployment_target_id", "service_id", "tag", "defaults"]):
                target_id = row["deployment_target_id"]
                service_id = row["service_id"]
                tag = row.get("tag") or "default"
                deployment_id = f"{target_id}:{service_id}:{tag}"
                deployment = Deployment(
                    id=deployment_id,
                    deployment_target_id=target_id,
                    service_id=service_id,
                    tag=tag,
                )
                model.deployments[deployment_id] = deployment
                if target_id in model.deployment_targets:
                    model.deployment_targets[target_id].deployments[deployment_id] = deployment

        # Synthesize missing entities from primary_targets
        for target_id in primary_targets:
            _synthesize_target_chain(model, target_id)

        # Mark high-frequency flags
        for sid in HIGH_FREQUENCY_SERVICES:
            if sid in model.services:
                model.services[sid].high_frequency = True

        return model

    def environment_config(self) -> Dict[str, dict]:
        """Returns env -> {"targets": [target_info_dicts], "weight": float}.

        Equivalent to the old build_environment_config_from_schedule().
        """
        config: Dict[str, dict] = {}
        for target_id in self.primary_targets:
            parts = target_id.split(":")
            if len(parts) < 7:
                continue
            env = parts[0]
            target_info = {
                "provider": parts[1],
                "account": parts[2],
                "region": parts[3],
                "partition": parts[4],
                "target_type": parts[5],
                "target": parts[6],
            }
            if env not in config:
                config[env] = {"targets": [], "weight": ENV_WEIGHT_MAP.get(env, 0.01)}
            config[env]["targets"].append(target_info)
        return config

    def get_deployed_deps(self, target_id: str, dep_service_ids: List[str]) -> List[str]:
        """Return deployment_ids of dependencies that are actually deployed on this target.

        Args:
            target_id: The 7-component target_id (infra context).
            dep_service_ids: List of service_ids from SERVICE_DEPENDENCIES.

        Returns:
            List of deployment_ids that exist in the model's deployments dict.
        """
        result = []
        for dep_service_id in dep_service_ids:
            dep_deployment_id = f"{target_id}:{dep_service_id}:default"
            if dep_deployment_id in self.deployments:
                result.append(dep_deployment_id)
        return result

    def get_region_profile(self, region: str) -> dict:
        """Get latency/error profile for a region."""
        return self.region_profiles.get(region, self.default_region_profile)

    def get_active_release_id(self, env: str, region: str, stack: str, service: str,
                               timestamp: datetime) -> Optional[str]:
        """Binary search across all deployments matching (env, region, stack, service).

        Returns the release_id of the most recent release created before timestamp.
        """
        # Walk primary targets to find matching deployment(s)
        for target_id in self.primary_targets:
            parts = target_id.split(":")
            if parts[0] != env or parts[3] != region:
                continue
            deployment_id = f"{target_id}:social:{stack}:{service}:default"
            dep = self.deployments.get(deployment_id)
            if not dep or not dep.release_timeline:
                continue
            timeline = dep.release_timeline
            # Binary search: find latest entry where created_at <= timestamp
            idx = bisect_right(timeline, (timestamp,)) - 1
            if idx >= 0:
                return timeline[idx][1]
        return None

    def get_active_deployment_window(self, stack: str, service: str, env: str, region: str,
                                      timestamp: datetime):
        """Check if timestamp falls within a deployment window for this service."""
        for target_id in self.primary_targets:
            parts = target_id.split(":")
            if parts[0] != env or parts[3] != region:
                continue
            deployment_id = f"{target_id}:social:{stack}:{service}:default"
            dep = self.deployments.get(deployment_id)
            if not dep or not dep.deployment_windows:
                continue
            windows = dep.deployment_windows
            # Binary search
            lo, hi = 0, len(windows) - 1
            while lo <= hi:
                mid = (lo + hi) // 2
                if windows[mid].end_time < timestamp:
                    lo = mid + 1
                elif windows[mid].start_time > timestamp:
                    hi = mid - 1
                else:
                    return windows[mid]
        return None

    def get_deployment_log_events(self) -> List[Dict]:
        """Returns list of deployment_start/deployment_complete log entries."""
        events = []
        for dep in self.deployments.values():
            for window in dep.deployment_windows:
                deploy_request_id = f"deploy_{uuid.uuid4().hex[:16]}"
                base = {
                    "service": window.service,
                    "stack": window.stack,
                    "user_id": "system",
                    "success": True,
                    "release_id": window.release_id,
                    "object_type": "deployment",
                    "object_id": window.deployment_id,
                    "persona_name": "system",
                }
                events.append({
                    **base,
                    "timestamp": window.start_time,
                    "action": "deployment_start",
                    "request_id": deploy_request_id,
                    "message": f"Deployment started: rolling restart for release {window.release_id}",
                    "trace_id": ''.join(random.choices('0123456789abcdef', k=32)),
                    "span_id": ''.join(random.choices('0123456789abcdef', k=16)),
                })
                events.append({
                    **base,
                    "timestamp": window.end_time,
                    "action": "deployment_complete",
                    "request_id": deploy_request_id,
                    "message": f"Deployment complete: release {window.release_id} fully rolled out",
                    "trace_id": ''.join(random.choices('0123456789abcdef', k=32)),
                    "span_id": ''.join(random.choices('0123456789abcdef', k=16)),
                })
        events.sort(key=lambda e: e["timestamp"])
        return events

    def to_serializable(self) -> Dict:
        """Serialize for passing to parallel workers via ProcessPoolExecutor.

        Serializes: release timelines, deployment windows, environment config,
        incidents (from services), primary targets, and region profiles.
        """
        timelines = {}
        windows = {}
        for dep_id, dep in self.deployments.items():
            if dep.release_timeline:
                timelines[dep_id] = [
                    (created_at.isoformat(), release_id, build_num)
                    for created_at, release_id, build_num in dep.release_timeline
                ]
            if dep.deployment_windows:
                windows[dep_id] = [
                    {
                        "deployment_id": w.deployment_id,
                        "release_id": w.release_id,
                        "stack": w.stack,
                        "service": w.service,
                        "env": w.env,
                        "region": w.region,
                        "start_time": w.start_time.isoformat(),
                        "end_time": w.end_time.isoformat(),
                        "throughput_factor": w.throughput_factor,
                        "error_rate_boost": w.error_rate_boost,
                        "latency_multiplier": w.latency_multiplier,
                    }
                    for w in dep.deployment_windows
                ]

        # Collect all incidents from services
        incidents_data = []
        for service in self.services.values():
            for inc in service.incidents:
                incidents_data.append({
                    "service_key": inc.service_key,
                    "start_time": inc.start_time.isoformat(),
                    "end_time": inc.end_time.isoformat(),
                    "failure_rate": inc.failure_rate,
                    "error_codes": inc.error_codes,
                    "error_type": inc.error_type,
                    "error_message": inc.error_message,
                    "region_scope": inc.region_scope,
                })

        return {
            "timelines": timelines,
            "windows": windows,
            "incidents": incidents_data,
            "env_config": self.environment_config(),
            "primary_targets": self.primary_targets,
            "region_profiles": self.region_profiles,
            "default_region_profile": self.default_region_profile,
        }

    @classmethod
    def from_serializable(cls, data: Dict) -> QaironModel:
        """Reconstruct a minimal model from serialized form in worker processes.

        Only reconstructs what workers need: release timelines, deployment windows,
        environment config, region profiles. Does NOT reconstruct full topology.
        """
        # Import here to avoid circular import at module level
        from generate_monitoring_data import DeploymentWindow, ServiceIncident

        model = cls()
        model.primary_targets = data.get("primary_targets", [])
        model.region_profiles = data.get("region_profiles", dict(REGION_PROFILES))
        model.default_region_profile = data.get("default_region_profile", dict(DEFAULT_REGION_PROFILE))

        # Reconstruct deployments with timelines and windows
        for dep_id, timeline_data in data.get("timelines", {}).items():
            dep = model.deployments.get(dep_id)
            if dep is None:
                parts = dep_id.split(":")
                dep = Deployment(
                    id=dep_id,
                    deployment_target_id=":".join(parts[:7]),
                    service_id=":".join(parts[7:10]),
                    tag=parts[10] if len(parts) > 10 else "default",
                )
                model.deployments[dep_id] = dep
            dep.release_timeline = [
                (datetime.fromisoformat(created_at), release_id, build_num)
                for created_at, release_id, build_num in timeline_data
            ]

        for dep_id, win_list in data.get("windows", {}).items():
            dep = model.deployments.get(dep_id)
            if dep is None:
                parts = dep_id.split(":")
                dep = Deployment(
                    id=dep_id,
                    deployment_target_id=":".join(parts[:7]),
                    service_id=":".join(parts[7:10]),
                    tag=parts[10] if len(parts) > 10 else "default",
                )
                model.deployments[dep_id] = dep
            dep.deployment_windows = [
                DeploymentWindow(
                    deployment_id=w["deployment_id"],
                    release_id=w["release_id"],
                    stack=w["stack"],
                    service=w["service"],
                    env=w["env"],
                    region=w["region"],
                    start_time=datetime.fromisoformat(w["start_time"]),
                    end_time=datetime.fromisoformat(w["end_time"]),
                    throughput_factor=w["throughput_factor"],
                    error_rate_boost=w["error_rate_boost"],
                    latency_multiplier=w["latency_multiplier"],
                )
                for w in win_list
            ]

        # Reconstruct incidents into service stubs
        for inc_data in data.get("incidents", []):
            service_key = inc_data["service_key"]
            if service_key not in model.services:
                parts = service_key.split(":")
                model.services[service_key] = Service(
                    id=service_key,
                    name=parts[2] if len(parts) > 2 else service_key,
                    stack_id=":".join(parts[:2]) if len(parts) > 1 else service_key,
                    application=parts[0] if parts else "",
                    stack=parts[1] if len(parts) > 1 else "",
                )
            model.services[service_key].incidents.append(
                ServiceIncident(
                    service_key=inc_data["service_key"],
                    start_time=datetime.fromisoformat(inc_data["start_time"]),
                    end_time=datetime.fromisoformat(inc_data["end_time"]),
                    failure_rate=inc_data["failure_rate"],
                    error_codes=inc_data["error_codes"],
                    error_type=inc_data["error_type"],
                    error_message=inc_data["error_message"],
                    region_scope=inc_data.get("region_scope"),
                )
            )

        return model

    def write_fixture_tsvs(self, output_dir: Path):
        """Write build/release/artifact TSVs from model data."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        build_records = []
        build_artifact_records = []
        release_records = []
        release_artifact_records = []
        deployment_current_release = []

        # Collect builds from services
        for service in self.services.values():
            for build in service.builds:
                build_records.append({
                    "id": build.id,
                    "service_id": build.service_id,
                    "build_num": build.build_num,
                    "vcs_ref": build.vcs_ref,
                    "ver": build.ver,
                    "created_at": build.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "defaults": "{}",
                })
                for artifact in build.artifacts:
                    build_artifact_records.append({
                        "id": artifact.id,
                        "build_id": artifact.build_id,
                        "input_repo_id": artifact.input_repo_id,
                        "output_repo_id": artifact.output_repo_id,
                        "name": artifact.name,
                        "upload_path": artifact.upload_path,
                        "data": "{}",
                        "created_at": artifact.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    })

        # Collect releases from deployments
        for dep in self.deployments.values():
            for release in dep.releases:
                release_records.append({
                    "id": release.id,
                    "deployment_id": release.deployment_id,
                    "build_id": release.build_id,
                    "build_num": release.build_num,
                    "created_at": release.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "defaults": "{}",
                })
                for artifact in release.artifacts:
                    release_artifact_records.append({
                        "id": artifact.id,
                        "release_id": artifact.release_id,
                        "input_repo_id": artifact.input_repo_id,
                        "output_repo_id": artifact.output_repo_id,
                        "name": artifact.name,
                        "upload_path": artifact.upload_path,
                        "data": "{}",
                        "created_at": artifact.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    })
            if dep.current_release:
                deployment_current_release.append({
                    "deployment_id": dep.id,
                    "release_id": dep.current_release.id,
                })

        def write_tsv(filename, table_name, columns, records):
            filepath = output_dir / filename
            with open(filepath, 'w') as f:
                f.write(f"# {table_name}\n")
                f.write(f"# Format: {chr(9).join(columns)}\n")
                f.write("# Generated by generate_monitoring_data.py\n\n")
                for rec in records:
                    f.write('\t'.join(str(rec[col]) for col in columns) + '\n')
            print(f"    Wrote {len(records)} records to {filepath}")

        write_tsv("33_builds.txt", "Builds",
                  ["id", "service_id", "build_num", "vcs_ref", "ver", "created_at", "defaults"],
                  build_records)

        write_tsv("34_build_artifacts.txt", "Build Artifacts",
                  ["id", "build_id", "input_repo_id", "output_repo_id", "name", "upload_path", "data", "created_at"],
                  build_artifact_records)

        write_tsv("35_releases.txt", "Releases",
                  ["id", "deployment_id", "build_id", "build_num", "created_at", "defaults"],
                  release_records)

        write_tsv("36_release_artifacts.txt", "Release Artifacts",
                  ["id", "release_id", "input_repo_id", "output_repo_id", "name", "upload_path", "data", "created_at"],
                  release_artifact_records)

        write_tsv("37_deployment_current_release.txt", "Deployment Current Release",
                  ["deployment_id", "release_id"],
                  deployment_current_release)

        print(f"    Fixture records: {len(build_records)} builds, {len(build_artifact_records)} build artifacts, "
              f"{len(release_records)} releases, {len(release_artifact_records)} release artifacts, "
              f"{len(deployment_current_release)} deployment current releases")


# =============================================================================
# TSV PARSING HELPER
# =============================================================================

def _parse_tsv(filepath: Path, columns: List[str]) -> List[dict]:
    """Parse a TSV file, skipping comments and blank lines."""
    records = []
    if not filepath.exists():
        return records
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            cols = line.split('\t')
            row = {}
            for i, col_name in enumerate(columns):
                if col_name.startswith('_'):
                    continue
                if i < len(cols) and cols[i]:
                    row[col_name] = cols[i]
                else:
                    row[col_name] = ""
            records.append(row)
    return records


# =============================================================================
# SYNTHESIZE MISSING ENTITY CHAINS
# =============================================================================

def _synthesize_target_chain(model: QaironModel, target_id: str):
    """Ensure the full entity chain for target_id exists in the model.

    If any part of the chain (environment, provider, region, partition, target)
    is missing, create it.  This handles GCP/Azure targets when TSVs are AWS-only.
    """
    parts = target_id.split(":")
    if len(parts) != 7:
        return

    env, provider_type, account, region_name, partition_name, target_type, target_name = parts

    # Environment
    if env not in model.environments:
        model.environments[env] = Environment(
            id=env,
            traffic_weight=ENV_WEIGHT_MAP.get(env, 0.01),
        )

    # Provider
    provider_id = f"{env}:{provider_type}:{account}"
    if provider_id not in model.providers:
        provider = Provider(id=provider_id, environment=env, provider_type=provider_type, account=account)
        model.providers[provider_id] = provider
        model.environments[env].providers[provider_id] = provider

    # Region
    region_id = f"{provider_id}:{region_name}"
    if region_id not in model.regions:
        region = Region(id=region_id, name=region_name, provider_id=provider_id)
        model.regions[region_id] = region
        model.providers[provider_id].regions[region_id] = region

    # Partition
    partition_id = f"{region_id}:{partition_name}"
    if partition_id not in model.partitions:
        partition = Partition(id=partition_id, name=partition_name, region_id=region_id)
        model.partitions[partition_id] = partition
        model.regions[region_id].partitions[partition_id] = partition

    # Deployment target
    if target_id not in model.deployment_targets:
        target = DeploymentTarget(
            id=target_id,
            partition_id=partition_id,
            target_type=target_type,
            name=target_name,
            environment=env,
            provider=provider_type,
            account=account,
            region=region_name,
            partition=partition_name,
            is_primary=True,
        )
        model.deployment_targets[target_id] = target
        model.partitions[partition_id].targets[target_id] = target
    else:
        model.deployment_targets[target_id].is_primary = True

    # Ensure deployments exist for all services on primary targets
    for service in model.services.values():
        deployment_id = f"{target_id}:{service.id}:default"
        if deployment_id not in model.deployments:
            dep = Deployment(
                id=deployment_id,
                deployment_target_id=target_id,
                service_id=service.id,
                tag="default",
            )
            model.deployments[deployment_id] = dep
            model.deployment_targets[target_id].deployments[deployment_id] = dep
