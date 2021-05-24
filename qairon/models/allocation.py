from sqlalchemy import *
from sqlalchemy.orm import validates, relationship

from db import db


class Allocation(db.Model):
    watermarks = ('HIGH', 'LOW')
    watermarks_enum = Enum(*watermarks, name='watermark')

    __tablename__ = "allocation"

    id = Column(String, primary_key=True)
    value = Column(Float, nullable=False)
    allocation_type_id = Column(String, ForeignKey('allocation_type.id'))
    deployment_proc_id = Column(String, ForeignKey('deployment_proc.id'))
    watermark = db.Column(watermarks_enum)
    UniqueConstraint('deployment_proc_id', 'type', 'watermark')
    defaults = Column(Text)

    deployment_proc = relationship('DeploymentProc', back_populates='allocations')
    type = relationship('AllocationType', back_populates='allocations')

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
