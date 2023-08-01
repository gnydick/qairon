from sqlalchemy import *
from sqlalchemy.orm import relationship

from db import db
import datetime


class DeploymentTargetBin(db.Model):
    exclude = ['deployments', 'fleets']

    __tablename__ = "deployment_target_bin"


    id = Column(String, primary_key=True)
    name = Column(String, nullable=False, index=true, server_default='default')
    deployment_target_id = Column(String, ForeignKey('deployment_target.id'), nullable=False, index=true)
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=true)
    last_updated_at = Column(DateTime, nullable=True, onupdate=func.now(), index=true)
    defaults = Column(Text)

    deployment_target = relationship('DeploymentTarget', back_populates='deployment_target_bins')
    deployments = relationship("Deployment", back_populates="deployment_target_bin", lazy='select')
    fleets = relationship("Fleet", secondary='target_bins_fleets', back_populates="deployment_target_bins", lazy='select')

    def __repr__(self):
        return self.id


@db.event.listens_for(DeploymentTargetBin, 'before_update')
@db.event.listens_for(DeploymentTargetBin, 'before_insert')
def my_before_insert_listener(mapper, connection, deployment_target_bin):
    __update_id__(deployment_target_bin)


def __update_id__(deployment_target_bin):
    deployment_target_bin.id = deployment_target_bin.deployment_target_id + ':' + deployment_target_bin.name
