from typing import Literal

import docker
from docker.models.containers import Container

from mssql_backups.models.tables import Backup


def get_container(config: Backup) -> Container:
    client = docker.from_env()

    if not config.is_container or config.container_name is None:
        raise ValueError("La configuración no corresponde a un contenedor")

    container = client.containers.get(config.container_name)
    return container


def list_files(config: Backup, dir: Literal["backup_dir", "data_dir"]):
    container: Container = get_container(config)
    try:
        if dir == "backup_dir":
            path = config.backup_dir
        else:
            path = config.data_dir

        exec_result = container.exec_run(f"ls {path}")
        output = exec_result.output
        text = ""
        if isinstance(output, bytes):
            text = output.decode("utf-8")
        return text.splitlines()
    except Exception as e:
        print(f"Error al listar archivos en el contenedor: {e}")
