from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import Any

from mssql_backups.utils.local import get_db_path


def cache_required(func: Callable[..., Any]) -> Callable[..., Any]:
    """Verifica que la caché local exista antes de ejecutar la función."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        db_path = get_db_path()
        if not db_path.exists():
            raise FileNotFoundError(f"Memoria caché no encontrada: {db_path}")
        return func(*args, **kwargs)

    return wrapper


cache_exists = cache_required


__all__ = ["cache_exists", "cache_required"]
