from sqlalchemy import *
from sqlalchemy.orm import validates, relationship

from db import db
import datetime


class DeploymentTarget(db.Model):
    exclude = ['fleets', 'deployment_targets']

    __tablename__ = "deployment_target"

    id = Column(String, primary_key=True)
    deployment_target_type_id = Column(String, ForeignKey('deployment_target_type.id'), nullable=False, index=True)
    partition_id = Column(String, ForeignKey('partition.id'), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    last_updated_at = Column(DateTime, nullable=True, onupdate=func.now(), index=True)
    name = Column(String(255), nullable=False, index=True)

    defaults = Column(Text)
    native_id = Column(String, index=True)

    partition = relationship("Partition", back_populates="deployment_targets")

    deployments = relationship("Deployment", back_populates="deployment_target")
    fleets = relationship("Fleet", back_populates="deployment_target", lazy='select')
    type = relationship("DeploymentTargetType", back_populates="targets")



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
