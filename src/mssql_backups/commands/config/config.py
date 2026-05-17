from __future__ import annotations

import typer

from mssql_backups.decorators import cache_required, timed_command

from .bak import app as bak_app
from .conn import app as conn_app
from .db import app as db_app

app = typer.Typer(name="config", help="Administrar configuraciones guardadas en SQLite")

app.add_typer(bak_app, name="bak")
app.add_typer(conn_app, name="conn")
app.add_typer(db_app, name="db")


@app.command()
@timed_command()
@cache_required
def status():
    """
    Mostrar estatus de las configuraciones guardars. Utiliza este comando para ver de forma
    rapida el listado de configuracion guardadas en cache.
    """
    from .bak import ls as bak_ls
    from .conn import ls as conn_ls
    from .db import ls as db_ls

    conn_ls()
    print()
    bak_ls(conn=None)
    print()
    db_ls(bak=None)
