from __future__ import annotations

import inspect
from collections.abc import Callable
from functools import wraps
from typing import Any, Protocol

import typer

from mssql_backups.context import ctx
from mssql_backups.commands._common import console


class _PromptFactory(Protocol):
    def __call__(self, *args: Any, **kwargs: Any) -> str: ...


def confirm_destructive_action(
    message: str | _PromptFactory,
    *,
    cancel_message: str = "Operación cancelada",
    exit_code: int = 1,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Pide confirmación antes de ejecutar una acción destructiva.

    Comprueba en el siguiente orden si se debe omitir la confirmación:
    1. Si la función llamada recibe un argumento `force` y su valor es truthy.
    2. Si el diccionario global `mssql_backups.context.ctx` contiene
       alguna clave truthy en `("force", "yes", "y", "assume_yes", "non_interactive")`.

    Esto permite definir una opción global `--force` en el callback principal
    que actualice `mssql_backups.context.ctx["force"] = True` y así omitir
    los prompts en todos los comandos.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any):
            # Detectar si se debe forzar la acción sin confirmación.
            force_flag = False

            # 1) Intentar ligar args/kwargs con la firma para detectar
            #    un parámetro llamado "force" incluso si fue pasado posicionalmente.
            try:
                sig = inspect.signature(func)
                bound = sig.bind_partial(*args, **kwargs)
                if "force" in bound.arguments:
                    force_flag = bool(bound.arguments.get("force"))
            except Exception:
                # Si falla, mirar directamente en kwargs.
                force_flag = bool(kwargs.get("force", False))

            # 2) Si no se encontró en los argumentos, comprobar el contexto
            #    global definido en `mssql_backups.context.ctx`.
            if not force_flag:
                try:
                    for name in ("force", "yes", "y", "assume_yes", "non_interactive"):
                        if bool(ctx.get(name, False)):
                            force_flag = True
                            break
                except Exception:
                    # Si por alguna razón el contexto no está disponible,
                    # continuar con la confirmación interactiva.
                    pass

            if force_flag:
                return func(*args, **kwargs)

            # Construir el prompt y pedir confirmación.
            try:
                prompt = (
                    message if isinstance(message, str) else message(*args, **kwargs)
                )
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
