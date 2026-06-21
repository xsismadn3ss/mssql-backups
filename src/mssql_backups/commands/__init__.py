from .bak import app as bak
from .cache import app as cache
from .config import app as config
from .db import app as db
from .restore import app as restore


def commands_dict():
    """Listado de comandos en formato de diccionario"""
    return {
        "bak": bak,
        "cache": cache,
        "config": config,
        "db": db,
        "restore": restore,
    }


__all__ = [
    "bak",
    "cache",
    "config",
    "db",
    "restore",
    "commands_dict",
]
