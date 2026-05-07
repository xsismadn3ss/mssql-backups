from __future__ import annotations

from pathlib import Path

import typer

from mssql_backups.service._common import required_text, session_scope
from mssql_backups.utils.sql import build_restore_query, execute_sql_command

from ._common import (
    build_backup_config,
    build_db_config,
    console,
    get_backup,
    get_connection,
    list_backup_files,
)


def begin(
    conn: str | None = typer.Option(None, help="Nombre de la conexión guardada"),
    bak: str | None = typer.Option(None, help="Nombre de la configuración de backup"),
) -> None:
    """
    Inicia la restauración de una configuración de backup
    """
    connection_name = required_text(conn, "Nombre de la conexión")
    backup_name = required_text(bak, "Nombre de la configuración de backup")

    with session_scope() as session:
        connection = get_connection(session, connection_name)
        if connection is None:
            console.print(f"[red]No existe una conexión llamada {connection_name}[/]")
            raise typer.Exit(code=1)

        backup = get_backup(session, backup_name)
        if backup is None:
            console.print(
                f"[red]No existe una configuración de backup llamada {backup_name}[/]"
            )
            raise typer.Exit(code=1)

        db_config = build_db_config(connection)
        backup_config = build_backup_config(backup)

    try:
        files = list_backup_files(backup)
    except FileNotFoundError as error:
        console.print(f"[red]{error}[/]")
        raise typer.Exit(code=1) from error

    if not files:
        console.print("[yellow]No se encontraron archivos de backups[/]")
        return

    console.print("[bold green]Archivos de backups encontrados:[/]")
    for file_name in files:
        console.print(f"[green]{file_name}[/]")

    for file_name in files:
        backup_path = str(Path(backup_config.backup_dir) / file_name)
        db_name = Path(file_name).stem
        query = build_restore_query(
            db_config, backup_path, backup_config.data_dir, db_name
        )

        console.print(f"\nRestaurando {file_name}")
        console.print(f"[cyan]{query}[/]")

        result = execute_sql_command(db_config, query)
        console.print(f"[dim green]{result}[/]")

    console.print("[bold green]\nRestauración completada[/]")
    console.print(f"[green]Se restauraron {len(files)} bases de datos[/]")
