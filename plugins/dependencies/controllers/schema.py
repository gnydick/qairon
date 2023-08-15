class QaironSchema:
    CREATE_FIELDS = dict(
        dependency_case=[
            'id',
            'relatable_type',
            'related_type',
            'allowed_relationship'
        ],
        dependency=[
            {'dependency_case_id': {'dotters': {'completer': 'dependency_case_completer'}}},
            {'relatable_id': {'dotters': {'completer': 'relatable_completer'}}},
        ],
        relatable=[
            'type',
            'object_id'
        ],
        related=[
            'type',
            'object_id'
        ]
    )

    MODELS = CREATE_FIELDS.keys()
