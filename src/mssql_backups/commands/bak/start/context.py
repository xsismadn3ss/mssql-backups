from __future__ import annotations

from pathlib import Path

import typer

from mssql_backups.models.tables import Backup, Connection
from mssql_backups.repository import (
    bak_repository,
    conn_repository,
    container_repository,
    local_file_repository,
)
from mssql_backups.commands._common import console, session_scope


def load_backup_context(conn: str, name: str) -> tuple[Connection, Backup, list[str]]:
    with session_scope() as session:
        connection = conn_repository.get(session, conn)
        if connection is None:
            console.print(f"[red]No se encontró la conexión {conn}[/red]")
            raise typer.Exit(code=1)

        backup = bak_repository.get(session, conn, name)
        if backup is None:
            console.print(
                f"[red]No se encontró la configuración de backup {name} para la conexión {conn}[/red]"
            )
            raise typer.Exit(code=1)

        db_names = [db.name for db in backup.db_names]
        return connection, backup, db_names


def build_backup_path(backup_dir: str, date_value: str) -> str:
    return (Path(backup_dir) / date_value).as_posix()


def ensure_backup_directory(backup: Backup, backup_path: str) -> None:
    with console.status(
        f"[cyan]Preparando carpeta de destino[/] [dim]{backup_path}[/]"
    ):
        if backup.is_container:
            result = container_repository.create_dir(backup, backup_path)
            if not result:
                console.print(
                    "[red]No se pudo crear el directorio de backups dentro del contenedor[/]"
                )
                raise typer.Exit(code=1)
        else:
            local_file_repository.create_dir(backup_path)
