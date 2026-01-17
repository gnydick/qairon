from sqlalchemy import *
from sqlalchemy.orm import relationship, validates

from db import db
from models.associations import deployment_current_release


class Deployment(db.Model):
    exclude = ['configs', 'zones', 'deployment_procs', 'releases']

    __tablename__ = "deployment"
    id = Column(String, primary_key=True)
    deployment_target_id = Column(String, ForeignKey('deployment_target.id'), nullable=False, index=True)
    service_id = Column(String, ForeignKey('service.id'), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    last_updated_at = Column(DateTime, nullable=True, onupdate=func.now(), index=True)
    tag = Column(String, nullable=False, default='default', index=True)

    defaults = Column(Text)

    deployment_target = relationship("DeploymentTarget", back_populates="deployments")
    service = relationship("Service", back_populates="deployments")
    configs = relationship("DeploymentConfig", back_populates="deployment", lazy='select')

    zones = relationship("Zone", secondary='deployments_zones', back_populates="deployments", lazy='select')
    deployment_procs = relationship("DeploymentProc", back_populates="deployment", lazy='select')

    # all releases for this deployment
    releases = relationship("Release", primaryjoin='Deployment.id==Release.deployment_id',
                            foreign_keys="Release.deployment_id", back_populates="deployment")

    # current release via join table (uselist=False ensures single result)
    current_release = relationship("Release", secondary=deployment_current_release,
                                   uselist=False, lazy='select')

    def __repr__(self):
        return self.id

    # makes sure the release is actually one that belongs to the deployment
    @validates('current_release')
    def validate_current_release_id(self, key, value):
        if value is not None:
            assert value in self.releases
            assert value.build.service_id == self.service_id
        return value


@db.event.listens_for(Deployment, 'before_update')
@db.event.listens_for(Deployment, 'before_insert')
def my_before_write_listener(mapper, connection, deployment):
    # if deployment.current_release:
    #     if deployment.current_release.build.service_id != deployment.service_id:
    #         raise ValueError("Release must be for the same service as deployed in this deployment.")

    __update_id__(deployment)


# DO NOT DELETE THIS SAMPLE CODE
# @db.event.listens_for(Deployment, 'init')
# def received_init(deployment, args, **kwargs):
#     from models import Service, Config
#     svc = db.session.query(Service).filter(Service.id == kwargs['service_id']).first()
#     for sc in svc.service_config_templates:
#         cfg = sc.__dict__
#         cfg.provider('service_id')
#         cfg.provider('_sa_instance_state')
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


@db.event.listens_for(Deployment, 'init')
def set_tag_default(deployment, args, kwargs):
    if kwargs.get('tag') is None:
        deployment.tag = 'default'
