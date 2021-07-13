from sqlalchemy import *
from sqlalchemy.orm import relationship, validates

from db import db


class ConfigTemplate(db.Model):
    __tablename__ = "config_template"
    id = Column(String, primary_key=True)
    doc = Column(Text, nullable=False)
    language_id = Column(String, ForeignKey('language.id'))
    
    service_configs = relationship('ServiceConfig', back_populates='template')
    deployment_configs = relationship('DeploymentConfig', back_populates='template')
    language = relationship('Language', back_populates='config_templates')

    def __repr__(self):
        return self.id
