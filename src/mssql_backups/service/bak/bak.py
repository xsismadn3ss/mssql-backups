from __future__ import annotations

import typer

from mssql_backups.decorators import cache_required

from .start.workflow import start_backup_process

app = typer.Typer(help="Gestiona procesos de backup")


@app.command()
@cache_required
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
    start_backup_process(conn=conn, name=name)
