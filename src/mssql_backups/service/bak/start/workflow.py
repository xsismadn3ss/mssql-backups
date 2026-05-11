from __future__ import annotations

from datetime import datetime

import typer
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)

from mssql_backups.decorators import (
    cache_required,
    load_backup_context,
    timed_command,
)
from mssql_backups.models.tables import Backup, Connection
from mssql_backups.repository import mssql_repository
from mssql_backups.service._common import console

from .context import build_backup_path, ensure_backup_directory
from .presentation import (
    show_backed_up_databases,
    show_failed_databases,
    show_skipped_databases,
)


@timed_command()
@cache_required
@load_backup_context(conn_param="conn", bak_param="name", db_names_param="db_names")
def start_backup_process(
    conn: str,
    name: str,
    *,
    connection: Connection,
    backup: Backup,
    db_names: list[str],
) -> None:
    if not db_names:
        console.print("[yellow]La configuración no tiene bases de datos asociadas[/]")
        raise typer.Exit(code=1)

    current_date = datetime.now().strftime("%Y%m%d")
    backup_path = build_backup_path(backup.backup_dir, current_date)

    ensure_backup_directory(backup, backup_path)

    total = len(db_names)
    backed_up_dbs: list[str] = []
    skipped_dbs: list[tuple[str, str]] = []
    failed_dbs: list[tuple[str, str]] = []

    with Progress(
        SpinnerColumn(style="cyan"),
        TextColumn("{task.description}", markup=True),
        BarColumn(bar_width=36),
        TimeElapsedColumn(),
        console=console,
        transient=False,
        refresh_per_second=4,
    ) as progress:
        task = progress.add_task(
            "[bold green]Iniciando backups[/]",
            total=total,
        )

        for index, db_name in enumerate(db_names, start=1):
            db_state = mssql_repository.get_db_state(connection, db_name)
            state_desc = db_state[0] if db_state else None

            if state_desc != "ONLINE":
                skipped_dbs.append((db_name, state_desc or "desconocido"))
                progress.update(task, description=f"[yellow]Omitiendo {db_name}[/]")
                console.print(
                    f"[yellow]Se omite {db_name} porque su estado es {state_desc or 'desconocido'}[/]"
                )
                progress.advance(task)
                continue

            file_path = f"{backup_path}/{db_name}.bak"
            progress.update(
                task,
                description=f"[cyan]Backup {index}/{total}: {db_name}[/]",
            )

            with console.status(f"[cyan]Creando backup para {db_name}[/]"):
                try:
                    mssql_repository.backup_db(
                        connection,
                        file_path,
                        db_name,
                        stream_output=False,
                    )
                except Exception as error:
                    failed_dbs.append((db_name, str(error)))
                    console.print(f"[red]No se pudo respaldar {db_name}: {error}[/]")
                else:
                    backed_up_dbs.append(db_name)
                    console.print(
                        f"[green]Backup creado[/] {db_name} -> [dim]{file_path}[/]"
                    )

            progress.advance(task)

    show_backed_up_databases(backed_up_dbs, backup_path)
    console.print(f"[green]Ruta universal:[/] [dim]{backup_path}[/]")
    show_skipped_databases(skipped_dbs)
    show_failed_databases(failed_dbs)

    if failed_dbs:
        console.print(f"[yellow]Proceso finalizado con {len(failed_dbs)} errores[/]")
        raise typer.Exit(code=1)

    console.print(
        f"[green]Proceso completado:[/] {len(backed_up_dbs)} de {total} bases de datos respaldadas"
    )
