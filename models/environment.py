from sqlalchemy import *
from sqlalchemy.orm import relationship

from db import db


class Environment(db.Model):
    __tablename__ = "environment"
    id = Column(String, primary_key=True)
    defaults = Column(Text)
    providers = relationship("Provider", back_populates="environment")

    def __repr__(self):
        return self.id
