from sqlalchemy import *
from sqlalchemy.orm import relationship

from db import db
import datetime


class ServiceOwner(db.Model):
    __tablename__ = "service_owner"

    id = Column(String, primary_key=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=true)
    last_updated_at = Column(DateTime, nullable=True, onupdate=func.now(), index=true)
    name = Column(String, nullable=False, index=true)
    defaults = Column(Text)

    services = relationship("Service", secondary='services_owners', back_populates="owners")

    def __repr__(self):
        return self.id


@db.event.listens_for(ServiceOwner, 'before_update')
@db.event.listens_for(ServiceOwner, 'before_insert')
def my_before_insert_listener(mapper, connection, service_owner):
    __update_id__(service_owner)


def __update_id__(service_owner):
    service_owner.id =
