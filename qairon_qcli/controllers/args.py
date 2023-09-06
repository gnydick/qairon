import argparse
import importlib

import argcomplete

from qairon_qcli.lib import dynamic
from qairon_qcli.controllers.rest_controller import RestController
from qairon_qcli.controllers.schema import QaironSchema


def __gen_completers__(rest):
    resources = QaironSchema.CREATE_FIELDS.keys()
    for res in resources:
        def completer(self, prefix, action=None, parser=None, parsed_args=None, resource=res):
            return rest.resource_get_search(prefix, resource)

        completer.__name__ = "%s_completer" % res
        setattr(RestController, ("%s_completer" % res), completer)


def __gen_attr_completers__(rest, res, attr):
    def completer(self, prefix, parsed_args, resource=res, attribute=attr):
        return rest.resource_get_attr_search(prefix, parsed_args, resource, attribute)

    name = "%s_%s_completer" % (res, attr)
    completer.__name__ = "%s_completer" % res

    setattr(RestController, name, completer)


def __populate_args__(rest, parser, fields):
    for field in fields:
        if type(field) == str:
            parser.add_argument(field)
        elif type(field) == dict:
            for flag in field.keys():
                config = field[flag]
                arg = None
                if 'dotters' in config:
                    if 'args' in config:
                        settings = config['args']
                        arg = parser.add_argument(flag, **settings)
                    else:
                        arg = parser.add_argument(flag)
                    for d, m in config['dotters'].items():
                        setattr(arg, d, getattr(rest, m))

                elif 'args' in config:
                    settings = config['args']
                    parser.add_argument(flag, **settings)


def __add_list_parser__(parsers):
    list_parser = parsers.add_parser('list')
    list_parser.required = False
    list_parser.add_argument('-f', help='output fields', dest='output_fields', action='append')
    list_parser.add_argument('-o', help='format: [ json(default) | plain ]', dest='output_format')

    query_parser = parsers.add_parser('query')
    query_parser.required = False
    query_parser.add_argument('query')
    query_parser.add_argument('-f', help='output fields', dest='output_fields', action='append')
    query_parser.add_argument('-o', help='format: [ json(default) | plain ]', dest='output_format')


def __add_set_field_parser__(rest, parsers, resource):
    set_field_parser = parsers.add_parser('set_field')
    set_field_parser.add_argument('resource_id').completer = getattr(rest, '%s_completer' % resource)
    set_field_parser.add_argument('field')
    set_field_parser.add_argument('value')


def __add_get_field_parser__(rest, parsers, resource):
    get_field_parser = parsers.add_parser('get_field')
    get_field_parser.add_argument('id').completer = getattr(rest, '%s_completer' % resource)
    get_field_parser.add_argument('field')
    get_field_parser.add_argument('-f', help='output field for related object', dest='output_fields',
                                  action='append')
    get_field_parser.add_argument('-o', help='format: [ json(default) | plain ]', dest='output_format')


def __add_get_field_query_parser__(rest, parsers, resource):
    get_field_query_parser = parsers.add_parser('get_field_query')
    get_field_query_parser.add_argument('field')
    get_field_query_parser.required = False
    get_field_query_parser.add_argument('query')
    get_field_query_parser.add_argument('-f', help='output fields', dest='output_fields', action='append')
    get_field_query_parser.add_argument('-o', help='format: [ json(default) | plain ]', dest='output_format')


class CLIArgs:

    def __init__(self, rest):
        self.rest = rest
        self.model_subparsers = dict()
        self.discovered_plugins = dict()

        plugins_with_controllers = dynamic.plugin_has_module('controllers', 'qairon_qcli.plugins')
        for plugin_with_controllers in plugins_with_controllers:
            package_spec = importlib.util.find_spec('qairon_qcli.plugins.%s.%s' % (plugin_with_controllers, 'controllers.schema'))
            if package_spec is not None:
                module = importlib.import_module('qairon_qcli.plugins.%s.%s' % (plugin_with_controllers, 'controllers'))
                qs = getattr(module, 'QaironSchema')
                QaironSchema.CREATE_FIELDS.update(qs.CREATE_FIELDS)
                RestController.schema.CREATE_FIELDS.update(qs.CREATE_FIELDS)



        __gen_completers__(rest)

        __gen_attr_completers__(rest, 'service', 'repos')
        __gen_attr_completers__(rest, 'deployment', 'zones')

    def subnet_allocator_bits_completer(self, prefix):
        return ['additional_mask_bits']

    def __gen_parsers__(self, context_parsers):
        plugins_with_controllers = dynamic.plugin_has_module('controllers','qairon_qcli.plugins')
        for plugin_base_name in plugins_with_controllers:
            plugin = 'qairon_qcli.plugins.%s' % plugin_base_name
            plugin_package = importlib.import_module(plugin)
            self.discovered_plugins[plugin_base_name] = plugin_package
            if hasattr(plugin_package, "cli"):
                cli_module = importlib.import_module(plugin_package.__name__ + '.cli')
                plugin_parser = context_parsers.add_parser(plugin_base_name)
                new_subparsers = plugin_parser.add_subparsers(help='command', dest='command')
                new_subparsers.required = True
                for command in cli_module.COMMANDS.keys():
                    parser = new_subparsers.add_parser(command)
                    __populate_args__(self.rest, parser, plugin_package.COMMANDS[command])

        for model in QaironSchema.MODELS:
            model_parser = context_parsers.add_parser(model)
            parsers_for_model_parser = model_parser.add_subparsers(help='command', dest='command')
            parsers_for_model_parser.required = True
            self.model_subparsers[model] = parsers_for_model_parser

            __add_list_parser__(parsers_for_model_parser)
            __add_set_field_parser__(self.rest, parsers_for_model_parser, model)
            __add_get_field_parser__(self.rest, parsers_for_model_parser, model)
            __add_get_field_query_parser__(self.rest, parsers_for_model_parser, model)
            _model_com_get_parser = parsers_for_model_parser.add_parser('get')
            _model_com_get_parser.add_argument('resource_id').completer = getattr(self.rest, '%s_completer' % model)
            _model_com_get_parser.add_argument('-f', help='output field for related object', dest='output_fields',
                                               action='append')
            _model_com_get_parser.add_argument('-o', help='format: [ json(default) | plain ]', dest='output_format')
            _model_com_create_parser = parsers_for_model_parser.add_parser('create')
            __populate_args__(self.rest, _model_com_create_parser, QaironSchema.CREATE_FIELDS[model])
            _model_com_delete_parser = parsers_for_model_parser.add_parser('delete')
            _model_com_delete_parser.add_argument('resource_id').completer = getattr(self.rest, '%s_completer' % model)

        service_subparsers = self.model_subparsers['service']
        assign_repo_parser = service_subparsers.add_parser('assign_repo')
        assign_repo_parser.add_argument(metavar='service_id', dest='owner_id').completer = getattr(self.rest,
                                                                                                   'service_completer')
        assign_repo_parser.add_argument(metavar='repo_id', dest='item_id').completer = getattr(self.rest,
                                                                                               'repo_completer')

        unassign_repo_parser = service_subparsers.add_parser('unassign_repo')
        unassign_repo_parser.add_argument(metavar='service_id', dest='owner_id').completer = getattr(self.rest,
                                                                                                     'service_completer')
        unassign_repo_parser.add_argument(metavar='repo_id', dest='item_id').completer = getattr(self.rest,
                                                                                                 'service_repos_completer')

        deployment_sub_parsers = self.model_subparsers['deployment']
        clone_dep_parser = deployment_sub_parsers.add_parser('clone')
        clone_dep_parser.add_argument('id').completer = getattr(self.rest, 'deployment_completer')
        clone_dep_parser.add_argument('deployment_target_id',
                                      help='destination deployment target')

        assign_zone_parser = deployment_sub_parsers.add_parser('assign_zone')
        assign_zone_parser.add_argument(metavar='deployment_id', dest='owner_id').completer = getattr(self.rest,
                                                                                                      'deployment_completer')
        assign_zone_parser.add_argument(metavar='zone_id', dest='item_id').completer = getattr(self.rest,
                                                                                               'zone_completer')

        unassign_zone_parser = deployment_sub_parsers.add_parser('unassign_zone')
        unassign_zone_parser.add_argument(metavar='deployment_id', dest='owner_id').completer = getattr(self.rest,
                                                                                                        'deployment_completer')
        unassign_zone_parser.add_argument(metavar='zone_id', dest='item_id').completer = getattr(self.rest,
                                                                                                 'deployment_zones_completer')

        network_sub_parsers = self.model_subparsers['network']
        subnet_allocator_parser = network_sub_parsers.add_parser('allocate_subnet')
        subnet_allocator_parser.add_argument('id', help='Network ID').completer = getattr(self.rest,
                                                                                          'network_completer')
        subnet_allocator_parser.add_argument('additional_mask_bits',
                                             help='Subnet bits').completer = self.subnet_allocator_bits_completer
        subnet_allocator_parser.add_argument('name', help='Name of subnet')

    def assign_args(self):
        parser = argparse.ArgumentParser(description='qaironRegistry CLI')
        parser.add_argument('-q', help='Quiet', required=False, action='store_true')
        context_parsers = parser.add_subparsers(help='context to operate in', dest='resource')

        self.__gen_parsers__(context_parsers)

        test_parser = context_parsers.add_parser('test')
        test_parser.add_argument('command', nargs='*')
        return parser

    def parse_args(self):
        parser = self.assign_args()
        argcomplete.autocomplete(parser)

        return parser.parse_known_args()
