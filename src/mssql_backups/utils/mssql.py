"""
Listado de utilidades para trabajar con MSSQL usando `sqlcmd`.
"""

from mssql_backups.models.tables import Connection


def sqlcmd_base_args(config: Connection) -> list[str]:
    """Construye los argumentos base de `sqlcmd` para conectarse a SQL Server."""
    server = f"{config.host},{config.port}"
    command = ["sqlcmd", "-S", server, "-d", "master", "-b", "-l", "30", "-C"]

    if config.username:
        command.extend(["-U", config.username, "-P", config.password])
    else:
        command.append("-E")

    return command


def engine(config: Connection) -> list[str]:
    """Compatibilidad temporal con el nombre anterior; ahora devuelve argumentos de `sqlcmd`."""
    return sqlcmd_base_args(config)
