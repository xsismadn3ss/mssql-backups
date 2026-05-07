from __future__ import annotations

from pathlib import Path

from sqlalchemy import Engine, text
from sqlmodel import Session, select

from mssql_backups.constants.restore_db import SQL_COMMAND as RESTORE_DB
from mssql_backups.models.tables import Backup, Connection
from mssql_backups.service._common import console
from mssql_backups.utils.container import list_container_files


def get_connection(session: Session, name: str) -> Connection | None:
    statement = select(Connection).where(Connection.name == name)
    return session.exec(statement).first()


def get_backup(session: Session, name: str) -> Backup | None:
    statement = select(Backup).where(Backup.name == name)
    return session.exec(statement).first()


def list_backup_files(backup: Backup) -> list[str]:
    if backup.is_container:
        result = list_container_files(backup)
        if not result:
            return []
        return result.splitlines()

    backup_dir = Path(backup.backup_dir).expanduser()
    if not backup_dir.exists():
        raise FileNotFoundError(f"No existe la carpeta de backups: {backup.backup_dir}")

    return sorted(
        path.name
        for path in backup_dir.iterdir()
        if path.is_file() and path.suffix.lower() == ".bak"
    )


def print_files(files: list[str]) -> None:
    console.print("[bold cyan]Archivos de backups encontrados:[/]")
    if not files:
        console.print("[yellow]No se encontraron archivos de backups[/]")
        return

    for file_name in files:
        console.print(f"[green]{file_name}[/]")


def get_logical_names_from_backup(engine: Engine, backup_path: str):
    query = text(f"RESTORE FILELISTONLY FROM DISK = '{backup_path}'")
    with engine.begin() as conn:
        result = conn.execute(query).fetchall()
        return [row[0] for row in result]


def build_restore_query(
    backup_path: str, data_dir: str, db_name: str, name_data: str, name_log: str
) -> str:
    """
    Construye la instrucción RESTORE usando el archivo .bak real.
    """

    data_path = f"{data_dir}/{db_name}.mdf"
    log_path = f"{data_dir}/{db_name}_log.ldf"

    sql_command = RESTORE_DB.format(
        DB_NAME=db_name,
        BACKUP_PATH=backup_path,
        LOGICAL_NAME_DATA=name_data,
        DATA_PATH=data_path,
        LOGICAL_NAME_LOG=name_log,
        LOG_PATH=log_path,
    )
    return sql_command
