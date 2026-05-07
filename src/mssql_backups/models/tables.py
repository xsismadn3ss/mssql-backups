import uuid
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class Connection(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    name: str = Field(unique=True, index=True)
    host: str
    port: int
    username: str
    password: str

    backups: List["Backup"] = Relationship(back_populates="conn")
    db_names: List["DbName"] = Relationship(back_populates="conn")


class Backup(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    name: str = Field(unique=True, index=True)
    description: str | None = Field(default=None, nullable=True)
    backup_dir: str = Field()
    data_dir: str = Field()
    is_container: bool = Field(default=False)
    container_name: str | None = Field(default=None, nullable=True)

    conn_id: Optional[uuid.UUID] = Field(foreign_key="connection.id", default=None)
    conn: Optional[Connection] = Relationship(back_populates="backups")


class DbName(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    name: str = Field(unique=True, index=True)

    conn_id: Optional[uuid.UUID] = Field(foreign_key="connection.id", default=None)
    conn: Optional[Connection] = Relationship(back_populates="db_names")
