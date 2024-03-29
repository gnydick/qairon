from flask_admin.contrib.sqla import ModelView
from wtforms import StringField

from views.default_view import DefaultView


class AllocationView(DefaultView):
    column_display_pk = True
    can_view_details = True
    can_export = True
    column_exclude_list = ['type']
    edit_template = 'base_edit.html'
    create_template = 'base_create.html'
    list_template = 'base_list.html'
