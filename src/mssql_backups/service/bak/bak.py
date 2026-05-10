from datetime import datetime
from time import sleep

import typer

from mssql_backups.models.tables import Connection
from mssql_backups.repository import (
    bak_repository,
    container_repository,
    local_file_repository,
    mssql_repository,
)
from mssql_backups.service._common import console, session_scope

app = typer.Typer(help="Gestiona procesos de backup")


@app.command()
def start(
    name: str = typer.Option(
        ...,
        "--name",
        "-n",
        help="Nombre de configuración de backup",
        prompt_required=True,
        prompt=True,
    ),
    conn: str = typer.Option(
        ...,
        "--conn",
        "-c",
        help="Nombre de conexión",
        prompt_required=True,
        prompt=True,
    ),
):
    """
    Inicia un nuevo proceso de backup para multiples bases de datos
    """
    with session_scope() as session:
        with console.status("Buscando configuración guardada...") as status:
            bak = bak_repository.get(session, conn, name)

            if bak is None:
                console.print(
                    f"[red]No se encontró la configuración de backup {name} para la conexión {conn}[/red]"
                )
                raise typer.Exit()
            dbs = bak.db_names
            names = [db.name for db in bak.db_names]
            status.update(
                f"[green]Bases de datos para realizar backup:[/] [dim]\n- {'\n- '.join(names)}[/]"
            )
            sleep(3)

            # crear query para backup
            conn_config: Connection = bak.conn  # type: ignore
            current_date = datetime.now().strftime("%Y%m%d")
            backup_path = f"{bak.backup_dir}/{current_date}"
            status.update(
                f"[cyan]Todos los backups serán guardados en:[/] [dim]{backup_path}[/]"
            )
            sleep(3)

            if bak.is_container:
                result = container_repository.create_dir(bak, backup_path)
                if not result:
                    console.print(
                        "[red]No se pudo crear el directorio de backups dentro del contenedor"
                    )
                    raise typer.Exit(code=1)
            else:
                local_file_repository.create_dir(backup_path)

            i = 1
            total = len(dbs)

            for db in dbs:
                db_state = mssql_repository.get_db_state(conn_config, db.name)
                state_desc = db_state[0] if db_state else None

                if state_desc != "ONLINE":
                    console.print(
                        f"[yellow]Se omite {db.name} porque su estado es {state_desc or 'desconocido'}[/]"
                    )
                    i += 1
                    continue

                file_path = f"{backup_path}/{db.name}.bak"
                status.update(
                    f"Backup {i}/{total}: \n[bold]Creando backup para {db.name}[/]"
                )
                mssql_repository.backup_db(conn_config, file_path, db.name)
                status.update(
                    f"Backup {i}/{total}: \n[bold]Backup creado para {db.name}[/]"
                )
                i += 1

    files_created = container_repository.list_files(bak, "backup_dir")
    console.print(f"[green]Backup completado. Archivos creados:[/] {files_created}")
