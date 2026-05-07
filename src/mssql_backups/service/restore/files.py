from __future__ import annotations

import typer

from ._common import (
    console,
    get_backup,
    list_backup_files,
    print_files,
    required_text,
    session_scope,
)


def files(
    bak: str | None = typer.Argument(None, help="Nombre de la configuración de backup"),
) -> None:
    """
    Lista los archivos de backup disponibles
    """

    backup_name = required_text(bak, "Nombre de la configuración de backup")

    with session_scope() as session:
        backup = get_backup(session, backup_name)

        if backup is None:
            console.print(
                f"[red]No existe una configuración de backup llamada {backup_name}[/]"
            )
            raise typer.Exit(code=1)

    try:
        files = list_backup_files(backup)
    except FileNotFoundError as error:
        console.print(f"[red]{error}[/]")
        raise typer.Exit(code=1) from error

    print_files(files)
