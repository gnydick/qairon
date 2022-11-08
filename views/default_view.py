from flask_admin.contrib.sqla import ModelView

from views.QaironModelView import QaironModelView


class DefaultView(QaironModelView):
    can_view_details = True
    form_excluded_columns = ['created_at', 'last_updated_at']
    column_searchable_list = ['id']
    column_sortable_list = ['id']
    list_display_pk = True
    column_display_pk = True
    can_export = True
    edit_template = 'base_edit.html'
    create_template = 'base_create.html'
    list_template = 'base_list.html'