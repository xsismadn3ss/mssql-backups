from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from time import monotonic, sleep
from typing import Iterable

from mssql_backups.models.tables import Backup, Connection
from mssql_backups.repository import mssql_repository


class RestoreState(str, Enum):
    PREPARING = "preparing"
    RESTORING = "restoring"
    WAITING = "waiting"
    ONLINE = "online"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass(slots=True)
class RestoreResult:
    db_name: str
    state: RestoreState
    database_state: str | None = None
    message: str = ""
    attempts: int = 0
    elapsed_seconds: float = 0.0


class RestoreStateMachine:
    """Ejecuta el RESTORE y hace una verificación corta para confirmar ONLINE."""

    TRANSIENT_DATABASE_STATES = {"RESTORING", "RECOVERING", "RECOVERY_PENDING"}
    FAILURE_DATABASE_STATES = {"SUSPECT", "EMERGENCY", "OFFLINE"}

    def __init__(
        self,
        connection: Connection,
        *,
        poll_seconds: float = 1.0,
        timeout_seconds: int = 15,
    ) -> None:
        self.connection = connection
        self.poll_seconds = poll_seconds
        self.timeout_seconds = timeout_seconds

    def _backup_path(self, backup: Backup, file_name: str) -> str:
        return f"{backup.backup_dir}/{file_name}"

    def _db_name(self, file_name: str) -> str:
        return Path(file_name).stem

    def _get_db_state(self, db_name: str) -> str | None:
        state = mssql_repository.get_db_state(self.connection, db_name)
        return state[0] if state else None

    def _build_result(
        self,
        *,
        db_name: str,
        state: RestoreState,
        database_state: str | None,
        message: str,
        attempts: int,
        elapsed_seconds: float,
    ) -> RestoreResult:
        return RestoreResult(
            db_name=db_name,
            state=state,
            database_state=database_state,
            message=message,
            attempts=attempts,
            elapsed_seconds=elapsed_seconds,
        )

    def restore_file(
        self, backup: Backup, file_name: str, *, status=None
    ) -> RestoreResult:
        db_name = self._db_name(file_name)
        backup_path = self._backup_path(backup, file_name)
        start = monotonic()

        if status is not None:
            status.update(f"[cyan]Preparando restore de {db_name}[/]")

        try:
            logical_names = mssql_repository.get_logical_names(
                self.connection, backup_path
            )
        except Exception as error:
            return self._build_result(
                db_name=db_name,
                state=RestoreState.FAILED,
                database_state=None,
                message=f"No se pudieron leer los nombres lógicos del backup: {error}",
                attempts=0,
                elapsed_seconds=monotonic() - start,
            )

        try:
            if status is not None:
                status.update(f"[cyan]Ejecutando RESTORE de {db_name}...[/]")
            mssql_repository.restore_db(
                self.connection,
                backup_path,
                backup.data_dir,
                db_name,
                *logical_names,
            )
        except Exception as error:
            return self._build_result(
                db_name=db_name,
                state=RestoreState.FAILED,
                database_state=None,
                message=f"Falló la instrucción RESTORE: {error}",
                attempts=0,
                elapsed_seconds=monotonic() - start,
            )

        if status is not None:
            status.update(f"[cyan]Verificación breve de {db_name}...[/]")

        return self.wait_until_online(db_name, status=status, start_time=start)

    def wait_until_online(
        self,
        db_name: str,
        *,
        status=None,
        start_time: float | None = None,
    ) -> RestoreResult:
        started = monotonic() if start_time is None else start_time
        attempts = 0

        while True:
            database_state = self._get_db_state(db_name)
            normalized_state = database_state.upper() if database_state else None
            elapsed = monotonic() - started

            if normalized_state == "ONLINE":
                return self._build_result(
                    db_name=db_name,
                    state=RestoreState.ONLINE,
                    database_state=database_state,
                    message="La base de datos quedó ONLINE.",
                    attempts=attempts,
                    elapsed_seconds=elapsed,
                )

            if normalized_state in self.FAILURE_DATABASE_STATES:
                return self._build_result(
                    db_name=db_name,
                    state=RestoreState.FAILED,
                    database_state=database_state,
                    message=f"La base quedó en un estado no recuperable: {database_state}",
                    attempts=attempts,
                    elapsed_seconds=elapsed,
                )

            if (
                normalized_state is not None
                and normalized_state not in self.TRANSIENT_DATABASE_STATES
            ):
                return self._build_result(
                    db_name=db_name,
                    state=RestoreState.FAILED,
                    database_state=database_state,
                    message=f"La base quedó en un estado inesperado: {database_state}",
                    attempts=attempts,
                    elapsed_seconds=elapsed,
                )

            if elapsed >= self.timeout_seconds:
                return self._build_result(
                    db_name=db_name,
                    state=RestoreState.FAILED,
                    database_state=database_state,
                    message=(
                        f"No se pudo confirmar que {db_name} saliera de restauración en un tiempo corto. "
                        f"Estado actual: {database_state or 'desconocido'}"
                    ),
                    attempts=attempts,
                    elapsed_seconds=elapsed,
                )

            attempts += 1
            if status is not None:
                status.update(
                    f"[cyan]Esperando {db_name}... estado actual: {database_state or 'no visible'}[/]"
                )
            sleep(self.poll_seconds)

    def restore_all(
        self, backup: Backup, files: Iterable[str], *, status=None
    ) -> list[RestoreResult]:
        results: list[RestoreResult] = []
        for file_name in files:
            result = self.restore_file(backup, file_name, status=status)
            results.append(result)
        return results
