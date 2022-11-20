from sqlalchemy import *
from sqlalchemy.orm import relationship

from db import db
import datetime


class Partition(db.Model):
    exclude = ['deployment_targets', 'networks']

    __tablename__ = "partition"

    id = Column(String, primary_key=True)
    region_id = Column(String, ForeignKey('region.id',  onupdate='CASCADE'), nullable=False, index=true)
    native_id = Column(String, index=true)
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=true)
    last_updated_at = Column(DateTime, nullable=True, onupdate=func.now(), index=true)
    name = Column(String, nullable=False, index=true)
    defaults = Column(Text)

    region = relationship("Region", uselist=False, back_populates="partitions")

    deployment_targets = relationship("DeploymentTarget", back_populates="partition", lazy='select')

    networks = relationship("Network", back_populates="partition", lazy='select')

    def __repr__(self):
        return self.id


@db.event.listens_for(Partition, 'before_update')
@db.event.listens_for(Partition, 'before_insert')
def my_before_insert_listener(mapper, connection, partition):
    __update_id__(partition)


def __update_id__(partition):
    partition.id = partition.region_id + ':' + partition.name
