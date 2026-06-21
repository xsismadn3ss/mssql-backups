import typer
from sqlmodel import Session

from mssql_backups.commands._common import console
from mssql_backups.commands.selectors.selector import selector
from mssql_backups.repository import conn_repository


def select_conn(session: Session):
    options = [conn.name for conn in conn_repository.list(session)]

    if not options:
        console.print("[red]No hay conexiones disponibles[/]")
        raise typer.Exit(code=1)
    option = selector(options, title="Conexiones guardadas")

    if not option:
        console.print("\n[bold red]No se seleccionó ninguna conexión[/]")
        raise typer.Exit(code=1)
    return option
