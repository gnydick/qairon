from flask_admin.contrib.sqla import ModelView
from wtforms import StringField

from views.default_view import DefaultView


class WithIdView(DefaultView):
    column_exclude_list = ['tenant_id']
    form_extra_fields = {
        'id': StringField('Id')
    }