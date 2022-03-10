from sqlalchemy import *
from sqlalchemy.orm import relationship, validates

from db import db
import datetime


class ConfigTemplate(db.Model):
    __tablename__ = "config_template"
    id = Column(String, primary_key=True)
    language_id = Column(String, ForeignKey('language.id'))
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    last_updated_at = Column(DateTime, nullable=True, onupdate=func.now())
    doc = Column(Text, nullable=False)
    defaults = Column(Text)

    
    service_configs = relationship('ServiceConfig', back_populates='template')
    deployment_configs = relationship('DeploymentConfig', back_populates='template')
    language = relationship('Language', back_populates='config_templates')

    def __repr__(self):
        return self.id
