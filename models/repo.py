from sqlalchemy import *
from sqlalchemy.orm import relationship

from db import db


class Repo(db.Model):
    exclude = ['services', 'input_build_artifacts', 'output_build_artifacts', 'input_release_artifacts',
              'output_release_artifacts']

    __tablename__ = "repo"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    repo_type_id = Column(String, ForeignKey('repo_type.id', onupdate='CASCADE'), index=true)
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=true)
    last_updated_at = Column(DateTime, nullable=True, onupdate=func.now(), index=true)

    url = Column(String(253))
    defaults = Column(Text)

    type = relationship("RepoType", back_populates="repos")
    services = relationship("Service", secondary='services_repos', back_populates="repos", lazy='select')
    input_build_artifacts = relationship("BuildArtifact", back_populates="input_repo",
                                         foreign_keys="BuildArtifact.input_repo_id",
                                         primaryjoin='Repo.id==BuildArtifact.input_repo_id')
    output_build_artifacts = relationship("BuildArtifact", back_populates="output_repo",
                                          foreign_keys="BuildArtifact.output_repo_id",
                                          primaryjoin='Repo.id==BuildArtifact.output_repo_id')
    input_release_artifacts = relationship("ReleaseArtifact", back_populates="input_repo",
                                           foreign_keys="ReleaseArtifact.input_repo_id",
                                           primaryjoin='Repo.id==ReleaseArtifact.input_repo_id')
    output_release_artifacts = relationship("ReleaseArtifact", back_populates="output_repo",
                                            foreign_keys="ReleaseArtifact.output_repo_id",
                                            primaryjoin='Repo.id==ReleaseArtifact.output_repo_id')

    def __repr__(self):
        return self.id


@db.event.listens_for(Repo, 'before_update')
@db.event.listens_for(Repo, 'before_insert')
def my_before_insert_listener(mapper, connection, repo):
    __update_id__(repo)


def __update_id__(repo):
    repo.id = repo.repo_type_id + ':' + repo.name
