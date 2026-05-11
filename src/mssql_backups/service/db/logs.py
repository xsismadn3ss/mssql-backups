from __future__ import annotations

import re
from pathlib import Path

import typer
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table

from mssql_backups.decorators import (
    cache_required,
    load_backup_context,
    timed_command,
)
from mssql_backups.models.tables import Backup, Connection
from mssql_backups.repository import (
    container_repository,
    local_file_repository,
    mssql_repository,
)
from mssql_backups.service._common import console

app = typer.Typer(help="Administrar logs", name="logs")

SIZE_RE = re.compile(r"^\s*(\d+)\s*(MB|GB)?\s*$", re.IGNORECASE)
BYTES_PER_MB = 1024 * 1024
BYTES_PER_GB = 1024 * 1024 * 1024
DEFAULT_TARGET = "100MB"
DEFAULT_THRESHOLD = "500MB"


def _format_size(size_bytes: int) -> str:
    if size_bytes >= BYTES_PER_GB:
        return f"{size_bytes / BYTES_PER_GB:.2f} GB"
    if size_bytes >= BYTES_PER_MB:
        return f"{size_bytes / BYTES_PER_MB:.2f} MB"
    if size_bytes >= 1024:
        return f"{size_bytes / 1024:.2f} KB"
    return f"{size_bytes} B"


def _parse_size(size_text: str) -> int:
    match = SIZE_RE.fullmatch(size_text)
    if match is None:
        raise ValueError("Usa un tamaño como 100MB o 1GB")

    amount = int(match.group(1))
    if amount <= 0:
        raise ValueError("El tamaño debe ser mayor que 0")

    unit = (match.group(2) or "MB").upper()
    multiplier = {
        "MB": BYTES_PER_MB,
        "GB": BYTES_PER_GB,
    }.get(unit)

    if multiplier is None:
        raise ValueError("Solo se admiten tamaños en MB o GB")

    return amount * multiplier


def _list_log_files(backup: Backup) -> list[tuple[str, int]]:
    try:
        if backup.is_container:
            return container_repository.list_files_with_size(
                backup,
                "data_dir",
                extension=".ldf",
            )

        return local_file_repository.list_files_with_size(
            backup.data_dir,
            extension=".ldf",
        )
    except Exception as error:
        console.print(
            f"[red]No se pudieron listar los archivos de la carpeta data: {error}[/]"
        )
        raise typer.Exit(code=1)


def _physical_path(backup: Backup, relative_path: str) -> str:
    return str(Path(backup.data_dir) / relative_path)


def _show_found_logs(
    log_files: list[tuple[str, int]],
    *,
    threshold_bytes: int,
) -> None:
    table = Table(
        title=f"Archivos .ldf encontrados (umbral: {_format_size(threshold_bytes)})"
    )
    table.add_column("Archivo", justify="left")
    table.add_column("Tamaño", justify="right")
    table.add_column("Estado", justify="center")

    for file_name, size_bytes in log_files:
        state = (
            "[green]Reducir[/]" if size_bytes > threshold_bytes else "[yellow]Omitir[/]"
        )
        table.add_row(file_name, _format_size(size_bytes), state)

    console.print(table)


def _show_reduced_logs(
    reduced_logs: list[tuple[str, str, int]],
    *,
    target_bytes: int,
) -> None:
    table = Table(title="Logs reducidos")
    table.add_column("Archivo", justify="left")
    table.add_column("Base de datos", justify="left")
    table.add_column("Tamaño original", justify="right")
    table.add_column("Objetivo", justify="right")

    for file_name, database_name, size_bytes in reduced_logs:
        table.add_row(
            file_name,
            database_name,
            _format_size(size_bytes),
            _format_size(target_bytes),
        )

    console.print(table)


def _show_failed_logs(failed_logs: list[tuple[str, str]]) -> None:
    if not failed_logs:
        return

    table = Table(title="Logs que no se pudieron reducir")
    table.add_column("Archivo", justify="left")
    table.add_column("Motivo", justify="left")

    for file_name, error in failed_logs:
        table.add_row(file_name, error)

    console.print(table)


@app.command()
@timed_command()
@cache_required
@load_backup_context
def reduce(
    conn: str = typer.Option(
        None,
        "--conn",
        "-c",
        help="Nombre de la configuración de conexión",
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
    connection: Connection,
    backup: Backup,
    target: str = typer.Option(
        DEFAULT_TARGET,
        "--target",
        help="Tamaño objetivo del log. Ejemplos: 100MB, 50MB, 1GB",
    ),
    threshold: str = typer.Option(
        DEFAULT_THRESHOLD,
        "--threshold",
        help="Solo reduce logs que pesen más que este valor. Ejemplos: 500MB, 1GB",
    ),
) -> None:
    """Reducir logs de la base de datos"""
    try:
        target_bytes = _parse_size(target)
        threshold_bytes = _parse_size(threshold)
    except ValueError as error:
        console.print(f"[red]{error}[/]")
        raise typer.Exit(code=1)

    if target_bytes > threshold_bytes:
        console.print(
            "[red]El tamaño objetivo no puede ser mayor que el umbral de reducción[/]"
        )
        raise typer.Exit(code=1)

    target_mb = target_bytes // BYTES_PER_MB
    threshold_label = _format_size(threshold_bytes)
    target_label = _format_size(target_bytes)

    with console.status("Buscando archivos .ldf..."):
        log_files = _list_log_files(backup)

    if not log_files:
        console.print(
            f"[yellow]No se encontraron archivos .ldf en la carpeta data de {backup.name}[/]"
        )
        return

    console.print(
        f"[green]Se encontraron {len(log_files)} archivos .ldf en la carpeta data[/]"
    )
    console.print(
        f"[cyan]Umbral de reducción:[/] {threshold_label} | [cyan]Objetivo:[/] {target_label}"
    )
    _show_found_logs(log_files, threshold_bytes=threshold_bytes)

    reducible_logs = [
        (file_name, size_bytes)
        for file_name, size_bytes in log_files
        if size_bytes > threshold_bytes
    ]

    skipped_count = len(log_files) - len(reducible_logs)
    if skipped_count:
        console.print(
            f"[yellow]Se omitieron {skipped_count} logs por pesar {threshold_label} o menos[/]"
        )

    if not reducible_logs:
        console.print(
            f"[yellow]No hay logs mayores a {threshold_label} para reducir[/]"
        )
        return

    reduced_logs: list[tuple[str, str, int]] = []
    failed_logs: list[tuple[str, str]] = []

    with Progress(
        SpinnerColumn(style="cyan"),
        TextColumn("{task.description}", markup=True),
        BarColumn(bar_width=36),
        TimeElapsedColumn(),
        console=console,
        transient=False,
        refresh_per_second=4,
    ) as progress:
        overall_task = progress.add_task(
            f"[bold green]Reduciendo logs > {threshold_label} a {target_label}[/]",
            total=len(reducible_logs),
        )

        for file_name, size_bytes in reducible_logs:
            progress.update(
                overall_task,
                description=f"[cyan]Reduciendo {file_name}[/]",
            )

            physical_path = _physical_path(backup, file_name)
            with console.status(f"[cyan]Reduciendo {file_name}[/]"):
                try:
                    file_info = mssql_repository.get_log_file_info(
                        connection,
                        physical_path,
                    )
                    if file_info is None:
                        raise ValueError(
                            f"No se pudo identificar el log físico {physical_path}"
                        )

                    database_name, logical_name = file_info
                    mssql_repository.shrink_log_file(
                        connection,
                        database_name,
                        logical_name,
                        target_mb,
                    )

                    reduced_logs.append((file_name, database_name, size_bytes))
                    console.print(
                        f"[green]Reducido[/] {file_name} [dim]({database_name})[/]"
                    )
                except Exception as error:
                    failed_logs.append((file_name, str(error)))
                    console.print(f"[red]No se pudo reducir[/] {file_name}: {error}")

            progress.advance(overall_task)

    if reduced_logs:
        _show_reduced_logs(reduced_logs, target_bytes=target_bytes)

    if failed_logs:
        _show_failed_logs(failed_logs)
        console.print(f"[yellow]Proceso finalizado con {len(failed_logs)} errores[/]")
        raise typer.Exit(code=1)

    console.print(f"[green]Proceso finalizado. Logs reducidos: {len(reduced_logs)}[/]")
