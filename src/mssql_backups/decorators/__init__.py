from functools import wraps

from mssql_backups.utils.local import get_db_path


def cache_required(func):
    """Decorador que verifica si la memoria caché existe antes de ejecutar la función.
    Utiliza este decorador para indicar que una función requiere la memoria caché para ejecutarse."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        db_path = get_db_path()
        if not db_path.exists():
            raise FileNotFoundError(f"Memoria caché no encontrada en {db_path}")
        return func(*args, **kwargs)

    return wrapper


def errror_hanlder(func):
    """Decorador principal que maneja errores y muestra mensajes de error en la consola para excepciones controladas y no controladas."""
    from rich.console import Console

    console = Console()

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as e:
            console.print(f"[bold red]Error:[/][red]\n{e}[/]\n")
            console.print(
                "[bold]Ayuda:[/] \nEjecuta [bold blue on cyan]mssql-backups cache init[/] para inicializar la memoria caché"
            )
        except Exception as e:
            console.print(f"Error inesperado: \n[red]{e}[/]")

    return wrapper
