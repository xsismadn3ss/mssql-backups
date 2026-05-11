from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager

import typer
from rich.console import Console
from sqlmodel import Session

from mssql_backups.utils.local import create_tables, get_engine

console = Console()


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    engine = get_engine()
    create_tables(engine)
    with Session(engine) as session:
        yield session   


def required_text(
    value: str | None, prompt_text: str, *, hide_input: bool = False
) -> str:
    candidate = value

    while True:
        if candidate is None:
            candidate = typer.prompt(prompt_text, hide_input=hide_input)

        candidate = candidate.strip()
        if candidate:
            return candidate

        console.print("[red]El valor no puede estar vacío[/]")
        candidate = None


def optional_text(value: str | None, prompt_text: str) -> str | None:
    candidate = value
    if candidate is None:
        candidate = typer.prompt(prompt_text, default="", show_default=False)

    candidate = candidate.strip()
    return candidate or None


def required_int(value: int | None, prompt_text: str) -> int:
    candidate = value

    while True:
        if candidate is None:
            candidate = typer.prompt(prompt_text, type=int)

        if candidate > 0:
            return candidate

        console.print("[red]El valor debe ser mayor que 0[/]")
        candidate = None


def required_bool(value: bool | None, prompt_text: str) -> bool:
    if value is None:
        return typer.confirm(prompt_text)

    return value
