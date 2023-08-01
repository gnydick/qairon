from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from db import db


class Relatable(db.Model):
    __tablename__ = 'relatable'
    __table_args__ = {'schema': 'dependencies'}
    id = Column(String, primary_key=True)
    discriminator = Column(String)
    __mapper_args__ = {
        'polymorphic_on': discriminator,
    }
    # add other common attributes here
    related = relationship('Related', backref='relatable')


class Related(db.Model):
    __tablename__ = 'related'
    __table_args__ = {'schema': 'dependencies'}
    id = Column(String, primary_key=True)
    discriminator = Column(String)
    __mapper_args__ = {
        'polymorphic_on': discriminator,
    }
    # add other common attributes here
    relatable_id = Column(String, ForeignKey('dependencies.relatable.id'))
