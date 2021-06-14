from flask_admin.contrib.sqla import ModelView
from wtforms import StringField

from qairon.models import Deployment


class DeploymentTargetView(ModelView):
    # edit_template = 'config_edit.html'
    # create_template = 'config_create.html'
    # column_list = ['id', 'name', 'type']
    column_searchable_list = [Deployment.id]
    column_sortable_list = ['id']
    can_view_details = True
    can_export = True
    # form_excluded_columns = ['id'] #, 'type']
    column_exclude_list = ['defaults']
    edit_template = 'base_edit.html'
    create_template = 'base_create.html'
    list_template = 'base_list.html'