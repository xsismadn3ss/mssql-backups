import docker
from docker.models.containers import Container

from src.models.models import ContainerConfig


def get_container(container_config: ContainerConfig) -> Container:
    client = docker.from_env()

    container = client.containers.get(container_config.name)
    return container


def list_container_files(container_config: ContainerConfig):
    container: Container = get_container(container_config)
    try:
        exec_result = container.exec_run(f"ls {container_config.backup_dir}")
        return exec_result.output.decode()
    except Exception as e:
        print(f"Error al listar archivos en el contenedor: {e}")
