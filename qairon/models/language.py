from sqlalchemy import *
from sqlalchemy.orm import relationship, validates

from db import db


class Language(db.Model):
    __tablename__ = "language"
    id = Column(String, primary_key=True)

    config_templates = relationship("ConfigTemplate", back_populates="language")

    def __repr__(self):
        return self.id

    @validates('id')
    def validate_name(self, key, value):
        assert value != ''
        return value
