import io
import sys

from alembic import command
from flask_migrate import Config
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.ddl import DropTable

from app import migrate
from controllers import RestController, CLIArgs, CLIController


@compiles(DropTable, "postgresql")
def _compile_drop_table(element, compiler):
    return compiler.visit_drop_table(element) + " CASCADE"


def before_feature(context, scenario):
    from app import app, migrate
    with app.app_context():
        context.rest = RestController()
        context.args = CLIArgs(context.rest)
        context.cli = CLIController()

        migrate.db.drop_all()
        migrate.db.create_all()
        context.real_stdout = sys.stdout
        context.stdout_mock = io.StringIO()
        sys.stdout = context.stdout_mock


def after_feature(context, scenario):
    sys.stdout = context.real_stdout
