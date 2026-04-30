from typing import List

from src.models.models import ContainerConfig, DbConfigComplete
from src.utils.container import list_container_files
from src.utils.terminal import execute_command


def get_files(config: DbConfigComplete | ContainerConfig) -> List[str]:
    if isinstance(config, DbConfigComplete):
        command = ["ls ", config.backup_dir]
        output = str(execute_command(command))
        return output.splitlines()
    elif isinstance(config, ContainerConfig):
        output = str(list_container_files(config))
        return output.splitlines()
