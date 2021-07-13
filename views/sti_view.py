from flask_admin.contrib.sqla import ModelView
from wtforms import StringField


class StiView(ModelView):
    column_display_pk = True
    # column_searchable_list = ['id']
    # column_sortable_list = ['id']
    can_view_details = True
    can_export = True

    # form_extra_fields = {
    #     'id': StringField('Id')
    # }
    edit_template = 'base_edit.html'
    create_template = 'base_create.html'
    list_template = 'base_list.html'