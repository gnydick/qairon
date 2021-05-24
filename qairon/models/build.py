from datetime import datetime

from sqlalchemy import *
from sqlalchemy.orm import relationship

from db import db


class Build(db.Model):
    __tablename__ = "build"

    id = Column(String, primary_key=True)
    build_num = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False)
    last_updated_at = Column(DateTime, nullable=False)
    service_id = Column(String, ForeignKey('service.id'), nullable=False)
    git_tag = Column(String, nullable=False)
    service = relationship('Service', back_populates='builds')
    releases = relationship('Release', back_populates='build')

    def __repr__(self):
        return self.id


@db.event.listens_for(Build, 'before_insert')
def my_before_insert_listener(mapper, connection, build):
    now = datetime.now()
    build.created_at = now
    build.last_updated_at = now
    __update_id__(build)


@db.event.listens_for(Build, 'before_update')
def my_before_update_listener(mapper, connection, build):
    now = datetime.now()
    build.last_updated_at = now
    __update_id__(build)


def __update_id__(build):
    build.id = '%s:%s:%s' % (build.service_id, build.git_tag, build.build_num)
