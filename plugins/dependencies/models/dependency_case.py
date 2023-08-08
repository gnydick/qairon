from sqlalchemy import Column, ForeignKey, String, Enum, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from app import db
from models import CardinalityEnum






class DependencyCase(db.Model):
    __tablename__ = 'dependency_case'

    id = Column(String, primary_key=True)
    allowed_related_type = Column(String)
    allowed_relationship = db.Column(CardinalityEnum.cardinality_types_enum)
    dependencies = relationship('Dependency', back_populates='dependency_case')

    def __repr__(self):
        return self.id
