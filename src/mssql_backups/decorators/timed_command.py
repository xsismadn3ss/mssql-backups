from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from time import perf_counter
from typing import Any, Protocol

from mssql_backups.commands._common import console


class _LabelFactory(Protocol):
    def __call__(self, *args: Any, **kwargs: Any) -> str: ...


def timed_command(
    label: str | _LabelFactory | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Mide y muestra el tiempo total de ejecución de un comando."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any):
            started_at = perf_counter()
            try:
                return func(*args, **kwargs)
            finally:
                try:
                    if label is None:
                        resolved_label = None
                    elif isinstance(label, str):
                        resolved_label = label
                    else:
                        resolved_label = label(*args, **kwargs)
                except Exception:
                    resolved_label = None

                command_label = resolved_label or getattr(
                    func, "__name__", func.__class__.__name__
                ).replace("_", " ")
                elapsed = perf_counter() - started_at
                console.print(f"[dim]Duración de {command_label}: {elapsed:.2f}s[/]")

        return wrapper

    return decorator


__all__ = ["timed_command"]
