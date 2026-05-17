from __future__ import annotations

import inspect
from collections.abc import Callable
from functools import wraps
from typing import Any

import typer

from mssql_backups.repository import bak_repository, conn_repository
from mssql_backups.commands._common import console, session_scope

from ._helpers import _signature_without


def load_backup_context(
    func: Callable[..., Any] | None = None,
    *,
    conn_param: str = "conn",
    bak_param: str = "bak",
    connection_param: str = "connection",
    backup_param: str = "backup",
    db_names_param: str | None = None,
) -> Callable[..., Any]:
    """Carga una conexión y su backup desde la caché e inyecta los objetos."""

    def decorator(inner: Callable[..., Any]) -> Callable[..., Any]:
        signature = inspect.signature(inner)
        required_params = {conn_param, bak_param, connection_param, backup_param}
        hidden_params = {connection_param, backup_param}

        if db_names_param is not None:
            required_params.add(db_names_param)
            hidden_params.add(db_names_param)

        missing = required_params - set(signature.parameters)
        if missing:
            raise ValueError(
                f"load_backup_context requiere los parámetros: {', '.join(sorted(missing))}"
            )

        public_signature = _signature_without(signature, hidden_params)

        @wraps(inner)
        def wrapper(*args, **kwargs):
            bound = signature.bind_partial(*args, **kwargs)

            has_context = (
                connection_param in bound.arguments
                and bound.arguments[connection_param] is not None
                and backup_param in bound.arguments
                and bound.arguments[backup_param] is not None
            )
            if db_names_param is not None:
                has_context = has_context and db_names_param in bound.arguments

            if has_context:
                return inner(*args, **kwargs)

            if conn_param not in bound.arguments or bak_param not in bound.arguments:
                raise TypeError(
                    f"Se esperaban los argumentos '{conn_param}' y '{bak_param}' para cargar la configuración"
                )

            conn_value = bound.arguments[conn_param]
            bak_value = bound.arguments[bak_param]

            with session_scope() as session:
                connection = conn_repository.get(session, conn_value)
                if connection is None:
                    console.print(
                        f"[red]No existe una conexión llamada {conn_value}[/]"
                    )
                    raise typer.Exit(code=1)

                backup = bak_repository.get(session, conn_value, bak_value)
                if backup is None:
                    console.print(
                        f"[red]No existe una configuración de backup llamada {bak_value} para la conexión {conn_value}[/]"
                    )
                    raise typer.Exit(code=1)

                db_names = None
                if db_names_param is not None:
                    db_names = [db_name.name for db_name in backup.db_names]

            kwargs[connection_param] = connection
            kwargs[backup_param] = backup
            if db_names_param is not None:
                kwargs[db_names_param] = db_names
            return inner(*args, **kwargs)

        setattr(wrapper, "__signature__", public_signature)
        return wrapper

    return decorator if func is None else decorator(func)


__all__ = ["load_backup_context"]
