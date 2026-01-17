from sqlalchemy import *
from sqlalchemy.orm import relationship, validates

from db import db
import datetime


class DeploymentProc(db.Model):
    exclude = ['allocations']

    __tablename__ = "deployment_proc"
    id = Column(String, primary_key=True)
    deployment_id = Column(String, ForeignKey('deployment.id'), nullable=False, index=True)
    proc_id = Column(String, ForeignKey('proc.id'), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    last_updated_at = Column(DateTime, nullable=True, onupdate=func.now(), index=True)
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
    # Extract service_id from proc_id (format: {service_id}:{name})
    proc_service_id = ':'.join(deployment_proc.proc_id.rsplit(':', 1)[:-1])

    # Get deployment's service_id - either from loaded relationship or query
    if deployment_proc.deployment is not None:
        deployment_service_id = deployment_proc.deployment.service_id
    else:
        # Query the deployment to get its service_id
        from models.deployment import Deployment
        dep = db.session.get(Deployment, deployment_proc.deployment_id)
        deployment_service_id = dep.service_id if dep else None

    assert deployment_service_id == proc_service_id, \
        f"Proc service_id ({proc_service_id}) must match deployment service_id ({deployment_service_id})"

    deployment_proc.id = deployment_proc.deployment_id + ':' + deployment_proc.proc_id
