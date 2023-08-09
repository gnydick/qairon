class QaironSchema:
    CREATE_FIELDS = dict(
        dependency=[
            {'dependency_case_id': {'dotters': {'completer': 'dependency_case_completer'}}},
            'relatable_id'
        ],
        relatable=[
            'relatable_type',
            'relatable_id'
        ],
        related=[
            'related_type',
            'related_id'
        ]
    )

    MODELS = CREATE_FIELDS.keys()
