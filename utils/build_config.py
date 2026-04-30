from getpass import getpass

import click

from models.models import BackupConfig, ContainerConfig, DbConfig, DbConfigComplete
from utils.colors import fore_green
from utils.int import int_try_parse


def build_db_config() -> DbConfig:
    user = input(fore_green("DB_USER: "))
    click.clear()
    password = getpass(fore_green("DB_PASSWORD: "))
    click.clear()
    host = input(fore_green("DB_HOST: "))
    click.clear()
    port = input(fore_green("DB_PORT: "))
    click.clear()

    config = DbConfig(
        user=user,
        password=password,
        host=host,
        port=int_try_parse(port),
    )
    return config


def build_backup_config() -> BackupConfig:
    backupdir = input(fore_green("BACKUP_DIR: "))
    click.clear()
    data_dir = input(fore_green("DATA_DIR: "))
    click.clear()

    config = BackupConfig(
        backup_dir=backupdir,
        data_dir=data_dir,
    )
    return config


def build_db_config_complete() -> DbConfigComplete:
    base_config = build_db_config()
    backup_config = build_backup_config()
    config = DbConfigComplete(
        **base_config.model_dump(),
        **backup_config.model_dump(),
    )
    return config


def build_container_config() -> ContainerConfig:
    name = input(fore_green("CONTAINER_NAME: "))
    click.clear()
    backup_config = build_backup_config()
    config = ContainerConfig(
        name=name,
        **backup_config.model_dump(),
    )
    return config
