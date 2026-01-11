from json_stream import streamable_list

from .rest_controller import RestController


class OperationsController:

    def __init__(self):
        self.rest = RestController()

    # =========================================================================
    # INTERNAL HELPERS
    # =========================================================================

    @streamable_list
    def _stream_(self, data):
        """
        Unified streaming helper - handles single rows, batches, or iterables.
        - dict: yields single row
        - iterable of lists (batches): flattens and yields each row
        - iterable of dicts: yields each row
        """
        if isinstance(data, dict):
            yield data
        else:
            for item in data:
                if isinstance(item, list):
                    yield from item
                else:
                    yield item

    # =========================================================================
    # QUERY METHODS (READ) - Always return streamable
    # =========================================================================

    def get(self, resource, resource_id):
        row = self.rest.get_instance(resource, resource_id)
        return self._stream_(row)

    def get_collection(self, resource, collection, resource_id=None):
        batches = self.rest._get_all_(resource, resource_id, collection)
        return self._stream_(batches)

    def get_field(self, resource, resource_id, field):
        batches = self.rest._get_all_(resource, resource_id, path=field)
        return self._stream_(batches)

    def get_parent(self, resource, relation, resource_id=None):
        value = self.rest.get_field(resource, resource_id, field=relation, index='relationships')
        return self._stream_(value['data'])

    def list(self, resource):
        batches = self.rest.query(resource)
        return self._stream_(batches)

    def query(self, resource, query=None, **kwargs):
        batches = self.rest.query(resource, query, **kwargs)
        return self._stream_(batches)

    # =========================================================================
    # COMMAND METHODS (CREATE, UPDATE, DELETE) - Return streamable
    # =========================================================================

    def create(self, args_dict):
        response = self.rest.create_resource(args_dict)
        outer_data = response.json()
        data = outer_data.get('data')
        errors = outer_data.get('errors')
        if data:
            return self._stream_(data), None
        return None, errors

    def update(self, resource, resource_id, field, value):
        body = {"data": {"id": resource_id, "type": resource, "attributes": {field: value}}}
        response = self.rest.patch_resource(resource, resource_id, json=body)
        data = response.json()['data']
        return self._stream_(data)

    def delete(self, resource, resource_id):
        response = self.rest.delete_resource(resource, resource_id)
        return self._stream_({
            'id': resource_id,
            'type': resource,
            'attributes': {'status': response.status_code}
        })

    # =========================================================================
    # COMPOSITE COMMANDS - Business logic that composes CRUD operations
    # =========================================================================

    def add_to_collection(self, resource, singular_resource, items, owner_id, item_id):
        result = self.rest.add_to_many_to_many(resource, owner_id, singular_resource, items, item_id)
        return self._stream_(result)

    def allocate_subnet(self, network_id, additional_mask_bits, name):
        response = self.rest.allocate_subnet(network_id, additional_mask_bits, name)
        data = response.json()['data']
        return self._stream_(data)

    def clone_config(self, config_id, deployment_id):
        config = self.rest.get_instance('config', config_id)
        config.pop('id')
        config['deployment_id'] = deployment_id
        config['resource'] = 'config'
        response = self.rest.create_resource(config)
        data = response.json().get('data')
        return self._stream_(data)

    def clone_deployment(self, deployment_id, deployment_target_id, version=None):
        dep = self.rest.get_instance('deployment', deployment_id)
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

        response = self.rest.create_resource(dep)
        new_dep_data = response.json().get('data')
        new_dep_id = new_dep_data['id']

        for config in configs:
            config.pop('id')
            config['deployment_id'] = new_dep_id
            config['resource'] = 'config'
            self.rest.create_resource(config)

        for dep_proc in dep_procs:
            old_dep_proc_id = dep_proc['id']
            dep_proc.pop('id')
            dep_proc.pop('deployment_id')
            dep_proc['deployment_id'] = new_dep_id
            dep_proc['resource'] = 'deployment_proc'
            response = self.rest.create_resource(dep_proc)
            if response.status_code == 201:
                new_depproc_id = response.json()['id']
                cpu_allocations = self.rest.query('cpu_allocation', 'deployment_proc_id', 'equals', old_dep_proc_id)
                for cpu_alloc in cpu_allocations:
                    ca = self.rest.get_instance('cpu_allocation', cpu_alloc[0])
                    ca.pop('id')
                    ca.pop('deployment_proc_id')
                    ca['deployment_proc_id'] = new_depproc_id
                    ca.pop('deployment_proc')
                    ca['resource'] = 'cpu_allocation'
                    self.rest.create_resource(ca)
                memory_allocations = self.rest.query('memory_allocation', 'deployment_proc_id', 'equals',
                                                     old_dep_proc_id)
                for memory_alloc in memory_allocations:
                    ca = self.rest.get_instance('memory_allocation', memory_alloc[0])
                    ca.pop('id')
                    ca.pop('deployment_proc_id')
                    ca['deployment_proc_id'] = new_depproc_id
                    ca.pop('deployment_proc')
                    ca['resource'] = 'memory_allocation'
                    self.rest.create_resource(ca)

        return self._stream_(new_dep_data)

    def clone_nodegroup(self, resource_id, name):
        nodegroup = self.rest.get_instance('deployment', resource_id)
        nodegroup['name'] = name
        nodegroup.pop('id')
        nodegroup['resource'] = 'nodegroup'
        response = self.rest.create_resource(nodegroup)
        data = response.json().get('data')
        return self._stream_(data)

    def del_from_collection(self, resource, singular_resource, items, owner_id, item_id):
        result = self.rest.del_from_many_to_many(resource, owner_id, singular_resource, items, item_id)
        return self._stream_(result)

    def promote(self, srcid, dstid):
        src_version = self.rest.get_instance('deployment', srcid)['version']
        return self.set_field('deployment', dstid, 'version', src_version)

    def set_field(self, resource, resource_id, field, value):
        return self.update(resource, resource_id, field, value)

    def set_version(self, resource, resource_id, version):
        return self.update(resource, resource_id, 'version', version)
