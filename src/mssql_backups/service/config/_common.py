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
    if not backups:
        print_empty("No datos guardados")
        return

    from rich.table import Table

    table = Table(title="Lista de backups")
    table.add_column("Nombre", justify="left")
    table.add_column("Conexión", justify="left")
    table.add_column("Descripción", justify="left")
    table.add_column("backup_dir", justify="left")
    table.add_column("data_dir", justify="left")
    table.add_column("contenedor", justify="left")

    for backup in backups:
        table.add_row(
            f"[magenta]{backup.name}[/]",
            f"[magenta]{backup.conn.name}[/]" if backup.conn else "",
            backup.description or "",
            f"[cyan]{backup.backup_dir}[/]",
            f"[cyan]{backup.data_dir}[/]",
            f"[blue]{backup.container_name}[/]" or "",
        )

    console.print(table)
