import docker
from docker.models.containers import Container

from mssql_backups.models.tables import Backup


def get_container(config: Backup) -> Container:
    client = docker.from_env()

    if not config.is_container or config.container_name is None:
        raise ValueError("La configuración no corresponde a un contenedor")

    container = client.containers.get(config.container_name)
    return container


def list_container_files(config: Backup):
    container: Container = get_container(config)
    try:
        exec_result = container.exec_run(f"ls {config.backup_dir}")
        output = exec_result.output
        text = ""
        if isinstance(output, bytes):
            text = output.decode("utf-8")
        return text
    except Exception as e:
        print(f"Error al listar archivos en el contenedor: {e}")
