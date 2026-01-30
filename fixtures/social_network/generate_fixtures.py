#!/usr/bin/env python3
"""Generate complete fixture data for Qairon social network platform."""

import os
import sys
import json
import random
import re
import hashlib
import argparse
from datetime import datetime, timedelta
from collections import defaultdict

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from sqlalchemy import insert, text
from base import app
from db import db
from models.associations import (
    deps_to_zones,
    subnets_to_fleets,
    target_to_fleets,
    svcs_to_repos,
    deployment_current_release
)

random.seed(42)
NOW = datetime.utcnow()

# Suppress SQLAlchemy SQL logging for performance
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

# Constants
ENVIRONMENTS = ['prod', 'stg', 'dev', 'int', 'infra', 'local']
PROVIDER_TYPES = ['aws', 'gcp', 'azure', 'dev']
DEPLOYMENT_TARGET_TYPES = ['eks', 'ecs', 'lambda', 'fargate', 'ec2', 'batch', 'apprunner']
REPO_TYPES = ['git', 'ecr', 'helm', 's3', 'npm', 'pypi', 'maven', 'docker']
LANGUAGES = ['yaml', 'json', 'toml', 'hcl', 'xml', 'properties', 'ini', 'env']

ALLOCATION_TYPES = [
    ('cpu', 'cores'),
    ('memory', 'GB'),
    ('disk', 'GB'),
    ('gpu', 'units'),
    ('network_bandwidth', 'Gbps'),
    ('iops', 'ops-sec'),
    ('connections', 'count'),
    ('replicas', 'count'),
]

PROVIDERS = {
    'prod': [('aws', '111111111111'), ('aws', '111111111112'), ('aws', '111111111113'), ('gcp', 'social-prod-001'), ('azure', 'prod-sub-001'), ('gcp', 'social-prod-002'), ('azure', 'prod-sub-002')],
    'stg': [('aws', '222222222221'), ('aws', '222222222222'), ('aws', '222222222223'), ('gcp', 'social-stg-001'), ('azure', 'stg-sub-001'), ('gcp', 'social-stg-002')],
    'dev': [('aws', '333333333331'), ('aws', '333333333332'), ('aws', '333333333333'), ('gcp', 'social-dev-001'), ('azure', 'dev-sub-001'), ('aws', '333333333334'), ('gcp', 'social-dev-002')],
    'int': [('aws', '444444444441'), ('aws', '444444444442'), ('aws', '444444444444'), ('gcp', 'social-int-001'), ('azure', 'int-sub-001'), ('azure', 'int-sub-002')],
    'infra': [('aws', '555555555555'), ('aws', '555555555556'), ('aws', '555555555557'), ('gcp', 'social-infra-001'), ('azure', 'infra-sub-001'), ('aws', '555555555558'), ('gcp', 'social-infra-002')],
    'local': [('dev', 'local-001'), ('dev', 'local-002'), ('dev', 'local-003'), ('dev', 'local-004'), ('dev', 'local-005'), ('dev', 'local-006'), ('dev', 'local-007')],
}

REGIONS_BY_PROVIDER = {
    'aws': ['us-east-1', 'us-west-2', 'eu-west-1', 'ap-southeast-1', 'ca-central-1', 'eu-central-1', 'ap-northeast-1'],
    'gcp': ['us-central1', 'us-east4', 'europe-west1', 'asia-east1', 'southamerica-east1', 'europe-west4', 'asia-southeast1'],
    'azure': ['eastus', 'westus2', 'westeurope', 'southeastasia', 'canadacentral', 'northeurope', 'japaneast'],
    'dev': ['local-1', 'local-2', 'local-3', 'local-4', 'local-5', 'local-6', 'local-7'],
}

PARTITIONS = ['platform', 'data', 'dmz', 'edge', 'mgmt', 'security', 'shared-services']
NETWORKS = ['primary', 'secondary', 'management', 'monitoring', 'transit', 'backup', 'peering']
SUBNETS = ['public-az1', 'public-az2', 'app-az1', 'app-az2', 'data-az1', 'data-az2', 'cache-az1']

FLEET_TYPES_BY_PROVIDER = {
    'aws': ['eks-managed-nodes', 'eks-fargate', 'ecs-ec2', 'ecs-fargate', 'lambda', 'ec2-asg', 'ec2-spot',
            'eks-gpu-nodes', 'sagemaker-endpoint', 'emr-cluster', 'redshift-cluster', 'elasticache-cluster',
            'opensearch-cluster', 'rds-cluster', 'msk-cluster', 'neptune-cluster'],
    'gcp': ['gke-standard', 'gke-autopilot', 'cloud-run', 'cloud-functions', 'compute-engine'],
    'azure': ['aks-standard', 'container-instances', 'azure-functions', 'vmss-standard', 'app-service'],
    'dev': ['docker', 'kind', 'minikube', 'podman', 'colima'],
}

FLEET_NAMES = ['general', 'compute-opt', 'memory-opt', 'spot', 'dedicated', 'gpu-opt', 'storage-opt']

APPLICATIONS = ['social', 'infra']

STACKS = {
    'social': ['user', 'social', 'content', 'feed', 'messaging', 'notifications', 'search', 'discovery',
               'moderation', 'ads', 'payments', 'creator', 'live', 'analytics', 'platform'],
    'infra': ['observability', 'cicd', 'security', 'networking', 'data'],
}

SERVICES = {
    'social:user': ['identity', 'profile', 'privacy', 'account', 'preferences'],
    'social:social': ['connections', 'blocks', 'suggestions', 'contacts', 'groups'],
    'social:content': ['posts', 'media', 'stories', 'comments', 'reactions', 'shares', 'hashtags'],
    'social:feed': ['timeline', 'ranking', 'fanout', 'aggregation', 'curation'],
    'social:messaging': ['dm', 'group-chat', 'realtime', 'presence', 'read-receipts'],
    'social:notifications': ['push', 'email', 'sms', 'inapp', 'notification-preferences'],
    'social:search': ['users-search', 'content-search', 'hashtags-search', 'indexer', 'autocomplete'],
    'social:discovery': ['trending', 'explore', 'recommendations', 'interests', 'nearby'],
    'social:moderation': ['content-review', 'auto-mod', 'reports', 'spam', 'trust-safety'],
    'social:ads': ['campaigns', 'targeting', 'bidding', 'delivery', 'ad-analytics'],
    'social:payments': ['processor', 'subscriptions', 'wallet', 'payouts', 'invoicing'],
    'social:creator': ['studio', 'creator-analytics', 'monetization', 'shop', 'partnerships'],
    'social:live': ['streaming', 'live-chat', 'gifts', 'vod', 'clips'],
    'social:analytics': ['events', 'warehouse', 'pipeline', 'reporting', 'ml-features'],
    'social:platform': ['api-gateway', 'rate-limiter', 'feature-flags', 'ab-testing', 'config-service'],
    'infra:observability': ['logging', 'metrics', 'tracing', 'alerting', 'dashboards'],
    'infra:cicd': ['pipelines', 'build-artifacts', 'deploy-service', 'testing', 'environments'],
    'infra:security': ['vault', 'scanner', 'compliance', 'identity-provider', 'secrets-manager'],
    'infra:networking': ['dns', 'cdn', 'load-balancer', 'firewall', 'vpn'],
    'infra:data': ['backup', 'replication', 'migration', 'archival', 'restore'],
}

PROCS = ['api', 'worker', 'consumer', 'scheduler', 'migrator', 'cron', 'exporter']

CONFIG_TEMPLATES = {
    'yaml': ['k8s-deployment', 'k8s-service', 'k8s-hpa', 'k8s-configmap', 'k8s-secret', 'app-config',
             'database-config', 'cache-config', 'logging-config', 'tracing-config', 'helm-values'],
    'json': ['feature-flags', 'aws-sqs-config', 'aws-sns-config', 'aws-s3-config', 'aws-dynamodb-config',
             'aws-elasticache-config', 'aws-rds-config', 'aws-opensearch-config', 'aws-kinesis-config'],
    'toml': ['cargo-config', 'rust-config', 'python-project', 'pyproject-toml', 'black-config'],
    'hcl': ['terraform-main', 'terraform-variables', 'terraform-backend', 'terraform-provider', 'terraform-outputs'],
    'xml': ['spring-config', 'pom-xml', 'logback-xml', 'web-xml', 'persistence-xml'],
    'properties': ['app-properties', 'db-properties', 'cache-properties', 'logging-properties', 'jvm-properties'],
    'ini': ['uwsgi-config', 'gunicorn-config', 'supervisor-config', 'pytest-config', 'mypy-config'],
    'env': ['dotenv-base', 'dotenv-dev', 'dotenv-stg', 'dotenv-prod', 'dotenv-test'],
}

PRIMARY_DEPLOYMENT_TARGETS = [
    'prod:aws:111111111111:us-east-1:platform:eks:main',
    'prod:aws:111111111111:us-west-2:platform:eks:main',
    'stg:aws:222222222221:us-east-1:platform:eks:main',
    'dev:aws:333333333331:us-east-1:platform:eks:main',
    'int:aws:444444444441:us-east-1:platform:eks:main',
    'infra:aws:555555555555:us-east-1:platform:eks:main',
]

CORE_SERVICES = [
    'social:user:identity',
    'social:content:posts',
    'social:feed:timeline',
    'social:platform:api-gateway',
    'social:platform:rate-limiter',
]

HIGH_FREQUENCY_SERVICES = [
    'social:user:identity',
    'social:content:posts',
    'social:feed:timeline',
    'social:platform:api-gateway',
    'social:messaging:dm',
    'social:content:media',
]

BUILD_ARTIFACT_NAMES = ['docker-image', 'helm-chart', 'test-report', 'sbom', 'changelog', 'coverage-report', 'lint-report']
RELEASE_ARTIFACT_NAMES = ['manifest', 'values', 'migration', 'rollback-plan', 'changelog', 'runbook', 'smoke-test']


class CIDRPool:
    """Allocates unique CIDR blocks for networks and subnets."""

    def __init__(self):
        self.network_counter = 0
        self.subnet_counters = defaultdict(int)

    def next_network_cidr(self):
        """Allocate a /20 network CIDR.

        Each /20 spans 16 /24 blocks, so we step by 16 in the 3rd octet.
        The 2nd+3rd octets form a 16-bit space (65536 values).
        When that overflows, we carry into the 1st octet (10 -> 11 -> ...).
        """
        flat = self.network_counter * 16
        octet1 = 10 + flat // 65536
        octet2 = (flat % 65536) // 256
        octet3 = flat % 256
        cidr = f"{octet1}.{octet2}.{octet3}.0/20"
        self.network_counter += 1
        return cidr

    def next_subnet_cidr(self, network_cidr):
        """Allocate a /24 subnet within a /20 network."""
        base_ip, prefix = network_cidr.split('/')
        octets = [int(x) for x in base_ip.split('.')]

        subnet_idx = self.subnet_counters[network_cidr]
        self.subnet_counters[network_cidr] += 1

        cidr = f"{octets[0]}.{octets[1]}.{octets[2] + subnet_idx}.0/24"
        return cidr


def random_date(days_ago_min, days_ago_max):
    """Generate a random datetime between days_ago_max and days_ago_min from now."""
    days_ago = random.uniform(days_ago_min, days_ago_max)
    return NOW - timedelta(days=days_ago)


def bulk_insert(table_name, rows, batch_size=5000):
    """Bulk insert rows into a table."""
    if not rows:
        return
    table = db.metadata.tables[table_name]
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i+batch_size]
        db.session.execute(insert(table), batch)
    db.session.flush()


def generate_zones(region_id, provider_type):
    """Generate 5-7 zones for a region."""
    zones = []
    region_name = region_id.split(':')[-1]
    all_letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
    num_zones = random.randint(5, 7)

    if provider_type == 'aws':
        for letter in all_letters[:num_zones]:
            zone_id = f"{region_id}:{region_name}{letter}"
            zones.append({
                'id': zone_id,
                'region_id': region_id,
                'name': f"{region_name}{letter}",
                'native_id': f"{region_name}{letter}",
                'created_at': random_date(300, 350),
                'defaults': '{}',
            })
    elif provider_type == 'gcp':
        for letter in all_letters[:num_zones]:
            zone_name = f"{region_name}-{letter}"
            zone_id = f"{region_id}:{zone_name}"
            zones.append({
                'id': zone_id,
                'region_id': region_id,
                'name': zone_name,
                'native_id': zone_name,
                'created_at': random_date(300, 350),
                'defaults': '{}',
            })
    elif provider_type == 'azure':
        for i in range(1, num_zones + 1):
            zone_name = f"zone-{i}"
            zone_id = f"{region_id}:{zone_name}"
            zones.append({
                'id': zone_id,
                'region_id': region_id,
                'name': zone_name,
                'native_id': zone_name,
                'created_at': random_date(300, 350),
                'defaults': '{}',
            })
    else:  # dev
        for letter in all_letters[:num_zones]:
            zone_name = f"{region_name}-{letter}"
            zone_id = f"{region_id}:{zone_name}"
            zones.append({
                'id': zone_id,
                'region_id': region_id,
                'name': zone_name,
                'native_id': zone_name,
                'created_at': random_date(300, 350),
                'defaults': '{}',
            })

    return zones


def generate(txt_output_dir=None):
    """Generate all fixture data in dependency order."""

    cidr_pool = CIDRPool()

    # Track generated IDs for cross-referencing
    all_providers = []
    all_regions = []
    all_zones = []
    all_partitions = []
    all_networks = []
    all_subnets = []
    all_fleet_types = []
    all_deployment_targets = []
    all_fleets = []
    all_stacks = []
    all_services = []
    all_procs = []
    all_repos = []
    all_config_templates = []
    all_deployments = []
    all_deployment_procs = []
    all_builds = []
    all_releases = []

    # =========================================================================
    # TIER 0: Reference/Lookup Tables
    # =========================================================================
    print("Tier 0: Reference tables...")

    # Environments
    env_rows = [{'id': env, 'created_at': random_date(350, 365), 'defaults': '{}'} for env in ENVIRONMENTS]
    bulk_insert('environment', env_rows)
    print(f"  - {len(env_rows)} environments")

    # Provider types
    pt_rows = [{'id': pt, 'created_at': random_date(350, 365), 'defaults': '{}'} for pt in PROVIDER_TYPES]
    bulk_insert('provider_type', pt_rows)
    print(f"  - {len(pt_rows)} provider_types")

    # Deployment target types
    dtt_rows = [{'id': dtt, 'created_at': random_date(350, 365), 'defaults': '{}'} for dtt in DEPLOYMENT_TARGET_TYPES]
    bulk_insert('deployment_target_type', dtt_rows)
    print(f"  - {len(dtt_rows)} deployment_target_types")

    # Allocation types
    at_rows = [{'id': at[0], 'unit': at[1], 'created_at': random_date(350, 365), 'defaults': '{}'}
               for at in ALLOCATION_TYPES]
    bulk_insert('allocation_type', at_rows)
    print(f"  - {len(at_rows)} allocation_types")

    # Repo types
    rt_rows = [{'id': rt, 'created_at': random_date(350, 365), 'defaults': '{}'} for rt in REPO_TYPES]
    bulk_insert('repo_type', rt_rows)
    print(f"  - {len(rt_rows)} repo_types")

    # Languages
    lang_rows = [{'id': lang, 'created_at': random_date(350, 365), 'defaults': '{}'} for lang in LANGUAGES]
    bulk_insert('language', lang_rows)
    print(f"  - {len(lang_rows)} languages")

    # =========================================================================
    # TIER 1: Infrastructure
    # =========================================================================
    print("\nTier 1: Infrastructure...")

    # Providers (5-7 per environment)
    provider_rows = []
    for env, providers in PROVIDERS.items():
        num_providers = random.randint(5, len(providers))
        selected = random.sample(providers, num_providers)
        for provider_type, native_id in selected:
            provider_id = f"{env}:{provider_type}:{native_id}"
            provider_rows.append({
                'id': provider_id,
                'environment_id': env,
                'provider_type_id': provider_type,
                'native_id': native_id,
                'created_at': random_date(320, 350),
                'defaults': '{}',
            })
            all_providers.append(provider_id)
    bulk_insert('provider', provider_rows)
    print(f"  - {len(provider_rows)} providers")

    # Regions (5-7 per provider)
    region_rows = []
    for provider_id in all_providers:
        provider_type = provider_id.split(':')[1]
        all_region_names = REGIONS_BY_PROVIDER[provider_type]
        num_regions = random.randint(5, len(all_region_names))
        region_names = random.sample(all_region_names, num_regions)
        for region_name in region_names:
            region_id = f"{provider_id}:{region_name}"
            region_rows.append({
                'id': region_id,
                'provider_id': provider_id,
                'name': region_name,
                'native_id': region_name,
                'created_at': random_date(310, 340),
                'defaults': '{}',
            })
            all_regions.append((region_id, provider_type))
    bulk_insert('region', region_rows)
    print(f"  - {len(region_rows)} regions")

    # Zones
    zone_rows = []
    for region_id, provider_type in all_regions:
        zones = generate_zones(region_id, provider_type)
        zone_rows.extend(zones)
        all_zones.extend([z['id'] for z in zones])
    bulk_insert('zone', zone_rows)
    print(f"  - {len(zone_rows)} zones")

    # Partitions (5-7 per region)
    partition_rows = []
    for region_id, _ in all_regions:
        num_partitions = random.randint(5, len(PARTITIONS))
        selected = random.sample(PARTITIONS, num_partitions)
        for partition_name in selected:
            partition_id = f"{region_id}:{partition_name}"
            partition_rows.append({
                'id': partition_id,
                'region_id': region_id,
                'name': partition_name,
                'native_id': f"vpc-{partition_name}",
                'created_at': random_date(300, 330),
                'defaults': '{}',
            })
            all_partitions.append(partition_id)
    bulk_insert('partition', partition_rows)
    print(f"  - {len(partition_rows)} partitions")

    # Networks (5-7 per partition)
    network_rows = []
    for partition_id in all_partitions:
        num_networks = random.randint(5, len(NETWORKS))
        selected = random.sample(NETWORKS, num_networks)
        for network_name in selected:
            network_id = f"{partition_id}:{network_name}"
            network_cidr = cidr_pool.next_network_cidr()
            network_rows.append({
                'id': network_id,
                'partition_id': partition_id,
                'name': network_name,
                'cidr': network_cidr,
                'native_id': f"vpc-{hashlib.md5(network_id.encode()).hexdigest()[:8]}",
                'created_at': random_date(290, 320),
                'defaults': '{}',
            })
            all_networks.append((network_id, network_cidr))
    bulk_insert('network', network_rows)
    print(f"  - {len(network_rows)} networks")

    # Subnets (5-7 per network)
    subnet_rows = []
    for network_id, network_cidr in all_networks:
        num_subnets = random.randint(5, len(SUBNETS))
        selected = random.sample(SUBNETS, num_subnets)
        for subnet_name in selected:
            subnet_id = f"{network_id}:{subnet_name}"
            subnet_cidr = cidr_pool.next_subnet_cidr(network_cidr)
            subnet_rows.append({
                'id': subnet_id,
                'network_id': network_id,
                'name': subnet_name,
                'cidr': subnet_cidr,
                'native_id': f"subnet-{hashlib.md5(subnet_id.encode()).hexdigest()[:8]}",
                'created_at': random_date(280, 310),
                'defaults': '{}',
            })
            all_subnets.append(subnet_id)
    bulk_insert('subnet', subnet_rows)
    print(f"  - {len(subnet_rows)} subnets")

    # Fleet types
    fleet_type_rows = []
    for provider_type, fleet_types in FLEET_TYPES_BY_PROVIDER.items():
        for ft_name in fleet_types:
            ft_id = f"{provider_type}:{ft_name}"
            fleet_type_rows.append({
                'id': ft_id,
                'provider_type_id': provider_type,
                'name': ft_name,
                'created_at': random_date(310, 340),
                'defaults': '{}',
            })
            all_fleet_types.append((ft_id, provider_type))
    bulk_insert('fleet_type', fleet_type_rows)
    print(f"  - {len(fleet_type_rows)} fleet_types")

    # Deployment targets (5-7 per partition)
    DT_NAMES = {'eks': 'main', 'ecs': 'services', 'lambda': 'functions',
                'fargate': 'tasks', 'ec2': 'instances', 'batch': 'jobs', 'apprunner': 'apps'}
    dt_rows = []
    for partition_id in all_partitions:
        num_dts = random.randint(5, len(DEPLOYMENT_TARGET_TYPES))
        selected = random.sample(DEPLOYMENT_TARGET_TYPES, num_dts)
        for dt_type in selected:
            dt_name = DT_NAMES[dt_type]
            dt_id = f"{partition_id}:{dt_type}:{dt_name}"
            dt_rows.append({
                'id': dt_id,
                'partition_id': partition_id,
                'deployment_target_type_id': dt_type,
                'name': dt_name,
                'native_id': f"{dt_type}-{hashlib.md5(dt_id.encode()).hexdigest()[:8]}",
                'created_at': random_date(270, 300),
                'defaults': '{}',
            })
            all_deployment_targets.append(dt_id)
    bulk_insert('deployment_target', dt_rows)
    print(f"  - {len(dt_rows)} deployment_targets")

    # Fleets (5-7 per DT)
    fleet_rows = []
    dt_to_provider_type = {}
    dt_counter_by_ptype = defaultdict(int)
    for dt_id in all_deployment_targets:
        # Extract provider type from dt_id
        # dt_id format: env:provider:account:region:partition:dt_type:name
        parts = dt_id.split(':')
        provider_type = parts[1]
        dt_to_provider_type[dt_id] = provider_type

        fleet_types = FLEET_TYPES_BY_PROVIDER[provider_type]
        dt_idx = dt_counter_by_ptype[provider_type]
        dt_counter_by_ptype[provider_type] += 1
        num_fleets = random.randint(5, len(FLEET_NAMES))
        selected_fleet_names = random.sample(FLEET_NAMES, num_fleets)
        for i, fleet_name in enumerate(selected_fleet_names):
            fleet_type_name = fleet_types[(dt_idx * num_fleets + i) % len(fleet_types)]
            fleet_type_id = f"{provider_type}:{fleet_type_name}"
            fleet_id = f"{dt_id}:{fleet_type_id}:{fleet_name}"
            fleet_rows.append({
                'id': fleet_id,
                'deployment_target_id': dt_id,
                'fleet_type_id': fleet_type_id,
                'name': fleet_name,
                'native_id': f"fleet-{hashlib.md5(fleet_id.encode()).hexdigest()[:8]}",
                'created_at': random_date(260, 290),
                'defaults': '{}',
            })
            all_fleets.append(fleet_id)
    bulk_insert('fleet', fleet_rows)
    print(f"  - {len(fleet_rows)} fleets")

    # Capacities (5 per fleet, rotating through all 8 allocation types)
    capacity_rows = []
    capacity_values = {
        'cpu': lambda: random.uniform(4, 64),
        'memory': lambda: random.uniform(8, 256),
        'disk': lambda: random.uniform(50, 500),
        'gpu': lambda: random.randint(0, 8),
        'network_bandwidth': lambda: random.uniform(1, 25),
        'iops': lambda: random.uniform(1000, 50000),
        'connections': lambda: random.randint(100, 10000),
        'replicas': lambda: random.randint(2, 20),
    }
    for fleet_idx, fleet_id in enumerate(all_fleets):
        num_caps = random.randint(5, 7)
        for i in range(num_caps):
            alloc_type, _ = ALLOCATION_TYPES[(fleet_idx * num_caps + i) % len(ALLOCATION_TYPES)]
            capacity_id = f"{fleet_id}:{alloc_type}"
            value = capacity_values[alloc_type]()

            capacity_rows.append({
                'id': capacity_id,
                'fleet_id': fleet_id,
                'allocation_type_id': alloc_type,
                'value': value,
                'created_at': random_date(250, 280),
                'defaults': '{}',
            })
    bulk_insert('capacity', capacity_rows)
    print(f"  - {len(capacity_rows)} capacities")

    # =========================================================================
    # TIER 2: Application
    # =========================================================================
    print("\nTier 2: Application...")

    # Applications
    app_rows = [{'id': app, 'created_at': random_date(350, 365), 'defaults': '{}'}
                for app in APPLICATIONS]
    bulk_insert('application', app_rows)
    print(f"  - {len(app_rows)} applications")

    # Stacks
    stack_rows = []
    for app, stacks in STACKS.items():
        for stack_name in stacks:
            stack_id = f"{app}:{stack_name}"
            stack_rows.append({
                'id': stack_id,
                'application_id': app,
                'name': stack_name,
                'created_at': random_date(340, 360),
                'defaults': '{}',
            })
            all_stacks.append(stack_id)
    bulk_insert('stack', stack_rows)
    print(f"  - {len(stack_rows)} stacks")

    # Services
    service_rows = []
    for stack_id, services in SERVICES.items():
        for service_name in services:
            service_id = f"{stack_id}:{service_name}"
            service_rows.append({
                'id': service_id,
                'stack_id': stack_id,
                'name': service_name,
                'artifact_name': service_name,
                'created_at': random_date(330, 350),
                'defaults': '{}',
            })
            all_services.append(service_id)
    bulk_insert('service', service_rows)
    print(f"  - {len(service_rows)} services")

    # Procs (5-7 per service)
    proc_rows = []
    service_to_procs = {}
    for service_id in all_services:
        num_procs = random.randint(5, len(PROCS))
        selected = random.sample(PROCS, num_procs)
        service_to_procs[service_id] = selected
        for proc_name in selected:
            proc_id = f"{service_id}:{proc_name}"
            proc_rows.append({
                'id': proc_id,
                'service_id': service_id,
                'name': proc_name,
                'created_at': random_date(320, 340),
                'defaults': '{}',
            })
            all_procs.append(proc_id)
    bulk_insert('proc', proc_rows)
    print(f"  - {len(proc_rows)} procs")

    # =========================================================================
    # TIER 3: Repos & Config Templates
    # =========================================================================
    print("\nTier 3: Repos & Config Templates...")

    # Repos
    repo_rows = []
    stack_to_repos = defaultdict(list)

    # Per-stack repos (git, ecr, helm, s3, docker)
    for stack_id in all_stacks:
        app, stack_name = stack_id.split(':')
        for repo_type in ['git', 'ecr', 'helm', 's3', 'docker']:
            repo_name = f"{app}-{stack_name}"
            repo_id = f"{repo_type}:{repo_name}"
            repo_rows.append({
                'id': repo_id,
                'repo_type_id': repo_type,
                'name': repo_name,
                'url': f"https://{repo_type}.example.com/{repo_name}",
                'created_at': random_date(330, 350),
                'defaults': '{}',
            })
            all_repos.append(repo_id)
            stack_to_repos[stack_id].append(repo_id)

    # Shared repos (npm, pypi, maven)
    for repo_type in ['npm', 'pypi', 'maven']:
        for i, suffix in enumerate(['auth', 'utils', 'logging', 'metrics', 'config']):
            repo_name = f"shared-{suffix}"
            repo_id = f"{repo_type}:{repo_name}"
            repo_rows.append({
                'id': repo_id,
                'repo_type_id': repo_type,
                'name': repo_name,
                'url': f"https://{repo_type}.example.com/{repo_name}",
                'created_at': random_date(340, 360),
                'defaults': '{}',
            })
            all_repos.append(repo_id)

    bulk_insert('repo', repo_rows)
    print(f"  - {len(repo_rows)} repos")

    # Config templates
    ct_rows = []
    for lang, templates in CONFIG_TEMPLATES.items():
        for template_name in templates:
            ct_id = template_name
            ct_rows.append({
                'id': ct_id,
                'language_id': lang,
                'doc': f"# Template: {template_name}\nkey: value",
                'created_at': random_date(340, 360),
                'defaults': '{}',
            })
            all_config_templates.append(ct_id)
    bulk_insert('config_template', ct_rows)
    print(f"  - {len(ct_rows)} config_templates")

    # =========================================================================
    # TIER 4: Deployments
    # =========================================================================
    print("\nTier 4: Deployments...")

    deployment_rows = []
    for dt_id in all_deployment_targets:
        # Determine which services to deploy
        if dt_id in PRIMARY_DEPLOYMENT_TARGETS:
            services_to_deploy = all_services
        else:
            services_to_deploy = CORE_SERVICES

        for service_id in services_to_deploy:
            deployment_id = f"{dt_id}:{service_id}:default"
            deployment_rows.append({
                'id': deployment_id,
                'deployment_target_id': dt_id,
                'service_id': service_id,
                'tag': 'default',
                'created_at': random_date(310, 330),
                'defaults': '{}',
            })
            all_deployments.append(deployment_id)
    bulk_insert('deployment', deployment_rows)
    print(f"  - {len(deployment_rows)} deployments")

    # Deployment procs (matches service's procs)
    dp_rows = []
    for deployment_id in all_deployments:
        service_id = ':'.join(deployment_id.split(':')[7:10])
        procs_for_svc = service_to_procs.get(service_id, PROCS[:5])
        for proc_name in procs_for_svc:
            proc_id = f"{service_id}:{proc_name}"
            dp_id = f"{deployment_id}:{proc_id}"
            dp_rows.append({
                'id': dp_id,
                'deployment_id': deployment_id,
                'proc_id': proc_id,
                'created_at': random_date(300, 320),
                'defaults': '{}',
            })
            all_deployment_procs.append(dp_id)
    bulk_insert('deployment_proc', dp_rows)
    print(f"  - {len(dp_rows)} deployment_procs")

    # =========================================================================
    # TIER 5: Temporal (Builds & Releases)
    # =========================================================================
    print("\nTier 5: Builds & Releases...")

    # Builds
    build_rows = []
    service_to_builds = defaultdict(list)

    for service_id in all_services:
        # Determine build frequency
        if service_id in HIGH_FREQUENCY_SERVICES:
            num_builds = 40
        elif random.random() < 0.3:
            num_builds = 20
        else:
            num_builds = 10

        build_num_start = random.randint(50, 200)

        for i in range(num_builds):
            build_num = build_num_start + i
            vcs_ref = hashlib.md5(f"{service_id}:{build_num}".encode()).hexdigest()[:7]
            ver = re.sub(r"[^0-9a-zA-Z.-]", '-', vcs_ref)
            build_id = f"{service_id}:{build_num}"

            # Spread builds across the year
            days_ago = 350 - (i * 350 / num_builds)
            created_at = random_date(days_ago - 5, days_ago + 5)

            build_rows.append({
                'id': build_id,
                'service_id': service_id,
                'build_num': build_num,
                'vcs_ref': vcs_ref,
                'ver': ver,
                'created_at': created_at,
                'defaults': '{}',
            })
            all_builds.append(build_id)
            service_to_builds[service_id].append((build_id, created_at, build_num))

    bulk_insert('build', build_rows)
    print(f"  - {len(build_rows)} builds")

    # Releases
    release_rows = []
    deployment_to_releases = defaultdict(list)

    for deployment_id in all_deployments:
        # Extract environment and service from deployment_id
        parts = deployment_id.split(':')
        env = parts[0]
        service_id = ':'.join(parts[7:10])

        # Get builds for this service
        builds = service_to_builds.get(service_id, [])
        if not builds:
            continue

        # For primary DTs, do full promotion pipeline
        dt_id = ':'.join(parts[:7])
        if dt_id in PRIMARY_DEPLOYMENT_TARGETS:
            # Promote ~70% of builds to this environment
            for build_id, build_created_at, build_num in builds:
                if random.random() > 0.7:
                    continue

                # Calculate promotion delay based on environment
                if env == 'dev':
                    delay_days = random.uniform(0, 1)
                elif env == 'int':
                    delay_days = random.uniform(1, 3)
                elif env == 'stg':
                    delay_days = random.uniform(3, 7)
                elif env == 'prod':
                    delay_days = random.uniform(7, 14)
                elif env == 'infra':
                    delay_days = random.uniform(2, 5)
                else:
                    delay_days = random.uniform(0, 2)

                release_created_at = build_created_at + timedelta(days=delay_days)
                release_id = f"{deployment_id}:{build_num}"

                release_rows.append({
                    'id': release_id,
                    'build_id': build_id,
                    'deployment_id': deployment_id,
                    'build_num': build_num,
                    'created_at': release_created_at,
                    'defaults': '{}',
                })
                all_releases.append(release_id)
                deployment_to_releases[deployment_id].append((release_id, release_created_at))
        else:
            # For non-primary DTs, just use the 5 most recent builds
            recent_builds = sorted(builds, key=lambda x: x[1], reverse=True)[:5]
            for build_id, build_created_at, build_num in recent_builds:
                delay_days = random.uniform(0, 3)
                release_created_at = build_created_at + timedelta(days=delay_days)
                release_id = f"{deployment_id}:{build_num}"

                release_rows.append({
                    'id': release_id,
                    'build_id': build_id,
                    'deployment_id': deployment_id,
                    'build_num': build_num,
                    'created_at': release_created_at,
                    'defaults': '{}',
                })
                all_releases.append(release_id)
                deployment_to_releases[deployment_id].append((release_id, release_created_at))

    # Gap-fill: ensure every deployment has at least 5 releases
    gap_fill_rows = []
    for deployment_id in all_deployments:
        existing = deployment_to_releases.get(deployment_id, [])
        if len(existing) >= 5:
            continue
        parts = deployment_id.split(':')
        service_id = ':'.join(parts[7:10])
        builds = service_to_builds.get(service_id, [])
        if not builds:
            continue
        # Find builds not yet used for this deployment
        used_build_nums = {r_id.split(':')[-1] for r_id, _ in existing}
        available = [(bid, bca, bnum) for bid, bca, bnum in builds if str(bnum) not in used_build_nums]
        needed = 5 - len(existing)
        # Pick from available builds (or reuse if not enough)
        fill_builds = available[:needed] if len(available) >= needed else available + builds[:needed - len(available)]
        for build_id, build_created_at, build_num in fill_builds[:needed]:
            delay_days = random.uniform(0, 3)
            release_created_at = build_created_at + timedelta(days=delay_days)
            release_id = f"{deployment_id}:{build_num}"
            # Avoid duplicate release IDs
            if any(r_id == release_id for r_id, _ in existing):
                continue
            gap_fill_rows.append({
                'id': release_id,
                'build_id': build_id,
                'deployment_id': deployment_id,
                'build_num': build_num,
                'created_at': release_created_at,
                'defaults': '{}',
            })
            all_releases.append(release_id)
            deployment_to_releases[deployment_id].append((release_id, release_created_at))
            existing.append((release_id, release_created_at))

    all_release_rows = release_rows + gap_fill_rows
    bulk_insert('release', all_release_rows)
    print(f"  - {len(all_release_rows)} releases ({len(gap_fill_rows)} gap-filled)")

    # Export deployment schedule JSON for monitoring data generator
    print("\n  Exporting deployment schedule...")
    _export_deployment_schedule(deployment_to_releases, all_deployments)

    # =========================================================================
    # TIER 6: Artifacts
    # =========================================================================
    print("\nTier 6: Artifacts...")

    # Build artifacts
    ba_rows = []
    for build_id in all_builds:
        service_id = ':'.join(build_id.split(':')[:-1])
        stack_id = ':'.join(service_id.split(':')[:-1])

        # Get stack repos
        repos = stack_to_repos.get(stack_id, [])
        git_repo = next((r for r in repos if r.startswith('git:')), None)
        ecr_repo = next((r for r in repos if r.startswith('ecr:')), None)
        helm_repo = next((r for r in repos if r.startswith('helm:')), None)
        s3_repo = next((r for r in repos if r.startswith('s3:')), None)

        num_ba = random.randint(5, len(BUILD_ARTIFACT_NAMES))
        selected_ba = random.sample(BUILD_ARTIFACT_NAMES, num_ba)
        for artifact_name in selected_ba:
            ba_id = f"{build_id}:{artifact_name}"

            # Select repos based on artifact type
            if artifact_name == 'docker-image':
                input_repo = git_repo
                output_repo = ecr_repo
            elif artifact_name == 'helm-chart':
                input_repo = git_repo
                output_repo = helm_repo
            else:
                input_repo = git_repo
                output_repo = s3_repo

            ba_rows.append({
                'id': ba_id,
                'build_id': build_id,
                'input_repo_id': input_repo,
                'output_repo_id': output_repo,
                'name': artifact_name,
                'upload_path': f"/builds/{build_id}/{artifact_name}",
                'data': json.dumps({'size': random.randint(1000, 1000000)}),
                'created_at': random_date(300, 330),
                'defaults': '{}',
            })
    bulk_insert('build_artifact', ba_rows)
    print(f"  - {len(ba_rows)} build_artifacts")

    # Release artifacts
    ra_rows = []
    for release_id in all_releases:
        deployment_id = ':'.join(release_id.split(':')[:-1])
        service_id = ':'.join(deployment_id.split(':')[7:10])
        stack_id = ':'.join(service_id.split(':')[:-1])

        repos = stack_to_repos.get(stack_id, [])
        ecr_repo = next((r for r in repos if r.startswith('ecr:')), None)
        helm_repo = next((r for r in repos if r.startswith('helm:')), None)
        s3_repo = next((r for r in repos if r.startswith('s3:')), None)

        num_ra = random.randint(5, len(RELEASE_ARTIFACT_NAMES))
        selected_ra = random.sample(RELEASE_ARTIFACT_NAMES, num_ra)
        for artifact_name in selected_ra:
            ra_id = f"{release_id}:{artifact_name}"

            if artifact_name == 'manifest':
                input_repo = ecr_repo
            elif artifact_name == 'values':
                input_repo = helm_repo
            else:
                input_repo = helm_repo

            ra_rows.append({
                'id': ra_id,
                'release_id': release_id,
                'input_repo_id': input_repo,
                'output_repo_id': s3_repo,
                'name': artifact_name,
                'upload_path': f"/releases/{release_id}/{artifact_name}",
                'data': json.dumps({'checksum': hashlib.md5(ra_id.encode()).hexdigest()}),
                'created_at': random_date(290, 320),
                'defaults': '{}',
            })
    bulk_insert('release_artifact', ra_rows)
    print(f"  - {len(ra_rows)} release_artifacts")

    # =========================================================================
    # TIER 7: Configs
    # =========================================================================
    print("\nTier 7: Configs...")

    # Deployment configs (5-7 per deployment, rotating through all templates)
    dc_rows = []
    for dep_idx, deployment_id in enumerate(all_deployments):
        num_dc = random.randint(5, 7)
        for i in range(num_dc):
            ct_name = all_config_templates[(dep_idx * num_dc + i) % len(all_config_templates)]
            dc_id = f"{deployment_id}:{ct_name}:{ct_name}:default"
            dc_rows.append({
                'id': dc_id,
                'deployment_id': deployment_id,
                'config_template_id': ct_name,
                'name': ct_name,
                'tag': 'default',
                'config': '{}',
                'created_at': random_date(280, 310),
                'defaults': '{}',
            })
    bulk_insert('deployment_config', dc_rows)
    print(f"  - {len(dc_rows)} deployment_configs")

    # Service configs (5-7 per service, rotating through all templates)
    sc_rows = []
    for svc_idx, service_id in enumerate(all_services):
        num_sc = random.randint(5, 7)
        for i in range(num_sc):
            ct_name = all_config_templates[(svc_idx * num_sc + i) % len(all_config_templates)]
            sc_id = f"{service_id}:{ct_name}:{ct_name}:default"
            sc_rows.append({
                'id': sc_id,
                'service_id': service_id,
                'config_template_id': ct_name,
                'name': ct_name,
                'tag': 'default',
                'config': '{}',
                'created_at': random_date(290, 320),
                'defaults': '{}',
            })
    bulk_insert('service_config', sc_rows)
    print(f"  - {len(sc_rows)} service_configs")

    # Stack configs (13 per stack to ensure all ~50 templates get 5+ usages)
    stc_rows = []
    for stack_idx, stack_id in enumerate(all_stacks):
        for i in range(13):
            ct_name = all_config_templates[(stack_idx * 13 + i) % len(all_config_templates)]
            stc_id = f"{stack_id}:{ct_name}:{ct_name}:default"
            stc_rows.append({
                'id': stc_id,
                'stack_id': stack_id,
                'config_template_id': ct_name,
                'name': ct_name,
                'tag': 'default',
                'config': '{}',
                'created_at': random_date(300, 330),
                'defaults': '{}',
            })
    bulk_insert('stack_config', stc_rows)
    print(f"  - {len(stc_rows)} stack_configs")

    # =========================================================================
    # TIER 8: Allocations
    # =========================================================================
    print("\nTier 8: Allocations...")

    alloc_rows = []
    alloc_type_usage = defaultdict(int)

    for i, dp_id in enumerate(all_deployment_procs):
        # Base allocations (5 types: cpu, memory, disk, network_bandwidth, replicas)
        base_alloc_types = ['cpu', 'memory', 'disk', 'network_bandwidth', 'replicas']
        for alloc_type in base_alloc_types:
            for watermark in ['HIGH', 'LOW']:
                alloc_id = f"{dp_id}:{alloc_type}:{watermark}"

                # Generate values
                if alloc_type == 'cpu':
                    high_val = random.uniform(2, 16)
                    value = high_val if watermark == 'HIGH' else high_val * 0.5
                elif alloc_type == 'memory':
                    high_val = random.uniform(4, 64)
                    value = high_val if watermark == 'HIGH' else high_val * 0.5
                elif alloc_type == 'disk':
                    high_val = random.uniform(20, 200)
                    value = high_val if watermark == 'HIGH' else high_val * 0.6
                elif alloc_type == 'network_bandwidth':
                    high_val = random.uniform(1, 10)
                    value = high_val if watermark == 'HIGH' else high_val * 0.7
                elif alloc_type == 'replicas':
                    high_val = random.randint(3, 20)
                    value = high_val if watermark == 'HIGH' else max(1, high_val // 2)
                else:
                    value = random.uniform(10, 100)

                alloc_rows.append({
                    'id': alloc_id,
                    'deployment_proc_id': dp_id,
                    'allocation_type_id': alloc_type,
                    'watermark': watermark,
                    'value': value,
                    'created_at': random_date(270, 300),
                    'defaults': '{}',
                })
                alloc_type_usage[alloc_type] += 1

        # Extra allocations for remaining types (gpu, iops, connections)
        # Add to every 3rd deployment_proc to ensure coverage
        if i % 3 == 0:
            extra_types = ['gpu', 'iops', 'connections']
            for alloc_type in extra_types:
                for watermark in ['HIGH', 'LOW']:
                    alloc_id = f"{dp_id}:{alloc_type}:{watermark}"

                    if alloc_type == 'gpu':
                        high_val = random.randint(1, 8)
                        value = high_val if watermark == 'HIGH' else max(1, high_val // 2)
                    elif alloc_type == 'iops':
                        high_val = random.uniform(1000, 10000)
                        value = high_val if watermark == 'HIGH' else high_val * 0.6
                    elif alloc_type == 'connections':
                        high_val = random.randint(100, 1000)
                        value = high_val if watermark == 'HIGH' else high_val // 2
                    else:
                        value = random.uniform(10, 100)

                    alloc_rows.append({
                        'id': alloc_id,
                        'deployment_proc_id': dp_id,
                        'allocation_type_id': alloc_type,
                        'watermark': watermark,
                        'value': value,
                        'created_at': random_date(270, 300),
                        'defaults': '{}',
                    })
                    alloc_type_usage[alloc_type] += 1

    bulk_insert('allocation', alloc_rows)
    print(f"  - {len(alloc_rows)} allocations")
    print(f"    Allocation type coverage: {dict(alloc_type_usage)}")

    # =========================================================================
    # ASSOCIATIONS (M2M)
    # =========================================================================
    print("\nAssociations (M2M)...")

    # services_repos (5+ repos per service via stack repos, plus shared repos)
    sr_rows = []
    # Collect shared repos (npm, pypi, maven)
    shared_repos = [r for r in all_repos if any(r.startswith(f"{rt}:shared-") for rt in ['npm', 'pypi', 'maven'])]
    for service_id in all_services:
        stack_id = ':'.join(service_id.split(':')[:-1])
        repos = stack_to_repos.get(stack_id, [])
        for repo_id in repos:
            sr_rows.append({
                'service_id': service_id,
                'repo_id': repo_id,
            })
    # Link shared repos to services (round-robin to ensure each shared repo has 5+ services)
    for i, repo_id in enumerate(shared_repos):
        # Link to 5+ services
        for j in range(min(5, len(all_services))):
            svc = all_services[(i * 5 + j) % len(all_services)]
            sr_rows.append({
                'service_id': svc,
                'repo_id': repo_id,
            })
    bulk_insert('services_repos', sr_rows)
    print(f"  - {len(sr_rows)} services_repos links")

    # deployments_zones (5+ zones per deployment)
    dz_rows = []
    # Pre-build region -> zones lookup
    region_to_zones = defaultdict(list)
    for zone_id in all_zones:
        zparts = zone_id.split(':')
        zregion = ':'.join(zparts[:4])
        region_to_zones[zregion].append(zone_id)

    for deployment_id in all_deployments:
        parts = deployment_id.split(':')
        region_id = ':'.join(parts[:4])
        for zone_id in region_to_zones.get(region_id, []):
            dz_rows.append({
                'deployment_id': deployment_id,
                'zone_id': zone_id,
            })
    bulk_insert('deployments_zones', dz_rows)
    print(f"  - {len(dz_rows)} deployments_zones links")

    # subnets_fleets (5+ fleets per subnet, 5+ subnets per fleet)
    sf_rows = []
    fleet_to_partition = {}
    for fleet_id in all_fleets:
        # Extract partition from fleet_id
        parts = fleet_id.split(':')
        partition_id = ':'.join(parts[:5])
        fleet_to_partition[fleet_id] = partition_id

    partition_to_subnets = defaultdict(list)
    for subnet_id in all_subnets:
        # Extract partition from subnet (via network)
        # subnet_id: region:partition:network:subnet
        parts = subnet_id.split(':')
        partition_id = ':'.join(parts[:5])
        partition_to_subnets[partition_id].append(subnet_id)

    for fleet_id in all_fleets:
        partition_id = fleet_to_partition[fleet_id]
        subnets = partition_to_subnets.get(partition_id, [])[:5]

        for subnet_id in subnets:
            sf_rows.append({
                'subnet_id': subnet_id,
                'fleet_id': fleet_id,
            })
    bulk_insert('subnets_fleets', sf_rows)
    print(f"  - {len(sf_rows)} subnets_fleets links")

    # target_fleets (each DT links to its 5 fleets + neighbors)
    tf_rows = []
    dt_to_fleets = defaultdict(list)
    for fleet_id in all_fleets:
        dt_id = ':'.join(fleet_id.split(':')[:7])
        dt_to_fleets[dt_id].append(fleet_id)

    dt_list = list(all_deployment_targets)
    dt_index = {dt_id: idx for idx, dt_id in enumerate(dt_list)}
    for dt_id in dt_list:
        own_fleets = dt_to_fleets.get(dt_id, [])

        # Add own fleets
        for fleet_id in own_fleets:
            tf_rows.append({
                'deployment_target_id': dt_id,
                'fleet_id': fleet_id,
            })

        # Add 4 fleets from neighboring DTs (to ensure each fleet has 5+ DTs)
        idx = dt_index[dt_id]
        neighbor_dts = [dt_list[(idx + i) % len(dt_list)] for i in range(1, 5)]

        for neighbor_dt in neighbor_dts:
            neighbor_fleets = dt_to_fleets.get(neighbor_dt, [])
            if neighbor_fleets:
                fleet_id = neighbor_fleets[0]
                tf_rows.append({
                    'deployment_target_id': dt_id,
                    'fleet_id': fleet_id,
                })
    bulk_insert('target_fleets', tf_rows)
    print(f"  - {len(tf_rows)} target_fleets links")

    # deployment_current_release (latest release per deployment)
    dcr_rows = []
    for deployment_id in all_deployments:
        releases = deployment_to_releases.get(deployment_id, [])
        if releases:
            # Get most recent release
            latest_release = max(releases, key=lambda x: x[1])
            dcr_rows.append({
                'deployment_id': deployment_id,
                'release_id': latest_release[0],
            })
    bulk_insert('deployment_current_release', dcr_rows)
    print(f"  - {len(dcr_rows)} deployment_current_release links")

    # =========================================================================
    # EXPORT TSV FIXTURES
    # =========================================================================
    if txt_output_dir:
        print(f"\nExporting TSV fixtures to {txt_output_dir}...")
        _export_txt_fixtures(txt_output_dir, {
            'env_rows': env_rows,
            'pt_rows': pt_rows,
            'dtt_rows': dtt_rows,
            'at_rows': at_rows,
            'rt_rows': rt_rows,
            'lang_rows': lang_rows,
            'provider_rows': provider_rows,
            'region_rows': region_rows,
            'zone_rows': zone_rows,
            'partition_rows': partition_rows,
            'network_rows': network_rows,
            'subnet_rows': subnet_rows,
            'fleet_type_rows': fleet_type_rows,
            'dt_rows': dt_rows,
            'fleet_rows': fleet_rows,
            'capacity_rows': capacity_rows,
            'repo_rows': repo_rows,
            'app_rows': app_rows,
            'stack_rows': stack_rows,
            'service_rows': service_rows,
            'proc_rows': proc_rows,
            'ct_rows': ct_rows,
            'build_rows': build_rows,
            'deployment_rows': deployment_rows,
            'dp_rows': dp_rows,
            'release_rows': all_release_rows,
            'alloc_rows': alloc_rows,
            'ba_rows': ba_rows,
            'ra_rows': ra_rows,
            'dc_rows': dc_rows,
            'sc_rows': sc_rows,
            'stc_rows': stc_rows,
            'sr_rows': sr_rows,
            'dz_rows': dz_rows,
            'sf_rows': sf_rows,
            'tf_rows': tf_rows,
        })

    print("\n=== Generation Summary ===")
    print(f"Total providers: {len(all_providers)}")
    print(f"Total regions: {len(all_regions)}")
    print(f"Total zones: {len(all_zones)}")
    print(f"Total partitions: {len(all_partitions)}")
    print(f"Total networks: {len(all_networks)}")
    print(f"Total subnets: {len(all_subnets)}")
    print(f"Total deployment_targets: {len(all_deployment_targets)}")
    print(f"Total fleets: {len(all_fleets)}")
    print(f"Total stacks: {len(all_stacks)}")
    print(f"Total services: {len(all_services)}")
    print(f"Total procs: {len(all_procs)}")
    print(f"Total repos: {len(all_repos)}")
    print(f"Total config_templates: {len(all_config_templates)}")
    print(f"Total deployments: {len(all_deployments)}")
    print(f"Total deployment_procs: {len(all_deployment_procs)}")
    print(f"Total builds: {len(all_builds)}")
    print(f"Total releases: {len(all_releases)}")


def _write_tsv_file(output_dir, filename, display_name, columns, rows):
    """Write a single TSV fixture file."""
    filepath = os.path.join(output_dir, filename)
    with open(filepath, 'w') as f:
        f.write(f"# {display_name}\n")
        f.write(f"# Format: {chr(9).join(columns)}\n")
        f.write(f"# Generated by generate_fixtures.py\n\n")
        for row in rows:
            values = []
            for col in columns:
                val = row.get(col, '')
                if val is None:
                    val = ''
                elif isinstance(val, float):
                    val = f"{val:.6g}"
                else:
                    val = str(val)
                val = val.replace('\n', '\\n').replace('\r', '')
                values.append(val)
            f.write('\t'.join(values) + '\n')
    return len(rows)


def _export_txt_fixtures(output_dir, data):
    """Export all generated data to TSV fixture files.

    Writes files matching the format expected by convert_to_json.py MAPPINGS.
    Column order matches MAPPINGS exactly so the converter can parse them.
    """
    os.makedirs(output_dir, exist_ok=True)

    specs = [
        ("01_environments.txt", "Environments", ["id"], data['env_rows']),
        ("02_provider_types.txt", "Provider Types", ["id"], data['pt_rows']),
        ("03_deployment_target_types.txt", "Deployment Target Types", ["id"], data['dtt_rows']),
        ("04_allocation_types.txt", "Allocation Types", ["id", "unit"], data['at_rows']),
        ("05_repo_types.txt", "Repo Types", ["id"], data['rt_rows']),
        ("06_languages.txt", "Languages", ["id"], data['lang_rows']),
        ("07_providers.txt", "Providers", ["environment_id", "provider_type_id", "native_id"], data['provider_rows']),
        ("08_regions.txt", "Regions", ["provider_id", "name"], data['region_rows']),
        ("09_zones.txt", "Zones", ["region_id", "name", "native_id"], data['zone_rows']),
        ("10_partitions.txt", "Partitions", ["region_id", "name", "native_id"], data['partition_rows']),
        ("11_networks.txt", "Networks", ["partition_id", "name", "cidr"], data['network_rows']),
        ("12_subnets.txt", "Subnets", ["network_id", "name", "cidr", "native_id"], data['subnet_rows']),
        ("13_fleet_types.txt", "Fleet Types", ["provider_type_id", "name"], data['fleet_type_rows']),
        ("14_deployment_targets.txt", "Deployment Targets", ["partition_id", "deployment_target_type_id", "name"], data['dt_rows']),
        ("15_fleets.txt", "Fleets", ["deployment_target_id", "fleet_type_id", "name"], data['fleet_rows']),
        ("16_capacities.txt", "Capacities", ["allocation_type_id", "fleet_id", "value"], data['capacity_rows']),
        ("17_repos.txt", "Repos", ["repo_type_id", "name", "url"], data['repo_rows']),
        ("18_applications.txt", "Applications", ["id", "defaults"], data['app_rows']),
        ("19_stacks.txt", "Stacks", ["application_id", "name", "defaults"], data['stack_rows']),
        ("20_services.txt", "Services", ["stack_id", "name", "artifact_name", "defaults"], data['service_rows']),
        ("21_procs.txt", "Procs", ["service_id", "name", "defaults"], data['proc_rows']),
        ("22_config_templates.txt", "Config Templates", ["id", "language_id", "doc"], data['ct_rows']),
        ("23_builds.txt", "Builds", ["service_id", "build_num", "vcs_ref", "defaults"], data['build_rows']),
        ("24_deployments.txt", "Deployments", ["deployment_target_id", "service_id", "tag", "defaults"], data['deployment_rows']),
        ("25_deployment_procs.txt", "Deployment Procs", ["deployment_id", "proc_id", "defaults"], data['dp_rows']),
        ("26_releases.txt", "Releases", ["deployment_id", "build_id", "build_num", "defaults"], data['release_rows']),
        ("27_allocations.txt", "Allocations", ["deployment_proc_id", "allocation_type_id", "watermark", "value", "defaults"], data['alloc_rows']),
        ("28_build_artifacts.txt", "Build Artifacts", ["build_id", "input_repo_id", "output_repo_id", "name", "upload_path", "data"], data['ba_rows']),
        ("29_release_artifacts.txt", "Release Artifacts", ["release_id", "input_repo_id", "output_repo_id", "name", "upload_path", "data"], data['ra_rows']),
        ("30_deployment_configs.txt", "Deployment Configs", ["deployment_id", "config_template_id", "name", "tag", "config", "defaults"], data['dc_rows']),
        ("31_service_configs.txt", "Service Configs", ["service_id", "config_template_id", "name", "tag", "config", "defaults"], data['sc_rows']),
        ("32_stack_configs.txt", "Stack Configs", ["stack_id", "config_template_id", "name", "tag", "config", "defaults"], data['stc_rows']),
        ("33_services_repos.txt", "Services Repos", ["service_id", "repo_id"], data['sr_rows']),
        ("34_deployments_zones.txt", "Deployments Zones", ["deployment_id", "zone_id"], data['dz_rows']),
        ("35_subnets_fleets.txt", "Subnets Fleets", ["subnet_id", "fleet_id"], data['sf_rows']),
        ("36_target_fleets.txt", "Target Fleets", ["deployment_target_id", "fleet_id"], data['tf_rows']),
    ]

    total_rows = 0
    for filename, display_name, columns, rows in specs:
        count = _write_tsv_file(output_dir, filename, display_name, columns, rows)
        total_rows += count
        print(f"  {filename}: {count} rows")

    print(f"\n  Total: {total_rows} rows across {len(specs)} files")
    print(f"  Output: {output_dir}")


def _export_deployment_schedule(deployment_to_releases, all_deployments):
    """Export deployment schedule as JSON for use by the monitoring data generator.

    Groups deployments by stack and environment to enable multi-region stagger
    coordination during monitoring data generation.
    """
    schedule = {
        "generated_at": NOW.isoformat(),
        "deployments": {},
        "primary_deployment_targets": PRIMARY_DEPLOYMENT_TARGETS,
        "stack_region_groups": {},
    }

    # Build deployments section
    for deployment_id in all_deployments:
        releases = deployment_to_releases.get(deployment_id, [])
        if not releases:
            continue
        schedule["deployments"][deployment_id] = {
            "releases": sorted([
                {
                    "release_id": release_id,
                    "build_num": int(release_id.rsplit(':', 1)[1]),
                    "created_at": created_at.isoformat(),
                }
                for release_id, created_at in releases
            ], key=lambda r: r["created_at"]),
        }

    # Build stack_region_groups: group deployment targets by stack_id and env
    # deployment_id format: env:provider:account:region:partition:target_type:target:app:stack:service:tag
    stack_region_map = defaultdict(lambda: defaultdict(set))
    for deployment_id in all_deployments:
        parts = deployment_id.split(':')
        if len(parts) < 11:
            continue
        env = parts[0]
        target_id = ':'.join(parts[:7])
        stack_id = f"{parts[7]}:{parts[8]}"
        # Only include primary deployment targets
        if target_id in PRIMARY_DEPLOYMENT_TARGETS:
            stack_region_map[stack_id][env].add(target_id)

    schedule["stack_region_groups"] = {
        stack_id: {
            env: sorted(list(targets))
            for env, targets in envs.items()
            if len(targets) > 0
        }
        for stack_id, envs in sorted(stack_region_map.items())
    }

    output_path = os.path.join(os.path.dirname(__file__), 'deployment_schedule.json')
    with open(output_path, 'w') as f:
        json.dump(schedule, f, indent=2)
    print(f"    Wrote deployment schedule to {output_path}")
    print(f"    {len(schedule['deployments'])} deployments, {len(schedule['stack_region_groups'])} stack groups")


def clear_all():
    """Clear all data from the database using TRUNCATE CASCADE for speed."""
    table_names = [t.name for t in reversed(db.metadata.sorted_tables)]
    if table_names:
        db.session.execute(text(f"TRUNCATE {', '.join(table_names)} CASCADE"))
    db.session.commit()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Generate Qairon fixture data')
    parser.add_argument('--txt-output', metavar='DIR',
                        help='Export TSV fixture files to this directory')
    args = parser.parse_args()

    with app.app_context():
        print("=" * 60)
        print("Qairon Fixture Generator")
        print("=" * 60)
        print("\nClearing existing data...")
        clear_all()
        print("Generating fixtures...")
        generate(txt_output_dir=args.txt_output)
        db.session.commit()
        print("\n" + "=" * 60)
        print("Done!")
        print("=" * 60)


if __name__ == '__main__':
    main()
