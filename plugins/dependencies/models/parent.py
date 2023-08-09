from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship

from db import db



class Parent(db.Model):
    __tablename__ = 'parent'
    exclude = []
    id = Column(String, primary_key=True)
    children = relationship('Child', back_populates='parent')


    def __repr__(self):
        return self.id
