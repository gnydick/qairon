from datetime import datetime

from sqlalchemy import *
from sqlalchemy.orm import relationship

from db import db
import datetime


class Release(db.Model):
    __tablename__ = "release"

    id = Column(String, primary_key=True)
    build_id = Column(String, ForeignKey('build.id'), nullable=False, index=true)
    deployment_id = Column(String, ForeignKey('deployment.id'), nullable=False, index=true)
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=true)
    last_updated_at = Column(DateTime, nullable=True, onupdate=func.now(), index=true)
    build_num = Column(Integer, nullable=False, index=true)
    defaults = Column(Text)
    build = relationship('Build', back_populates='releases')

    deployment = relationship('Deployment', back_populates='releases', foreign_keys=[deployment_id])

    release_artifacts = relationship('ReleaseArtifact', back_populates='release', lazy='selectin')

    def __repr__(self):
        return self.id


@db.event.listens_for(Release, 'before_insert')
def my_before_insert_listener(mapper, connection, release):
    __update_id__(release)


@db.event.listens_for(Release, 'before_update')
def my_before_update_listener(mapper, connection, release):
    __update_id__(release)


def __update_id__(release):
    release.id = '%s:%s' % (release.deployment_id, release.build_num)
