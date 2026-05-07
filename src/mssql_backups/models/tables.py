from sqlmodel import Field, SQLModel


class Connection(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    host: str
    port: int
    username: str
    password: str


class Backup(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    description: str | None = Field(default=None, nullable=True)
    backup_dir: str = Field()
    data_dir: str = Field()
    is_container: bool = Field(default=False)
