#!/usr/bin/env python
from models import *
from app import db

deployment_target_classes = {
    Fleet: "deployment_target_id",
    Deployment: "deployment_target_id",
    Deployment: "current_release_id",
    DeploymentProc: "deployment_id",
    Allocation: "deployment_proc_id",
    Release: "deployment_id",
    DeploymentConfig: "deployment_id"
}

provider_classes = {
    Provider: "environment_id",
    Region: "provider_id",
    Partition: "region_id",
    DeploymentTarget: "partition_id",
    Network: "partition_id",
    Zone: "region_id",
    Deployment: "deployment_target_id",
    DeploymentProc: "deployment_id",
    Allocation: "deployment_proc_id",
    Release: "deployment_id",
    Build: "service_id",
    DeploymentConfig: "deployment_id",
    BuildArtifact: "build_id",
    BuildArtifact: "input_repo_id",
    BuildArtifact: "output_repo_id",
    ReleaseArtifact: "release_id",
    ReleaseArtifact: "input_repo_id",
    ReleaseArtifact: "output_repo_id"
}

sess = db.session()

for k, v in deployment_target_classes.items():
    instances = sess.query(k).all()
    for instance in instances:
        setattr(instance, v, getattr(instance, v))

    sess.flush()
    sess.commit()

for k, v in provider_classes.items():
    instances = sess.query(k).all()
    for instance in instances:
        setattr(instance, v, getattr(instance, v))

    sess.flush()
    sess.commit()