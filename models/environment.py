from sqlalchemy import *
from sqlalchemy.orm import relationship

from db import db
import datetime


class Environment(db.Model):
    __tablename__ = "environment"
    id = Column(String, primary_key=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=true)
    last_updated_at = Column(DateTime, nullable=True, onupdate=func.now(), index=true)
    defaults = Column(Text)
    providers = relationship("Provider", back_populates="environment", lazy='selectin')

    def __repr__(self):
        return self.id
