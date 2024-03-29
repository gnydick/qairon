from sqlalchemy import *
from sqlalchemy.orm import relationship, validates

from db import db
import datetime


class Language(db.Model):
    exclude = ['config_templates']

    __tablename__ = "language"
    id = Column(String, primary_key=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    last_updated_at = Column(DateTime, nullable=True, onupdate=func.now(), index=True)
    config_templates = relationship("ConfigTemplate", back_populates="language", lazy='select')
    defaults = Column(Text)

    def __repr__(self):
        return self.id

    @validates('id')
    def validate_name(self, key, value):
        assert value != ''
        return value
