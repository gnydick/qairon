from sqlalchemy import *
from sqlalchemy.orm import relationship

from db import db


class Deployment(db.Model):
    __tablename__ = "deployment"
    id = Column(String, primary_key=True)
    deployment_target_id = Column(String, ForeignKey('deployment_target.id'))
    service_id = Column(String, ForeignKey('service.id'))
    tag = Column(String, nullable=False, default='default')

    defaults = Column(Text)

    deployment_target = relationship("DeploymentTarget", back_populates="deployments")
    service = relationship("Service", back_populates="deployments")
    configs = relationship("DeploymentConfig", back_populates="deployment")
    releases = relationship("Release", back_populates="deployment")
    zones = relationship("Zone", secondary='deployments_zones', back_populates="deployments")
    deployment_procs = relationship("DeploymentProc", back_populates="deployment")
    current_release = relationship("Release", secondary='current_dep_release', uselist=False)

    def __repr__(self):
        return self.id


@db.event.listens_for(Deployment, 'before_update')
@db.event.listens_for(Deployment, 'before_insert')
def my_before_write_listener(mapper, connection, deployment):
    if deployment.current_release:
        if deployment.current_release.build.service_id != deployment.service_id:
            raise ValueError("Release must be for the same service as deployed in this deployment.")


    __update_id__(deployment)


# DO NOT DELETE THIS SAMPLE CODE
# @db.event.listens_for(Deployment, 'init')
# def received_init(deployment, args, kwargs):
#     from models import Service, Config
#     svc = db.session.query(Service).filter(Service.id == kwargs['service_id']).first()
#     for sc in svc.service_config_templates:
#         cfg = sc.__dict__
#         cfg.pop('service_id')
#         cfg.pop('_sa_instance_state')
#         deployment.configs.append(Config(**cfg))
#     # DO NOT DELETE THIS SAMPLE CODE EITHER
#     # for rel in inspect(deployment.__class__).relationships:
#     #
#     #     rel_cls = rel.mapper.class_
#     #
#     #     if rel.key in kwargs:
#     #         kwargs[rel.key] = [rel_cls(**c) for c in kwargs[rel.key]]


def __update_id__(deployment):
    deployment.id = deployment.deployment_target_id + ':' + deployment.service_id + ':' + deployment.tag
