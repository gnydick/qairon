from abc import ABC

from flask_admin.contrib.sqla.form import AdminModelConverter
from flask_admin.model.form import converts
from wtforms import fields


class NetworkModelConverter(AdminModelConverter):

    def __init__(self, session, view):
        super(AdminModelConverter, self).__init__()

        self.session = session
        self.view = view

    @converts("sqlalchemy.dialects.postgresql.base.CIDR")
    def conv_PGCidr(self, field_args, **extra):
        return fields.StringField(**field_args)
