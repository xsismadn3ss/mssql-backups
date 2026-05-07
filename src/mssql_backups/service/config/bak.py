from __future__ import annotations

import typer
from sqlmodel import select

from mssql_backups.models.tables import Backup
from mssql_backups.service._common import (
    console,
    optional_text,
    required_bool,
    required_text,
    session_scope,
)

from ._common import print_backups

app = typer.Typer(help="Administrar backups guardados")


@app.command()
def ls() -> None:
    with console.status("Cargando backups"):
        with session_scope() as session:
            statement = select(Backup).order_by(Backup.name)
            backups = list(session.exec(statement).all())

        print_backups(backups)


@app.command()
def add(
    name: str | None = typer.Option(None, "--name", help="Nombre del backup"),
    description: str | None = typer.Option(
        None, "--description", help="Descripción del backup"
    ),
    backup_dir: str | None = typer.Option(
        None, "--backup-dir", help="Directorio de backups"
    ),
    data_dir: str | None = typer.Option(None, "--data-dir", help="Directorio de datos"),
    is_container: bool | None = typer.Option(
        None,
        "--is-container/--no-is-container",
        help="Indica si el backup se guarda en un contenedor",
    ),
    container_name: str | None = typer.Option(
        None, "--container-name", help="Nombre del contenedor"
    ),
) -> None:
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
            existing = session.exec(
                select(Backup).where(Backup.name == backup_name)
            ).first()
            if existing is not None:
                console.print(f"[red]Ya existe un backup llamado {backup_name}[/]")
                raise typer.Exit(code=1)

            backup = Backup(
                name=backup_name,
                description=backup_description,
                backup_dir=backup_directory,
                data_dir=data_directory,
                is_container=container_flag,
                container_name=container_name_value,
            )
            session.add(backup)
            session.commit()
        console.print(f"[green]Backup guardado:[/] {backup_name}")


@app.command()
def rm(
    name: str | None = typer.Option(
        None, "--name", help="Nombre del backup a eliminar"
    ),
) -> None:
    backup_name = required_text(name, "Nombre del backup a eliminar")

    with console.status("Eliminando backup..."):
        with session_scope() as session:
            backup = session.exec(
                select(Backup).where(Backup.name == backup_name)
            ).first()

            if backup is None:
                console.print(f"[red]No existe un backup llamado {backup_name}[/]")
                raise typer.Exit(code=1)

            session.delete(backup)
            session.commit()

        console.print(f"[green]Backup eliminado:[/] {backup_name}")
