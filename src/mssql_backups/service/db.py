import typer

from mssql_backups.repository import conn_repository, mssql_repository
from mssql_backups.service._common import console, session_scope
from mssql_backups.utils.mssql import engine

app = typer.Typer(help="Realizar pruebas rapidas de la conexion a la base de datos")


@app.command()
def test(
    conn: str = typer.Option(
        ...,
        "--conn",
        "-c",
        prompt_required=True,
        help="nombre de la conexion",
        prompt=True,
    ),
):
    """Validar conexion de la base de datos"""
    with session_scope() as session:
        # Obtener configuracion de conexion
        connection = conn_repository.get(session, conn)
        if not connection:
            console.print(f"[yellow]La conexion '{conn}' no existe[/]")
            raise typer.Exit(code=1)

    # Validar conexion a la base de datos
    with console.status(
        f"Validando conexion con [cyan]{connection.host}:{connection.port}({connection.name})[/]..."
    ):
        mssql_engine = engine(connection)
        if not mssql_repository.test_conn(mssql_engine):
            console.print("[red]Error: la conexion no es valida[/]")
            console.print("[dim]Asegurate de que la configuracion es correcta[/]")

            raise typer.Exit(code=1)
        else:
            console.print("[green]Conexion valida[/]")


@app.command()
def ls(
    conn: str = typer.Option(
        ...,
        "--conn",
        "-c",
        prompt_required=True,
        help="nombre de la conexion",
        prompt=True,
    ),
):
    """Listar las bases de datos para la conexion seleccionada"""
    with session_scope() as session:
        # Obtener configuracion de conexion
        connection = conn_repository.get(session, conn)
        if not connection:
            console.print(f"[yellow]La conexion '{conn}' no existe[/]")
            raise typer.Exit(code=1)

    # Obtener lista de bases de datos
    with console.status(
        f"Obteniendo lista de bases de datos para [cyan]{connection.host}:{connection.port}({connection.name})[/]..."
    ):
        mssql_engine = engine(connection)
        databases = mssql_repository.list_db(mssql_engine)
        if not databases:
            console.print("[yellow]No se encontraron bases de datos[/]")
            raise typer.Exit(code=1)

        console.print("[green]Bases de datos encontradas:[/]")
        for db in databases:
            console.print(f"  - {db[0]}")
