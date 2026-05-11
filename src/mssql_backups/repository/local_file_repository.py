from __future__ import annotations

from pathlib import Path


def _normalize_extension(extension: str | None) -> str | None:
    if extension is None:
        return None

    normalized = extension.strip().lower()
    if not normalized:
        return None

    if not normalized.startswith("."):
        normalized = f".{normalized}"

    return normalized


def _matches_extension(file_path: Path, extension: str | None) -> bool:
    normalized = _normalize_extension(extension)
    if normalized is None:
        return True

    return file_path.suffix.lower() == normalized


def list_files(path: str, extension: str | None = None) -> list[str]:
    dir_path = Path(path).expanduser()
    if not dir_path.exists() or not dir_path.is_dir():
        return []

    files = [
        file_path.name
        for file_path in dir_path.iterdir()
        if file_path.is_file() and _matches_extension(file_path, extension)
    ]
    return sorted(files, key=str.lower)


def list_files_with_size(
    path: str, extension: str | None = None
) -> list[tuple[str, int]]:
    dir_path = Path(path).expanduser()
    if not dir_path.exists() or not dir_path.is_dir():
        return []

    files: list[tuple[str, int]] = []
    for file_path in dir_path.rglob("*"):
        if not file_path.is_file():
            continue

        if not _matches_extension(file_path, extension):
            continue

        try:
            size_bytes = file_path.stat().st_size
        except OSError:
            continue

        files.append((file_path.relative_to(dir_path).as_posix(), size_bytes))

    return sorted(files, key=lambda item: item[0].lower())


def create_dir(path: str) -> None:
    dir_path = Path(path).expanduser()
    dir_path.mkdir(parents=True, exist_ok=True)
