from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from db import db


class Relatable(db.Model):
    __tablename__ = 'relatable'
    exclude = []
    id = Column(String, primary_key=True)
    relatable_id = Column(String, nullable=False)
    type = Column(String)

    dependency = relationship('Dependency', back_populates='relatable')

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
    relatable.id = relatable.type + ':' + relatable.relatable_id
