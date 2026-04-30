from abc import ABC
from dataclasses import dataclass
from os import getenv

from dotenv import load_dotenv

load_dotenv()  # Cargar variables de entorno desde el archivo .env


class ABCConfig(ABC):
    @classmethod
    def validate(cls) -> None:
        pass


@dataclass(frozen=True)
class DbConfig(ABCConfig):
    user = getenv("DB_USER", None)
    password = getenv("DB_PASSWORD", None)
    host = getenv("DB_HOST", None)
    port = int(getenv("DB_PORT", 0))

    @classmethod
    def validate(cls):
        if cls.user is None:
            raise ValueError("DB_USER no está definido")
        if cls.password is None:
            raise ValueError("DB_PASSWORD no está definido")
        if cls.host is None:
            raise ValueError("DB_HOST no está definido")
        if cls.port == 0:
            raise ValueError("DB_PORT no está definido o es inválido")


@dataclass(frozen=True)
class ContainerConfig(ABCConfig):
    name: str = getenv("CONTAINER_NAME", None)  # type: ignore
    backup_dir: str = getenv("CONTAINER_BACKUP_DIR", None)  # type: ignore
    data_dir: str = getenv("CONTAINER_DATA_DIR", None)  # type: ignore

    @classmethod
    def validate(cls) -> None:
        if cls.name is None:
            raise ValueError("CONTAINER_NAME no está definido")
        if cls.backup_dir is None:
            raise ValueError("CONTAINER_BACKUP_DIR no está definido")
        if cls.data_dir is None:
            raise ValueError("CONTAINER_DATA_DIR no está definido")
