from flask import g
from sqlalchemy import Column, PrimaryKeyConstraint, String
from sqlalchemy.ext.declarative import declared_attr


class TenantMixin:
    __abstract__ = True

    # 1) define the tenant_id column
    @declared_attr
    def tenant_id(cls):
        return Column(String, nullable=False, primary_key=True, default=lambda: g.tenant_id)

    # 2) define the composite PK (tenant_id + your model's own PK)
    @declared_attr
    def __table_args__(cls):
        # NOTE: replace "id" below with whatever your model's other PK column is called
        return (
            PrimaryKeyConstraint("tenant_id", "id"),
        )
