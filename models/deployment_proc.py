from sqlalchemy import *
from sqlalchemy.orm import relationship, validates

from db import db
import datetime


class DeploymentProc(db.Model):
    exclude = ['allocations']

    __tablename__ = "deployment_proc"


    id = Column(String, primary_key=True)
    deployment_id = Column(String, ForeignKey('deployment.id'), index=true)
    proc_id = Column(String, ForeignKey('proc.id'), index=true)
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=true)
    last_updated_at = Column(DateTime, nullable=True, onupdate=func.now(), index=true)
    defaults = Column(Text)

    allocations = relationship("Allocation", back_populates="deployment_proc",
                               primaryjoin="and_(Allocation.deployment_proc_id==DeploymentProc.id)")
    deployment = relationship("Deployment", back_populates="deployment_procs")
    proc = relationship("Proc", back_populates="deployment_procs")

    def __repr__(self):
        return self.id




@db.event.listens_for(DeploymentProc, 'before_update')
@db.event.listens_for(DeploymentProc, 'before_insert')
def my_before_insert_listener(mapper, connection, deployment_proc):
    __update_id__(deployment_proc)


def __update_id__(deployment_proc):
    assert deployment_proc.deployment.service_id == deployment_proc.proc.service_id

    deployment_proc.id = deployment_proc.deployment_id + ':' + deployment_proc.proc_id
