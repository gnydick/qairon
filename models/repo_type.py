from sqlalchemy import *
from sqlalchemy.orm import relationship, validates

from db import db
import datetime


class RepoType(db.Model):
    __tablename__ = "repo_type"
    id = Column(String, primary_key=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=true)
    last_updated_at = Column(DateTime, nullable=True, onupdate=func.now(), index=true)
    defaults = Column(Text)

    repos = relationship("Repo", back_populates="type")

    def __repr__(self):
        return self.id

    @validates('id')
    def validate_name(self, key, value):
        assert value != ''
        return value
