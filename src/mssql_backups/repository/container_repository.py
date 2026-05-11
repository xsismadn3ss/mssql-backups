from __future__ import annotations

import shlex
from collections.abc import Iterable
from typing import Literal

import docker
from docker.models.containers import Container

from mssql_backups.models.tables import Backup


def _decode_output(output: bytes | str | Iterable[bytes]) -> str:
    if isinstance(output, bytes):
        return output.decode("utf-8")
    if isinstance(output, str):
        return output
    return b"".join(output).decode("utf-8")


def _normalize_extension(extension: str | None) -> str | None:
    if extension is None:
        return None

    normalized = extension.strip().lower()
    if not normalized:
        return None

    if not normalized.startswith("."):
        normalized = f".{normalized}"

    return normalized


def _matches_extension(file_name: str, extension: str | None) -> bool:
    normalized = _normalize_extension(extension)
    if normalized is None:
        return True

    return file_name.lower().endswith(normalized)


def get_container(config: Backup) -> Container:
    client = docker.from_env()

    if not config.is_container or config.container_name is None:
        raise ValueError("La configuración no corresponde a un contenedor")

    container = client.containers.get(config.container_name)
    return container


def list_files(
    config: Backup,
    dir: Literal["backup_dir", "data_dir"],
    extension: str | None = None,
) -> list[str]:
    container: Container = get_container(config)
    try:
        path = config.backup_dir if dir == "backup_dir" else config.data_dir

        exec_result = container.exec_run(["sh", "-lc", f"ls -1 {shlex.quote(path)}"])
        if exec_result.exit_code != 0:
            raise RuntimeError(_decode_output(exec_result.output))

        text = _decode_output(exec_result.output)
        files = [line.strip() for line in text.splitlines() if line.strip()]
        return sorted(
            [
                file_name
                for file_name in files
                if _matches_extension(file_name, extension)
            ],
            key=str.lower,
        )
    except Exception as e:
        print(f"Error al listar archivos en el contenedor: {e}")
        return []


def list_files_with_size(
    config: Backup,
    dir: Literal["backup_dir", "data_dir"],
    extension: str | None = None,
) -> list[tuple[str, int]]:
    container: Container = get_container(config)
    try:
        path = config.backup_dir if dir == "backup_dir" else config.data_dir
        newline = chr(10)
        command = f"find {shlex.quote(path)} -type f -printf '%P|%s{newline}'"

        exec_result = container.exec_run(["sh", "-lc", command])
        if exec_result.exit_code != 0:
            raise RuntimeError(_decode_output(exec_result.output))

        text = _decode_output(exec_result.output)
        files: list[tuple[str, int]] = []

        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue

            file_name, size_text = line.split("|", 1)
            file_name = file_name.strip()

            if not _matches_extension(file_name, extension):
                continue

            try:
                size_bytes = int(size_text.strip())
            except ValueError:
                continue

            files.append((file_name, size_bytes))

        return sorted(files, key=lambda item: item[0].lower())
    except Exception as e:
        print(f"Error al listar archivos con tamaño en el contenedor: {e}")
        return []


def create_dir(config: Backup, path: str):
    container: Container = get_container(config)
    try:
        exec_result = container.exec_run(["sh", "-lc", f"mkdir -p {shlex.quote(path)}"])
        if exec_result.exit_code != 0:
            print(f"Error al crear directorio en el contenedor: {exec_result.output}")
            return False
        return True
    except Exception as e:
        print(f"Error al crear directorio en el contenedor: {e}")
        return False
