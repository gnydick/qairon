from flask_admin.contrib.sqla import ModelView
from models import Environment, Deployment
from views.default_view import DefaultView


class DeploymentView(DefaultView):
    can_view_details = True
    column_searchable_list = [Environment.id, Deployment.tag]
    column_filters = [Environment.id]
    can_export = True
    edit_template = 'base_edit.html'
    create_template = 'base_create.html'
    list_template = 'base_list.html'
