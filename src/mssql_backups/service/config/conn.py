from __future__ import annotations

import typer
from rich.table import Table
from sqlmodel import Session

from mssql_backups.callbacks import confirm
from mssql_backups.decorators import (
    cache_required,
    confirm_destructive_action,
    with_session,
)
from mssql_backups.models.tables import Connection
from mssql_backups.repository import conn_repository as repository
from mssql_backups.service._common import (
    console,
    required_int,
    required_text,
)

app = typer.Typer(help="Administrar conexiones guardadas")


@app.command()
@cache_required
@with_session
def ls(session: Session) -> None:
    """Listar todas las configuraciones de conexiones guardadas."""
    with console.status("Cargando conexiones..."):
        connections = repository.list(session)

        if not connections:
            console.print("[yellow]No hay conexiones guardadas[/]")
            return

        table = Table(title="Lista de conexiones")
        table.add_column("Nombre", justify="left")
        table.add_column("host", justify="left")
        table.add_column("port", justify="left")
        table.add_column("username", justify="left")

        for connection in connections:
            table.add_row(
                f"[magenta]{connection.name}[/]",
                f"{connection.host}",
                f"[cyan]{connection.port}[/]",
                f"[green]{connection.username}[/]",
            )

        console.print(table)


@app.command()
@cache_required
@with_session
def add(
    session: Session,
    name: str | None = typer.Option(None, "--name", "-n", help="Nombre de la conexión"),
    host: str | None = typer.Option(None, "--host", "-h", help="Host del servidor"),
    port: int | None = typer.Option(None, "--port", "-p", help="Puerto del servidor"),
    username: str | None = typer.Option(
        None, "--username", "-u", help="Usuario de SQL Server"
    ),
    password: str | None = typer.Option(
        None, "--password", "-pass", help="Contraseña de SQL Server"
    ),
) -> None:
    """Agregar una nueva configuración de conexión guardada."""
    connection_name = required_text(name, "Nombre de la conexión")
    connection_host = required_text(host, "Host")
    connection_port = required_int(port, "Puerto")
    connection_username = required_text(username, "Usuario")
    connection_password = required_text(password, "Contraseña", hide_input=True)

    with console.status("Guardando conexión..."):
        connection = Connection(
            name=connection_name,
            host=connection_host,
            port=connection_port,
            username=connection_username,
            password=connection_password,
        )
        result = repository.add(session, connection)
        if result is None:
            console.print(f"[red]Ya existe una conexión llamada {connection_name}[/]")
            raise typer.Exit(code=1)

    console.print(f"[green]Conexión guardada:[/] {connection_name}")


@app.command()
@cache_required
@confirm_destructive_action(
    lambda *args, **kwargs: (
        f"¿Eliminar la conexión {kwargs.get('name') or 'seleccionada'}?"
    )
)
@with_session
def rm(
    session: Session,
    name: str | None = typer.Option(
        None,
        "--name",
        "-n",
        help="Nombre de la conexión a eliminar",
        prompt=True,
        prompt_required=True,
    ),
) -> None:
    """Eliminar una configuración de conexión guardada."""
    name = required_text(name, "Nombre de la conexión a eliminar")

    with console.status("Eliminando conexión..."):
        result = repository.remove(session, name)
        if result is None:
            console.print(f"[red]No existe una conexión llamada {name}[/]")
            raise typer.Exit(code=1)
        console.print(f"[green]Conexión eliminada:[/] {name}")


@app.callback()
def callback(force: bool = False):
    confirm(force)
