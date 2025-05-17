from sqlalchemy import *
from sqlalchemy.orm import relationship, validates

from db import db
from mixins.models import TenantMixin
import datetime


class AllocationType(db.Model,TenantMixin):
    exclude = ['allocations', 'capacities', 'tenant_id']


    __tablename__ = "allocation_type"

    id = Column(String, primary_key=True)
    unit = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    last_updated_at = Column(DateTime, nullable=True, onupdate=func.now(), index=True)
    defaults = Column(Text)

    allocations = relationship("Allocation", back_populates="type", lazy='select')
    capacities = relationship("Capacity", back_populates="type", lazy='select')

    def __repr__(self):
        return self.id

    @validates('id')
    def validate_name(self, key, value):
        assert value != ''
        return value
