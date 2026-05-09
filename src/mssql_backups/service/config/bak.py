from __future__ import annotations

import typer
from rich.table import Table

from mssql_backups.models.tables import Backup
from mssql_backups.repository import bak_repository as repository
from mssql_backups.service._common import (
    RequiredOption,
    console,
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
                console.print("[yellow]No hay configuración de backups guardados[/]")
                return

            table = Table(title="Configuraciones de backups")
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
    conn: str = RequiredOption(
        ...,
        "--conn",
        "-c",
        help="Nombre de la conexión",
    ),
    bak: str = RequiredOption(
        ...,
        "--name",
        "-n",
        help="Nombre del backup",
    ),
    description: str = RequiredOption(
        ...,
        "--description",
        "-d",
        help="Descripción del backup",
    ),
    backup_dir: str = RequiredOption(
        ...,
        "--backup-dir",
        "-bdir",
        help="Directorio de backups",
    ),
    data_dir: str = RequiredOption(
        ...,
        "--data-dir",
        "-ddir",
        help="Directorio de datos",
    ),
    is_container: bool = typer.Option(
        ...,
        "--is-container/--no-is-container",
        "-ic",
        help="Indica si el backup se guarda en un contenedor",
        prompt=True,
        prompt_required=True,
    ),
    container_name: str = typer.Option(
        ...,
        "--container-name",
        "-cn",
        help="Nombre del contenedor",
        prompt=True,
        prompt_required=True,
    ),
) -> None:
    is_container = required_bool(is_container, "¿El backup está en un contenedor?")

    if is_container:
        container_name_value = required_text(container_name, "Nombre del contenedor")
    else:
        container_name_value = None

    with console.status("Guardando configuración"):
        with session_scope() as session:
            backup = Backup(
                name=bak,
                description=description,
                backup_dir=backup_dir,
                data_dir=data_dir,
                is_container=is_container,
                container_name=container_name_value,
            )
            result = repository.add(session, conn, backup)
            if result:
                console.print(f"[green]Backup guardado:[/] {bak}")
                return

            console.print(
                f"[red]No se pudo guardar el backup {bak} para la conexión {conn}[/]"
            )
            raise typer.Exit(code=1)


@app.command()
def rm(
    conn: str = RequiredOption(..., "--conn", "-c", help="Nombre de la conexión"),
    bak: str = RequiredOption(..., "--bak", "-b", help="Nombre del backup a eliminar"),
) -> None:

    with console.status("Eliminando backup..."):
        with session_scope() as session:
            result = repository.rm(session, conn, bak)
            if result:
                console.print(f"[green]Backup eliminado:[/] {bak}")
                return

            console.print(
                f"[red]No existe un backup llamado {bak} para la conexión {conn}[/]"
            )
            raise typer.Exit(code=1)
