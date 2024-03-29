from sqlalchemy import *
from sqlalchemy.orm import relationship

from db import db
import datetime


class Region(db.Model):
    exclude = ['partitions', 'zones']


    __tablename__ = "region"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False, index=True)
    provider_id = Column(String, ForeignKey('provider.id'), nullable=True, index=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    last_updated_at = Column(DateTime, nullable=True, onupdate=func.now(), index=True)
    defaults = Column(Text)
    native_id = Column(String, index=True)

    partitions = relationship("Partition", back_populates="region", lazy='select')
    provider = relationship("Provider", back_populates="regions")
    zones = relationship("Zone", back_populates="region", lazy='select')

    def __repr__(self):
        return self.id


@db.event.listens_for(Region, 'before_update')
@db.event.listens_for(Region, 'before_insert')
def my_before_insert_listener(mapper, connection, region):
    __update_id__(region)


def __update_id__(region):
    region.id = region.provider_id + ':' + region.name
