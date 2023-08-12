from sqlalchemy import Column, ForeignKey, String, Enum, ForeignKeyConstraint, DateTime, func, true
from sqlalchemy.orm import relationship


from db import db

cardinality_types = ('OTO', 'OTM')
cardinality_types_enum = Enum(*cardinality_types, name='relationship_type')

class DependencyCase(db.Model):
    __tablename__ = 'dependency_case'
    exclude = []
    id = Column(String, primary_key=True)
    allowed_related_type = Column(String, nullable=False)
    allowed_relationship = Column(cardinality_types_enum, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=true)
    last_updated_at = Column(DateTime, nullable=True, onupdate=func.now(), index=true)
    dependencies = relationship('Dependency', back_populates='dependency_case')

    def __repr__(self):
        return self.id
