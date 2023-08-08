class QaironSchema:
    CREATE_FIELDS = dict(
        relatable=[
            {'allocation_type_id': {'dotters': {'completer': 'allocation_type_completer'}}},
            {'deployment_proc_id': {'dotters': {'completer': 'deployment_proc_completer'}}},
            'watermark',
            'value',
            {'-d': {'args': {'dest': 'defaults'}}}
        ]
    )

    MODELS = CREATE_FIELDS.keys()
