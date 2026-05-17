from __future__ import annotations

import inspect
from collections.abc import Callable
from functools import wraps
from typing import Any

from mssql_backups.commands._common import session_scope

from ._helpers import _signature_without


def with_session(
    func: Callable[..., Any] | None = None,
    *,
    session_param: str = "session",
) -> Callable[..., Any]:
    """Abre una sesión de SQLModel e inyecta la sesión en la función envuelta."""

    def decorator(inner: Callable[..., Any]) -> Callable[..., Any]:
        signature = inspect.signature(inner)
        if session_param not in signature.parameters:
            raise ValueError(
                f"with_session requiere un parámetro llamado '{session_param}'"
            )

        public_signature = _signature_without(signature, {session_param})

        @wraps(inner)
        def wrapper(*args, **kwargs):
            bound = signature.bind_partial(*args, **kwargs)

            if (
                session_param in bound.arguments
                and bound.arguments[session_param] is not None
            ):
                return inner(*args, **kwargs)

            with session_scope() as session:
                kwargs[session_param] = session
                return inner(*args, **kwargs)

        setattr(wrapper, "__signature__", public_signature)
        return wrapper

    return decorator if func is None else decorator(func)


transactional = with_session


__all__ = ["transactional", "with_session"]
