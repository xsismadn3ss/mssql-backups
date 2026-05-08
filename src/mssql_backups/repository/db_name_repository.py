import uuid
from typing import List, Optional

from sqlmodel import Session, select

from mssql_backups.models.tables import Connection, DbName


def _get_conn_id(session: Session, conn: str) -> Optional[uuid.UUID]:
    return session.exec(
        select(Connection.id).where(Connection.name == conn)
    ).one_or_none()


def _get_db_name(session: Session, conn_id: uuid.UUID, name: str) -> Optional[str]:
    return session.exec(
        select(DbName.name).where(DbName.conn_id == conn_id).where(DbName.name == name)
    ).one_or_none()


def list(session: Session, conn: Optional[str]):
    if conn is None:
        return session.exec(select(DbName)).fetchall()

    conn_id = _get_conn_id(session, conn)

    if conn_id is None:
        return []
    statement = select(DbName).where(DbName.conn_id == conn_id)
    return session.exec(statement).fetchall()


def add(session: Session, conn: str, name: str):
    conn_id = session.exec(
        select(Connection.id).where(Connection.name == conn)
    ).one_or_none()

    if conn_id is None:
        return False

    if _get_db_name(session, conn_id, name) is not None:
        return False
    db_name = DbName(name=name, conn_id=conn_id)
    session.add(db_name)
    session.commit()


def add_all(session: Session, conn: str, names: List[str]):
    conn_id = session.exec(
        select(Connection.id).where(Connection.name == conn)
    ).one_or_none()

    omitidos: List[str] = []
    agregados: List[str] = []

    if conn_id is None:
        return [], []

    for name in names:
        exists = _get_db_name(session, conn_id, name) is not None
        if exists:
            omitidos.append(name)
        else:
            db_name = DbName(name=name, conn_id=conn_id)
            session.add(db_name)
            agregados.append(name)
    if len(agregados) > 0:
        session.commit()
    return agregados, omitidos


def remove(session: Session, name: str, conn: str):
    conn_id = _get_conn_id(session, conn)

    if conn_id is None:
        return False

    db_name = _get_db_name(session, conn_id, name)

    if db_name is None:
        return False
    session.delete(db_name)
    session.commit()
    return True


def remove_all(session: Session, conn: str, names: List[str]):
    conn_id = _get_conn_id(session, conn)

    if conn_id is None:
        return [], []

    omitidos: List[str] = []
    eliminados: List[str] = []

    for name in names:
        db = session.exec(
            select(DbName).where(DbName.conn_id == conn_id and DbName.name == name)
        ).first()
        if not db:
            omitidos.append(name)
        else:
            session.delete(db)
            eliminados.append(name)
    if len(eliminados) > 0:
        session.commit()
    return omitidos, eliminados
