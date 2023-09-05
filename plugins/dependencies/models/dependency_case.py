from sqlalchemy import Column, String, Enum, DateTime, func
from sqlalchemy.orm import relationship

from db import db

cardinality_types = ('OTO', 'OTM')
cardinality_types_enum = Enum(*cardinality_types, name='relationship_type')


class DependencyCase(db.Model):
    collection_name = 'dependency_case'
    __tablename__ = 'plugin_dependencies_dependency_case'
    exclude = ['created_at', 'last_updated_at']
    id = Column(String, primary_key=True)
    relatable_type = Column(String, nullable=False)
    related_type = Column(String, nullable=False)
    allowed_relationship = Column(cardinality_types_enum, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    last_updated_at = Column(DateTime, nullable=True, onupdate=func.now(), index=True)
    dependencies = relationship('Dependency', back_populates='dependency_case')

    def __repr__(self):
        return self.id
