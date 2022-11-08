from flask_admin.contrib.sqla import ModelView


class QaironModelView(ModelView):
    form_excluded_columns = ['created_at', 'last_updated_at']
