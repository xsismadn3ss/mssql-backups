from config.app import DbConfig, ContainerConfig
from utils.container import list_container_files, execute_sql_in_container
from constants.restore_db import SQL_COMMAND
from constants.test_db import SQL_COMMAND as TEST_SQL_COMMAND

def main():
    DbConfig.validate()  # validar configuración de la base de datos
    ContainerConfig.validate()

    # Listar archivos en el directorio de backup del contenedor
    backups: str = list_container_files(ContainerConfig.backup_dir)  # type: ignore
    files = backups.splitlines()

    result = execute_sql_in_container(ContainerConfig, DbConfig, sql_command=TEST_SQL_COMMAND) # type: ignore
    print(result)
    return

    for file in files:
        backup_path = f"{ContainerConfig.backup_dir}/{file}"

        database_name = file[:-4]
        logical_name_data = f"{database_name}_data"
        logical_name_log = f"{database_name}_log"
        data_path = f"{ContainerConfig.data_dir}/{database_name}.mdf"
        log_path = f"{ContainerConfig.data_dir}/{database_name}_log.ldf"

        sql_command = SQL_COMMAND.format(
            DB_NAME=database_name,
            BACKUP_PATH=backup_path,
            LOGICAL_NAME_DATA=logical_name_data,
            DATA_PATH=data_path,
            LOGICAL_NAME_LOG=logical_name_log,
            LOG_PATH=log_path,
        )

        # Ejecutar el comando SQL en el contenedor


if __name__ == "__main__":
    main()
