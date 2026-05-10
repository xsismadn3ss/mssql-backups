from pathlib import Path
from typing import List


def list_files(path: str) -> List[str]:
    dir = Path(path).expanduser()
    if not dir.exists():
        return []

    return sorted(path.name for path in dir.iterdir())


def create_dir(path: str) -> None:
    dir = Path(path).expanduser()
    dir.mkdir(parents=True, exist_ok=True)
