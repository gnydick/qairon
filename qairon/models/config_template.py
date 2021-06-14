from sqlalchemy import *
from sqlalchemy.orm import relationship, validates

from qairon.db import db


class ConfigTemplate(db.Model):
    __tablename__ = "config_template"
    id = Column(String, primary_key=True)
    version = Column(String, nullable=False)
    config_template_type_id = Column(String, ForeignKey('config_template_type.id'))
    doc = Column(Text, nullable=False)
    language_id = Column(String, ForeignKey('language.id'))
    
    config_template_type = relationship('ConfigTemplateType', back_populates='config_templates')
    service_configs = relationship('ServiceConfig', back_populates='template')
    deployment_configs = relationship('DeploymentConfig', back_populates='template')
    language = relationship('Language', back_populates='config_templates')

    def __repr__(self):
        return self.id

@validates('id')
def validate_name(self, key, value):
    assert value != ''
    return value


@db.event.listens_for(ConfigTemplate, 'before_update')
@db.event.listens_for(ConfigTemplate, 'before_insert')
def my_before_insert_listener(mapper, connection, config_template):
    __update_id__(config_template)


def __update_id__(config_template):
    config_template.id = config_template.config_template_type_id + ':' + config_template.version
