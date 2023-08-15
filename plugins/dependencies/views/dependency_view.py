from plugins.dependencies.models import Dependency
from views import DefaultView


@property
def column_exclude_list(self):
    c = getattr(self.model, 'exclude')
    return c


class DependencyView(DefaultView):
    model = Dependency
    can_view_details = True
    form_excluded_columns = column_exclude_list
    column_searchable_list = ['id']
    column_sortable_list = ['id']
    list_display_pk = True
    column_display_pk = True
    can_export = True
    edit_template = 'base_edit.html'
    create_template = 'base_create.html'
    list_template = 'base_list.html'
