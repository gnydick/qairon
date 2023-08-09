from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship

from db import db


class Child(db.Model):
    __tablename__ = 'child'
    exclude = []
    id = Column(String, primary_key=True)
    parent_id = Column(String, ForeignKey('parent.id'))
    name = Column(String, nullable=False)

    parent = relationship('Parent', back_populates='children')

    def __repr__(self):
        return self.id

@db.event.listens_for(Child, 'before_update')
@db.event.listens_for(Child, 'before_insert')
def my_before_insert_listener(mapper, connection, child):
    __update_id__(child)


def __update_id__(child):
    child.id = child.parent_id + ':' + child.name
