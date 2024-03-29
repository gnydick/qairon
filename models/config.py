from sqlalchemy import *
from sqlalchemy.ext.declarative import ConcreteBase
from sqlalchemy.orm import relationship

from db import db


class DeploymentConfig(db.Model):
    exclude = []

    __tablename__ = "deployment_config"
    id = Column(String, primary_key=True)

    config_template_id = Column(String, ForeignKey('config_template.id'), index=True)
    deployment_id = Column(String, ForeignKey('deployment.id'), index=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    last_updated_at = Column(DateTime, nullable=True, onupdate=func.now(), index=True)
    name = Column(String, nullable=False, index=True)

    tag = Column(String, nullable=False, default='default', index=True)

    config = Column(Text)
    defaults = Column(Text)

    template = relationship("ConfigTemplate", back_populates="deployment_configs")

    deployment = relationship("Deployment", back_populates="configs")

    def __repr__(self):
        return self.deployment.id + ':' + self.config_template_id + ':' + self.name + ':' + self.tag


class ServiceConfig(db.Model):
    exclude = []

    __tablename__ = "service_config"
    id = Column(String, primary_key=True)

    config_template_id = Column(String, ForeignKey('config_template.id'))
    service_id = Column(String, ForeignKey('service.id'))
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    last_updated_at = Column(DateTime, nullable=True, onupdate=func.now())
    name = Column(String, nullable=False)

    tag = Column(String, nullable=False, default='default')
    config = Column(Text)
    defaults = Column(Text)

    template = relationship("ConfigTemplate", back_populates="service_configs")

    service = relationship("Service", back_populates="configs")

    def __repr__(self):
        return self.service.id + ':' + self.config_template_id + ':' + self.name + ':' + self.tag


class StackConfig(db.Model):
    exclude = []
    __tablename__ = "stack_config"
    id = Column(String, primary_key=True)

    config_template_id = Column(String, ForeignKey('config_template.id'))
    stack_id = Column(String, ForeignKey('stack.id'))
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    last_updated_at = Column(DateTime, nullable=True, onupdate=func.now())
    name = Column(String, nullable=False)

    tag = Column(String, nullable=False, default='default')
    config = Column(Text)
    defaults = Column(Text)

    template = relationship("ConfigTemplate", back_populates="stack_configs")

    stack = relationship("Stack", back_populates="configs")

    def __repr__(self):
        return self.stack.id + ':' + self.config_template_id + ':' + self.name + ':' + self.tag

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


@db.event.listens_for(StackConfig, 'before_update')
@db.event.listens_for(StackConfig, 'before_insert')
def my_before_insert_listener(mapper, connection, config):
    __update_stack_id__(config)


def __update_stack_id__(config):
    config.id = config.stack_id + ':' + config.config_template_id + ':' + config.name + ':' + config.tag
