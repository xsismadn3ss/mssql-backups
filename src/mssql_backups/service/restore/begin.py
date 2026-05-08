from __future__ import annotations

from pathlib import Path
from time import time

import typer

from mssql_backups.repository import (
    bak_repository,
    conn_repository,
    container_repository,
    local_file_repository,
    mssql_repository,
)
from mssql_backups.service._common import console, session_scope
from mssql_backups.utils.mssql import engine


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
    Inicia la restauración de una configuración de backup
    """

    # Validar que la conexión y que la configuración de backup existan
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

    # Obtener archivos
    if backup.is_container:
        files = container_repository.list_files(backup, "backup_dir")
    else:
        files = local_file_repository.list_files(backup.backup_dir)

    if not files:
        console.print("[yellow]No se encontraron archivos de backups[/]")
        return

    str_files = ""
    for file in files:
        str_files += f"{file}\n"
    console.print(
        f"[bold green]Archivos de backups encontrados:[/] [dim]\n{str_files}[/]"
    )

    with console.status("...") as status:
        mssql_engine = engine(connection)

        start_time = time()
        i = 1
        restored_dbs = []
        for file in files:
            status.update(f"Restaurando backup... [bold cyan]{i}/{len(files)}[/]")
            backup_path = f"{backup.backup_dir}/{file}"
            db_name = Path(file).stem

            logical_names = mssql_repository.get_logical_names(
                mssql_engine, backup_path
            )

            with console.status(f"[cyan]Resturando[/] {db_name}"):
                mssql_repository.restore_db(
                    mssql_engine, backup_path, backup.data_dir, db_name, *logical_names
                )

            # verificar si se restauro correctamente
            with mssql_engine.connect() as mssql_conn:
                verify = mssql_conn.exec_driver_sql(
                    "SELECT state_desc FROM sys.databases WHERE name = ?",
                    (db_name,),
                ).first()
                if verify:
                    console.print(f"[dim green]{db_name}")
                    restored_dbs.append(db_name)
                else:
                    console.print(f"[dim red]{f'{db_name}'.rjust(10)}")
            i += 1

    total = len(restored_dbs)
    console.print(
        f"\n[bold green]Restauración completada.[/] \nSe restauraron {total}/{len(files)} bases de datos."
    )
    elapsed = time() - start_time
    elapsed_min = elapsed / 60
    console.print(f"Tiempo total: {elapsed:.2f}s ({elapsed_min:.2f}m)")
