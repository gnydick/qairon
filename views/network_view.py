from flask_admin.contrib.sqla import ModelView
from models import Partition, Network
from converters import NetworkModelConverter
from views.default_view import DefaultView


class NetworkView(DefaultView):
    model_form_converter = NetworkModelConverter
    can_view_details = True
    column_searchable_list = [Partition.id, Network.name]
    column_filters = [Partition.id]
    can_export = True
    # list_template = 'network_list.html'
    # column_editable_list = [Network.name, "cid, Network.defaults]
    edit_template = 'base_edit.html'
    create_template = 'base_create.html'
    list_template = 'base_list.html'
