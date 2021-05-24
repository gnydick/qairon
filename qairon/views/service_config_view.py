from flask_admin.contrib.sqla import ModelView
from models import Service




class ServiceConfigView(ModelView):
    # edit_template = 'service_config_edit.html'
    # create_template = 'service_config_create.html'
    column_searchable_list = [Service.id]
    can_view_details = True
    can_export = True
    form_excluded_columns = ['id']

    edit_template = 'base_edit.html'
    create_template = 'base_create.html'
    list_template = 'base_list.html'