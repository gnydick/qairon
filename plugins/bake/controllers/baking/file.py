import ast
import json
import os

from controllers.output_controller import simplify_rows
from plugins.aws.controllers.aws import AwsServiceController
from plugins.bake.controllers.baking.abstract_bake import AbstractBakingController


class FileBakingController(AbstractBakingController):

    def __init__(self, metadata):
        super().__init__(metadata)
        self.local_data = {
            'release_job_number': metadata.release_job_number,
            'deployment_id': metadata.deployment_id,
            'build_id': metadata.build_id
        }
        blob_repo_type = 'ecr'

        repos = simplify_rows(self.rest.get_field('service', self.deployment['service_id'], 'repos'))

        candidate_repos = [repo for repo in repos if repo['type_id'] == blob_repo_type]
        # this condition supports old DSL for baking of repo as a single object on the baker
        if len(candidate_repos) == 1:
            self.repo = candidate_repos[0]
        # this condition supports new DSL for having mutliple output repos
        elif len(candidate_repos) > 1:
            self.repos = {}
            for repo in candidate_repos:
                self.repos[repo['id']] = repo

    def bake(self):
        svc_configs = simplify_rows(self.rest.get_field('service', self.deployment['service_id'], 'configs'))

        svc_cfg = [svc_cfg for svc_cfg in svc_configs if
                   svc_cfg['template_id'] == 'bake_files' and svc_cfg['name'] == 'default']
        assert len(svc_cfg) == 1
        cfg = svc_cfg[0]['config']
        data = json.loads(cfg)
        for k, v in data.items():
            if k == 'files':
                self.files(v)

    def files(self, instruction):
        for k, v in instruction.items():
            if k == 'substitutions':
                self.substition(v)
            elif k == 'create':
                self.create(v)

    def create(self, creates_list):
        for instruction in creates_list:
            with open(instruction['filename'], 'w') as file:
                config = self.__filter_config__(instruction, "in-place")
                file.write(config[0])

    def __filter_config__(self, instruction, config_type):
        config = [conf['config'] for conf in self.deployment['configs']
                  if conf['config_template_id'] == config_type and
                  conf['name'] == instruction['name']]
        return config

    def substition(self, subs_list):
        for instruction in subs_list:
            output = ''
            filename = ''
            if os.getenv('LOCAL_DEV'):
                filename = instruction['filename'] + '.tmpl'
            else:
                filename = instruction['filename']
            with open(filename, 'r') as file:
                output = file.read()

            for field in instruction['fields']:
                value = ''
                if field['type'] == 'dict_env_var':
                    jp = os.getenv(field['value']['var'])
                    try:
                        job_parameters = json.loads(jp)
                    except:
                        job_parameters = ast.literal_eval(jp)

                    parameter = field['value']['parameter']
                    value = job_parameters[parameter]
                if field['type'] == 'meta_hash':
                    object_type = field['value']['object']
                    key = field['value']['key']
                    field_name = field['value']['field']
                    obj = getattr(self, object_type)
                    value = str(obj[key][field_name])
                if field['type'] == 'meta':
                    object_type = field['value']['object']
                    field_name = field['value']['field']
                    obj = getattr(self, object_type)
                    value = str(obj[field_name])
                if field['type'] == 'one_from_collection':
                    object_type = field['collection']
                    data_field = field['data_field']
                    filters = field['filters']
                    objs = getattr(self, object_type)
                    for filter in filters:
                        objs = [cfg for cfg in objs if cfg[filter['field_name']] == filter['value']]
                    assert len(objs) == 1
                    value = objs[0][data_field]
                if field['type'] == 'aws_secret':
                    aws = AwsServiceController()
                    secret = aws.get_secret_string_for_deployment(self.local_data['deployment_id'],
                                                                  field['secret_name'])
                    value = secret['SecretString']
                if field['type'] == 'config_kv_list':
                    object_type = field['value']['object']
                    field_name = field['value']['field']
                    filter_value = field['value']['filter']
                    cfgs = getattr(self, object_type)
                    objs = [cfg for cfg in cfgs if cfg[field_name] == filter_value]
                    value = ""
                    x = 0
                    for cfg_obj in objs:
                        for k, v in json.loads(cfg_obj['config']).items():
                            # assume all config kv's get indented
                            if x > 0:
                                value += "\n"
                            value += format("  %s=%s" % (k, v))
                            x = x + 1
                elif field['type'] == 'local':
                    value = self.local_data[field['value']]

                pattern = '%%--%s--%%' % field['name']
                output = output.replace(pattern, value)
            with open(instruction['filename'], 'w') as file:
                file.write(output)
