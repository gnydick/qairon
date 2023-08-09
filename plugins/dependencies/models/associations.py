from sqlalchemy import Table, Column, String, ForeignKey

from db import db

dependency_to_relateds = Table('dependency_relateds', db.metadata,
                               Column('dependency_id', String,
                                      ForeignKey('dependency.id', onupdate='CASCADE')),
                               Column('related_id', String,
                                      ForeignKey('related.id', onupdate='CASCADE')))
