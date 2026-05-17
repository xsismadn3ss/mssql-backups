from __future__ import annotations

from typing import Tuple

import typer

from mssql_backups.models.tables import Backup, Connection
from mssql_backups.repository import (
    bak_repository,
    conn_repository,
    container_repository,
    local_file_repository,
)
from mssql_backups.commands._common import console, session_scope

from .state_machine import RestoreResult, RestoreState

STATE_STYLES = {
    RestoreState.PREPARING: "magenta",
    RestoreState.RESTORING: "yellow",
    RestoreState.WAITING: "cyan",
    RestoreState.ONLINE: "green",
    RestoreState.FAILED: "red",
    RestoreState.SKIPPED: "dim",
}


def format_eta(eta_ms: int | None) -> str:
    if eta_ms is None or eta_ms <= 0:
        return ""

    eta_seconds = max(0, eta_ms // 1000)
    minutes, seconds = divmod(eta_seconds, 60)
    if minutes:
        return f"ETA {minutes:02d}:{seconds:02d}"
    return f"ETA {seconds:02d}s"


def format_restore_line(
    db_name: str,
    state: RestoreState,
    *,
    percent_complete: float | None = None,
    eta_ms: int | None = None,
    database_state: str | None = None,
) -> str:
    color = STATE_STYLES.get(state, "white")
    parts: list[str] = [f"[{color}]{db_name}[/]", f"[dim]{state.value.upper()}[/]"]

    if database_state:
        parts.append(f"[bold]{database_state}[/]")

    if percent_complete is not None:
        parts.append(f"[bold]{percent_complete:.0f}%[/]")

    eta = format_eta(eta_ms)
    if eta:
        parts.append(f"[dim]{eta}[/]")

    return " • ".join(parts)


def load_backup_context(conn: str, bak: str) -> Tuple[Connection, Backup]:
    with session_scope() as session:
        connection = conn_repository.get(session, conn)
        if connection is None:
            console.print(f"[red]No existe una conexión llamada {conn}[/]")
            raise typer.Exit(code=1)

        backup = bak_repository._get_bak(session, connection.id, bak)
        if backup is None:
            console.print(
                f"[red]No existe una configuración de backup llamada [bold]{bak}[/] para la conexión [bold]{conn}[/][/]"
            )
            raise typer.Exit(code=1)

    return connection, backup


def list_backup_files(backup: Backup) -> list[str]:
    if backup.is_container:
        return container_repository.list_files(backup, "backup_dir") or []

    return local_file_repository.list_files(backup.backup_dir)


def print_backup_files(files: list[str]) -> None:
    str_files = ""
    for file in files:
        str_files += f"{file}\n"

    console.print(
        f"[bold green]Archivos de backups encontrados:[/] [dim]\n{str_files}[/]"
    )


def print_restore_result(result: RestoreResult) -> None:
    console.print(
        format_restore_line(
            result.db_name,
            result.state,
            database_state=result.database_state,
        )
    )
    if result.message and result.state != RestoreState.ONLINE:
        console.print(f"[dim yellow]{result.message}[/]")


def print_restore_summary(results: list[RestoreResult], elapsed_seconds: float) -> None:
    restored = [result for result in results if result.state == RestoreState.ONLINE]
    failed = [result for result in results if result.state == RestoreState.FAILED]

    console.print(
        f"\n[bold green]Restauración completada.[/] \nSe restauraron {len(restored)}/{len(results)} bases de datos."
    )

    if failed:
        console.print("[bold yellow]Bases de datos con problemas:[/]")
        for result in failed:
            console.print(
                f"[yellow]- {result.db_name}: {result.database_state or 'desconocido'}[/]"
            )

    elapsed_min = elapsed_seconds / 60
    console.print(f"Tiempo total: {elapsed_seconds:.2f}s ({elapsed_min:.2f}m)")
