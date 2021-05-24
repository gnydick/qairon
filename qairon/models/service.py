from sqlalchemy import *
from sqlalchemy.orm import relationship

from db import db


class Service(db.Model):
    __tablename__ = "service"
    id = Column(String, primary_key=True)
    stack_id = Column(String, ForeignKey('stack.id'), nullable=False)
    repo_id = Column(String, ForeignKey('repo.id'))
    name = Column(String, nullable=False)

    scm_url = Column(String)
    artifact_name = Column(String)
    defaults = Column(Text)

    repo = relationship("Repo", back_populates="services")
    stack = relationship("Stack", back_populates="services")
    builds = relationship("Build", back_populates="service")
    deployments = relationship("Deployment", back_populates="service")

    configs = relationship("ServiceConfig", back_populates="service")
    procs = relationship("Proc", back_populates="service")

    def __repr__(self):
        return self.id


@db.event.listens_for(Service, 'before_update')
@db.event.listens_for(Service, 'before_insert')
def my_before_insert_listener(mapper, connection, service):
    __update_id__(service)


def __update_id__(service):
    service.id = service.stack_id + ':' + service.name
