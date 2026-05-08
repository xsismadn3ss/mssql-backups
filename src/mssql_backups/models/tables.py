import uuid
from typing import List, Optional

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel


class Connection(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    name: str = Field(unique=True, index=True)
    host: str
    port: int
    username: str
    password: str

    backups: List["Backup"] = Relationship(
        back_populates="conn",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class Backup(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("conn_id", "name"),)

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    name: str = Field(index=True)
    description: str | None = Field(default=None, nullable=True)
    backup_dir: str = Field()
    data_dir: str = Field()
    is_container: bool = Field(default=False)
    container_name: str | None = Field(default=None, nullable=True)

    conn_id: Optional[uuid.UUID] = Field(foreign_key="connection.id", default=None)
    conn: Optional[Connection] = Relationship(back_populates="backups")

    db_names: List["DbName"] = Relationship(
        back_populates="backup",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class DbName(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("backup_id", "name"),)

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    name: str = Field(index=True)

    backup_id: Optional[uuid.UUID] = Field(foreign_key="backup.id", default=None)
    backup: Optional[Backup] = Relationship(back_populates="db_names")
