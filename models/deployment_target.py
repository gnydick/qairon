from sqlalchemy import *
from sqlalchemy.orm import validates, relationship

from db import db


class DeploymentTarget(db.Model):
    __tablename__ = "deployment_target"

    id = Column(String, primary_key=True)
    deployment_target_type_id = Column(String, ForeignKey('deployment_target_type.id'))
    partition_id = Column(String, ForeignKey('partition.id'))

    name = Column(String(255), nullable=False)

    defaults = Column(Text)
    native_id = Column(String)

    partition = relationship("Partition", back_populates="deployment_targets")

    fleets = relationship("Fleet", back_populates="deployment_target")
    type = relationship("DeploymentTargetType", back_populates="targets")
    deployments = relationship('Deployment', back_populates='deployment_target')



    def __repr__(self):
        return self.id


@validates('id')
def validate_name(self, key, value):
    assert value != ''
    return value


@db.event.listens_for(DeploymentTarget, 'before_update')
@db.event.listens_for(DeploymentTarget, 'before_insert')
def my_before_insert_listener(mapper, connection, target):
    __update_id__(target)


def __update_id__(target):
    target.id = target.partition_id + ':' + target.deployment_target_type_id + ':' + target.name
