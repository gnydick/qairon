"""
Qairon composite ID validation and extraction.

All IDs are colon-delimited composites that build hierarchically:

    {env}:{provider}:{account}:{region}:{partition}:{target_type}:{target}:{app}:{stack}:{service}:{tag}:{release_num}

ID field counts:
    provider_id:    3  (env:provider:account)
    region_id:      4  (env:provider:account:region)
    partition_id:   5  (env:provider:account:region:partition)
    target_id:      7  (env:provider:account:region:partition:target_type:target)
    stack_id:       2  (app:stack)
    service_id:     3  (app:stack:service)
    deployment_id: 11  (target_id + service_id + tag)
    release_id:    12  (deployment_id + release_num)
"""

# Expected field counts for each ID type
ID_FIELD_COUNTS = {
    "provider_id": 3,
    "region_id": 4,
    "partition_id": 5,
    "target_id": 7,
    "stack_id": 2,
    "service_id": 3,
    "deployment_id": 11,
    "release_id": 12,
}

# Field names for each position in a release_id
RELEASE_ID_FIELDS = [
    "environment", "provider", "account", "region", "partition",
    "target_type", "target", "application", "stack", "service",
    "tag", "release",
]


def validate_id(value: str, id_type: str) -> str:
    """Validate a composite ID has the correct number of colon-delimited fields.

    Args:
        value: The composite ID string.
        id_type: One of the keys in ID_FIELD_COUNTS.

    Returns:
        The validated ID string (unchanged).

    Raises:
        ValueError: If the field count doesn't match.
    """
    expected = ID_FIELD_COUNTS[id_type]
    parts = value.split(":")
    if len(parts) != expected:
        raise ValueError(
            f"Invalid {id_type}: expected {expected} fields, got {len(parts)}: {value!r}"
        )
    return value


def split_release_id(release_id: str) -> dict:
    """Split a release_id into all its component tags and composite IDs.

    Args:
        release_id: A 12-field colon-delimited release ID.

    Returns:
        Dict with single-word tags and composite IDs.

    Raises:
        ValueError: If release_id doesn't have exactly 12 fields.
    """
    validate_id(release_id, "release_id")
    parts = release_id.split(":")
    env, provider, account, region, partition, target_type, target, \
        application, stack, service, tag, release = parts

    return {
        # Single-word tags
        "environment": env,
        "provider": provider,
        "account": account,
        "region": region,
        "partition": partition,
        "target_type": target_type,
        "target": target,
        "application": application,
        "stack": stack,
        "service": service,
        "tag": tag,
        "release": release,
        # Composite IDs
        "provider_id": f"{env}:{provider}:{account}",
        "region_id": f"{env}:{provider}:{account}:{region}",
        "partition_id": f"{env}:{provider}:{account}:{region}:{partition}",
        "target_id": f"{env}:{provider}:{account}:{region}:{partition}:{target_type}:{target}",
        "stack_id": f"{application}:{stack}",
        "service_id": f"{application}:{stack}:{service}",
        "deployment_id": ":".join(parts[:11]),
        "release_id": release_id,
    }


def deployment_id_from_release_id(release_id: str) -> str:
    """Extract deployment_id (first 11 fields) from a release_id."""
    validate_id(release_id, "release_id")
    return ":".join(release_id.split(":")[:11])


def target_id_from_release_id(release_id: str) -> str:
    """Extract target_id (first 7 fields) from a release_id."""
    validate_id(release_id, "release_id")
    return ":".join(release_id.split(":")[:7])


def derive_dep_deployment_id(parent_release_id: str, dep_stack: str, dep_service: str) -> str:
    """Derive a dependency's deployment_id from the parent's release_id.

    The dependency inherits the parent's infrastructure context
    (env:provider:account:region:partition:target_type:target).
    Only the service path changes.
    """
    parts = parent_release_id.split(":")
    target_id = ":".join(parts[:7])
    application = parts[7]
    return f"{target_id}:{application}:{dep_stack}:{dep_service}:default"


def derive_dep_release_id(parent_release_id: str, dep_stack: str, dep_service: str,
                           release_num: int) -> str:
    """Derive a dependency's release_id from the parent's release_id.

    The dependency inherits the parent's infrastructure context.
    Only the service path and release number change.
    """
    dep_deployment_id = derive_dep_deployment_id(parent_release_id, dep_stack, dep_service)
    return f"{dep_deployment_id}:{release_num}"
