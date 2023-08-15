from sqlalchemy import Column, String, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship, validates

from db import db


class Related(db.Model):
    __tablename__ = 'related'
    exclude = ['created_at', 'last_updated_at', 'dependency_case']
    id = Column(String, primary_key=True)
    dependency_id = Column(String, ForeignKey('dependency.id'), nullable=False)
    object_id = Column(String, nullable=False)
    type = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    last_updated_at = Column(DateTime, nullable=True, onupdate=func.now(), index=True)

    dependency = relationship('Dependency', back_populates='relateds')
    dependency_case = relationship('DependencyCase', secondary='dependency', viewonly=True, uselist=False)

    __mapper_args__ = {
        'polymorphic_on': type,
    }

    def __repr__(self):
        return self.id

    @validates('type')
    def before_before_insert_listener(self, key, value):
        if self.dependency_case.related_type == value:
            return value
        else:
            raise Exception


@db.event.listens_for(Related, 'before_update')
@db.event.listens_for(Related, 'before_insert')
def my_before_insert_listener(mapper, connection, related):
    __update_id__(related)


def __update_id__(related):
    related.id = ':'.join([related.type, related.dependency.id, related.object_id])
