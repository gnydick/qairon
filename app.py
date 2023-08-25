import importlib
import inspect
from os.path import exists

import json_api_doc
from flask_admin import Admin
from flask_migrate import Migrate, Config
from flask_restless import APIManager

import models
from base import app
from controllers import RestController
from db import db
from lib import dynamic
from models import *
from serializers.default import QcliSerializer
from views import *

app.url_map.strict_slashes = False

version = 'development'
version_file = ".version"
if exists(version_file):
    with open(version_file) as file:
        version = file.readline().strip()

print(("version: %s" % version))

if app.debug:
    from werkzeug.debug import DebuggedApplication

    app.wsgi_app = DebuggedApplication(app.wsgi_app, evalex=True)

## server plugins

plugins_installed = dynamic.discover_namespace('plugins')
migrate = Migrate(app, db)
restmanager = APIManager(app, session=db.session)
qclimanager = APIManager(app, session=db.session)

with app.app_context():
    def postprocessor(result, **kwargs):
        result = result['data']


    model_classes = []
    plugin_models = []
    for module in dynamic.plugin_has_module('models'):
        model_module = importlib.import_module('plugins.%s.%s' % (module, 'models'))
        plugin_models = [member for name, member in inspect.getmembers(model_module, inspect.isclass)]

    for m in inspect.getmembers(models, inspect.isclass):
        if m[1].__module__.startswith('models.'):
            model_classes.append(getattr(models, m[0]))

    for m in plugin_models:
        model_classes.append(m)

    for model_class in model_classes:
        custom_serializer = QcliSerializer(model_class, str(model_class), qclimanager, primary_key='id')
        restmanager.create_api(model_class, primary_key='id', methods=['GET', 'POST', 'DELETE', 'PATCH'],
                               url_prefix='/api/rest/v1', page_size=5, max_page_size=100,
                               allow_client_generated_ids=True, allow_to_many_replacement=True,
                               exclude=getattr(model_class, 'exclude'))
        qclimanager.create_api(model_class, primary_key='id', methods=['GET', 'POST', 'DELETE', 'PATCH'],
                               url_prefix='/api/qcli/v1', page_size=5, max_page_size=100,
                               allow_client_generated_ids=True, allow_to_many_replacement=True,
                               exclude=getattr(model_class, 'exclude'), serializer=custom_serializer)

    # set optional bootswatch theme
    admin = Admin(app, name='QAIRON: %s' % version, template_mode='bootstrap3', base_template='admin/master.html')
    categories = {
        'Global': {},
        'Platform': {},
        'Partition': {
            'Networking': {},
        },
        'Resources': {},
        'Software': {
            'Services': {},
            'Stacks': {}
        },
        'CI/CD': {},
        'Deploy': {},
        'Templates': {},
        'Types': {},
        'Plugins': {}
    }


    def add_sub_category(children, parent):
        for k, v in children.items():
            admin.add_sub_category(k, parent)
            add_sub_category(v, k)


    plugins_with_views = dynamic.plugin_has_module('views')

    for plugin in plugins_with_views:
        categories['Plugins'][plugin.capitalize()] = {}

    for parent, children in categories.items():
        admin.add_category(parent)
        for k, v in children.items():
            admin.add_sub_category(k, parent)
            add_sub_category(v, k)
    for plugin in plugins_with_views:
        categories['Plugins'][plugin.capitalize()] = {}
        view_module = importlib.import_module('plugins.%s.%s' % (plugin, 'views'))
        plugin_views = [member for name, member in inspect.getmembers(view_module, inspect.isclass)]
        for plugin_view in plugin_views:
            admin.add_view(plugin_view(plugin_view.model, db.session, category=plugin.capitalize()))

    admin.add_view(WithIdView(Environment, db.session, category='Global'))
    admin.add_view(WithIdView(Application, db.session, category='Software', name='Applications'))
    admin.add_view(DefaultView(Stack, db.session, category='Stacks'))
    admin.add_view(DefaultView(StackConfig, db.session, category='Stacks'))
    admin.add_view(ServiceView(Service, db.session, category='Services'))
    admin.add_view(DefaultView(ServiceConfig, db.session, category='Services'))

    admin.add_view(DefaultView(Build, db.session, category='CI/CD'))
    admin.add_view(DefaultView(BuildArtifact, db.session, category='CI/CD'))
    admin.add_view(DefaultView(Release, db.session, category='CI/CD'))
    admin.add_view(DefaultView(ReleaseArtifact, db.session, category='CI/CD'))

    admin.add_view(WithIdView(ProviderType, db.session, category='Types'
                                                                 ''))
    admin.add_view(DefaultView(Provider, db.session, category='Platform'))
    admin.add_view(DefaultView(Region, db.session, category='Platform'))
    admin.add_view(DefaultView(Zone, db.session, category='Platform'))

    admin.add_view(WithIdView(DeploymentTargetType, db.session, category='Types'))
    admin.add_view(DefaultView(DeploymentTarget, db.session, category='Deploy'))
    admin.add_view(DefaultView(DeploymentTargetBin, db.session, category='Deploy'))

    admin.add_view(DefaultView(FleetType, db.session, category='Types'))
    admin.add_view(DefaultView(Fleet, db.session, category='Resources'))

    admin.add_view(DefaultView(Deployment, db.session, category='Deploy'))
    admin.add_view(DefaultView(DeploymentConfig, db.session, category='Deploy'))

    admin.add_view(DefaultView(DeploymentProc, db.session, category='Deploy'))

    admin.add_view(WithIdView(ConfigTemplate, db.session, category='Templating'))
    admin.add_view(WithIdView(Language, db.session, category='Templating'))

    admin.add_view(DefaultView(Proc, db.session, category='Software'))

    admin.add_view(DefaultView(Partition, db.session, category='Partition'))
    admin.add_view(NetworkView(Network, db.session, category='Networking', name='VPC CIDR'))
    admin.add_view(SubnetView(Subnet, db.session, category='Networking'))

    admin.add_view(WithIdView(AllocationType, db.session, category='Types'))
    admin.add_view(DefaultView(Allocation, db.session, category='Resources'))
    admin.add_view(DefaultView(Capacity, db.session, category='Resources'))

    admin.add_view(WithIdView(RepoType, db.session, category='Types'))
    admin.add_view(DefaultView(Repo, db.session, category='CI/CD'))

from flask import Response

from models import Deployment, Environment, Provider, Region

rest = RestController()


@app.after_request
def after_request(response):
    response.headers["qairon-version"] = version
    return response


@app.route('/up')
def health():
    return "hello"


@app.route('/api/rest/v1/deployment/<deployment_id>/json', methods=['GET'])
def get_deployment_json(deployment_id):
    from db import db
    s = db.session
    tfs = s.query(Deployment).filter(Deployment.id == deployment_id).all()
    return json_api_doc.serialize(tfs)


@app.route('/api/tf/v1/deployment/gen/<dep_id>')
@app.route('/api/tf/v1/deployment/gen/<dep_id>/<config_tag>')
def gen_config(dep_id, config_tag=None):
    from db import db
    s = db.session
    config_tag = 'default' if config_tag is None else config_tag
    tfs = s.query(Config).filter(Config.deployment_id == dep_id, Config.config_type_id == 'tf',
                                 Config.tag == config_tag).all()
    tf_files = list(map(lambda x: x.name, tfs))

    result = ''

    for file in tf_files:
        res = _gen_tf(dep_id, 'tf', file, config_tag)
        result += res + '\n'
    return Response(result, mimetype='text/plain')


@app.route('/api/tf/v1/deployment/gen/<dep_id>/<config_type>/<name>')
@app.route('/api/tf/v1/deployment/gen/<dep_id>/<config_type>/<name>/<config_tag>')
def gen_tf(dep_id, config_type, name, config_tag=None):
    return Response(_gen_tf(dep_id, config_type, name, config_tag), mimetype='text/plain')


def __clean_config_reader__(query):
    import ast
    if query is not None:
        config = query.config
    else:
        config = '{}'
    return ast.literal_eval(config)


def __clean_outputs_reader__(query):
    import ast
    if query is not None:
        config = query.config
    else:
        config = '{}'
    return ast.literal_eval(config)


def _gen_tf(dep_id, config_type, name, tag=None):
    import ast
    from string import Template
    from db import db
    s = db.session
    app_result = s.query(Config).filter(Config.deployment_id == dep_id, Config.config_type_id == 'vars').first()
    appvars = __clean_config_reader__(app_result)
    dep = s.query(Deployment).get(dep_id)
    env = s.query(Environment).get(dep.environment.id)
    # inheritance order
    # provider
    # region
    # zone
    # appvars

    provvars = ast.literal_eval(s.query(Provider).get('aws').defaults)
    regvars = __clean_outputs_reader__(s.query(Region).get('us-east-1'))

    depcfg = ast.literal_eval(
        dep.defaults)
    envvars = ast.literal_eval(env.defaults)
    servicevars = ast.literal_eval(dep.service.defaults)

    config_type_tmpl = s.query(Config).get(dep_id + ':tf:' + name + ':default').config

    config_type_cfg = Template(config_type_tmpl)

    post_prov_cfg = config_type_cfg.safe_substitute(provvars)
    post_prov_tmpl = Template(post_prov_cfg)
    post_env_cfg = post_prov_tmpl.safe_substitute(envvars)
    post_env_tmpl = Template(post_env_cfg)
    post_dep_cfg = post_env_tmpl.safe_substitute(depcfg)
    post_dep_tmpl = Template(post_dep_cfg)
    svc_cfg = post_dep_tmpl.safe_substitute(servicevars)
    post_svc_cfg = Template(svc_cfg)
    app_cfg = post_svc_cfg.safe_substitute(appvars)
    return app_cfg
