from sqlalchemy import *
from sqlalchemy.orm import relationship, validates

from db import db
import datetime


class ConfigTemplate(db.Model):
    __tablename__ = "config_template"
    id = Column(String, primary_key=True)
    language_id = Column(String, ForeignKey('language.id'), index=true)
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=true)
    last_updated_at = Column(DateTime, nullable=True, onupdate=func.now(), index=true)
    doc = Column(Text, nullable=False)
    defaults = Column(Text)

    
    service_configs = relationship('ServiceConfig', back_populates='template', lazy='joined')
    deployment_configs = relationship('DeploymentConfig', back_populates='template', lazy='joined')
    language = relationship('Language', back_populates='config_templates')

    def __repr__(self):
        return self.id
