import typer
from rich.console import Console

from mssql_backups.utils.local import create_tables, get_db_path, get_engine

app = typer.Typer(name="cache", help="Administrar cache de datos para configuración")


@app.command()
def init():
    console = Console()

    with console.status("Creando cache..."):
        db_path = get_db_path()
        engine = get_engine()
        create_tables(engine)
        console.print(f"[cyan]Cache creado en[/] [dim]{db_path}[/]")


@app.command()
def clean():
    base_dir = get_db_path().parent
    db_path = get_db_path()
    if db_path.exists():
        db_path.unlink()
    else:
        console = Console()
        console.print(
            f"[red]No se encontró el archivo de cache en[/] [dim]{db_path}[/]"
        )
        raise typer.Exit(1)
    if base_dir.exists():
        base_dir.rmdir()
    console = Console()
    console.print("[cyan]Cache eliminado[/]")
