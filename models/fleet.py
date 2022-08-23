from sqlalchemy import *
from sqlalchemy.orm import relationship

from db import db
import datetime


class Fleet(db.Model):
    __tablename__ = "fleet"
    id = Column(String, primary_key=True)
    deployment_target_id = Column(String, ForeignKey('deployment_target.id'), index=true)
    fleet_type_id = Column(String, ForeignKey('fleet_type.id'), index=true)
    native_id = Column(String, index=true)
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=true)
    last_updated_at = Column(DateTime, nullable=True, onupdate=func.now(), index=true)

    name = Column(String, index=true)

    defaults = Column(Text)

    deployment_target = relationship("DeploymentTarget", back_populates="fleets")
    deployment_target_bins = relationship("DeploymentTargetBin", secondary='target_bins_fleets', back_populates="fleets", lazy='joined')
    subnets = relationship("Subnet", secondary='subnets_fleets', back_populates="fleets", lazy='joined')
    type = relationship("FleetType", back_populates="fleets")
    capacities = relationship("Capacity", back_populates="fleet", lazy='joined')

    def __repr__(self):
        return self.id


@db.event.listens_for(Fleet, 'before_update')
@db.event.listens_for(Fleet, 'before_insert')
def my_before_insert_listener(mapper, connection, fleet):
    __update_id__(fleet)


def __update_id__(fleet):
    fleet.id = ':'.join([fleet.deployment_target_id, fleet.fleet_type_id, fleet.name])
