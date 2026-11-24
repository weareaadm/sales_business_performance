"""
python/phase2_staging.py
------------------------
Fase 2: Crea esquemas/tablas, carga dimensiones estáticas y CSVs en stg_demo1
bajo una estrategia transaccional unificada, y ejecuta los tests de Fase 2.
"""

import sys
from pathlib import Path

PYTHON_DIR = Path(__file__).resolve().parent
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from drivers.sqlserver import get_sql_connection
from run_staging import execute_sql_file, load_csv_to_table
from test_runner import run_phase_tests

STAGING_CSV_MAPPINGS = [
    ("salespeople.csv", "stg_demo1.salespeople"),
    ("suppliers.csv", "stg_demo1.suppliers"),
    ("products.csv", "stg_demo1.products"),
    ("customers.csv", "stg_demo1.customers"),
    ("sales_orders.csv", "stg_demo1.sales_orders"),
    ("order_lines.csv", "stg_demo1.sales_order_lines"),
]


def run_phase_2():
    print("\n--- [Fase 2] Creación de tablas y carga a Staging ---")
    base_dir = PYTHON_DIR.parent
    sql_dir = base_dir / "sql"
    data_dir = base_dir / "data" / "generated"

    conn = get_sql_connection()
    cursor = conn.cursor()
    try:
        # 1. DDL de esquemas/tablas (operaciones DDL en SQL Server)
        execute_sql_file(cursor, conn, sql_dir / "01_create_schema_and_tables.sql", commit=True)

        # 2. Carga DML unificada de dimensiones estáticas + 6 CSVs antes de confirmar
        prev_autocommit = conn.autocommit
        conn.autocommit = False
        try:
            execute_sql_file(cursor, conn, sql_dir / "01_staging.sql", commit=False)
            for csv_file, table in STAGING_CSV_MAPPINGS:
                load_csv_to_table(cursor, conn, data_dir / csv_file, table, commit=False)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.autocommit = prev_autocommit

        print("✓ Fase 2 completada.")
        run_phase_tests("phase2_staging")
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    run_phase_2()