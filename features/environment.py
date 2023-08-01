import io
import sys

from alembic import command
from flask_migrate import Config
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.ddl import DropTable

from app import migrate
from controllers import RestController, CLIArgs, QCLIController, PrintingOutputController


@compiles(DropTable, "postgresql")
def _compile_drop_table(element, compiler):
    return compiler.visit_drop_table(element) + " CASCADE"


def before_feature(context, scenario):
    from app import app, migrate
    with app.app_context():
        # creates a new string output
        context.stdout_mock = io.StringIO()
        context.rest = RestController()
        context.args = CLIArgs(context.rest)

        # the CLIController latches onto stdout, we have to tell it to use our mock stdout
        poc = PrintingOutputController()
        context.cli = QCLIController(poc)

        migrate.db.drop_all()
        migrate.db.create_all()
        context.real_stdout = sys.stdout
        sys.stdout = context.stdout_mock


def after_feature(context, scenario):
    sys.stdout = context.real_stdout
