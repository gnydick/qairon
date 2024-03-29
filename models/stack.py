from sqlalchemy import *
from sqlalchemy.orm import relationship

from db import db
import datetime


class Stack(db.Model):
    exclude = ['services', 'configs']


    __tablename__ = "stack"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False, index=True)
    application_id = Column(String, ForeignKey('application.id'), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    last_updated_at = Column(DateTime, nullable=True, onupdate=func.now(), index=True)
    defaults = Column(Text)

    application = relationship('Application', back_populates='stacks')
    configs = relationship("StackConfig", back_populates="stack", lazy='select')
    services = relationship("Service", back_populates="stack", lazy='select')

    def __repr__(self):
        return self.id


@db.event.listens_for(Stack, 'before_update')
@db.event.listens_for(Stack, 'before_insert')
def my_before_insert_listener(mapper, connection, stack):
    __update_id__(stack)


def __update_id__(stack):
    stack.id = stack.application_id + ':' + stack.name
