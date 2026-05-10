from __future__ import annotations

import subprocess

from mssql_backups.constants.restore_db import SQL_COMMAND as RESTORE_DB
from mssql_backups.models.tables import Connection
from mssql_backups.utils.mssql import sqlcmd_base_args
from mssql_backups.utils.terminal import execute_command


def _sql_literal(value: str) -> str:
    return value.replace("'", "''")


def _sql_identifier(value: str) -> str:
    return value.replace("]", "]]")


def _run_sqlcmd(
    connection: Connection,
    query: str,
    *,
    stream_output: bool = False,
    extra_args: list[str] | None = None,
) -> str:
    command = sqlcmd_base_args(connection)
    if extra_args:
        command.extend(extra_args)
    command.extend(["-Q", query])
    try:
        return execute_command(command, stream_output=stream_output)
    except subprocess.CalledProcessError as error:
        output = error.output or ""
        raise RuntimeError(
            f"sqlcmd falló con código {error.returncode}. Salida:\n{output}"
        ) from error


def _single_value_query(connection: Connection, query: str) -> str | None:
    output = _run_sqlcmd(
        connection,
        f"SET NOCOUNT ON; {query}",
        stream_output=False,
        extra_args=["-h", "-1", "-W"],
    )
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    return lines[0] if lines else None


def _read_filelist_output(output: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue
        cols = [part.strip().strip('"') for part in line.split(",")]
        if len(cols) >= 3:
            rows.append(cols)
    return rows


def test_conn(connection: Connection) -> bool:
    try:
        result = _run_sqlcmd(
            connection,
            "SET NOCOUNT ON; SELECT 1;",
            stream_output=False,
            extra_args=["-h", "-1", "-W"],
        )
        return "1" in result.split()
    except Exception:
        return False


def get_db_name(_connection: Connection, _name: str) -> None:
    raise NotImplementedError("Use sqlcmd-based helpers with Connection objects.")


def list_db(connection: Connection) -> list[tuple[str]]:
    output = _run_sqlcmd(
        connection,
        "SET NOCOUNT ON; SELECT name FROM sys.databases ORDER BY name;",
        stream_output=False,
        extra_args=["-h", "-1", "-W"],
    )
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    return [(line,) for line in lines]


def get_db_state(connection: Connection, name: str) -> tuple[str] | None:
    state = _single_value_query(
        connection,
        f"SELECT state_desc FROM sys.databases WHERE name = '{_sql_literal(name)}'",
    )
    return (state,) if state is not None else None


def get_logical_names(connection: Connection, backup_path: str) -> tuple[str, str]:
    query = f"RESTORE FILELISTONLY FROM DISK = '{_sql_literal(backup_path)}'"
    output = _run_sqlcmd(
        connection,
        query,
        stream_output=False,
        extra_args=["-s", ",", "-W", "-h", "-1"],
    )
    rows = _read_filelist_output(output)

    logical_data = None
    logical_log = None

    for row in rows:
        logical_name = row[0]
        file_type = row[2].upper() if len(row) > 2 else ""
        if file_type == "L":
            logical_log = logical_name
        elif logical_data is None:
            logical_data = logical_name

    if not logical_data or not logical_log:
        raise ValueError(
            f"No se pudieron determinar los nombres lógicos en el backup: {backup_path}. Salida:\n{output}"
        )

    return logical_data, logical_log


def restore_db(
    connection: Connection,
    backup_path: str,
    data_dir: str,
    db_name: str,
    name_data: str,
    name_log: str,
) -> None:
    data_path = f"{data_dir}/{db_name}.mdf"
    log_path = f"{data_dir}/{db_name}_log.ldf"

    sql_command = RESTORE_DB.format(
        DB_NAME=_sql_identifier(db_name),
        BACKUP_PATH=_sql_literal(backup_path),
        LOGICAL_NAME_DATA=_sql_literal(name_data),
        DATA_PATH=_sql_literal(data_path),
        LOGICAL_NAME_LOG=_sql_literal(name_log),
        LOG_PATH=_sql_literal(log_path),
    )

    _run_sqlcmd(connection, sql_command, stream_output=True)


def backup_db(
    connection: Connection,
    path: str,
    db_name: str,
) -> None:
    query = (
        f"BACKUP DATABASE [{_sql_identifier(db_name)}] "
        f"TO DISK = '{_sql_literal(path)}' WITH INIT;"
    )
    _run_sqlcmd(connection, query, stream_output=True)
