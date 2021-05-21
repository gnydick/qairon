from sqlalchemy import *
from sqlalchemy.orm import relationship, validates

from db import db


class DeploymentTargetType(db.Model):
    __tablename__ = "deployment_target_type"
    id = Column(String, primary_key=True)
    defaults = Column(Text)

    targets = relationship("DeploymentTarget", back_populates="type")

    def __repr__(self):
        return self.id

    @validates('id')
    def validate_name(self, key, value):
        assert value != ''
        return value
