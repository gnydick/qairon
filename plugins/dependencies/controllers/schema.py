class QaironSchema:
    CREATE_FIELDS = dict(
        dependency_case=[
            'id'
        ],
        dependency=[
            {'dependency_case_id': {'dotters': {'completer': 'dependency_case_completer'}}},
            'relatable_id'
        ],
        relatable=[
            'type',
            'relatable_id'
        ],
        related=[
            'type',
            'related_id'
        ]
    )

    MODELS = CREATE_FIELDS.keys()
