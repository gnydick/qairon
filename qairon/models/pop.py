from sqlalchemy import *
from sqlalchemy.orm import relationship, validates

from db import db


class Pop(db.Model):
    __tablename__ = "pop"
    id = Column(String, primary_key=True)
    pop_type_id = Column(String, ForeignKey('pop_type.id'), nullable=False)
    native = Column(Text)
    defaults = Column(Text)

    type = relationship("PopType", back_populates="pops")
    regions = relationship("Region", back_populates="pop")

    def __repr__(self):
        return self.id

    @validates('id')
    def validate_name(self, key, value):
        assert value != ''
        return value


@db.event.listens_for(Pop, 'before_update')
@db.event.listens_for(Pop, 'before_insert')
def my_before_insert_listener(mapper, connection, pop):
    __update_id__(pop)


def __update_id__(pop):
    pop.id = pop.pop_type_id + ':' + pop.native