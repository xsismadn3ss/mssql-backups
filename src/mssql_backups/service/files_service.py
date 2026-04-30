from typing import List

from mssql_backups.models.models import ContainerConfig, DbConfigComplete
from mssql_backups.utils.container import list_container_files
from mssql_backups.utils.terminal import execute_command


def get_files(config: DbConfigComplete | ContainerConfig) -> List[str]:
    if isinstance(config, DbConfigComplete):
        command = ["ls ", config.backup_dir]
        output = str(execute_command(command))
        return output.splitlines()
    elif isinstance(config, ContainerConfig):
        output = str(list_container_files(config))
        return output.splitlines()
