from sqlalchemy import *
from sqlalchemy.ext.declarative import ConcreteBase
from sqlalchemy.orm import relationship

from db import db
import datetime


# class Config(ConcreteBase, db.Model):
#     __tablename__ = "config"
#     id = Column(String, primary_key=True)
#
#     config_template_id = Column(String, ForeignKey('config_template.id'))
#     configurable_id = Column(String, ForeignKey('deployment.id'))
#     name = Column(String, nullable=False)
#
#     tag = Column(String, nullable=False, default='default')
#     config = Column(Text)
#
#     __mapper_args__ = {
#         'polymorphic_identity': 'config',
#         'concrete': True
#     }


class DeploymentConfig(db.Model):
    __tablename__ = "deployment_config"
    id = Column(String, primary_key=True)

    config_template_id = Column(String, ForeignKey('config_template.id'))
    deployment_id = Column(String, ForeignKey('deployment.id'))
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    last_updated_at = Column(DateTime, nullable=True, onupdate=func.now())
    name = Column(String, nullable=False)

    tag = Column(String, nullable=False, default='default')

    config = Column(Text)
    defaults = Column(Text)

    template = relationship("ConfigTemplate", back_populates="deployment_configs")

    deployment = relationship("Deployment", back_populates="configs")

    # __mapper_args__ = {
    #     'polymorphic_identity': 'deployment_config',
    #     'concrete': True
    # }

    def __repr__(self):
        return self.deployment.id + ':' + self.config_template_id + ':' + self.name + ':' + self.tag


class ServiceConfig(db.Model):
    __tablename__ = "service_config"
    id = Column(String, primary_key=True)

    config_template_id = Column(String, ForeignKey('config_template.id'))
    service_id = Column(String, ForeignKey('service.id'))
    name = Column(String, nullable=False)

    tag = Column(String, nullable=False, default='default')
    config = Column(Text)

    template = relationship("ConfigTemplate", back_populates="service_configs")

    service = relationship("Service", back_populates="configs")

    # __mapper_args__ = {
    #     'polymorphic_identity': 'service_config',
    #     'concrete': True
    # }


    def __repr__(self):
        return self.service.id + ':' + self.config_template_id + ':' + self.name + ':' + self.tag


# @db.event.listens_for(Config, 'init')
# def received_init(target, args, kwargs):
#     for rel in inspect(target.__class__).relationships:
#
#         rel_cls = rel.mapper.class_
#
#         if rel.key in kwargs:
#             kwargs[rel.key] = [rel_cls(**c) for c in kwargs[rel.key]]


@db.event.listens_for(DeploymentConfig, 'before_update')
@db.event.listens_for(DeploymentConfig, 'before_insert')
def my_before_insert_listener(mapper, connection, config):
    __update_deployment_id__(config)


def __update_deployment_id__(config):
    config.id = config.deployment_id + ':' + config.config_template_id + ':' + config.name + ':' + config.tag


@db.event.listens_for(ServiceConfig, 'before_update')
@db.event.listens_for(ServiceConfig, 'before_insert')
def my_before_insert_listener(mapper, connection, config):
    __update_service_id__(config)


def __update_service_id__(config):
    config.id = config.service_id + ':' + config.config_template_id + ':' + config.name + ':' + config.tag
