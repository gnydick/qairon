from sqlalchemy import Column, ForeignKey, String, Enum, ForeignKeyConstraint
from sqlalchemy.orm import relationship


from db import db

cardinality_types = ('OTO', 'OTM')
cardinality_types_enum = Enum(*cardinality_types, name='relationship_type')

class DependencyCase(db.Model):
    __tablename__ = 'dependency_case'
    exclude = []
    id = Column(String, primary_key=True)
    allowed_related_type = Column(String)
    allowed_relationship = db.Column(cardinality_types_enum)
    dependencies = relationship('Dependency', back_populates='dependency_case')

    def __repr__(self):
        return self.id
