from __future__ import annotations

from rich.table import Table

from mssql_backups.commands._common import console


def show_backed_up_databases(backed_up_dbs: list[str], backup_path: str) -> None:
    if not backed_up_dbs:
        console.print("[yellow]No se generó ningún backup[/]")
        return

    table = Table(title="Bases de datos respaldadas")
    table.add_column("Base de datos", justify="left")
    table.add_column("Archivo generado", justify="left")

    for db_name in backed_up_dbs:
        table.add_row(db_name, f"{backup_path}/{db_name}.bak")

    console.print(table)


def show_skipped_databases(skipped_dbs: list[tuple[str, str]]) -> None:
    if not skipped_dbs:
        return

    table = Table(title="Bases de datos omitidas")
    table.add_column("Base de datos", justify="left")
    table.add_column("Estado", justify="left")

    for db_name, state in skipped_dbs:
        table.add_row(db_name, state)

    console.print(table)


def show_failed_databases(failed_dbs: list[tuple[str, str]]) -> None:
    if not failed_dbs:
        return

    table = Table(title="Bases de datos con error")
    table.add_column("Base de datos", justify="left")
    table.add_column("Error", justify="left")

    for db_name, error in failed_dbs:
        table.add_row(db_name, error)

    console.print(table)
