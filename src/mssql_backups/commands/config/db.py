import typer
from rich.table import Table
from sqlmodel import Session

from mssql_backups.callbacks import confirm
from mssql_backups.commands._common import console
from mssql_backups.commands.selectors import bak_selector, conn_selector, db_selector
from mssql_backups.decorators import (
    cache_required,
    confirm_destructive_action,
    with_session,
)
from mssql_backups.repository import bak_repository
from mssql_backups.repository import db_name_repository as repository

app = typer.Typer(
    help="Manajear nombres de bases de datos relacionados con configuraciones de backup"
)


@app.command()
@cache_required
@with_session
def ls(
    session: Session,
    bak: str | None = typer.Option(
        None,
        "--bak",
        "-b",
        help="nombre de la configuracion de backup, filtra los resultados por este valor",
    ),
    all: bool = typer.Option(
        False, "--all", "-a", help="Mostrar todas las bases de datos"
    ),
):
    """
    Listar nombres de bases de datos
    """
    if not bak and not all:
        bak = bak_selector.select_bak(session)

    with console.status("Cargando..."):
        db_names = repository.ls(session, bak)
        if len(db_names) == 0:
            console.print("[yellow]No hay configuración de bases de datos guardadas[/]")
            return

        table = Table(title="Bases de datos")
        table.add_column("Nombre")
        table.add_column("Backup")
        for db_name in db_names:
            backup_name = db_name.backup.name if db_name.backup else "-"
            conn_name = (
                db_name.backup.conn.name
                if db_name.backup and db_name.backup.conn
                else "-"
            )
            table.add_row(
                f"[green]{db_name.name}[/]", f"[blue]{backup_name} | {conn_name}[/]"
            )
        console.print(table)


@app.command()
@cache_required
@with_session
def add(
    session: Session,
    bak: str | None = typer.Option(
        None,
        "--bak",
        "-b",
        help="nombre de la configuracion de backup",
    ),
    conn: str | None = typer.Option(
        None,
        "--conn",
        "-c",
        help="nombre de la conexion",
    ),
    name: str = typer.Option(
        ...,
        "--name",
        "-n",
        help="nombre de la base de datos, tambien puede ser una lista de nombres separados por comas",
        prompt=True,
        prompt_required=True,
    ),
):
    """
    Agregar un nombre de base de datos para una configuracion de backup

    Tambien se pueden guardar multiples nombres de base de datos separados por comas
    """
    if not conn:
        conn = conn_selector.select_conn(session)
    if not bak:
        bak = bak_selector.select_bak(session, conn)

    names = [n.strip() for n in name.split(",") if n.strip()]

    backup = bak_repository.get(session, conn, bak)
    if backup is None:
        console.print(f"[red]No se pudo encontrar la configuracion de backup: {bak}[/]")
        raise typer.Exit(code=1)

    if len(names) == 1:
        result = repository.add(session, bak, names[0])
        if result:
            console.print(f"[green]Agregado: {names[0]}[/]")
        else:
            console.print(f"[red]No se pudo agregar: {names[0]}[/]")
            raise typer.Exit(code=1)
    else:
        agregados, omitidos = repository.add_all(session, bak, names)
        if agregados:
            console.print(f"[green]Agregados: {', '.join(agregados)}[/]")
        if omitidos:
            console.print(f"[red]Omitidos: {', '.join(omitidos)}[/]")
            raise typer.Exit(code=1)


@app.command()
@cache_required
@confirm_destructive_action(
    lambda *args, **kwargs: (
        f"¿Eliminar {kwargs.get('name') or 'las bases seleccionadas'} de la configuración {kwargs.get('bak') or 'seleccionada'}?"
    )
)
@with_session
def rm(
    session: Session,
    bak: str | None = typer.Option(
        None,
        "--bak",
        "-b",
        help="nombre de la configuracion de backup",
    ),
    name: str | None = typer.Option(
        None,
        "--name",
        "-n",
        help="nombre de la base de datos, tambien puede ser una lista de nombres separados por comas",
    ),
):
    """
    Eliminar un nombre de base de datos para una configuracion de backup

    Si se proporcionan multiples nombres separados por comas, se eliminaran todos los que existan en la configuracion de backup.
    """
    if not bak:
        bak = bak_selector.select_bak(session)

    if name:
        names = [n.strip() for n in name.split(",") if n.strip()]
    else:
        names = list(db_selector.select_dbs(session, bak))

    if len(names) == 1:
        result = repository.remove(session, bak, names[0])
        if result:
            console.print(f"[green]Eliminado: {names[0]}[/]")
        else:
            console.print(f"[red]No se pudo eliminar: {names[0]}[/]")
    else:
        omitidos, eliminados = repository.remove_all(session, bak, names)

        if eliminados:
            console.print(f"[green]Eliminados: {', '.join(eliminados)}[/]")
        if omitidos:
            console.print(f"[red]Omitidos: {', '.join(omitidos)}[/]")


@app.callback()
def callback(force: bool = False):
    confirm(force)
