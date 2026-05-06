import click

from mssql_backups.service.list_app import list_app
from mssql_backups.service.restore_app import restore_app
from mssql_backups.utils.colors import fore_green


@click.group()
def cli():
    """CLI interactivo para MSSQL Server

    Herramienta para resturar bases de datos usando archivos .bak, tambien permite
    crear backups de bases de datos."""
    pass


@cli.command()
def restore():
    """Restaurar bases de datos, sigue las instrucciones del asistente"""
    restore_app()


@cli.command()
def backup_dialog():
    """Crear backups de bases de datos de forma interactiva"""
    pass


@cli.command()
def backup():
    """Crear backups de bases de datos usando parametros"""
    pass


@cli.command()
def list():
    """Listar bases de datos disponibles"""
    list_app()


if __name__ == "__main__":
    print(fore_green(f"{'MSSQL Backups':-^60}"))
    cli()
