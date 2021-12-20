from sqlalchemy import *
from sqlalchemy.ext.declarative import AbstractConcreteBase

from sqlalchemy.orm import relationship

from db import db


class BuildArtifact(db.Model):
    __tablename__ = "build_artifact"
    id = Column(String, primary_key=True)

    build_id = Column(String, ForeignKey('build.id'), nullable=False)
    input_repo_id = Column(String, ForeignKey('repo.id'), nullable=False)
    output_repo_id = Column(String, ForeignKey('repo.id'), nullable=False)
    name = Column(String, nullable=False)
    upload_path = Column(String, nullable=False)
    data = Column(Text)

    build = relationship('Build', back_populates='build_artifacts')
    input_repo = relationship("Repo", back_populates="input_build_artifacts", foreign_keys=[input_repo_id])
    output_repo = relationship("Repo", back_populates="output_build_artifacts", foreign_keys=[output_repo_id])

    def __repr__(self):
        return self.build.id + ':' + self.name


class ReleaseArtifact(db.Model):
    __tablename__ = "release_artifact"
    id = Column(String, primary_key=True)
    release_id = Column(String, ForeignKey('release.id'), nullable=False)
    input_repo_id = Column(String, ForeignKey('repo.id'), nullable=False)
    output_repo_id = Column(String, ForeignKey('repo.id'), nullable=False)
    name = Column(String, nullable=False)
    upload_path = Column(String, nullable=False)
    data = Column(Text)

    input_repo = relationship("Repo", back_populates="input_release_artifacts", foreign_keys=[input_repo_id])
    output_repo = relationship("Repo", back_populates="output_release_artifacts", foreign_keys=[output_repo_id])
    release = relationship('Release', back_populates='release_artifacts')

    def __repr__(self):
        return self.release.id + ':' + self.name


@db.event.listens_for(BuildArtifact, 'before_update')
@db.event.listens_for(BuildArtifact, 'before_insert')
def my_before_insert_listener(mapper, connection, artifact):
    __update_artifact_id__(artifact)


def __update_artifact_id__(artifact):
    artifact.id = artifact.build_id + ':' + artifact.name


@db.event.listens_for(ReleaseArtifact, 'before_update')
@db.event.listens_for(ReleaseArtifact, 'before_insert')
def my_before_insert_listener_release(mapper, connection, artifact):
    __update_release_artifact_id__(artifact)


def __update_release_artifact_id__(artifact):
    artifact.id = artifact.release_id + ':' + artifact.name
