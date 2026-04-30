from typing import Dict, List, Tuple

from ..constants.restore_db import SQL_COMMAND as RESTORE_DB
from ..models.models import DbConfig
from ..utils.terminal import execute_command


def _parse_filelist_output(output: str) -> List[Dict[str, str]]:
    """
    Parsea la salida CSV-like de `sqlcmd -s"," -W -h -1` para RESTORE FILELISTONLY.
    Devuelve lista de dict con keys: LogicalName, PhysicalName, Type (D/L), ...
    """
    rows = []
    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue
        # dividir en columnas por coma (las rutas pueden contener comas raras, pero en la mayoría de casos funciona)
        cols = [c.strip() for c in line.split(",")]
        # columnas esperadas: LogicalName, PhysicalName, Type, [...]
        if len(cols) >= 3:
            rows.append(
                {
                    "LogicalName": cols[0].strip('"'),
                    "PhysicalName": cols[1].strip('"'),
                    "Type": cols[2].strip('"'),
                }
            )
    return rows


def get_logical_names_from_backup(
    config: DbConfig, backup_path: str
) -> Tuple[str, str]:
    """
    Ejecuta RESTORE FILELISTONLY y devuelve (logical_data_name, logical_log_name).
    Lanza ValueError si no encuentra ambos.
    """
    query = f"RESTORE FILELISTONLY FROM DISK = '{backup_path}'"
    cmd = [
        "sqlcmd",
        "-S",
        config.host,
        "-U",
        config.user,
        "-P",
        config.password,
        "-Q",
        query,
        "-s",
        ",",  # separador
        "-W",  # quitar padding
        "-h",
        "-1",  # no headers
    ]
    output = execute_command(cmd)
    rows = _parse_filelist_output(output)

    logical_data = None
    logical_log = None

    for r in rows:
        t = r.get("Type", "").upper()
        if t == "L":
            logical_log = r["LogicalName"]
        else:
            # cualquier cosa distinta de L la consideramos data (D)
            if logical_data is None:
                logical_data = r["LogicalName"]

    if not logical_data or not logical_log:
        raise ValueError(
            f"No se pudieron determinar los nombres lógicos en el backup: {backup_path}. Salida:\n{output}"
        )

    return logical_data, logical_log


def build_restore_query(
    config: DbConfig, backup_path: str, data_dir: str, db_name: str
) -> str:
    """
    Construye la instrucción RESTORE usando los nombres lógicos reales del backup.
    """
    logical_name_data, logical_name_log = get_logical_names_from_backup(
        config, backup_path
    )

    data_path = f"{data_dir}/{db_name}.mdf"
    log_path = f"{data_dir}/{db_name}_log.ldf"

    sql_command = RESTORE_DB.format(
        DB_NAME=db_name,
        BACKUP_PATH=backup_path,
        LOGICAL_NAME_DATA=logical_name_data,
        DATA_PATH=data_path,
        LOGICAL_NAME_LOG=logical_name_log,
        LOG_PATH=log_path,
    )
    return sql_command


def execute_sql_command(config: DbConfig, sql: str) -> str:
    """
    Ejecuta `sql` usando sqlcmd (lista de argumentos, no shell) para evitar problemas
    con comillas y saltos de línea.
    """
    cmd = [
        "sqlcmd",
        "-S",
        config.host,
        "-U",
        config.user,
        "-P",
        config.password,
        "-Q",
        sql,
    ]
    return execute_command(cmd)
