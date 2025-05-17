from views.tenant_model import TenantModelView


@property
def floof(self):
    c = getattr(self.model, 'exclude')
    return c


class DefaultView(TenantModelView):
    can_view_details = True
    form_excluded_columns = floof
    column_exclude_list = floof
    column_details_exclude_list = floof
    column_searchable_list = ['id']
    column_sortable_list = ['id']
    list_display_pk = True
    column_display_pk = True
    can_export = True
    edit_template = 'base_edit.html'
    create_template = 'base_create.html'
    list_template = 'base_list.html'
