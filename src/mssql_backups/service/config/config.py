from __future__ import annotations

import typer

from .bak import app as bak_app
from .conn import app as conn_app

app = typer.Typer(name="config", help="Administrar configuraciones guardadas en SQLite")

app.add_typer(bak_app, name="bak")
app.add_typer(conn_app, name="conn")


@app.command()
def status():
    """
    Mostrar estatus de las configuraciones guardars. Utiliza este comando para ver de forma
    rapida el listado de configuracion guardadas en cache.
    """
    from .bak import ls as bak_ls
    from .conn import ls as conn_ls

    conn_ls()
    print()
    bak_ls()
