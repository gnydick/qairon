from sqlalchemy import *
from sqlalchemy.orm import relationship, validates

from db import db
from mixins.models import TenantMixin
import datetime


class ConfigTemplate(db.Model,TenantMixin):
    exclude = ['service_configs', 'stack_configs', 'deployment_configs']

    __tablename__ = "config_template"

    id = Column(String, primary_key=True)
    language_id = Column(String, ForeignKey('language.id'), index=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    last_updated_at = Column(DateTime, nullable=True, onupdate=func.now(), index=True)
    doc = Column(Text, nullable=False)
    defaults = Column(Text)

    service_configs = relationship('ServiceConfig', back_populates='template', lazy='select')
    stack_configs = relationship('StackConfig', back_populates='template', lazy='select')
    deployment_configs = relationship('DeploymentConfig', back_populates='template', lazy='select')
    language = relationship('Language', back_populates='config_templates')

    def __repr__(self):
        return self.id
