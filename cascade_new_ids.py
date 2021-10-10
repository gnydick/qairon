#!/usr/bin/env python
from models import *
from app import db

deployment_target_classes = {
    Fleet: "name",
    Deployment: "service_id",
    DeploymentProc: "proc_id",
    Allocation: "value",
    Release: "tag",
    DeploymentConfig: "name"
}

provider_classes = {
    Region: "name",
    Partition: "name",
    DeploymentTarget: "name",
    Network: "cidr",
    Zone: "name"
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