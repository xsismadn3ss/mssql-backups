from __future__ import annotations

from mssql_backups.models.tables import Backup, Connection
from mssql_backups.service._common import console


def print_empty(message: str) -> None:
    console.print(f"[yellow]{message}[/]")


def print_connections(connections: list[Connection]) -> None:
    console.print("[bold cyan]Conexiones guardadas[/]")
    if not connections:
        print_empty("No hay conexiones guardadas")
        return

    for connection in connections:
        console.print(
            f"- {connection.name} | host={connection.host} | port={connection.port} | username={connection.username}"
        )


def print_backups(backups: list[Backup]) -> None:
    console.print("[bold cyan]Configuraciones de backups guardados[/]")
    if not backups:
        print_empty("No datos guardados")
        return

    for backup in backups:
        description = (
            f" | description={backup.description}" if backup.description else ""
        )
        container = "si" if backup.is_container else "no"
        console.print(
            f"- {backup.name}{description} | backup_dir={backup.backup_dir} | data_dir={backup.data_dir} | is_container={container} | container_name={backup.container_name}"
        )
