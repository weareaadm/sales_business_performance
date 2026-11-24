"""
python/phase4_validate.py
-------------------------
Fase 4: Ejecuta validaciones SQL (04_analysis.sql) y la suite de pruebas
de calidad y reconciliación Staging <-> DW antes de pasar a DAX / Power BI.
"""

import sys
from pathlib import Path

PYTHON_DIR = Path(__file__).resolve().parent
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from drivers.sqlserver import get_sql_connection
from run_staging import execute_sql_file
from test_runner import run_phase_tests


def run_phase_4():
    print("\n--- [Fase 4] Validación SQL previa a Power BI / DAX ---")
    sql_dir = PYTHON_DIR.parent / "sql"

    conn = get_sql_connection()
    cursor = conn.cursor()
    try:
        execute_sql_file(cursor, conn, sql_dir / "04_analysis.sql")
        print("✓ Fase 4 completada.")
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()

    run_phase_tests("phase4_validation")


if __name__ == "__main__":
    run_phase_4()