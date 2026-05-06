import click

from mssql_backups.constants.test_db import SQL_COMMAND
from mssql_backups.service.config_service import build_db_config
from mssql_backups.utils.sql import execute_sql_command


def list_app():
    click.clear()
    config = build_db_config()

    result = execute_sql_command(config, SQL_COMMAND)
    click.echo(str(result))
