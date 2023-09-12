from sqlalchemy import Column, String, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship, validates

from db import db
from plugins.dependencies.models import Dependency


class Related(db.Model):
    collection_name = 'related'
    __tablename__ = 'plugin_dependencies_related'
    exclude = ['created_at', 'last_updated_at', 'dependency_case']
    id = Column(String, primary_key=True)
    dependency_id = Column(String, ForeignKey('plugin_dependencies_dependency.id'), nullable=False)
    object_id = Column(String, nullable=False)
    related_type = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    last_updated_at = Column(DateTime, nullable=True, onupdate=func.now(), index=True)

    dependency = relationship('Dependency', back_populates='relateds')
    dependency_case = relationship('DependencyCase', secondary='plugin_dependencies_dependency', viewonly=True,
                                   uselist=False)

    __mapper_args__ = {
        'polymorphic_on': related_type,
    }

    def __repr__(self):
        return self.id


@db.event.listens_for(Related, 'before_update')
@db.event.listens_for(Related, 'before_insert')
def my_before_insert_listener(mapper, connection, related):
    __update_id__(related)


def __update_id__(related):
    dep = db.session.query(Dependency).filter(Dependency.id==related.dependency_id).first()
    assert dep.dependency_case.related_type == related.related_type
    related.id = ':'.join([related.related_type, related.dependency_id, related.object_id])
