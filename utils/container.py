import docker
from docker.models.containers import Container

from config.app import ContainerConfig


def get_container(container_config: ContainerConfig) -> Container:
    client = docker.from_env()

    container = client.containers.get(container_config.name)
    return container


def list_container_files(path: str):
    container: Container = get_container(ContainerConfig())
    try:
        exec_result = container.exec_run(f"ls {path}")
        return exec_result.output.decode()
    except Exception as e:
        print(f"Error al listar archivos en el contenedor: {e}")
