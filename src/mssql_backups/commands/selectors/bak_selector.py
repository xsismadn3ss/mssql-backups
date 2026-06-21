import typer
from sqlmodel import Session

from mssql_backups.commands._common import console
from mssql_backups.commands.selectors.selector import selector
from mssql_backups.repository import bak_repository


def select_bak(session: Session, conn=None):
    options = [bak.name for bak in bak_repository.ls(session, conn)]

    if not options:
        console.print("[red]No hay backups disponibles[/]")
        raise typer.Exit(code=1)
    option = selector(options, title="Backups disponibles")

    if not option:
        console.print("[bold red]No se seleccionó ningún backup[/]")
        raise typer.Exit(code=1)
    return option
