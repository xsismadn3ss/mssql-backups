from __future__ import annotations

from pathlib import Path
from time import time

import typer

from mssql_backups.service._common import required_text, session_scope
from mssql_backups.utils.mssql import engine

from ._common import (
    build_restore_query,
    console,
    get_backup,
    get_connection,
    get_logical_names_from_backup,
    list_backup_files,
)


def begin(
    conn: str | None = typer.Option(None, help="Nombre de la conexión guardada"),
    bak: str | None = typer.Option(None, help="Nombre de la configuración de backup"),
) -> None:
    """
    Inicia la restauración de una configuración de backup
    """
    connection_name = required_text(conn, "Nombre de la conexión")
    backup_name = required_text(bak, "Nombre de la configuración de backup")

    with session_scope() as session:
        connection = get_connection(session, connection_name)
        if connection is None:
            console.print(f"[red]No existe una conexión llamada {connection_name}[/]")
            raise typer.Exit(code=1)

        backup = get_backup(session, backup_name)
        if backup is None:
            console.print(
                f"[red]No existe una configuración de backup llamada {backup_name}[/]"
            )
            raise typer.Exit(code=1)

    try:
        files = list_backup_files(backup)
    except FileNotFoundError as error:
        console.print(f"[red]{error}[/]")
        raise typer.Exit(code=1) from error

    if not files:
        console.print("[yellow]No se encontraron archivos de backups[/]")
        return

    with console.status("...") as status:
        str_files = ""
        for file in files:
            str_files += f"{file}\n"
        status.update(
            f"[bold green]Archivos de backups encontrados:[/] [dim]\n{str_files}[/]"
        )

        mssql_engine = engine(connection)

        start_time = time()
        i = 1
        restored_dbs = []
        for file in files:
            status.update(f"Restaurando backup... [bold cyan]{i}/{len(files)}[/]")
            backup_path = f"{backup.backup_dir}/{file}"
            db_name = Path(file).stem

            logical_names = get_logical_names_from_backup(mssql_engine, backup_path)
            query = build_restore_query(
                backup_path, backup.data_dir, db_name, *logical_names
            )

            with console.status(
                f"[cyan]Resturando[/] {db_name} \n[dim magenta]Ejecutando:[/][dim]\n{query}[/]"
            ):
                with mssql_engine.connect().execution_options(
                    isolation_level="AUTOCOMMIT"
                ) as mssql_connection:
                    mssql_connection.exec_driver_sql(query)

            # verificar si se restuaro correctamente
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
