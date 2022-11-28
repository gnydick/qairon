import itertools
import json
import os
from subprocess import call

from .rest_controller import RestController

rest = RestController()


class SerializableGenerator(list):
    """Generator that is serializable by JSON"""

    def __init__(self, iterable):
        tmp_body = iter(iterable)
        try:
            self._head = iter([next(tmp_body)])
            self.append(tmp_body)
        except StopIteration:
            self._head = []

    def __iter__(self):
        return itertools.chain(self._head, *self[:1])


def serialize_rows(rows, output_fields=None):
    for row in rows:
        id = row['id']

        if output_fields:
            keys = output_fields
        else:
            keys = row['attributes'].keys()

        output = {'id': id}
        for key in [x for x in keys if x != "id"]:
            output[key] = row['attributes'][key]
        yield output


def serialize_row(row, output_fields=None):
    id = row['id']

    if output_fields:
        keys = output_fields
    else:
        keys = row['attributes'].keys()

    output = {'id': id}
    for key in [x for x in keys if x != "id"]:
        output[key] = row['attributes'][key]
    return output


class CLIController:

    def __output__(self, q, rows, field=None, output_fields=None, output_format=None):
        if not q:
            if output_format == None:
                output_format = "json"
            if type(rows) == list:
                items = serialize_rows(rows, output_fields)
                pass
            elif type(rows) == dict:
                item = serialize_row(rows, output_fields)

            if output_format == 'json':

                if type(rows) == list:
                    output = {field: [x for x in items]}

                    print(json.dumps(output))
                elif type(rows) == dict:
                    print(json.dumps({field: item}))

            elif output_format == 'plain':

                if type(rows) == list:
                    for row in items:
                        print(' '.join(str(x) for x in row.values()))
                elif type(rows) == dict:
                    output = ['""' if x == None else str(x) for x in item.values()]
                    print(' '.join(output))

    def get(self, resource, command=None, id=None, output_fields=None, output_format=None, q=False):
        row = rest.get_instance(resource, id)
        self.__output__(q, row, resource, output_fields=output_fields, output_format=output_format)


    def list(self, resource, command=None, resperpage=10, page=None, output_fields=None, output_format=None, q=False):
        rows = rest.query(resource, None, output_fields=output_fields, resperpage=resperpage, page=page)
        self.__output__(q, rows, output_fields=output_fields, field=None, output_format=output_format)

    def query(self, resource, command=None, query=None, output_fields=None, resperpage=None,
              page=None, output_format=None, q=False):
        rows = rest.query(resource, query, output_fields, resperpage=resperpage, page=page)
        self.__output__(q, rows, output_fields=output_fields, output_format=output_format)

    def get_version(self, resource, command=None, id=None, q=False):
        value = rest.get_field(resource, id, field='version')
        if not q:
            print(value)

    # This will always return an ID or list of IDs
    def get_field(self, resource, id, field, command=None, output_fields=None, output_format=None, q=False):
        value = rest.get_field(resource, id, field=field)
        self.__output__(q, value, field=field, output_fields=output_fields, output_format=output_format)

    def get_parent(self, resource, relation, command=None, id=None, q=False):
        value = rest.get_field(resource, id, field=relation, index='relationships')
        if not q:
            print(value['data']['id'])

    def get_collection(self, resource, collection, command=None, resperpage=None, page=None, id=None, q=False):

        # receives a stream of rows via yield
        # simplejson can handle a stream of objects and print them as array
        data = rest.get_collection(resource, id, collection)
        if not q:
            print(json.dumps(SerializableGenerator(iter(data))))

    def set_field(self, resource, id, field, value, command=None, q=False):
        response = self._set_field_(resource, id, field, value)
        if not q:
            if response.status_code == 200:
                print(response.json()['id'] + ': ' + field + '=' + value)

    def set_version(self, id, version, resource, command=None, q=False):
        body = {"id": id, "version": version}
        response = rest.update_resource(resource, id, json=body)
        if response.status_code == 200:
            if q is False:
                print(id + ' ' + version)

    def promote(self, resource, srcid, dstid, command=None, q=False):
        src_version = rest.get_instance('deployment', srcid)['version']
        response = self._set_field_('deployment', dstid, 'version', src_version)

        if not q:
            if response.status_code == 200:
                print(dstid + ' ' + src_version)

    def __create__(self, args_dict):
        return rest.create_resource(args_dict)

    def create(self, args_dict, q=False):
        results = self.__create__(args_dict)
        data = results.json()

        if not q:
            if results.status_code == 201:
                if 'id' in data.keys():
                    print(data['id'])
                elif 'name' in data.keys():
                    print(data['name'])
            else:
                print(results.reason)
                exit(255)

    def delete(self, resource, command=None, id=None, q=False):
        results = rest.delete_resource(resource, id)
        if results.status_code == 204:
            if not q:
                print(id + '-' + str(results.status_code))

    def allocate_subnet(self, resource, command=None, id=None, additional_mask_bits=None, name=None, q=False):
        results = rest.allocate_subnet(id, additional_mask_bits, name)
        if not q:
            if 200 <= results.status_code <= 299:
                print(results.json()['cidr'])
            else:
                print(results.status_code)

    def clone_nodegroup(self, id, name, resource, command=None, version=None, q=False):
        nodegroup = rest.get_instance('deployment', id)

        subnets = nodegroup['subnets']
        nodegroup['name'] = name
        nodegroup.pop('id')
        nodegroup['resource'] = 'nodegroup'

        response = rest.create_resource(nodegroup)
        status_code = response.status_code
        new_dep_id = response.json()['id']

        if status_code == 201:
            if not q:
                print(new_dep_id)

    def clone_deployment(self, id, deployment_target_id, resource, command=None, version=None, q=False):
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
            if not q:
                print(new_dep_id)

    def __clone_config__(self, config, deployment_id):
        config.pop('id')
        config['deployment_id'] = deployment_id
        config['resource'] = 'config'
        return config

    def clone_config(self, id, deployment_id, resource, command=None, version=None, q=False):
        config = rest.get_instance('config', id)
        new_config = self.__clone_config__(config, deployment_id)
        response = rest.create_resource(new_config)
        status_code = response.status_code
        new_config_id = response.json()['id']
        if status_code == 201:
            if not q:
                print(new_config_id)

    def add_to_collection(self, resource, owner_id, items, item_id, command=None, q=False):
        response = rest.add_to_many_to_many(resource, owner_id, items, item_id)
        data = response.json()
        collection = data[items]
        if not q:
            self.__print_object_list__(collection)

    def del_from_collection(self, resource, owner_id, items, item_id, command=None, q=False):
        response = rest.del_from_many_to_many(resource, owner_id, items, item_id)
        data = response.json()
        collection = data[items]
        if not q:
            self.__print_object_list__(collection)

    def _set_field_(self, resource, resource_id, field, value):
        body = {"id": resource_id, field: value}
        response = rest.update_resource(resource, resource_id, json=body)
        return response

    def __print_object_list__(self, collection):
        for item in collection:
            print(item['id'])

    def test(self, parama):
        pass

    def jenkins(self, args):  # dir, git_url, recursive=False):
        rest.list('service', 0, 'equal', args.git_url)
        recurse_flag = "-r" if args.recursive else ""
        command_line = "qairon jenkins %s %s %s " % (recurse_flag, args.dir, args.git_url)
        command = command_line.split()

        envvars = os.environ.copy()

        call(command, env=envvars)
