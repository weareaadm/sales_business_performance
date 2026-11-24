"""
tests/phase1_generate/test_catalogs.py
--------------------------------------
Pruebas unitarias para validar la integridad referencial, unicidad y reglas
financieras básicas en los catálogos de clientes, proveedores y productos.
"""

import sys
from pathlib import Path

TESTS_PHASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TESTS_PHASE_DIR.parents[2]
PYTHON_DIR = PROJECT_ROOT / "python"

for p in (str(PROJECT_ROOT), str(PYTHON_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

import pytest
import config
from generate.generate_customers import generate_customers
from generate.generate_products import generate_suppliers_and_products


def test_customers_generation():
    df_cust = generate_customers()

    assert len(df_cust) == config.TOTAL_CUSTOMERS
    assert df_cust["customer_id"].nunique() == config.TOTAL_CUSTOMERS
    assert df_cust["tax_id"].nunique() == config.TOTAL_CUSTOMERS

    valid_region_ids = {r["region_id"] for r in config.REGIONS}
    assert set(df_cust["region_id"].unique()).issubset(valid_region_ids)


def test_suppliers_and_products_generation():
    df_sup, df_prod = generate_suppliers_and_products()

    assert len(df_sup) == config.TOTAL_SUPPLIERS
    assert len(df_prod) == config.TOTAL_PRODUCTS

    assert df_sup["supplier_id"].nunique() == config.TOTAL_SUPPLIERS
    assert df_prod["product_id"].nunique() == config.TOTAL_PRODUCTS
    assert df_prod["product_sku"].nunique() == config.TOTAL_PRODUCTS

    assert set(df_prod["supplier_id"].unique()).issubset(set(df_sup["supplier_id"]))
    assert (df_prod["unit_base_price"] > df_prod["unit_base_cost"]).all()


if __name__ == "__main__":
    sys.exit(pytest.main(["-v", __file__]))