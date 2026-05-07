from __future__ import annotations

import typer

from .bak import app as bak_app
from .conn import app as conn_app


app = typer.Typer(name="config", help="Administrar configuraciones guardadas en SQLite")

app.add_typer(bak_app, name="bak")
app.add_typer(conn_app, name="conn")
