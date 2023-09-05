from sqlalchemy import Column, ForeignKey, String, DateTime, func, UniqueConstraint
from sqlalchemy.orm import relationship, validates

from db import db


class Dependency(db.Model):
    collection_name = 'dependency'
    __tablename__ = 'plugin_dependencies_dependency'
    exclude = ['created_at', 'last_updated_at']
    id = Column(String, primary_key=True)
    dependency_case_id = Column(String,
                                ForeignKey('plugin_dependencies_dependency_case.id'))
    relatable_id = Column(String, ForeignKey('plugin_dependencies_relatable.id'), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    last_updated_at = Column(DateTime, nullable=True, onupdate=func.now(), index=True)
    name = Column(String, nullable=False)

    dependency_case = relationship('DependencyCase', back_populates='dependencies')
    relatable = relationship('Relatable', back_populates='dependencies')
    relateds = relationship('Related', back_populates='dependency')

    UniqueConstraint(dependency_case_id, relatable_id, name='UniqueDependency')

    def __repr__(self):
        return self.id

    @validates('relatable')
    def before_before_insert_listener(self, key, relatable):
        if self.dependency_case.relatable_type == relatable.relatable_type:
            return relatable

@db.event.listens_for(Dependency, 'before_update')
@db.event.listens_for(Dependency, 'before_insert')
def my_before_insert_listener(mapper, connection, dependency):
    __update_id__(dependency)


def __update_id__(dependency):
    dependency.id = ':'.join([dependency.dependency_case_id, dependency.relatable_id, dependency.name])
