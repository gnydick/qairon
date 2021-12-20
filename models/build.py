import re
from datetime import datetime

from sqlalchemy import *
from sqlalchemy.ext.declarative import synonym_for
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, object_session, synonym

from db import db


class Build(db.Model):
    __tablename__ = "build"

    id = Column(String, primary_key=True)
    build_num = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False)
    last_updated_at = Column(DateTime, nullable=False)
    service_id = Column(String, ForeignKey('service.id'), nullable=False)
    ver = Column(String, nullable=False)
    vcs_ref = Column(String, nullable=False)
    build_args = Column(String, nullable=True)

    service = relationship('Service', back_populates='builds')
    releases = relationship('Release', back_populates='build')

    @hybrid_property
    def git_tag(self):
        return self.vcs_ref

    @git_tag.expression
    def git_tag(cls):
        return cls.vcs_ref

    git_tag.__setattr__("property", "None")

    def __repr__(self):
        return self.id


@db.event.listens_for(Build, 'before_insert')
def my_before_insert_listener(mapper, connection, build):
    now = datetime.now()
    build.created_at = now
    build.last_updated_at = now
    __update_fields__(build)


@db.event.listens_for(Build, 'before_update')
def my_before_update_listener(mapper, connection, build):
    now = datetime.now()
    build.last_updated_at = now
    __update_fields__(build)


def __update_fields__(build):
    build.id = '%s:%s' % (build.service_id, build.build_num)
    build.ver = re.sub(r"[^0-9a-zA-Z.-]", '-', build.vcs_ref)
