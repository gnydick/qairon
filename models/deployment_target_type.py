from sqlalchemy import *
from sqlalchemy.orm import relationship, validates

from db import db
from mixins.models import TenantMixin
import datetime


class DeploymentTargetType(db.Model,TenantMixin):
    exclude = ['targets']

    __tablename__ = "deployment_target_type"

    id = Column(String, primary_key=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    last_updated_at = Column(DateTime, nullable=True, onupdate=func.now(), index=True)
    defaults = Column(Text)

    targets = relationship("DeploymentTarget", back_populates="type", lazy='select')

    def __repr__(self):
        return self.id

    @validates('id')
    def validate_name(self, key, value):
        assert value != ''
        return value
