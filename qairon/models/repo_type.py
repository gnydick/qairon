from sqlalchemy import *
from sqlalchemy.orm import relationship, validates

from qairon.db import db


class RepoType(db.Model):
    __tablename__ = "repo_type"
    id = Column(String, primary_key=True)
    defaults = Column(Text)

    repos = relationship("Repo", back_populates="type")

    def __repr__(self):
        return self.id

    @validates('id')
    def validate_name(self, key, value):
        assert value != ''
        return value
