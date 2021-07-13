from sqlalchemy import *
from sqlalchemy.orm import relationship

from db import db


class Zone(db.Model):
    __tablename__ = "zone"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    region_id = Column(String, ForeignKey('region.id'), nullable=False)
    defaults = Column(Text)
    native_id = Column(String)

    region = relationship("Region", back_populates="zones")
    deployments = relationship("Deployment", secondary='deployments_zones', back_populates="zones")

    def __repr__(self):
        return self.id


@db.event.listens_for(Zone, 'before_update')
@db.event.listens_for(Zone, 'before_insert')
def my_before_insert_listener(mapper, connection, zone):
    __update_id__(zone)


def __update_id__(zone):
    zone.id = zone.region_id + ':' + zone.name
