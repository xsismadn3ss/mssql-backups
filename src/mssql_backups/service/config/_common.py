from __future__ import annotations

from rich.table import Table

from mssql_backups.models.tables import Backup, Connection
from mssql_backups.service._common import console


def print_empty(message: str) -> None:
    console.print(f"[yellow]{message}[/]")


def print_connections(connections: list[Connection]) -> None:
    if not connections:
        print_empty("No hay conexiones guardadas")
        return

    table = Table(title="Lista de conexiones")
    table.add_column("Nombre", justify="left")
    table.add_column("host", justify="left")
    table.add_column("port", justify="left")
    table.add_column("username", justify="left")

    for connection in connections:
        table.add_row(
            f"[magenta]{connection.name}[/]",
            f"{connection.host}",
            f"[cyan]{connection.port}[/]",
            f"[green]{connection.username}[/]",
        )

    console.print(table)


def print_backups(backups: list[Backup]) -> None:
    if not backups:
        print_empty("No datos guardados")
        return

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
