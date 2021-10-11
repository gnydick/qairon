from alembic import command
from flask_migrate import Config, Migrate

from app import migrate
from controllers import RestController, CLIArgs


def before_all(context):
    context.rest = RestController()
    context.args = CLIArgs(context.rest)
    config = Config()
    config.set_main_option("script_location", "migrations")
    # command.downgrade(config, "base")
    # command.upgrade(config, "head")
    migrate.db.drop_all()
    migrate.db.create_all()
