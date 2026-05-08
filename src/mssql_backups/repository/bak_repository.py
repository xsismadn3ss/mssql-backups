from typing import Optional

from sqlmodel import Session, select

from mssql_backups.models.tables import Backup, Connection


def _get_conn(session: Session, conn: str) -> Optional[Connection]:
    return session.exec(select(Connection).where(Connection.name == conn)).one_or_none()


def _get_bak(session: Session, conn_id, name: str) -> Optional[Backup]:
    return session.exec(
        select(Backup).where(Backup.conn_id == conn_id).where(Backup.name == name)
    ).one_or_none()


def ls(session: Session, conn: Optional[str]) -> list[Backup]:
    if conn is None:
        return list(session.exec(select(Backup).order_by(Backup.name)).all())

    connection = _get_conn(session, conn)
    if connection is None:
        return []

    return list(
        session.exec(
            select(Backup).where(Backup.conn_id == connection.id).order_by(Backup.name)
        ).all()
    )


def add(session: Session, conn: str, bak: Backup) -> bool:
    connection = _get_conn(session, conn)
    if connection is None:
        return False

    if _get_bak(session, connection.id, bak.name) is not None:
        return False

    bak.conn_id = connection.id
    session.add(bak)
    session.commit()
    session.refresh(bak)
    return True


def rm(session: Session, conn: str, name: str) -> bool:
    connection = _get_conn(session, conn)
    if connection is None:
        return False

    existing = _get_bak(session, connection.id, name)
    if existing is None:
        return False

    session.delete(existing)
    session.commit()
    return True
