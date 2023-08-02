from sqlalchemy import *
from sqlalchemy.orm import validates, relationship

from db import db
import datetime


class Allocation(db.Model):
    watermarks = ('HIGH', 'LOW')
    watermarks_enum = Enum(*watermarks, name='watermark')

    exclude = []

    __tablename__ = "allocation"

    id = Column(String, primary_key=True)
    value = Column(Float, nullable=False)
    allocation_type_id = Column(String, ForeignKey('allocation_type.id'), index=true)
    deployment_proc_id = Column(String, ForeignKey('deployment_proc.id'), index=true)
    watermark = db.Column(watermarks_enum)
    UniqueConstraint('deployment_proc_id', 'type', 'watermark')
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=true)
    last_updated_at = Column(DateTime, nullable=True, onupdate=func.now(), index=true)
    defaults = Column(Text)

    deployment_proc = relationship('DeploymentProc', back_populates='allocations')
    type = relationship('AllocationType', back_populates='allocations')

    Index('allocation_allocation_type_id_idx', 'allocation.allocation_type_id')

    def __repr__(self):
        return self.id


    @validates('id')
    def validate_name(self, key, value):
        assert value != ''
        return value


@db.event.listens_for(Allocation, 'before_update')
@db.event.listens_for(Allocation, 'before_insert')
def my_before_insert_listener(mapper, connection, resource_allocation):
    __update_id__(resource_allocation)


def __update_id__(resource_allocation):
    resource_allocation.id = resource_allocation.deployment_proc_id + ':' + resource_allocation.allocation_type_id + ':' + resource_allocation.watermark
