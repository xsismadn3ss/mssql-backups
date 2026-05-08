from sqlmodel import Session, select

from mssql_backups.models.tables import Connection


def list(session: Session):
    return session.exec(select(Connection).order_by(Connection.name)).all()


def _get(session: Session, name: str):
    return session.exec(
        select(Connection.name).where(Connection.name == name)
    ).one_or_none()


def get(session: Session, name: str):
    return session.exec(select(Connection).where(Connection.name == name)).first()


def add(session: Session, connection: Connection):
    if _get(session, connection.name):
        return
    session.add(connection)
    session.commit()
    session.refresh(connection)
    return connection


def remove(session: Session, name: str):
    if not _get(session, name):
        return
    connection = session.exec(select(Connection).where(Connection.name == name)).one()
    session.delete(connection)
    session.commit()
