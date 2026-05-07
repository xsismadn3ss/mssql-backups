from __future__ import annotations

import typer

from .begin import begin as begin_command
from .files import files as files_command


app = typer.Typer(name="restore", help="Restaurar bases de datos usando configuraciones guardadas en SQLite")

app.command(name="files")(files_command)
app.command(name="begin")(begin_command)