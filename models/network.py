from sqlalchemy import *
from sqlalchemy.orm import relationship

from db import db
import datetime

from sqlalchemy.dialects.postgresql.base import CIDR

import ipaddress as ip

class Network(db.Model):
    __tablename__ = "network"

    def __init__(self, **entries):
        self.__dict__.update(entries)

    id = Column(String, primary_key=True)
    partition_id = Column(String, ForeignKey('partition.id',  onupdate='CASCADE'), nullable=False, index=true)
    native_id = Column(String, index=true)
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=true)
    last_updated_at = Column(DateTime, nullable=True, onupdate=func.now(), index=true)

    name = Column(String, nullable=False, index=true)
    cidr = Column(CIDR, nullable=False, index=true)
    defaults = Column(Text)


    partition = relationship("Partition", back_populates="networks")
    subnets = relationship("Subnet", back_populates='network', lazy='selectin')

    def __repr__(self):
        return self.id

    def ipv4network(self):
        return ip.IPv4Network(address=self.cidr)


@db.event.listens_for(Network, 'before_update')
@db.event.listens_for(Network, 'before_insert')
def my_before_insert_listener(mapper, connection, network):
    __update_id__(network)


def __update_id__(network):
    network.id = network.partition_id + ':' + network.name
