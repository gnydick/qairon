from sqlalchemy import *
from sqlalchemy.orm import relationship, validates

from db import db
import datetime


class ProviderType(db.Model):
    exclude = ['providers', 'fleet_types']

    __tablename__ = "provider_type"
    id = Column(String, primary_key=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    last_updated_at = Column(DateTime, nullable=True, onupdate=func.now(), index=True)
    defaults = Column(Text)

    providers = relationship("Provider", back_populates="type", lazy='select')
    fleet_types = relationship("FleetType", back_populates="provider_type", lazy='select')

    def __repr__(self):
        return self.id

    @validates('id')
    def validate_name(self, key, value):
        assert value != ''
        return value
