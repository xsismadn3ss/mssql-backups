"""
Listado de utilidades para trabajar con MSSQL
"""

from urllib.parse import quote_plus

from sqlalchemy import Engine, create_engine

from mssql_backups.models.tables import Connection


def engine(config: Connection) -> Engine:
    driver = "ODBC Driver 18 for SQL Server"
    odbc_str = (
        f"DRIVER={{{driver}}};"
        f"SERVER={config.host},{config.port};"
        f"DATABASE=master;"
        f"UID={config.username};"
        f"PWD={config.password};"
        f"TrustServerCertificate=yes;"
        f"Encrypt=no;"
    )
    conn_str = f"mssql+pyodbc:///?odbc_connect={quote_plus(odbc_str)}"
    engine = create_engine(conn_str)
    return engine
