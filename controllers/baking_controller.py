import json
import os

from controllers import RestController




class BakingController:

    def __init__(self, deployment_id):
        self.rest = RestController()
        self.deployment_id = deployment_id
        self.dep_descriptor = self.rest.get_instance('deployment', deployment_id)
        self.configs = self.rest.get_field('deployment', self.deployment_id, 'configs')

    def bake(self):
        configs = self.rest.query('service_config', "service_id", "eq", self.dep_descriptor['service_id'])
        svc_cfgs = []
        for config in configs:
            svc_cfgs.append(self.rest.get_instance('service_config', config))

        for svc_cfg in svc_cfgs:
            cfg = svc_cfg['config']
            data = json.loads(cfg)
            for k,v in data.items():
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
        config = [conf['config'] for conf in self.configs
                  if conf['config_template_id'] == config_type and
                  conf['name'] == instruction['name']]
        return config

    def substition(self, subs_list):
        for instruction in subs_list:
            output = ''
            with open(instruction['filename'] + '.tmpl', 'r') as file:
                output = file.read()
            for field in instruction['fields']:
                pattern = '%%--%s--%%' % field['name']
                value = ''
                if field['type'] == 'env_var':
                    value = os.getenv(field['value'])
                if field['type'] == 'config_scalar':
                    value = self.__filter_config__(field, "scalar")[0]
                output = output.replace(pattern, value)
            with open(instruction['filename'], 'w') as file:
                file.write(output)
