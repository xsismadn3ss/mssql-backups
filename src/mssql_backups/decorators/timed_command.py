from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from time import perf_counter
from typing import Any

from mssql_backups.service._common import console


def timed_command(
    label: str | Callable[..., str] | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Mide y muestra el tiempo total de ejecución de un comando."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args, **kwargs):
            started_at = perf_counter()
            try:
                return func(*args, **kwargs)
            finally:
                try:
                    resolved_label = (
                        label(*args, **kwargs) if callable(label) else label
                    )
                except Exception:
                    resolved_label = None

                command_label = resolved_label or func.__name__.replace("_", " ")
                elapsed = perf_counter() - started_at
                console.print(f"[dim]Duración de {command_label}: {elapsed:.2f}s[/]")

        return wrapper

    return decorator


__all__ = ["timed_command"]
