"""
python/phase1_generate.py
-------------------------
Fase 1: Genera los archivos CSV en data/generated/ usando config.py.
"""

import sys
from pathlib import Path

PYTHON_DIR = Path(__file__).resolve().parent
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

import config
from generate.generate_customers import generate_customers
from generate.generate_products import generate_suppliers_and_products
from generate.generate_salespeople import generate_salespeople
from generate.generate_sales import generate_sales_data
from test_runner import run_phase_tests


def run_phase_1():
    print("\n--- [Fase 1] Generación de datos en Python ---")
    out_dir = config.OUTPUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    df_customers = generate_customers()
    df_customers.to_csv(out_dir / "customers.csv", index=False)

    df_suppliers, df_products = generate_suppliers_and_products()
    df_suppliers.to_csv(out_dir / "suppliers.csv", index=False)
    df_products.to_csv(out_dir / "products.csv", index=False)

    df_salespeople = generate_salespeople()
    df_salespeople.to_csv(out_dir / "salespeople.csv", index=False)

    df_orders, df_lines = generate_sales_data()
    df_orders.to_csv(out_dir / "sales_orders.csv", index=False)
    df_lines.to_csv(out_dir / "order_lines.csv", index=False)

    print(f"✓ CSVs generados en {out_dir} (Órdenes: {len(df_orders):,}, Líneas: {len(df_lines):,}).")

    # Ejecuta los tests correspondientes a Fase 1 dentro de la función
    run_phase_tests("phase1_generate")


if __name__ == "__main__":
    run_phase_1()