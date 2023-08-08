from sqlalchemy import Column, ForeignKey, String, Enum, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from app import db
from models import CardinalityEnum


class Dependency(db.Model):
    __tablename__ = 'dependency'

    id = Column(String, primary_key=True)
    dependency_case_id = Column(String,
                                ForeignKey('dependency_case.id', onupdate='CASCADE'))
    relatable_id = Column(String, ForeignKey('relatable.id'))

    dependency_case = relationship('DependencyCase', back_populates='dependencies')
    relatable = relationship('Relatable', back_populates='dependency')
    relateds = relationship('Related', secondary='dependency_relateds', back_populates="dependencies", lazy='select')

    def __repr__(self):
        return self.id

@db.event.listens_for(Dependency, 'before_update')
@db.event.listens_for(Dependency, 'before_insert')
def my_before_insert_listener(mapper, connection, dependency):
    __update_id__(dependency)


def __update_id__(dependency):
    dependency.id = dependency.dependency_case_id + dependency.relatable_id
