from flask import g
from flask_admin.contrib.sqla import ModelView
from sqlalchemy import func


class TenantModelView(ModelView):

    def get_query(self):
        # the normal list query, filtered to the current tenant
        return super().get_query().filter(self.model.tenant_id == g.tenant_id)

    def get_count_query(self):
        # a count(*) query against your model, with the same tenant filter
        return (
            self.session.query(func.count("*"))
            .select_from(self.model)
            .filter(self.model.tenant_id == g.tenant_id)
        )
