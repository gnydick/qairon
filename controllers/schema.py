class QaironSchema:
    CREATE_FIELDS = dict(
        allocation=[
            {'allocation_type_id': {'dotters': {'completer': 'allocation_type_completer'}}},
            {'deployment_proc_id': {'dotters': {'completer': 'deployment_proc_completer'}}},
            'watermark',
            'value',
            {'-d': {'args': {'dest': 'defaults'}}}
        ],
        allocation_type=[
            'id',
            'unit',
            {'-d': {'args': {'dest': 'defaults'}}}
        ],
        application=[
            'id',
            {'-d': {'args': {'dest': 'defaults'}}}
        ],
        build=[
            {'service_id': {'dotters': {'completer': 'service_completer'}}},
            'build_num',
            'git_tag'
        ],
        capacity=[
            {'fleet_id': {'dotters': {'completer': 'fleet_completer'}}},
            'value'
        ],
        deployment_config=[
            {'config_template_id': {'dotters': {'completer': 'config_template_completer'}}},
            {'deployment_id': {'dotters': {'completer': 'deployment_completer'}}},
            'name',
            {'-c': {'args': {'dest': 'config', 'default': '{}'}}},
            {'-t': {'args': {'dest': 'tag', 'help': 'tag', 'default': 'default'}}},
        ],
        service_config=[
            {'config_template_id': {'dotters': {'completer': 'config_template_completer'}}},
            {'service_id': {'dotters': {'completer': 'service_completer'}}},
            'name',
            {'-c': {'args': {'dest': 'config', 'default': '{}'}}},
            {'-t': {'args': {'dest': 'tag', 'help': 'tag', 'default': 'default'}}},
        ],
        config_template=[
            {'language_id': {'dotters': {'completer': 'language_completer'}}},
            'id',
            {'-c': {'args': {'dest': 'doc'}}},
        ],
        language=[
            'id'
        ],
        deployment=[
            {'service_id': {'dotters': {'completer': 'service_completer'}}},
            {'deployment_target_id': {'dotters': {'completer': 'deployment_target_completer'}}},
            {'-r': {'args': {'dest': 'current_release_id'}}},
            {'-d': {'args': {'dest': 'defaults'}}},
            {'-t': {'args': {'dest': 'tag', 'help': 'tag', 'default': 'default'}}}
        ],
        deployment_proc=[
            {'deployment_id': {'dotters': {'completer': 'deployment_completer'}}},
            {'proc_id': {'dotters': {'completer': 'proc_completer'}}},
            {'-d': {'args': {'dest': 'defaults'}}}
        ],
        deployment_target=[
            {'deployment_target_type_id': {'dotters': {'completer': 'deployment_target_type_completer'}}},
            {'partition_id': {'dotters': {'completer': 'partition_completer'}}},
            {'environment_id': {'dotters': {'completer': 'environment_completer'}}},
            'name',
            {'-d': {'args': {'dest': 'defaults'}}}
        ],
        deployment_target_type=[
            'id',
            {'-d': {'args': {'dest': 'defaults'}}}
        ],
        environment=[
            'id',
            {'-d': {'args': {'dest': 'defaults'}}}
        ],
        fleet=[
            {'fleet_type_id': {'dotters': {'completer': 'fleet_type_completer'}}},
            {'deployment_target_id': {'dotters': {'completer': 'deployment_target_completer'}}},
            'name',
            {'-d': {'args': {'dest': 'defaults'}}}
        ],
        fleet_type=[
            {'provider_type_id': {'dotters': {'completer': 'provider_type_completer'}}},
            'name',
            {'-d': {'args': {'dest': 'defaults'}}}
        ],
        network=[
            {'partition_id': {'dotters': {'completer': 'partition_completer'}}},
            'name',
            'cidr',
            {'-d': {'args': {'dest': 'defaults'}}}
        ],
        partition=[
            {'region_id': {'dotters': {'completer': 'region_completer'}}},
            'name',
            {'-n': {'args': {'dest': 'native_id'}}},
            {'-d': {'args': {'dest': 'defaults'}}}
        ],
        proc=[
            {'service_id': {'dotters': {'completer': 'service_completer'}}},
            'name',
            {'-d': {'args': {'dest': 'defaults'}}}
        ],
        provider=[
            {'provider_type_id': {'dotters': {'completer': 'provider_type_completer'}}},
            'native_id',
            'name',
            {'-d': {'args': {'dest': 'defaults'}}}
        ],
        provider_type=[
            'id',
            {'-d': {'args': {'dest': 'defaults'}}}
        ],
        region=[
            {'provider_id': {'dotters': {'completer': 'provider_completer'}}},
            'name',
            {'-d': {'args': {'dest': 'defaults'}}}
        ],
        release=[
            {'build_id': {'dotters': {'completer': 'build_completer'}}},
            {'deployment_id': {'dotters': {'completer': 'deployment_completer'}}},
            'build_num',
            {'-t': {'args': {'dest': 'tag', 'help': 'tag', 'default': 'default'}}}
        ],
        repo=[
            {'repo_type_id': {'dotters': {'completer': 'repo_type_completer'}}},
            'name',
            'url',
            {'-d': {'args': {'dest': 'defaults'}}}
        ],
        repo_type=[
            'id',
            {'-d': {'args': {'dest': 'defaults'}}}
        ],

        service=[
            {'stack_id': {'dotters': {'completer': 'stack_completer'}}},
            'name',
            {'-d': {'args': {'dest': 'defaults'}}},
        ],
        stack=[
            {'application_id': {'dotters': {'completer': 'application_completer'}}},
            'name',
            {'-d': {'args': {'dest': 'defaults'}}},
        ],
        subnet=[
            {'network_id': {'dotters': {'completer': 'network_completer'}}},
            {'-n': {'args': {'dest': 'native_id'}}},
            'name',
            'cidr'
        ],
        zone=[
            {'region_id': {'dotters': {'completer': 'region_completer'}}},
            'name',
            {'-n': {'args': {'dest': 'native_id'}}},
            {'-d': {'args': {'dest': 'defaults'}}}
        ]
    )

    MODELS = CREATE_FIELDS.keys()
