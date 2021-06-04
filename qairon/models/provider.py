from sqlalchemy import *
from sqlalchemy.orm import relationship, validates

from db import db


class Provider(db.Model):
    __tablename__ = "provider"
    id = Column(String, primary_key=True)
    provider_type_id = Column(String, ForeignKey('provider_type.id'), nullable=False)
    name = Column(String, nullable=False)
    native = Column(Text)
    defaults = Column(Text)

    type = relationship("ProviderType", back_populates="providers")
    regions = relationship("Region", back_populates="provider")

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
    provider.id = provider.provider_type_id + ':' + provider.native