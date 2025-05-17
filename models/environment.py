from sqlalchemy import *
from sqlalchemy.orm import relationship

from db import db
from mixins.models import TenantMixin
import datetime


class Environment(db.Model,TenantMixin):
    exclude = ['providers']

    __tablename__ = "environment"

    id = Column(String, primary_key=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    last_updated_at = Column(DateTime, nullable=True, onupdate=func.now(), index=True)
    defaults = Column(Text)
    providers = relationship("Provider", back_populates="environment", lazy='select')

    def __repr__(self):
        return self.id
