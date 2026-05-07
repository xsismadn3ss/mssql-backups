import uuid

from sqlmodel import Field, SQLModel


class Connection(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    name: str = Field(unique=True, index=True)
    host: str
    port: int
    username: str
    password: str


class Backup(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    name: str = Field(unique=True, index=True)
    description: str | None = Field(default=None, nullable=True)
    backup_dir: str = Field()
    data_dir: str = Field()
    is_container: bool = Field(default=False)
    container_name: str | None = Field(default=None, nullable=True)
