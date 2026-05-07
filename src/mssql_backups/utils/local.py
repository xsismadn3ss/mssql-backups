from pathlib import Path

from sqlmodel import SQLModel, create_engine


def get_db_path():
    base_dir = Path.home() / ".mssql-bakups"
    base_dir.mkdir(parents=True, exist_ok=True)
    db_path = base_dir / "config.db"
    return db_path


def get_engine():
    # Base de datos local con sqlite
    engine = create_engine(f"sqlite:///{get_db_path()}")
    return engine


def create_tables(engine):
    from mssql_backups.models import tables  # noqa: F401

    SQLModel.metadata.create_all(engine)
