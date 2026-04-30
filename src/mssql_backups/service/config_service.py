from mssql_backups.models.models import (
    BackupConfig,
    ContainerConfig,
    DbConfig,
    DbConfigComplete,
)
from mssql_backups.utils.build_config import (
    build_container_config,
    build_db_config,
    build_db_config_complete,
)
from mssql_backups.utils.colors import style_bright
from mssql_backups.utils.int import int_try_parse


def ask_config() -> tuple[DbConfigComplete, ...] | tuple[DbConfig, ContainerConfig]:
    # preguntar si la base de datos esta en un contenedor local
    # o en una instancia remota
    db_option = int_try_parse(
        input(
            style_bright(
                "En que entorno esta la base de datos? \n(1: contenedor local, 2: instancia local): "
            )
        )
    )

    if db_option == 1:
        db_config = build_db_config()
        container_config = build_container_config()
        return db_config, container_config

    elif db_option == 2:
        config = tuple([build_db_config_complete()])
        return config
    else:
        raise ValueError("Opción no válida")


def build_restore_config(config: BackupConfig, file_name: str) -> tuple[str, str, str]:
    backup_path = f"{config.backup_dir}/{file_name}"
    database_name = file_name[:-4]
    data_dir = config.data_dir
    return backup_path, data_dir, database_name
