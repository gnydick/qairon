from datetime import datetime

from sqlalchemy import *
from sqlalchemy.orm import relationship

from db import db


class Release(db.Model):
    __tablename__ = "release"

    id = Column(String, primary_key=True)
    build_id = Column(String, ForeignKey('build.id'), nullable=False)
    deployment_id = Column(String, ForeignKey('deployment.id'), nullable=False)
    build_num = Column(Integer, nullable=False)

    created_at = Column(DateTime, nullable=False)
    last_updated_at = Column(DateTime, nullable=False)

    build = relationship('Build', back_populates='releases')

    deployment = relationship('Deployment', back_populates='releases', foreign_keys=[deployment_id])

    release_artifacts = relationship('ReleaseArtifact', back_populates='release')

    def __repr__(self):
        return self.id


@db.event.listens_for(Release, 'before_insert')
def my_before_insert_listener(mapper, connection, release):
    now = datetime.now()
    release.created_at = now
    release.last_updated_at = now
    __update_id__(release)


@db.event.listens_for(Release, 'before_update')
def my_before_update_listener(mapper, connection, release):
    now = datetime.now()
    release.last_updated_at = now
    __update_id__(release)


def __update_id__(release):
    release.id = '%s:%s' % (release.deployment_id, release.build_num)
