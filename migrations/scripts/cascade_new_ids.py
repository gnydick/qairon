#!/usr/bin/env python
from base import app
from models import *
from app import db

repo_classes = {
    Repo: "repo_type_id"
}

service_classes = {
    Stack: "application_id",
    Service: "stack_id",
    ServiceConfig:"config_template_id"
}

provider_classes = {
    Provider: "environment_id",
    Region: "provider_id",
    Partition: "region_id",
    DeploymentTarget: "partition_id",
    Network: "partition_id",
    Zone: "region_id",
    DeploymentProc: "deployment_id",
    Allocation: "deployment_proc_id",
    Release: "deployment_id",
    Build: "service_id",
    BuildArtifact: "build_id",
    BuildArtifact: "input_repo_id",
    BuildArtifact: "output_repo_id",
    ReleaseArtifact: "release_id",
    ReleaseArtifact: "input_repo_id",
    ReleaseArtifact: "output_repo_id"
}

deployment_classes = {
    Deployment: "deployment_target_id",
    Fleet: "deployment_target_id",
    Fleet: "fleet_type_id",
    Capacity: "fleet_id",
    DeploymentProc: "deployment_id",
    Allocation: "deployment_proc_id",
    Allocation: "allocation_type_id",
    Release: "deployment_id",
    ReleaseArtifact: "release_id",
    DeploymentConfig: "config_template_id",
    DeploymentConfig: "deployment_id",
    Deployment: "current_release_id"
}

klasses = [repo_classes, service_classes, provider_classes, deployment_classes, ]
with app.app_context():
    sess = db.session()

    for klass in klasses:
        for k, v in klass.items():
            instances = sess.query(k).all()
            for instance in instances:
                setattr(instance, v, getattr(instance, v))

            sess.flush()
            sess.commit()
