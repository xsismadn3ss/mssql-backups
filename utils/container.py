import docker
from docker.models.containers import Container
from config.app import ContainerConfig, DbConfig


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


def execute_sql_in_container(
    container_config: ContainerConfig, db_config: DbConfig, sql_command: str
):
    container: Container = get_container(container_config)

    try:
        exec_result = container.exec_run(
            f'/opt/mssql-tools/bin/sqlcmd \
                -S {db_config.host} \
                -U {db_config.user} \
                -P {db_config.password} \
                -Q "{sql_command}"'
        )
        return exec_result.output.decode()
    except Exception as e:
        print(f"Error al ejecutar comando SQL en el contenedor: {e}")
