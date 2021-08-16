import json

# from controllers.bakers.baker import BakerInterface
import os

from plugins.controller.bakers import AbstractBakerController


class HelmBakerController(AbstractBakerController):

    def __init__(self, metadata):
        super().__init__(metadata)
        self.local_data = {
            'release_job_number': metadata.release_job_number,
            'deployment_id': metadata.deployment_id,
            'build_id': metadata.build_id
        }
        blob_repo_type = 'ecr'
        candidate_repos = [repo for repo in self.rest.get_field('service', self.deployment['service_id'], 'repos') if
                           repo['repo_type_id'] == blob_repo_type]
        assert len(candidate_repos) == 1
        self.repo = candidate_repos[0]

    def bake(self):
        svc_cfg = [svc_cfg for svc_cfg in self.rest.get_field('service', self.deployment['service_id'], 'configs') if
                   svc_cfg['config_template_id'] == 'helm_bake' and svc_cfg['name'] == 'default']
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
                if field['type'] == 'meta':
                    object_type = field['value']['object']
                    field_name = field['value']['field']
                    obj = getattr(self, object_type)
                    value = str(obj[field_name])
                elif field['type'] == 'local':
                    value = self.local_data[field['value']]

                pattern = '%%--%s--%%' % field['name']
                output = output.replace(pattern, value)
            with open(instruction['filename'], 'w') as file:
                file.write(output)
