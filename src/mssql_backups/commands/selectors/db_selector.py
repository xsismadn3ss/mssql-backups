import typer
from sqlmodel import Session

from mssql_backups.commands._common import console
from mssql_backups.commands.selectors.selector import space_selector
from mssql_backups.repository import db_name_repository


def select_dbs(session: Session, bak=None):
    dbs = db_name_repository.ls(session, bak)
    if not dbs:
        console.print("[bold red]No se encontraron bases de datos[/]")
        raise typer.Exit(code=1)

    options = [f"{db.name}" for db in dbs]
    selected = space_selector(options)
    if not selected:
        console.print("[bold red]No se seleccionó ninguna base de datos[/]")
        raise typer.Exit(code=1)

    return selected
