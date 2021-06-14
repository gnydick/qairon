from sqlalchemy import *
from sqlalchemy.orm import relationship, validates

from qairon.db import db


class ConfigTemplateType(db.Model):
    __tablename__ = "config_template_type"
    id = Column(String, primary_key=True)
    defaults = Column(Text)

    config_templates = relationship("ConfigTemplate", back_populates="config_template_type")

    def __repr__(self):
        return self.id

    @validates('id')
    def validate_name(self, key, value):
        assert value != ''
        return value


