import io
import sys

from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.ddl import DropTable

from qairon_qcli.controllers.args import CLIArgs
from qairon_qcli.controllers.output_controller import PrintingOutputController
from qairon_qcli.controllers.qcli_controller import QCLIController
from qairon_qcli.controllers.rest_controller import RestController


# from qairon_qcli.controllers import RestController, CLIArgs, QCLIController, PrintingOutputController


@compiles(DropTable, "postgresql")
def _compile_drop_table(element, compiler):
    return compiler.visit_drop_table(element) + " CASCADE"


def before_feature(context, feature):
    if 'db' not in feature.tags:
        return

    from app import app, migrate
    with app.app_context():
        context.stdout_mock = io.StringIO()
        context.rest = RestController()
        context.args = CLIArgs(context.rest)

        poc = PrintingOutputController()
        context.cli = QCLIController(poc)

        migrate.db.drop_all()
        migrate.db.create_all()
        if 'cli' in feature.tags:
            context.real_stdout = sys.stdout
            sys.stdout = context.stdout_mock


def after_feature(context, feature):
    if 'cli' in feature.tags:
        sys.stdout = context.real_stdout
