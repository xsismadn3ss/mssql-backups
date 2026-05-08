from __future__ import annotations

import typer
from rich.table import Table

from mssql_backups.models.tables import Backup
from mssql_backups.repository import bak_repository as repository
from mssql_backups.service._common import (
    console,
    optional_text,
    required_bool,
    required_text,
    session_scope,
)

app = typer.Typer(help="Administrar configuración de backups")


@app.command()
def ls(
    conn: str | None = typer.Option(None, "--conn", "-c", help="Nombre de la conexión"),
) -> None:
    """Listar configuración de backups guardados"""
    with console.status("Cargando backups"):
        with session_scope() as session:
            backups = repository.ls(session, conn)

            if not backups:
                console.print("[red]No se encontraron resultados[/]")
                raise typer.Exit(code=1)

            table = Table(title="Lista de backups")
            table.add_column("Nombre", justify="left")
            table.add_column("Conexión", justify="left")
            table.add_column("Descripción", justify="left")
            table.add_column("backup_dir", justify="left")
            table.add_column("data_dir", justify="left")
            table.add_column("contenedor", justify="left")

            for backup in backups:
                table.add_row(
                    f"[magenta]{backup.name}[/]",
                    f"[magenta]{backup.conn.name}[/]" if backup.conn else "",
                    backup.description or "",
                    f"[cyan]{backup.backup_dir}[/]",
                    f"[cyan]{backup.data_dir}[/]",
                    f"[blue]{backup.container_name}[/]" or "",
                )

            console.print(table)


@app.command()
def add(
    conn: str | None = typer.Option(None, "--conn", "-c", help="Nombre de la conexión"),
    name: str | None = typer.Option(None, "--name", "-n", help="Nombre del backup"),
    description: str | None = typer.Option(
        None, "--description", "-d", help="Descripción del backup"
    ),
    backup_dir: str | None = typer.Option(
        None, "--backup-dir", "-bdir", help="Directorio de backups"
    ),
    data_dir: str | None = typer.Option(
        None, "--data-dir", "-ddir", help="Directorio de datos"
    ),
    is_container: bool | None = typer.Option(
        None,
        "--is-container/--no-is-container",
        "-ic",
        help="Indica si el backup se guarda en un contenedor",
    ),
    container_name: str | None = typer.Option(
        None, "--container-name", "-cn", help="Nombre del contenedor"
    ),
) -> None:
    conn_name = required_text(conn, "Nombre de la conexión")
    backup_name = required_text(name, "Nombre del backup")
    backup_description = optional_text(description, "Descripción del backup")
    backup_directory = required_text(backup_dir, "Directorio de backups")
    data_directory = required_text(data_dir, "Directorio de datos")
    container_flag = required_bool(is_container, "¿El backup está en un contenedor?")

    if container_flag:
        container_name_value = required_text(container_name, "Nombre del contenedor")
    else:
        container_name_value = None

    with console.status("Guardando configuración"):
        with session_scope() as session:
            backup = Backup(
                name=backup_name,
                description=backup_description,
                backup_dir=backup_directory,
                data_dir=data_directory,
                is_container=container_flag,
                container_name=container_name_value,
            )
            result = repository.add(session, conn_name, backup)
            if result:
                console.print(f"[green]Backup guardado:[/] {backup_name}")
                return

            console.print(
                f"[red]No se pudo guardar el backup {backup_name} para la conexión {conn_name}[/]"
            )
            raise typer.Exit(code=1)


@app.command()
def rm(
    conn: str | None = typer.Option(None, "--conn", help="Nombre de la conexión"),
    name: str | None = typer.Option(
        None, "--name", help="Nombre del backup a eliminar"
    ),
) -> None:
    conn_name = required_text(conn, "Nombre de la conexión")
    backup_name = required_text(name, "Nombre del backup a eliminar")

    with console.status("Eliminando backup..."):
        with session_scope() as session:
            result = repository.rm(session, conn_name, backup_name)
            if result:
                console.print(f"[green]Backup eliminado:[/] {backup_name}")
                return

            console.print(
                f"[red]No existe un backup llamado {backup_name} para la conexión {conn_name}[/]"
            )
            raise typer.Exit(code=1)
