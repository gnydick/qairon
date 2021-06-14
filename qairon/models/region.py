from sqlalchemy import *
from sqlalchemy.orm import relationship

from qairon.db import db


class Region(db.Model):
    __tablename__ = "region"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    provider_id = Column(String, ForeignKey('provider.id'), nullable=True)
    defaults = Column(Text)
    native_id = Column(String)

    partitions = relationship("Partition", back_populates="region")
    provider = relationship("Provider", back_populates="regions")
    zones = relationship("Zone", back_populates="region")

    def __repr__(self):
        return self.id


@db.event.listens_for(Region, 'before_update')
@db.event.listens_for(Region, 'before_insert')
def my_before_insert_listener(mapper, connection, region):
    __update_id__(region)


def __update_id__(region):
    region.id = region.provider_id + ':' + region.name
