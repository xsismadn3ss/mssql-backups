from __future__ import annotations

from time import time

import typer
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)

from mssql_backups.service._common import console

from .helpers import (
    list_backup_files,
    load_backup_context,
    print_backup_files,
    print_restore_result,
    print_restore_summary,
)
from .state_machine import RestoreStateMachine


def begin(
    conn: str = typer.Option(
        None,
        "--conn",
        "-c",
        help="Nombre de la conexión guardada",
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
) -> None:
    """
    Inicia la restauración de una configuración de backup.
    """
    connection, backup = load_backup_context(conn, bak)

    files = list_backup_files(backup)
    if not files:
        console.print("[yellow]No se encontraron archivos de backups[/]")
        return

    print_backup_files(files)

    restore_machine = RestoreStateMachine(
        connection,
        poll_seconds=1.0,
        timeout_seconds=15,
    )

    start_time = time()
    results = []

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
            "[bold green]Progreso total[/]", total=len(files)
        )

        for file_name in files:
            db_name = file_name.rsplit(".", 1)[0]

            with console.status(f"[cyan]Restaurando {db_name}[/]") as status:
                result = restore_machine.restore_file(backup, file_name, status=status)

            results.append(result)
            print_restore_result(result)
            progress.advance(overall_task)

    print_restore_summary(results, time() - start_time)
