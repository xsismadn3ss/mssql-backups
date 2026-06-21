from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    version: str = "3.14.0"
    name: str = "MSSQL Backups"
