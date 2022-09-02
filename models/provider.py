from sqlalchemy import *
from sqlalchemy.orm import relationship, validates

from db import db
import datetime


class Provider(db.Model):
    __tablename__ = "provider"
    id = Column(String, primary_key=True)
    provider_type_id = Column(String, ForeignKey('provider_type.id'), nullable=False, index=true)
    environment_id = Column(String, ForeignKey('environment.id'), nullable=False, index=true)
    native_id = Column(String, index=true)
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=true)
    last_updated_at = Column(DateTime, nullable=True, onupdate=func.now(), index=true)
    defaults = Column(Text)

    environment = relationship("Environment", back_populates="providers")
    type = relationship("ProviderType", back_populates="providers")
    regions = relationship("Region", back_populates="provider", lazy='selectin')

    def __repr__(self):
        return self.id

    @validates('id')
    def validate_name(self, key, value):
        assert value != ''
        return value


@db.event.listens_for(Provider, 'before_update')
@db.event.listens_for(Provider, 'before_insert')
def my_before_insert_listener(mapper, connection, provider):
    __update_id__(provider)


def __update_id__(provider):
    provider.id = provider.environment_id + ':' + provider.provider_type_id + ':' + provider.native_id
