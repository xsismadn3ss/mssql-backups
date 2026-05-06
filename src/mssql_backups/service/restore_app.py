from typing import List

import click

from mssql_backups.models.models import (
    BackupConfig,
    ContainerConfig,
    DbConfig,
    DbConfigComplete,
)
from mssql_backups.service.config_service import ask_config, build_restore_config
from mssql_backups.service.files_service import get_files
from mssql_backups.utils.colors import (
    fore_green,
    fore_light_cyan,
    fore_light_green,
    fore_yellow,
    style_bright,
    style_dim,
)
from mssql_backups.utils.sql import build_restore_query, execute_sql_command


def restore_app():
    click.clear()
    config = ask_config()
    # Obtener archivos
    files: List[str] = []

    if len(config) == 2 and isinstance(config[1], ContainerConfig):
        files = get_files(config[1])
    elif len(config) == 1 and isinstance(config[0], DbConfigComplete):
        files = get_files(config[0])

    print(style_bright(fore_green("Archivos de backups encontrados:")))
    for file in files:
        print(fore_light_green(file))

    if len(files) == 0:
        print(fore_yellow("No se encontraron archivos de backups"))
        return

    # ----------
    # Obtener configuración de restauración
    c = config[1].model_dump() if len(config) == 2 else (config[0].model_dump())
    backup_config = BackupConfig(**c)

    # Iterar archivos
    for i in files:
        backup_path, data_dir, db_name = build_restore_config(backup_config, i)

        # Crear db config
        d = config[0].model_dump()
        db_config = DbConfig(**d)

        # crear query para restaurar
        query = build_restore_query(db_config, backup_path, data_dir, db_name)

        # Mostrando la consulta SQL a ejecutar
        print(f"\nRestaurando {backup_path} desde {backup_path}")
        print(fore_light_cyan(query))

        # Mostrar resultado al ejecutar el comando
        result = execute_sql_command(db_config, query)
        print(style_dim(fore_light_green(result)))

    print(style_bright(fore_green("\nRestauración completada")))
    print(
        fore_light_green("Se restauraron "),
        len(files),
        fore_light_cyan(" bases de datos"),
    )
