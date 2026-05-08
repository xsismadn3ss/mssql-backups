from sqlalchemy import Connection as SQLAlchemyConnection
from sqlalchemy import Engine, text

from mssql_backups.constants.restore_db import SQL_COMMAND as RESTORE_DB


def test_conn(engine: Engine) -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def get_db_name(conn: SQLAlchemyConnection, name: str):
    return conn.execute(
        text("SELECT name FROM sys.databases WHERE name = :name"),
        parameters={"name": name},
    ).fetchone()


def list_db(engine: Engine):
    with engine.connect() as conn:
        return conn.execute(
            text("SELECT name FROM sys.databases"),
        ).fetchall()


def get_logical_names(engine: Engine, backup_path: str):
    query = text(f"RESTORE FILELISTONLY FROM DISK = '{backup_path}'")
    with engine.begin() as conn:
        result = conn.execute(query).fetchall()
        return [row[0] for row in result]


def restore_db(
    engine: Engine,
    backup_path: str,
    data_dir: str,
    db_name: str,
    name_data: str,
    name_log: str,
):
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

    with engine.connect().execution_options(
        isolation_level="AUTOCOMMIT"
    ) as mssql_connection:
        mssql_connection.exec_driver_sql(sql_command)
