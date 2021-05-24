from sqlalchemy import *
from sqlalchemy.orm import relationship, validates

from db import db


class PopType(db.Model):
    __tablename__ = "pop_type"
    id = Column(String, primary_key=True)
    defaults = Column(Text)

    pops = relationship("Pop", back_populates="type")
    fleet_types = relationship("FleetType", back_populates="pop_type")

    def __repr__(self):
        return self.id

    @validates('id')
    def validate_name(self, key, value):
        assert value != ''
        return value
