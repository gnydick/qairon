from flask_admin.contrib.sqla import ModelView
from wtforms import StringField

from views.default_view import DefaultView


class WithIdView(DefaultView):
    form_extra_fields = {
        'id': StringField('Id')
    }