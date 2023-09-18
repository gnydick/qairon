#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
import importlib
import logging

from qairon_qcli.controllers import CLIArgs
from qairon_qcli.controllers import PrintingOutputController
from qairon_qcli.controllers import QCLIController
from qairon_qcli.controllers import QaironSchema
from qairon_qcli.controllers import RestController
from qairon_qcli.lib import dynamic

logger = logging.getLogger()

def _main_():
    try:
        rest = RestController()
        cli = QCLIController(PrintingOutputController())
        qaironargs = CLIArgs(rest)

        (args, junk) = qaironargs.parse_args()
        commands = ['delete', 'get', 'get_version', 'list', 'promote', 'query', 'get_field', 'get_field_query',
                    'set_field']
        if hasattr(args, 'resource'):
            if args.resource in QaironSchema.MODELS:
                if hasattr(args, 'command'):
                    command = args.command
                    if args.command in commands:
                        getattr(cli, command)(**vars(args))
                    elif args.command == 'setver':
                        args_dict = vars(args)
                        cli.set_version(**args_dict)
                    elif args.command == 'create':
                        cli.create(vars(args))
                    elif args.command == 'allocate_subnet':
                        if args.resource == 'network':
                            cli.allocate_subnet(**vars(args))
                    elif args.command == 'clone':
                        if args.resource == 'deployment':
                            cli.clone_deployment(**vars(args))
                        elif args.resource == 'config':
                            cli.clone_config()
                        elif args.resource == 'nodegroup':
                            cli.clone_nodegroup(**vars(args))
                    elif args.resource == 'deployment':
                        if args.command == 'assign_zone':
                            args_dict = vars(args)
                            args_dict['items'] = 'zones'
                            cli.add_to_collection(singular_resource='zone', **args_dict)
                        elif args.command == 'unassign_zone':
                            args_dict = vars(args)
                            args_dict['items'] = 'zones'
                            cli.del_from_collection(singular_resource='zone', **args_dict)
                    elif args.resource == 'service':
                        if args.command == 'assign_repo':
                            args_dict = vars(args)
                            args_dict['items'] = 'repos'
                            cli.add_to_collection(**args_dict)
                        elif args.command == 'unassign_repo':
                            args_dict = vars(args)
                            args_dict['items'] = 'repos'
                            cli.del_from_collection(**args_dict)
                    elif args.resource == 'test':
                        cli.test(args)
            else:
                potential_plugin_name = args.resource
                plugins_with_cli = dynamic.plugin_has_module('cli', 'qairon_qcli.plugins')
                if potential_plugin_name in plugins_with_cli:
                    plugin = qaironargs.discovered_plugins[potential_plugin_name]
                    module = importlib.import_module("%s.%s.%s" % (plugin.__name__, 'cli', potential_plugin_name))


                    if args.command in plugin.COMMANDS.keys():
                        command = args.command
                        getattr(module, command)(**vars(args))
    except Exception as e:
        logger.error(e)
        exit(255)


if __name__ == '__main__':
    _main_()
