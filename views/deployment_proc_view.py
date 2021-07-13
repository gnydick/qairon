from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.sqla.ajax import QueryAjaxModelLoader

from db import db
from models import *


class DeploymentProcView(ModelView):
    can_view_details = True
    # column_searchable_list = [Environment.id, Deployment.tag]
    # column_filters = [Environment.id]
    can_export = True

    # form_ajax_refs = {
    #     'proc': QueryAjaxModelLoader('proc', db.session, Proc, fields=['id'],
    #                                  filters=["service_id='cloudops:infra:qairon'"])
    # }
    edit_template = 'base_edit.html'
    create_template = 'base_create.html'
    list_template = 'base_list.html'
