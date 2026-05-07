from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import typer
from rich.console import Console
from sqlmodel import Session, select

from mssql_backups.models.models import BackupConfig, DbConfig
from mssql_backups.models.tables import Backup, Connection
from mssql_backups.utils.local import create_tables, get_engine


console = Console()


@contextmanager
def session_scope() -> Iterator[Session]:
	engine = get_engine()
	create_tables(engine)
	with Session(engine) as session:
		yield session


def required_text(value: str | None, prompt_text: str) -> str:
	candidate = value

	while True:
		if candidate is None:
			candidate = typer.prompt(prompt_text)

		candidate = candidate.strip()
		if candidate:
			return candidate

		console.print("[red]El valor no puede estar vacío[/]")
		candidate = None


def get_connection(session: Session, name: str) -> Connection | None:
	statement = select(Connection).where(Connection.name == name)
	return session.exec(statement).first()


def get_backup(session: Session, name: str) -> Backup | None:
	statement = select(Backup).where(Backup.name == name)
	return session.exec(statement).first()


def build_db_config(connection: Connection) -> DbConfig:
	return DbConfig(
		user=connection.username,
		host=connection.host,
		port=connection.port,
		password=connection.password,
	)


def build_backup_config(backup: Backup) -> BackupConfig:
	return BackupConfig(
		backup_dir=backup.backup_dir,
		data_dir=backup.data_dir,
	)


def list_backup_files(backup: Backup) -> list[str]:
	backup_dir = Path(backup.backup_dir).expanduser()
	if not backup_dir.exists():
		raise FileNotFoundError(f"No existe la carpeta de backups: {backup.backup_dir}")

	return sorted(
		path.name
		for path in backup_dir.iterdir()
		if path.is_file() and path.suffix.lower() == ".bak"
	)


def print_files(files: list[str]) -> None:
	console.print("[bold cyan]Archivos de backups encontrados:[/]")
	if not files:
		console.print("[yellow]No se encontraron archivos de backups[/]")
		return

	for file_name in files:
		console.print(f"[green]{file_name}[/]")