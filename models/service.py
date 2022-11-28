from sqlalchemy import *
from sqlalchemy.orm import relationship

from db import db
import datetime


class Service(db.Model):
    exclude = ['builds', 'deployments', 'configs', 'procs']
    children = ['builds', 'deployments', 'repos', 'configs', 'procs']

    __tablename__ = "service"
    id = Column(String, primary_key=True)
    stack_id = Column(String, ForeignKey('stack.id',  onupdate='CASCADE'), nullable=False, index=true)
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=true)
    last_updated_at = Column(DateTime, nullable=True, onupdate=func.now(), index=true)
    name = Column(String, nullable=False, index=true)

    artifact_name = Column(String, index=true)
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
