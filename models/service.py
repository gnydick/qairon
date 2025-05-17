from sqlalchemy import *
from sqlalchemy.orm import relationship

from db import db
from mixins.models import TenantMixin
import datetime


class Service(db.Model,TenantMixin):
    exclude = ['builds', 'deployments', 'configs', 'procs', 'tenant_id']
    children = ['builds', 'deployments', 'repos', 'configs', 'procs']

    __tablename__ = "service"

    id = Column(String, primary_key=True)
    stack_id = Column(String, ForeignKey('stack.id'), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    last_updated_at = Column(DateTime, nullable=True, onupdate=func.now(), index=True)
    name = Column(String, nullable=False, index=True)

    artifact_name = Column(String, index=True)
    defaults = Column(Text)

    stack = relationship("Stack", back_populates="services")
    builds = relationship("Build", back_populates="service", lazy='select')
    deployments = relationship("Deployment", back_populates="service", lazy='select')
    repos = relationship("Repo", secondary='services_repos', back_populates="services", lazy='select')

    configs = relationship("ServiceConfig", back_populates="service", lazy='select')
    procs = relationship("Proc", back_populates="service", lazy='select')

    def __repr__(self):
        return self.id


@db.event.listens_for(Service, 'before_update')
@db.event.listens_for(Service, 'before_insert')
def my_before_insert_listener(mapper, connection, service):
    __update_id__(service)


def __update_id__(service):
    service.id = service.stack_id + ':' + service.name
