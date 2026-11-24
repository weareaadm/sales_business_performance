"""
python/phase3_dw.py
-------------------
Fase 3: Pobla dimensiones y FactSales en dw_demo1 de forma transaccional
e idempotente, y ejecuta los tests de Fase 3.
"""

import sys
from pathlib import Path

PYTHON_DIR = Path(__file__).resolve().parent
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from drivers.sqlserver import get_sql_connection
from run_staging import execute_sql_file
from test_runner import run_phase_tests


def run_phase_3():
    print("\n--- [Fase 3] Construcción de Dimensiones y FactSales ---")
    sql_dir = PYTHON_DIR.parent / "sql"

    conn = get_sql_connection()
    cursor = conn.cursor()
    try:
        prev_autocommit = conn.autocommit
        conn.autocommit = False
        try:
            execute_sql_file(cursor, conn, sql_dir / "02_dimensions.sql", commit=False)
            execute_sql_file(cursor, conn, sql_dir / "03_facts.sql", commit=False)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.autocommit = prev_autocommit

        print("✓ Fase 3 completada.")
        run_phase_tests("phase3_dw")
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    run_phase_3()