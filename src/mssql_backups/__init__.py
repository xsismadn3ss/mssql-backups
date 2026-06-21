import typer
from rich.console import Console

from mssql_backups.commands import commands_dict
from mssql_backups.config import AppConfig
from mssql_backups.decorators import error_handler

app = typer.Typer(
    help="""
    [bold cyan]MSSQL Backups[/]

    - Restaura bases de datos usando archivos .bak, especificando la ruta de la carpeta de backups
    - Crear backups de bases de datos
    """
)

# Mapear comandos y a la aplicación principal
for key, value in commands_dict().items():
    app.add_typer(value, name=key)


@app.command(name="version")
def version_info():
    """Version del cli"""
    version = AppConfig.version
    name = AppConfig.name

    console = Console()
    console.print(f"[dim]{name}[/] [green]{version}[/]")


@error_handler
def main():
    app()


if __name__ == "__main__":
    main()
