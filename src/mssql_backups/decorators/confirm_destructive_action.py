from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import Any

import typer

from mssql_backups.service._common import console


def confirm_destructive_action(
    message: str | Callable[..., str],
    *,
    cancel_message: str = "Operación cancelada",
    exit_code: int = 1,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Pide confirmación antes de ejecutar una acción destructiva."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                prompt = message(*args, **kwargs) if callable(message) else message
            except Exception:
                prompt = "¿Deseas continuar?"

            if not prompt:
                prompt = "¿Deseas continuar?"

            if not typer.confirm(prompt, default=False):
                console.print(f"[yellow]{cancel_message}[/]")
                raise typer.Exit(code=exit_code)

            return func(*args, **kwargs)

        return wrapper

    return decorator


__all__ = ["confirm_destructive_action"]
