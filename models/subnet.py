import ipaddress as ip

from sqlalchemy import *
from sqlalchemy.dialects.postgresql import CIDR
from sqlalchemy.orm import relationship

from db import db
from mixins.models import TenantMixin
from models import Network


class Subnet(db.Model,TenantMixin):
    exclude = ['fleets']

    __tablename__ = "subnet"

    id = Column(String, primary_key=True)
    network_id = Column(String, ForeignKey('network.id'), nullable=False, index=True)
    native_id = Column(String, index=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    last_updated_at = Column(DateTime, nullable=True, onupdate=func.now(), index=True)
    name = Column(String, nullable=False, index=True)
    cidr = Column(CIDR, nullable=False, index=True)

    defaults = Column(Text)

    network = relationship("Network", back_populates="subnets")
    fleets = relationship("Fleet", secondary='subnets_fleets', back_populates="subnets", lazy='select')

    def __repr__(self):
        return self.id

    def net(self):
        return ip.IPv4Network(address=self.cidr)


class SubnetUnavailableError(RuntimeError):

    def __init__(self, message, errors):
        super().__init__(message)
        self.errors = errors





@db.event.listens_for(Subnet, 'before_update')
@db.event.listens_for(Subnet, 'before_insert')
def my_before_insert_listener(mapper, connection, subnet):
       __update_id__(subnet)


def __update_id__(subnet):
    subnet.id = subnet.network_id + ':' + subnet.name
