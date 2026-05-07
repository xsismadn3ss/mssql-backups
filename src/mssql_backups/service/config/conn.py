from __future__ import annotations

import typer
from sqlmodel import select

from mssql_backups.models.tables import Connection
from mssql_backups.service._common import (
    console,
    required_int,
    required_text,
    session_scope,
)

app = typer.Typer(help="Administrar conexiones guardadas")


@app.command()
def ls() -> None:
    with console.status("Cargando conexiones..."):
        with session_scope() as session:
            statement = select(Connection).order_by(Connection.name)
            connections = list(session.exec(statement).all())

        from ._common import print_connections

        print_connections(connections)


@app.command()
def add(
    name: str | None = typer.Option(None, "--name", help="Nombre de la conexión"),
    host: str | None = typer.Option(None, "--host", help="Host del servidor"),
    port: int | None = typer.Option(None, "--port", help="Puerto del servidor"),
    username: str | None = typer.Option(
        None, "--username", help="Usuario de SQL Server"
    ),
    password: str | None = typer.Option(
        None, "--password", help="Contraseña de SQL Server"
    ),
) -> None:
    connection_name = required_text(name, "Nombre de la conexión")
    connection_host = required_text(host, "Host")
    connection_port = required_int(port, "Puerto")
    connection_username = required_text(username, "Usuario")
    connection_password = required_text(password, "Contraseña", hide_input=True)

    with console.status("Guardando conexión..."):
        with session_scope() as session:
            existing = session.exec(
                select(Connection).where(Connection.name == connection_name)
            ).first()
            if existing is not None:
                console.print(
                    f"[red]Ya existe una conexión llamada {connection_name}[/]"
                )
                raise typer.Exit(code=1)

            connection = Connection(
                name=connection_name,
                host=connection_host,
                port=connection_port,
                username=connection_username,
                password=connection_password,
            )
            session.add(connection)
            session.commit()

        console.print(f"[green]Conexión guardada:[/] {connection_name}")


@app.command()
def rm(
    name: str | None = typer.Option(
        None, "--name", help="Nombre de la conexión a eliminar"
    ),
) -> None:
    connection_name = required_text(name, "Nombre de la conexión a eliminar")

    with console.status("Eliminando conexión..."):
        with session_scope() as session:
            connection = session.exec(
                select(Connection).where(Connection.name == connection_name)
            ).first()

            if connection is None:
                console.print(
                    f"[red]No existe una conexión llamada {connection_name}[/]"
                )
                raise typer.Exit(code=1)

            session.delete(connection)
            session.commit()

        console.print(f"[green]Conexión eliminada:[/] {connection_name}")
