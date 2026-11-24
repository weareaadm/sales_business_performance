"""
python/drivers/sqlserver.py
---------------------------
Driver de conexión centralizado para SQL Server. Lee credenciales desde
variables de entorno (.env o GitHub Actions Secrets) y crea la BD si no existe.
"""

import os
import re
import pyodbc
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


def _build_conn_str(server: str, port: str, database: str, username: str, password: str) -> str:
    return (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={server},{port};"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password};"
        f"TrustServerCertificate=yes;"
    )


def ensure_database_exists(database: str | None = None) -> str:
    server = os.getenv("MSSQL_SERVER", "localhost")
    port = os.getenv("MSSQL_PORT", "1433")
    target_db = database or os.getenv("MSSQL_DATABASE", "SAbupe")
    username = os.getenv("MSSQL_USER", "sa")
    password = os.getenv("MSSQL_SA_PASSWORD")

    if not password:
        raise ValueError(
            "✖ No se encontró la contraseña de SQL Server (MSSQL_SA_PASSWORD) en el entorno o .env."
        )

    if not re.match(r"^[A-Za-z0-9_]+$", target_db):
        raise ValueError(f"✖ Nombre de base de datos no válido: {target_db}")

    master_conn_str = _build_conn_str(server, port, "master", username, password)
    conn = pyodbc.connect(master_conn_str, autocommit=True)
    try:
        cursor = conn.cursor()
        cursor.execute(
            f"IF DB_ID(N'{target_db}') IS NULL CREATE DATABASE [{target_db}];"
        )
        cursor.close()
    finally:
        conn.close()

    return target_db


def get_sql_connection():
    """
    Crea la base de datos si no existe y retorna la conexión apuntando a ella.
    """
    server = os.getenv("MSSQL_SERVER", "localhost")
    port = os.getenv("MSSQL_PORT", "1433")
    username = os.getenv("MSSQL_USER", "sa")
    password = os.getenv("MSSQL_SA_PASSWORD")

    target_db = ensure_database_exists()
    connection_string = _build_conn_str(server, port, target_db, username, password)

    try:
        print(f"🔄 Intentando conectar a SQL Server en {server}:{port} (Base de datos: {target_db})...")
        conn = pyodbc.connect(connection_string, autocommit=True)
        print("✓ ¡Conexión establecida exitosamente con SQL Server!")
        return conn
    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        err_message = ex.args[1]
        print("✖ Error crítico al conectar con SQL Server:")
        print(f"  - SQLState: {sqlstate}")
        print(f"  - Detalle técnico: {err_message}")
        raise
    except Exception as e:
        print(f"✖ Ocurrió un error inesperado al intentar conectar: {e}")
        raise