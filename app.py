import inspect
import models
import flask_restless
from flask_admin import Admin
from flask_migrate import Migrate, Config

from base import app
from controllers import RestController
from db import db
from models import *
from views import *

if app.debug:
    from werkzeug.debug import DebuggedApplication

    app.wsgi_app = DebuggedApplication(app.wsgi_app, evalex=True)
from views.menus.divider import DividerMenu

migrate = Migrate(app, db)
restmanager = flask_restless.APIManager(app, flask_sqlalchemy_db=db)

# dynamically generate the rest endpoint for each data model
model_classes = [getattr(models, m[0]) for m in inspect.getmembers(models, inspect.isclass) if m[1].__module__.startswith('models.')]
for model_class in model_classes:
    restmanager.create_api(model_class, primary_key='id', methods=['GET', 'POST', 'DELETE', 'PUT'],
                           url_prefix='/api/rest/v1', max_results_per_page=-1)



admin = Admin(app, name='QAIRON', template_mode='bootstrap3')
admin.add_menu_item(DividerMenu(name='meta'), target_category='META')
admin.add_menu_item(DividerMenu(name='provider'), target_category='Platform')
admin.add_menu_item(DividerMenu(name='software'), target_category='Services')
admin.add_menu_item(DividerMenu(name='cicd'), target_category='CICD')
admin.add_menu_item(DividerMenu(name='deployment_targeting'), target_category='Deployment Targeting')
admin.add_menu_item(DividerMenu(name='deploying'), target_category='Deploying')
admin.add_menu_item(DividerMenu(name='configs'), target_category='Templating')
admin.add_menu_item(DividerMenu(name='types'), target_category='Types')

admin.add_view(WithIdView(Environment, db.session, category='META'))

admin.add_view(WithIdView(Application, db.session, category='Services'))
admin.add_view(DefaultView(Stack, db.session, category='Services'))
admin.add_view(ServiceView(Service, db.session, category='Services'))
admin.add_view(DefaultView(ServiceConfig, db.session, category='Services'))

admin.add_view(DefaultView(Build, db.session, category='CICD'))
admin.add_view(DefaultView(BuildArtifact, db.session, category='CICD'))
admin.add_view(DefaultView(Release, db.session, category='CICD'))
admin.add_view(DefaultView(ReleaseArtifact, db.session, category='CICD'))

admin.add_view(WithIdView(ProviderType, db.session, category='Types'))
admin.add_view(DefaultView(Provider, db.session, category='Platform'))
admin.add_view(DefaultView(Region, db.session, category='Platform'))
admin.add_view(DefaultView(Zone, db.session, category='Platform'))

admin.add_view(WithIdView(DeploymentTargetType, db.session, category='Types'))
admin.add_view(DefaultView(DeploymentTarget, db.session, category='Deployment Targeting'))
admin.add_view(DefaultView(DeploymentTargetBin, db.session, category='Deployment Targeting'))

admin.add_view(DefaultView(FleetType, db.session, category='Types'))
admin.add_view(DefaultView(Fleet, db.session, category='Deployment Targeting'))

admin.add_view(DefaultView(Deployment, db.session, category='Deploying'))
admin.add_view(DefaultView(DeploymentConfig, db.session, category='Deploying'))

admin.add_view(DefaultView(DeploymentProc, db.session, category='Deploying'))

admin.add_view(WithIdView(ConfigTemplate, db.session, category='Templating'))
admin.add_view(WithIdView(Language, db.session, category='Templating'))

admin.add_view(DefaultView(Proc, db.session, category='Services'))

admin.add_view(DefaultView(Partition, db.session, category='Platform'))
admin.add_view(NetworkView(Network, db.session, category='Platform'))
admin.add_view(SubnetView(Subnet, db.session, category='Platform'))

admin.add_view(WithIdView(AllocationType, db.session, category='Types'))
admin.add_view(DefaultView(Allocation, db.session, category='Deploying'))
admin.add_view(DefaultView(Capacity, db.session, category='Deployment Targeting'))

admin.add_view(WithIdView(RepoType, db.session, category='Types'))
admin.add_view(DefaultView(Repo, db.session, category='CICD'))

from socket import gethostname

from flask import Response

from models import Deployment, Environment, Provider, Region

rest = RestController()


@app.route('/api/health')
def health():
    return "I'm Alive!! " + gethostname()


@app.route('/api/rest/v1/network/<network_id>/allocate_subnet/<mask>/<name>', methods=['POST'])
def allocate_subnet(network_id, mask, name):
    result = rest.allocate_subnet(network_id, mask, name)
    return Response(result, mimetype='text/plain')


@app.route('/api/tf/v1/deployment/gen/<dep_id>')
@app.route('/api/tf/v1/deployment/gen/<dep_id>/<config_tag>')
def gen_config(dep_id, config_tag=None):
    from db import db
    s = db.session
    config_tag = 'default' if config_tag == None else config_tag
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


if __name__ == '__main__':
    app.run(host='0.0.0.0')
