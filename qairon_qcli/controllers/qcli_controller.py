import json
import os
import sys
from subprocess import call

from .output_controller import AbstractOutputController, SerializableGenerator, PrintingOutputController, simplify_rows
from .rest_controller import RestController

rest = RestController()


class QCLIController:

    def __init__(self, output_controller):
        self.oc = output_controller

    def get(self, resource, resource_id, **kwargs):
        row = rest.get_instance(resource, resource_id)
        self.oc.handle(row, **kwargs)

    def list(self, resource, **kwargs):
        rows = rest.query(resource)
        self.oc.handle(rows, **kwargs)

    def query(self, resource, query=None, **kwargs):
        rows = rest.query(resource, query, **kwargs)
        self.oc.handle(rows, **kwargs)

    # This will always return a list of IDs
    def get_field(self, resource, resource_id, field, **kwargs):

        value = rest._get_all_(resource, resource_id, path=field)
        self.oc.handle(value, **kwargs)

    def get_parent(self, resource, relation, resource_id=None, **kwargs):
        value = rest.get_field(resource, resource_id, field=relation, index='relationships')
        q = kwargs.get('q', False)
        if q is False:
            print(value['data']['id'])

    def add_to_collection(self, resource, singular_resource, items, owner_id, item_id, **kwargs):
        result = rest.add_to_many_to_many(resource, owner_id, singular_resource, items, item_id)
        self.oc.handle(result)

    def del_from_collection(self, resource, singular_resource, items, owner_id, item_id, **kwargs):
        result = rest.del_from_many_to_many(resource, owner_id, singular_resource, items, item_id)
        self.oc.handle(result)

    def get_collection(self, resource, collection, resource_id=None, **kwargs):

        # receives a stream of rows via yield
        # simplejson can handle a stream of objects and print them as array
        data = rest._get_all_(resource, resource_id, collection)
        q = kwargs.get('q', False)
        if q is False:
            print(json.dumps(SerializableGenerator(iter(data))))

    def set_field(self, resource, resource_id, field, value, **kwargs):
        response = self._set_field_(resource, resource_id, field, value)
        data = response.json()['data']
        self.oc.handle(data)

    def set_version(self, resource_id, version, resource, **kwargs):
        response = self._set_field_(resource, resource_id, "version", version)
        data = response.json()['data']
        self.oc.handle(data)

    def promote(self, resource, srcid, dstid, **kwargs):
        src_version = rest.get_instance('deployment', srcid)['version']
        response = self._set_field_('deployment', dstid, 'version', src_version)
        q = kwargs.get('q', False)
        if q is False:
            if response.status_code == 200:
                print(dstid + ' ' + src_version)

    def __create__(self, args_dict):
        return rest.create_resource(args_dict)

    def create(self, args_dict, **kwargs):
        results = self.__create__(args_dict)
        outer_data = results.json()
        data = outer_data.get('data', None)
        if data is not None:
            self.oc.handle(data, **kwargs)
        else:
            errors = outer_data.get('errors', None)
            kwargs['output_format'] = 'plain'
            self.oc._output_(errors[0], **kwargs)

    def delete(self, resource, resource_id, **kwargs):
        results = rest.delete_resource(resource, resource_id)
        if results.status_code == 204:
            q = kwargs.get('q', False)
            if q is False:
                print(resource_id + '-' + str(results.status_code))

    def allocate_subnet(self, network_id, additional_mask_bits, name, **kwargs):
        results = rest.allocate_subnet(network_id, additional_mask_bits, name)
        outer_data = results.json()
        data = outer_data['data']
        self.oc.handle(data)

    def __clone_config__(self, config, deployment_id):
        config.pop('id')
        config['deployment_id'] = deployment_id
        config['resource'] = 'config'
        return config

    def clone_config(self, config_id, deployment_id, **kwargs):
        config = rest.get_instance('config', config_id)
        new_config = self.__clone_config__(config, deployment_id)
        response = rest.create_resource(new_config)
        status_code = response.status_code
        new_config_id = response.json()['id']
        if status_code == 201:
            q = kwargs.get('q', False)
            if q is False:
                print(new_config_id)

    def _set_field_(self, resource, resource_id, field, value):
        body = {"data": {"id": resource_id, "type": resource, "attributes": {field: value}}}
        response = rest.patch_resource(resource, resource_id, json=body)
        return response

    def jenkins(self, args):  # dir, git_url, recursive=False):
        rest.list('service', 0, 'equal', args.git_url)
        recurse_flag = "-r" if args.recursive else ""
        command_line = "qairon jenkins %s %s %s " % (recurse_flag, args.dir, args.git_url)
        command = command_line.split()

        envvars = os.environ.copy()

        call(command, env=envvars)


def clone_nodegroup(resource_id, name, **kwargs):
    nodegroup = rest.get_instance('deployment', resource_id)

    subnets = nodegroup['subnets']
    nodegroup['name'] = name
    nodegroup.pop('id')
    nodegroup['resource'] = 'nodegroup'

    response = rest.create_resource(nodegroup)
    status_code = response.status_code
    new_dep_id = response.json()['id']

    if status_code == 201:
        q = kwargs.get('q', False)
        if q is False:
            print(new_dep_id)
