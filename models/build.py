import re
from datetime import datetime

from sqlalchemy import *
from sqlalchemy.ext.declarative import synonym_for
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, object_session, synonym

from db import db
import datetime


class Build(db.Model):
    exclude = ['releases', 'build_artifacts']

    __tablename__ = "build"

    id = Column(String, primary_key=True)
    build_num = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    last_updated_at = Column(DateTime, nullable=True, onupdate=func.now(), index=True)
    service_id = Column(String, ForeignKey('service.id'), nullable=False, index=True)
    ver = Column(String, nullable=False)
    vcs_ref = Column(String, nullable=False)
    defaults = Column(Text)
    service = relationship('Service', back_populates='builds')
    releases = relationship('Release', back_populates='build', lazy='select')

    build_artifacts = relationship('BuildArtifact', back_populates='build', lazy='select')

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
    __update_fields__(build)


@db.event.listens_for(Build, 'before_update')
def my_before_update_listener(mapper, connection, build):
    __update_fields__(build)


def __update_fields__(build):
    build.id = '%s:%s' % (build.service_id, build.build_num)
    build.ver = re.sub(r"[^0-9a-zA-Z.-]", '-', build.vcs_ref)
