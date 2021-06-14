from sqlalchemy import *
from sqlalchemy.orm import validates, relationship

from qairon.db import db


class Capacity(db.Model):
    __tablename__ = "capacity"

    id = Column(String, primary_key=True)
    fleet_id = Column(String, ForeignKey('fleet.id'))
    value = Column(Float, nullable=False)
    allocation_type_id = Column(String, ForeignKey('allocation_type.id'))
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
    capacity.id = ':'.join([capacity.type.id, capacity.fleet.id])
