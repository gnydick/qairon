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
    def get_field(self, resource, id, field, **kwargs):

        value = rest._get_all_(resource, id, path=field)
        self.oc.handle(value, **kwargs)

    def get_parent(self, resource, relation, resource_id=None, **kwargs):
        value = rest.get_field(resource, resource_id, field=relation, index='relationships')
        q = kwargs.get('q', False)
        if q is False:
            print(value['data']['id'])

    def add_to_collection(self, resource, singular_resource, items, owner_id, item_id, **kwargs):
        response = rest.add_to_many_to_many(resource, owner_id, singular_resource, items, item_id)

    def get_collection(self, resource, collection, resource_id=None, **kwargs):

        # receives a stream of rows via yield
        # simplejson can handle a stream of objects and print them as array
        data = rest._get_all_(resource, resource_id, collection)
        q = kwargs.get('q', False)
        if q is False:
            print(json.dumps(SerializableGenerator(iter(data))))

    def set_field(self, resource, resource_id, field, value, **kwargs):
        response = self._set_field_(resource, resource_id, field, value)
        q = kwargs.get('q', False)
        if q is False:
            if response.status_code == 200:
                print(response.json()['id'] + ': ' + field + '=' + value)

    def set_version(self, resource_id, version, resource, **kwargs):
        body = {"id": resource_id, "version": version}
        response = rest.update_resource(resource, resource_id, json=body)
        if response.status_code == 200:
            q = kwargs.get('q', False)
            if q is False:
                print(resource_id + ' ' + version)

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
        data = outer_data['data']
        q = kwargs.get('q', False)
        if q is False:
            if results.status_code == 201:
                if 'id' in data.keys():
                    print(data['id'])
                elif 'name' in data.keys():
                    print(data['name'])
            else:
                print(results.reason)
                exit(255)

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
        q = kwargs.get('q', False)
        if q is False:
            if 200 <= results.status_code <= 299:
                output_format = kwargs.get('output_format', None)
                if output_format is None:
                    output_format = 'json'
                if output_format == 'json':
                    self.oc.handle(data)
            else:
                print(results.status_code)



    def clone_deployment(self, id, deployment_target_id, resource, command=None, version=None, **kwargs):
        dep = rest.get_instance('deployment', id)
        configs = dep['configs']
        dep_procs = dep['deployment_proces']
        dep['deployment_target_id'] = deployment_target_id
        dep.pop('deployment_target')
        dep.pop('id')
        dep.pop('configs')
        dep.pop('service')
        dep['resource'] = 'deployment'

        if version is not None:
            dep['version'] = version
        response = rest.create_resource(dep)
        status_code = response.status_code
        new_dep_id = response.json()['id']
        for config in configs:
            config.pop('id')
            config['deployment_id'] = new_dep_id
            config['resource'] = 'config'
            config_status_code = rest.create_resource(config).status_code
            if config_status_code != 200:
                status_code = config_status_code
        for dep_proc in dep_procs:
            old_dep_proc_id = dep_proc['id']
            dep_proc.pop('id')
            dep_proc.pop('deployment_id')
            dep_proc['deployment_id'] = new_dep_id
            dep_proc['resource'] = 'deployment_proc'
            response = rest.create_resource(dep_proc)
            dep_proc_status = response.status_code
            if response.status_code != 200:
                status_code = dep_proc_status
                if response.status_code == 201:
                    new_depproc_id = response.json()['id']
                    cpu_allocations = rest.query('cpu_allocation', 'deployment_proc_id', 'equals', old_dep_proc_id)
                    for cpu_alloc in cpu_allocations:
                        ca = rest.get_instance('cpu_allocation', cpu_alloc[0])
                        ca.pop('id')
                        ca.pop('deployment_proc_id')
                        ca['deployment_proc_id'] = new_depproc_id
                        ca.pop('deployment_proc')
                        ca['resource'] = 'cpu_allocation'
                        response = rest.create_resource(ca)
                        cpu_status_code = response.status_code
                        if response.status_code != 200:
                            status_code = cpu_status_code
                    memory_allocations = rest.query('memory_allocation', 'deployment_proc_id', 'equals',
                                                    old_dep_proc_id)
                    for memory_alloc in memory_allocations:
                        ca = rest.get_instance('memory_allocation', memory_alloc[0])
                        ca.pop('id')
                        ca.pop('deployment_proc_id')
                        ca['deployment_proc_id'] = new_depproc_id
                        ca.pop('deployment_proc')
                        ca['resource'] = 'memory_allocation'
                        response = rest.create_resource(ca)
                        memory_status_code = response.status_code
                        if response.status_code != 200:
                            status_code = memory_status_code

        if status_code == 201:
            q = kwargs.get('q', False)
            if q is False:
                print(new_dep_id)

    def __clone_config__(self, config, deployment_id):
        config.pop('id')
        config['deployment_id'] = deployment_id
        config['resource'] = 'config'
        return config

    def clone_config(self, id, deployment_id, **kwargs):
        config = rest.get_instance('config', id)
        new_config = self.__clone_config__(config, deployment_id)
        response = rest.create_resource(new_config)
        status_code = response.status_code
        new_config_id = response.json()['id']
        if status_code == 201:
            q = kwargs.get('q', False)
            if q is False:
                print(new_config_id)

    def _set_field_(self, resource, resource_id, field, value):
        body = {"id": resource_id, field: value}
        response = rest.update_resource(resource, resource_id, json=body)
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
