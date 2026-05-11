from __future__ import annotations

import inspect
from collections.abc import Callable
from functools import wraps
from typing import Any

import typer

from mssql_backups.repository import conn_repository
from mssql_backups.service._common import console, session_scope

from ._helpers import _signature_without


def load_connection_context(
    func: Callable[..., Any] | None = None,
    *,
    conn_param: str = "conn",
    connection_param: str = "connection",
) -> Callable[..., Any]:
    """Carga una conexión desde la caché e inyecta el objeto resultante."""

    def decorator(inner: Callable[..., Any]) -> Callable[..., Any]:
        signature = inspect.signature(inner)
        required_params = {conn_param, connection_param}
        missing = required_params - set(signature.parameters)
        if missing:
            raise ValueError(
                f"load_connection_context requiere los parámetros: {', '.join(sorted(missing))}"
            )

        public_signature = _signature_without(signature, {connection_param})

        @wraps(inner)
        def wrapper(*args, **kwargs):
            bound = signature.bind_partial(*args, **kwargs)

            if (
                connection_param in bound.arguments
                and bound.arguments[connection_param] is not None
            ):
                return inner(*args, **kwargs)

            if conn_param not in bound.arguments or bound.arguments[conn_param] is None:
                raise TypeError(
                    f"Se esperaba el argumento '{conn_param}' para cargar la conexión"
                )

            conn_value = bound.arguments[conn_param]
            with session_scope() as session:
                connection = conn_repository.get(session, conn_value)
                if connection is None:
                    console.print(
                        f"[red]No existe una conexión llamada {conn_value}[/]"
                    )
                    raise typer.Exit(code=1)

            kwargs[connection_param] = connection
            return inner(*args, **kwargs)

        setattr(wrapper, "__signature__", public_signature)
        return wrapper

    return decorator if func is None else decorator(func)


__all__ = ["load_connection_context"]
