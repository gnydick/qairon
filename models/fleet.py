from sqlalchemy import *
from sqlalchemy.orm import relationship

from db import db


class Fleet(db.Model):
    __tablename__ = "fleet"
    id = Column(String, primary_key=True)
    deployment_target_id = Column(String, ForeignKey('deployment_target.id'))
    fleet_type_id = Column(String, ForeignKey('fleet_type.id'))

    name = Column(String(256))

    defaults = Column(Text)
    native_id = Column(String)

    deployment_target = relationship("DeploymentTarget", back_populates="fleets")
    subnets = relationship("Subnet", secondary='subnets_fleets', back_populates="fleets")
    type = relationship("FleetType", back_populates="fleets")
    capacities = relationship("Capacity", back_populates="fleet")

    def __repr__(self):
        return self.id


@db.event.listens_for(Fleet, 'before_update')
@db.event.listens_for(Fleet, 'before_insert')
def my_before_insert_listener(mapper, connection, fleet):
    __update_id__(fleet)


def __update_id__(fleet):
    fleet.id = ':'.join([fleet.deployment_target_id, fleet.fleet_type_id, fleet.name])
