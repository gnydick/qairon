from sqlalchemy import Column, String
from sqlalchemy import DateTime, func
from sqlalchemy.orm import relationship

from db import db


class Relatable(db.Model):
    __tablename__ = 'relatable'
    exclude = ['created_at', 'last_updated_at']
    id = Column(String, primary_key=True)
    object_id = Column(String, nullable=False)
    type = Column(String)

    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    last_updated_at = Column(DateTime, nullable=True, onupdate=func.now(), index=True)
    dependencies = relationship('Dependency', back_populates='relatable')

    __mapper_args__ = {
        'polymorphic_on': type,
    }

    def __repr__(self):
        return self.id


@db.event.listens_for(Relatable, 'before_update')
@db.event.listens_for(Relatable, 'before_insert')
def my_before_insert_listener(mapper, connection, relatable):
    __update_id__(relatable)


def __update_id__(relatable):
    relatable.id = relatable.type + ':' + relatable.object_id
