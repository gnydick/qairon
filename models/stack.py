from sqlalchemy import *
from sqlalchemy.orm import relationship

from db import db
import datetime


class Stack(db.Model):
    __tablename__ = "stack"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    application_id = Column(String, ForeignKey('application.id'), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    last_updated_at = Column(DateTime, nullable=True, onupdate=func.now())
    defaults = Column(Text)

    application = relationship('Application', back_populates='stacks')
    services = relationship("Service", back_populates="stack")

    def __repr__(self):
        return self.id


@db.event.listens_for(Stack, 'before_update')
@db.event.listens_for(Stack, 'before_insert')
def my_before_insert_listener(mapper, connection, stack):
    __update_id__(stack)


def __update_id__(stack):
    stack.id = stack.application_id + ':' + stack.name
