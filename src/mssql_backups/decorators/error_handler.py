from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import Any

from rich.console import Console


def errror_hanlder(func: Callable[..., Any]) -> Callable[..., Any]:
    """Maneja errores comunes de la CLI y muestra mensajes amigables."""
    console_local = Console()

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as e:
            console_local.print(f"[bold red]Error:[/][red]\n{e}[/]\n")
            console_local.print(
                "[bold]Ayuda:[/] \nEjecuta [bold blue on cyan]mssql-backups cache init[/] para inicializar la memoria caché"
            )
        except Exception as e:
            console_local.print(f"Error inesperado: \n[red]{e}[/]")

    return wrapper


error_handler = errror_hanlder


__all__ = ["errror_hanlder", "error_handler"]
