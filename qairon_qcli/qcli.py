#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).parents[1]

sys.path.append(
    str(PROJECT_DIR)
)

from qairon_qcli.controllers import CLIArgs
from qairon_qcli.controllers import CLIController
from qairon_qcli.controllers import PrintingOutputController
from qairon_qcli.controllers import RestController
from qairon_qcli.controllers import QaironSchema


def _main_():
    rest = RestController()
    cli = CLIController(PrintingOutputController())
    qaironargs = CLIArgs(rest)

    (args, junk) = qaironargs.parse_args()
    commands = ['delete', 'get', 'get_version', 'list', 'promote', 'query', 'get_field', 'get_field_query', 'set_field']
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
                        cli.add_to_collection(**args_dict)
                    elif args.command == 'unassign_zone':
                        args_dict = vars(args)
                        args_dict['items'] = 'zones'
                        cli.del_from_collection(**args_dict)
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
            plugin_name = 'plugins.%s.cli.%s' % (args.resource, args.resource)
            if plugin_name in qaironargs.discovered_plugins:
                plugin = qaironargs.discovered_plugins[plugin_name]
                if args.command in plugin.COMMANDS.keys():
                    command = args.command
                    getattr(plugin, command)(**vars(args))


if __name__ == '__main__':
    _main_()
