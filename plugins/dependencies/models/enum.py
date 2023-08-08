from sqlalchemy import Enum


class CardinalityEnum:
    cardinality_types = ('OTO', 'OTM')
    cardinality_types_enum = Enum(*cardinality_types, name='relationship_type')
