from sqlalchemy import *
from sqlalchemy.orm import relationship

from qairon.db import db


class Proc(db.Model):
    __tablename__ = "proc"

    id = Column(String, primary_key=True, nullable=False)
    service_id = Column(String, ForeignKey('service.id'), nullable=False)
    name = Column(String(64), nullable=False)
    service = relationship("Service", back_populates="procs")

    deployment_procs = relationship("DeploymentProc", back_populates="proc")

    def __repr__(self):
        return self.id


@db.event.listens_for(Proc, 'before_update')
@db.event.listens_for(Proc, 'before_insert')
def my_before_insert_listener(mapper, connection, proc):
    __update_id__(proc)


def __update_id__(proc):
    proc.id = proc.service_id + ':' + proc.name
