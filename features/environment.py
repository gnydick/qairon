from alembic import command
from flask_migrate import Config
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.ddl import DropTable

from app import migrate
from controllers import RestController, CLIArgs


@compiles(DropTable, "postgresql")
def _compile_drop_table(element, compiler, **kwargs):
    return compiler.visit_drop_table(element) + " CASCADE"


def before_all(context):
    context.rest = RestController()
    context.args = CLIArgs(context.rest)

    migrate.db.drop_all()
    migrate.db.create_all()

