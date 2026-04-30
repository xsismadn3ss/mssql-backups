from pydantic import BaseModel, Field


class DbConfig(BaseModel):
    user: str = Field(min_length=2)
    host: str = Field(min_length=2)
    port: int = Field(gt=0)
    password: str = Field(min_length=2)


class BackupConfig(BaseModel):
    backup_dir: str = Field(min_length=2)
    data_dir: str = Field(min_length=2)


class DbConfigComplete(DbConfig, BackupConfig): ...


class ContainerConfig(BackupConfig):
    name: str = Field(min_length=1)
