from sqlalchemy import *
from sqlalchemy.orm import relationship

from db import db


class Partition(db.Model):
    __tablename__ = "partition"

    id = Column(String, primary_key=True)
    region_id = Column(String, ForeignKey('region.id'), nullable=False)

    native = Column(Text)
    name = Column(String, nullable=False)
    defaults = Column(Text)

    region = relationship("Region", uselist=False, back_populates="partitions")

    deployment_targets = relationship("DeploymentTarget", back_populates="partition")

    networks = relationship("Network", back_populates="partition")

    def __repr__(self):
        return self.id


@db.event.listens_for(Partition, 'before_update')
@db.event.listens_for(Partition, 'before_insert')
def my_before_insert_listener(mapper, connection, partition):
    __update_id__(partition)


def __update_id__(partition):
    partition.id = partition.region_id + ':' + partition.name
