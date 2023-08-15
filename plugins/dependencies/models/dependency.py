from sqlalchemy import Column, ForeignKey, String, Enum, ForeignKeyConstraint, DateTime, func, true
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from db import db



class Dependency(db.Model):
    __tablename__ = 'dependency'
    exclude = []
    id = Column(String, primary_key=True)
    dependency_case_id = Column(String,
                                ForeignKey('dependency_case.id', onupdate='CASCADE'))
    relatable_id = Column(String, ForeignKey('relatable.id'))
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=true)
    last_updated_at = Column(DateTime, nullable=True, onupdate=func.now(), index=true)
    name = Column(String, nullable=False)

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
    dependency.id = ':'.join([dependency.dependency_case_id, dependency.relatable_id, dependency.name])
