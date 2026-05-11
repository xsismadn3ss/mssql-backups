import typer

from mssql_backups import service
from mssql_backups.decorators import error_handler

app = typer.Typer(
    help="""
    [bold cyan]MSSQL Backups[/]

    - Restaura bases de datos usando archivos .bak, especificando la ruta de la carpeta de backups
    - Crear backups de bases de datos
    """
)

app.add_typer(service.config, name="config")
app.add_typer(service.restore, name="restore")
app.add_typer(service.cache, name="cache")
app.add_typer(service.db, name="db")
app.add_typer(service.bak, name="bak")


@error_handler
def main():
    app()


if __name__ == "__main__":
    main()
