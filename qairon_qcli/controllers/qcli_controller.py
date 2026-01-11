import os
from subprocess import call

from .operations_controller import OperationsController
from .rest_controller import RestController


class QCLIController:

    def __init__(self, output_controller):
        self.oc = output_controller
        self.ops = OperationsController()

    # =========================================================================
    # QUERY METHODS - Pass streaming results to output controller
    # =========================================================================

    def get(self, resource, resource_id, **kwargs):
        rows = self.ops.get(resource, resource_id)
        self.oc.handle(rows, **kwargs)

    def get_collection(self, resource, collection, resource_id=None, **kwargs):
        rows = self.ops.get_collection(resource, collection, resource_id)
        self.oc.handle(rows, **kwargs)

    def get_field(self, resource, resource_id, field, **kwargs):
        rows = self.ops.get_field(resource, resource_id, field)
        self.oc.handle(rows, **kwargs)

    def get_parent(self, resource, relation, resource_id=None, **kwargs):
        rows = self.ops.get_parent(resource, relation, resource_id)
        self.oc.handle(rows, **kwargs)

    def list(self, resource, **kwargs):
        rows = self.ops.list(resource)
        self.oc.handle(rows, **kwargs)

    def query(self, resource, query=None, **kwargs):
        rows = self.ops.query(resource, query, **kwargs)
        self.oc.handle(rows, **kwargs)

    # =========================================================================
    # COMMAND METHODS - Pass streaming results to output controller
    # =========================================================================

    def add_to_collection(self, resource, singular_resource, items, owner_id, item_id, **kwargs):
        data = self.ops.add_to_collection(resource, singular_resource, items, owner_id, item_id)
        self.oc.handle(data, **kwargs)

    def allocate_subnet(self, network_id, additional_mask_bits, name, **kwargs):
        data = self.ops.allocate_subnet(network_id, additional_mask_bits, name)
        self.oc.handle(data, **kwargs)

    def clone_config(self, config_id, deployment_id, **kwargs):
        data = self.ops.clone_config(config_id, deployment_id)
        self.oc.handle(data, **kwargs)

    def clone_deployment(self, deployment_id, deployment_target_id, resource=None, command=None, version=None, **kwargs):
        data = self.ops.clone_deployment(deployment_id, deployment_target_id, version)
        self.oc.handle(data, **kwargs)

    def clone_nodegroup(self, resource_id, name, **kwargs):
        data = self.ops.clone_nodegroup(resource_id, name)
        self.oc.handle(data, **kwargs)

    def create(self, args_dict, **kwargs):
        data, errors = self.ops.create(args_dict)
        if data is not None:
            self.oc.handle(data, **kwargs)
        else:
            kwargs['output_format'] = 'plain'
            self.oc._output_(errors[0], **kwargs)

    def del_from_collection(self, resource, singular_resource, items, owner_id, item_id, **kwargs):
        data = self.ops.del_from_collection(resource, singular_resource, items, owner_id, item_id)
        self.oc.handle(data, **kwargs)

    def delete(self, resource, resource_id, **kwargs):
        data = self.ops.delete(resource, resource_id)
        self.oc.handle(data, **kwargs)

    def promote(self, resource, srcid, dstid, **kwargs):
        data = self.ops.promote(srcid, dstid)
        self.oc.handle(data, **kwargs)

    def set_field(self, resource, resource_id, field, value, **kwargs):
        data = self.ops.set_field(resource, resource_id, field, value)
        self.oc.handle(data, **kwargs)

    def set_version(self, resource_id, version, resource, **kwargs):
        data = self.ops.set_version(resource, resource_id, version)
        self.oc.handle(data, **kwargs)

    # =========================================================================
    # SPECIAL METHODS
    # =========================================================================

    def jenkins(self, args):
        rest = RestController()
        rest.list('service')
        recurse_flag = "-r" if args.recursive else ""
        command_line = "qairon jenkins %s %s %s " % (recurse_flag, args.dir, args.git_url)
        command = command_line.split()
        envvars = os.environ.copy()
        call(command, env=envvars)