import uuid
from typing import List, Optional

from sqlmodel import Session, select

from mssql_backups.models.tables import Backup, DbName


def _get_bak(session: Session, bak: str) -> Optional[Backup]:
    return session.exec(select(Backup).where(Backup.name == bak)).one_or_none()


def _get_db_name(session: Session, backup_id: uuid.UUID, name: str) -> Optional[DbName]:
    return session.exec(
        select(DbName).where(DbName.backup_id == backup_id).where(DbName.name == name)
    ).one_or_none()


def ls(session: Session, bak: Optional[str]) -> list[DbName]:
    if bak is None:
        return list(session.exec(select(DbName).order_by(DbName.name)).all())

    backup = _get_bak(session, bak)
    if backup is None:
        return []

    return list(
        session.exec(
            select(DbName).where(DbName.backup_id == backup.id).order_by(DbName.name)
        ).all()
    )


def add(session: Session, bak: str, name: str) -> bool:
    backup = _get_bak(session, bak)
    if backup is None:
        return False

    if _get_db_name(session, backup.id, name) is not None:
        return False

    db_name = DbName(name=name, backup_id=backup.id)
    session.add(db_name)
    session.commit()
    return True


def add_all(session: Session, bak: str, names: List[str]):
    backup = _get_bak(session, bak)

    omitidos: List[str] = []
    agregados: List[str] = []

    if backup is None:
        return [], []

    seen: set[str] = set()
    for name in names:
        if name in seen:
            omitidos.append(name)
            continue
        seen.add(name)

        exists = _get_db_name(session, backup.id, name) is not None
        if exists:
            omitidos.append(name)
        else:
            db_name = DbName(name=name, backup_id=backup.id)
            session.add(db_name)
            agregados.append(name)

    if agregados:
        session.commit()
    return agregados, omitidos


def remove(session: Session, bak: str, name: str) -> bool:
    backup = _get_bak(session, bak)
    if backup is None:
        return False

    db_name = _get_db_name(session, backup.id, name)
    if db_name is None:
        return False

    session.delete(db_name)
    session.commit()
    return True


def remove_all(session: Session, bak: str, names: List[str]):
    backup = _get_bak(session, bak)

    if backup is None:
        return [], []

    omitidos: List[str] = []
    eliminados: List[str] = []
    seen: set[str] = set()

    for name in names:
        if name in seen:
            omitidos.append(name)
            continue
        seen.add(name)

        db = _get_db_name(session, backup.id, name)
        if db is None:
            omitidos.append(name)
        else:
            session.delete(db)
            eliminados.append(name)

    if eliminados:
        session.commit()
    return omitidos, eliminados
