from sqlalchemy import *
from sqlalchemy.orm import relationship, validates

from db import db
import datetime


class FleetType(db.Model):
    exclude = ['fleets']

    __tablename__ = "fleet_type"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False, index=True)
    provider_type_id = Column(String, ForeignKey('provider_type.id'), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    last_updated_at = Column(DateTime, nullable=True, onupdate=func.now(), index=True)
    defaults = Column(Text)

    provider_type = relationship("ProviderType", back_populates="fleet_types")
    fleets = relationship("Fleet", back_populates="type", lazy='select')

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
    fleet_type.id = ':'.join([fleet_type.provider_type_id, fleet_type.name])
