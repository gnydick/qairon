from flask_admin.contrib.sqla import ModelView
from wtforms import StringField

from views.QaironModelView import QaironModelView


class WithIdView(QaironModelView):
    can_view_details = True
    column_searchable_list = ['id']
    column_sortable_list = ['id']
    list_display_pk = True
    column_display_pk = True
    can_export = True
    edit_template = 'base_edit.html'
    create_template = 'base_create.html'
    list_template = 'base_list.html'

    form_extra_fields = {
        'id': StringField('Id')
    }
