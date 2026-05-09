from __future__ import annotations

import typer

from mssql_backups.repository import (
    bak_repository,
    container_repository,
    local_file_repository,
)
from mssql_backups.service._common import RequiredOption, console, session_scope


def files(
    conn: str = RequiredOption(
        ...,
        "--conn",
        "-c",
        help="Nombre de la conexión",
    ),
    bak: str = RequiredOption(
        ...,
        "--bak",
        "-b",
        help="Nombre de la configuración de backup",
    ),
) -> None:
    """
    Lista los archivos de backup disponibles
    """

    with console.status("Cargando..."):
        with session_scope() as session:
            backup = bak_repository.get(session, conn, bak)

            if backup is None:
                console.print(
                    f"[red]No existe una configuración de backup llamada {bak} para la conexión {conn}[/]"
                )
                raise typer.Exit(code=1)

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
