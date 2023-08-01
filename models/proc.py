from sqlalchemy import *
from sqlalchemy.orm import relationship

from db import db
import datetime


class Proc(db.Model):
    exclude = ['deployment_procs']

    __tablename__ = "proc"


    id = Column(String, primary_key=True, nullable=False)
    service_id = Column(String, ForeignKey('service.id'), nullable=False, index=true)
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=true)
    last_updated_at = Column(DateTime, nullable=True, onupdate=func.now(), index=true)
    name = Column(String(64), nullable=False, index=true)
    defaults = Column(Text)

    service = relationship("Service", back_populates="procs")

    deployment_procs = relationship("DeploymentProc", back_populates="proc", lazy='select')

    def __repr__(self):
        return self.id


@db.event.listens_for(Proc, 'before_update')
@db.event.listens_for(Proc, 'before_insert')
def my_before_insert_listener(mapper, connection, proc):
    __update_id__(proc)


def __update_id__(proc):
    proc.id = proc.service_id + ':' + proc.name
