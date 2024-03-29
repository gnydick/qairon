from sqlalchemy import *
from sqlalchemy.orm import validates, relationship

from db import db
import datetime


class Capacity(db.Model):
    exclude = []

    __tablename__ = "capacity"

    id = Column(String, primary_key=True)
    fleet_id = Column(String, ForeignKey('fleet.id'), index=True)
    allocation_type_id = Column(String, ForeignKey('allocation_type.id'), index=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    last_updated_at = Column(DateTime, nullable=True, onupdate=func.now(), index=True)
    value = Column(Float, nullable=False)
    defaults = Column(Text)

    type = relationship('AllocationType', back_populates='capacities')
    fleet = relationship('Fleet', back_populates='capacities')

    def __repr__(self):
        return self.id

    @validates('id')
    def validate_name(self, key, value):
        assert value != ''
        return value


@db.event.listens_for(Capacity, 'before_update')
@db.event.listens_for(Capacity, 'before_insert')
def my_before_insert_listener(mapper, connection, capacity):
    __update_id__(capacity)


def __update_id__(capacity):
    capacity.id = ':'.join([capacity.relatable_type.id, capacity.fleet.id])
