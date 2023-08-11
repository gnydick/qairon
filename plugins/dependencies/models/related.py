from sqlalchemy import Column, ForeignKey, String, Enum, ForeignKeyConstraint, DateTime, func, true
from sqlalchemy.orm import relationship

from db import db


class Related(db.Model):
    __tablename__ = 'related'
    exclude = []
    id = Column(String,  primary_key=True)
    related_id = Column(String)
    type = Column(String)
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=true)
    last_updated_at = Column(DateTime, nullable=True, onupdate=func.now(), index=true)
    dependencies = relationship('Dependency', secondary='dependency_relateds', back_populates="relateds", lazy='select')
    __mapper_args__ = {
        'polymorphic_on': type,
    }

    def __repr__(self):
        return self.id
@db.event.listens_for(Related, 'before_update')
@db.event.listens_for(Related, 'before_insert')
def my_before_insert_listener(mapper, connection, related):
    __update_id__(related)


def __update_id__(related):
    related.id = related.type + ':' + related.related_id
