import sqlalchemy
from sqlalchemy import *
from sqlalchemy.dialects.postgresql import CIDR
from sqlalchemy.orm import relationship, Session
from models import Network
from db import db
import datetime

import ipaddress as ip


class Subnet(db.Model):
    __tablename__ = "subnet"
    id = Column(String, primary_key=True)
    network_id = Column(String, ForeignKey('network.id'), nullable=False)
    native_id = Column(String)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    last_updated_at = Column(DateTime, nullable=True, onupdate=func.now())
    name = Column(String, nullable=False)
    cidr = Column(CIDR, nullable=False, )

    defaults = Column(Text)
    native_id = Column(String)

    network = relationship("Network", back_populates="subnets")
    fleets = relationship("Fleet", secondary='subnets_fleets', back_populates="subnets")

    def __repr__(self):
        return self.id

    def net(self):
        return ip.IPv4Network(address=self.cidr)


class SubnetUnavailableError(RuntimeError):

    def __init__(self, message, errors):
        super().__init__(message)
        self.errors = errors


@db.event.listens_for(Subnet, 'before_update')
def my_before_update_listener(mapper, connection, subnet):
    __update_id__(subnet)


# TODO this shouldn't be a rest call, refactor it'
@db.event.listens_for(Subnet, 'before_insert')
def my_before_insert_listener(mapper, connection, subnet):
    newsubnet = ip.IPv4Network(address=subnet.cidr)
    session = db.session
    network = session.query(Network).filter_by(id=subnet.network_id).first()



    if newsubnet in [ip.IPv4Network(subnet.cidr) for subnet in network.subnets if subnet.id is not None]:
        error = SubnetUnavailableError("Already Used", null)
        return error
    __update_id__(subnet)


def __update_id__(subnet):
    subnet.id = subnet.network_id + ':' + subnet.name
