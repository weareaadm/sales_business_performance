"""
tests/phase1_generate/test_config.py
------------------------------------
Pruebas unitarias para validar la consistencia e integridad de las
configuraciones parametrizadas en config.py.
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


def test_total_orders_calculation():
    assert config.TOTAL_ORDERS == 150_000
    assert sum(config.ANNUAL_ORDER_TARGETS.values()) == 150_000


def test_monthly_weights_sum():
    total_weight = sum(config.MONTHLY_WEIGHTS.values())
    assert pytest.approx(total_weight, rel=1e-5) == 1.0


def test_salespeople_counts_sum():
    assert sum(config.REGION_SALESPERSON_COUNTS.values()) == config.TOTAL_SALESPEOPLE
    assert len(config.REGION_SALESPERSON_COUNTS) == len(config.REGIONS)


def test_product_categories_counts():
    total_products = sum(cat["product_count"] for cat in config.PRODUCT_CATEGORIES.values())
    total_suppliers = sum(cat["primary_supplier_count"] for cat in config.PRODUCT_CATEGORIES.values())

    assert total_products == config.TOTAL_PRODUCTS
    assert total_suppliers == config.TOTAL_SUPPLIERS


def test_customer_segments_weights():
    total_weight = sum(seg["weight"] for seg in config.CUSTOMER_SEGMENTS.values())
    assert pytest.approx(total_weight, rel=1e-5) == 1.0


def test_regions_and_warehouses_alignment():
    assert len(config.REGIONS) == 8
    assert len(config.WAREHOUSES) == 8

    for region in config.REGIONS:
        assert region["country"] == "Peru"

    region_ids_in_wh = {wh["region_id"] for wh in config.WAREHOUSES}
    region_ids = {r["region_id"] for r in config.REGIONS}
    assert region_ids_in_wh == region_ids