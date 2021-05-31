import argparse

import argcomplete

from .rest_controller import RestController
from .schema import QaironSchema


def __gen_completers__(rest):
    resources = QaironSchema.CREATE_FIELDS.keys()
    for res in resources:
        def completer(self, prefix, parsed_args, resource=res, **kwargs):
            return rest.resource_get_search(prefix, resource, **kwargs)

        completer.__name__ = "%s_completer" % res

        setattr(RestController, ("%s_completer" % res), completer)


def __populate_args__(rest, parser, fields):
    for field in fields:
        if type(field) == str:
            parser.add_argument(field)
        elif type(field) == dict:
            for key in field.keys():
                for k, v in field[key].items():
                    if k == 'args':
                        parser.add_argument(key, **v)
                    elif k == 'dotters':
                        for d, m in v.items():
                            arg = parser.add_argument(key)
                            setattr(arg, d, getattr(rest, m))


def __add_list_parser__(parsers):
    list_parser = parsers.add_parser('list')
    list_parser.required = False
    list_parser.add_argument('-p', help='page', dest='page')
    list_parser.add_argument('-r', help='results per page', dest='resperpage')
    list_parser.add_argument('-o', help='output fields', dest='output_fields', action='append')

    query_parser = parsers.add_parser('query')
    query_parser.required = False
    query_parser.add_argument('search_field')
    query_parser.add_argument('op')
    query_parser.add_argument('value')
    query_parser.add_argument('-p', help='page', dest='page')
    query_parser.add_argument('-r', help='results per page', dest='resperpage')
    query_parser.add_argument('-o', help='output fields', dest='output_fields', action='append')


def __add_set_field_parser__(rest, parsers, resource):
    field_update_parser = parsers.add_parser('set_field')
    field_update_parser.add_argument('id').completer = getattr(rest, '%s_completer' % resource)
    field_update_parser.add_argument('field')
    field_update_parser.add_argument('value')


def __add_get_field_parser__(rest, parsers, resource):
    field_update_parser = parsers.add_parser('get_field')
    field_update_parser.add_argument('id').completer = getattr(rest, '%s_completer' % resource)
    field_update_parser.add_argument('field')


class CLIArgs:

    def __init__(self, rest):
        self.rest = rest
        __gen_completers__(rest)
        self.schema = QaironSchema()
        self.model_subparsers = dict()

    def subnet_allocator_bits_completer(self, prefix, **kwargs):
        return ['additional_mask_bits']

    def __gen_parsers__(self, context_parsers):
        for model in self.schema.MODELS:
            model_parser = context_parsers.add_parser(model)
            parsers_for_model_parser = model_parser.add_subparsers(help='command', dest='command')
            parsers_for_model_parser.required = True
            self.model_subparsers[model] = parsers_for_model_parser

            __add_list_parser__(parsers_for_model_parser)
            __add_set_field_parser__(self.rest, parsers_for_model_parser, model)
            __add_get_field_parser__(self.rest, parsers_for_model_parser, model)
            _model_com_get_parser = parsers_for_model_parser.add_parser('get')
            _model_com_get_parser.add_argument('id').completer = getattr(self.rest, '%s_completer' % model)
            _model_com_create_parser = parsers_for_model_parser.add_parser('create')
            __populate_args__(self.rest, _model_com_create_parser, self.schema.CREATE_FIELDS[model])
            _model_com_delete_parser = parsers_for_model_parser.add_parser('delete')
            _model_com_delete_parser.add_argument('id').completer = getattr(self.rest, '%s_completer' % model)

        deployment_sub_parsers = self.model_subparsers['deployment']
        clone_dep_parser = deployment_sub_parsers.add_parser('clone')
        clone_dep_parser.add_argument('id').completer = getattr(self.rest, 'deployment_completer')
        clone_dep_parser.add_argument('deployment_target_id',
                                      help='destination deployment target')

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

    def parse_args(self, rest):
        parser = self.assign_args()
        argcomplete.autocomplete(parser)

        return parser.parse_known_args()
