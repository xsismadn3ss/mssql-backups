import typer
from rich.table import Table

from mssql_backups.repository import db_name_repository as repository
from mssql_backups.service._common import console, required_text, session_scope

app = typer.Typer(
    help="Manajear listado de nombres de bases de datos relacionadas con una conexion"
)


@app.command()
def ls(
    conn: str | None = typer.Option(
        None,
        "--conn",
        "-c",
        help="nombre de la conexion, filtra los resultados por este valor",
    ),
):
    """
    Listar nombres de bases de datos
    """

    with console.status("Cargando..."):
        with session_scope() as session:
            db_names = repository.list(session, conn)
            if len(db_names) == 0:
                console.print("[yellow]No se encontraron resultados[/]")
                return

            table = Table(title="Bases de datos")
            table.add_column("Nombre")
            table.add_column("conexion")
            for db_name in db_names:
                table.add_row(
                    f"[green]{db_name.name}[/]", f"[blue]{db_name.conn.name}[/]"
                )
            console.print(table)


@app.command()
def add(
    conn: str = typer.Option(..., "--conn", "-c", help="nombre de la conexion"),
    name: str = typer.Option(
        ...,
        "--name",
        "-n",
        help="nombre de la base de datos, tambien puede ser una lista de nombres separados por comas",
    ),
):
    """
    Agregar un nombre de base de datos para una conexion

    Tambien se pueden guardar multiples nombres de base de datos separados por comas
    """
    conn = required_text(conn, "Nombre de la conexion: ")
    name = required_text(name, "Nombre de la base de datos: ")

    names = name.split(",")
    names = [n.strip() for n in names]

    with session_scope() as session:
        if len(names) == 1:
            result = repository.add(session, conn, names[0])
            if result:
                console.print(f"[green]Agregado: {names[0]}[/]")
            else:
                console.print(f"[red]No se pudo agregar: {names[0]}[/]")
                raise typer.Exit(code=1)
        else:
            agregados, omitidos = repository.add_all(session, conn, names)
            if agregados:
                console.print(f"[green]Agregados: {', '.join(agregados)}[/]")
            if omitidos:
                console.print(f"[red]Omitidos: {', '.join(omitidos)}[/]")
                raise typer.Exit(code=1)


@app.command()
def rm(
    conn: str = typer.Option(None, "--conn", "-c", help="nombre de la conexion"),
    name: str = typer.Option(
        ...,
        "--name",
        "-n",
        help="nombre de la base de datos, tambien puede ser una lista de nombres separados por comas",
    ),
):
    """
    Eliminar un nombre de base de datos para una conexion

    Si se proporcionan multiples nombres separados por comas, se eliminaran todos los que existan en la conexion.
    """
    conn = required_text(conn, "Nombre de la conexion: ")
    name = required_text(name, "Nombre de la base de datos: ")

    names = name.split(",")
    names = [n.strip() for n in names]

    with session_scope() as session:
        if len(names) == 1:
            result = repository.remove(session, names[0], conn)
            if result:
                console.print(f"[green]Eliminado: {names[0]}[/]")
            else:
                console.print(f"[red]No se pudo eliminar: {names[0]}[/]")
        else:
            omitidos, eliminados = repository.remove_all(session, conn, names)

            if eliminados:
                console.print(f"[green]Eliminados: {', '.join(eliminados)}[/]")
            if omitidos:
                console.print(f"[red]Omitidos: {', '.join(omitidos)}[/]")
