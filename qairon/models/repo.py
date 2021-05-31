from sqlalchemy import *
from sqlalchemy.orm import relationship

from db import db


class Repo(db.Model):
    __tablename__ = "repo"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    repo_type_id = Column(String, ForeignKey('repo_type.id'))

    url = Column(String(253))
    defaults = Column(Text)

    type = relationship("RepoType", back_populates="repos")

    def __repr__(self):
        return self.id


@db.event.listens_for(Repo, 'before_update')
@db.event.listens_for(Repo, 'before_insert')
def my_before_insert_listener(mapper, connection, repo):
    __update_id__(repo)


def __update_id__(repo):
    repo.id = repo.repo_type_id + ':' + repo.name
