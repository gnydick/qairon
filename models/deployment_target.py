from sqlalchemy import *
from sqlalchemy.orm import validates, relationship

from db import db
from mixins.models import TenantMixin
import datetime


class DeploymentTarget(db.Model,TenantMixin):
    exclude = ['fleets', 'deployment_target_bins']

    __tablename__ = "deployment_target"

    id = Column(String, primary_key=True)
    deployment_target_type_id = Column(String, ForeignKey('deployment_target_type.id'), index=True)
    partition_id = Column(String, ForeignKey('partition.id'), index=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    last_updated_at = Column(DateTime, nullable=True, onupdate=func.now(), index=True)
    name = Column(String(255), nullable=False, index=True)

    defaults = Column(Text)
    native_id = Column(String)

    partition = relationship("Partition", back_populates="deployment_targets")

    fleets = relationship("Fleet", back_populates="deployment_target", lazy='select')
    type = relationship("DeploymentTargetType", back_populates="targets")
    deployment_target_bins = relationship('DeploymentTargetBin', back_populates='deployment_target', lazy='select')



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
