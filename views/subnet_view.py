from flask_admin.contrib.sqla import ModelView
from models import Network, Subnet
from converters import NetworkModelConverter


class SubnetView(ModelView):
    model_form_converter = NetworkModelConverter
    can_view_details = True
    column_searchable_list = [Subnet.name, Network.name]
    column_sortable_list = []
    column_filters = [Subnet.name, Network.name]
    can_export = True
    # column_editable_list = [Network.name, "cid, Network.defaults]
    edit_template = 'base_edit.html'
    create_template = 'base_create.html'
    list_template = 'base_list.html'
