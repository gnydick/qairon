from qairon.models import Service, Stack

from qairon.views import DefaultView


class ServiceView(DefaultView):
    column_searchable_list = [Service.id]
    column_filters = [Service.id, Stack.id, ]
    column_sortable_list = ['name', 'stack']
    can_export = True
    column_exclude_list = ['id']
    edit_template = 'base_edit.html'
    create_template = 'base_create.html'
    list_template = 'base_list.html'