from __future__ import annotations

import typer

from mssql_backups.decorators import (
    cache_required,
    load_backup_context,
    timed_command,
)
from mssql_backups.models.tables import Backup, Connection
from mssql_backups.repository import container_repository, local_file_repository
from mssql_backups.commands._common import console


@timed_command()
@cache_required
@load_backup_context(connection_param="_connection")
def files(
    conn: str = typer.Option(
        None,
        "--conn",
        "-c",
        help="Nombre de la conexión",
        prompt=True,
        prompt_required=True,
    ),
    bak: str = typer.Option(
        None,
        "--bak",
        "-b",
        help="Nombre de la configuración de backup",
        prompt=True,
        prompt_required=True,
    ),
    *,
    _connection: Connection,
    backup: Backup,
) -> None:
    """
    Lista los archivos de backup disponibles
    """

    with console.status("Cargando..."):
        if backup.is_container:
            files = container_repository.list_files(backup, "backup_dir")
        else:
            files = local_file_repository.list_files(backup.backup_dir)

        if not files:
            console.print(
                f"[red]No se encontraron archivos de backup para la configuración {bak}[/]"
            )
            raise typer.Exit(code=1)

        baks = [f for f in files if f.endswith(".bak")]
        not_baks = [f for f in files if not f.endswith(".bak")]

        console.print("Archivos encontrados:")
        if baks:
            console.print(f"[green]{len(baks)} archivos .bak encontrados[/]")
            console.print(f"[blue]{baks}[/]")
        if not_baks:
            console.print(f"\n[yellow]{len(not_baks)} archivos no .bak encontrados[/]")
            console.print(f"[magenta]{not_baks}[/]")
            console.print(
                "[dim]Considera eliminar los archivos no .bak para evitar conflictos[/]"
            )
