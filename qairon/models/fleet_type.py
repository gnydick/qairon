from sqlalchemy import *
from sqlalchemy.orm import relationship, validates

from db import db


class FleetType(db.Model):
    __tablename__ = "fleet_type"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    provider_type_id = Column(String, ForeignKey('provider_type.id'), nullable=True)

    defaults = Column(Text)

    provider_type = relationship("ProviderType", back_populates="fleet_types")
    fleets = relationship("Fleet", back_populates="type")

    def __repr__(self):
        return self.id

    @validates('id')
    def validate_name(self, key, value):
        assert value != ''
        return value


@db.event.listens_for(FleetType, 'before_update')
@db.event.listens_for(FleetType, 'before_insert')
def my_before_insert_listener(mapper, connection, fleet_type):
    __update_id__(fleet_type)


def __update_id__(fleet_type):
    fleet_type.id = ':'.join([fleet_type.pop_type_id, fleet_type.name])
