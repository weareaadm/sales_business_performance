"""
tests/phase1_generate/test_sales.py
-----------------------------------
Pruebas unitarias e integrales sobre las transacciones generadas en sales_orders y order_lines.
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
import pandas as pd
import config
from generate.generate_sales import generate_sales_data


@pytest.fixture(scope="module")
def sales_data():
    return generate_sales_data()


def test_sales_volume_and_integrity(sales_data):
    df_ord, df_lines = sales_data

    assert len(df_ord) == config.TOTAL_ORDERS
    assert df_ord["order_id"].nunique() == config.TOTAL_ORDERS
    assert df_lines["line_id"].nunique() == len(df_lines)
    assert set(df_lines["order_id"].unique()).issubset(set(df_ord["order_id"]))

    line_counts = df_lines.groupby("order_id")["line_id"].count()
    assert (line_counts >= config.MIN_LINES_PER_ORDER).all()
    assert (line_counts <= config.MAX_LINES_PER_ORDER).all()


def test_order_status_distribution_and_dates(sales_data):
    df_ord, _ = sales_data

    assert "status" in df_ord.columns
    expected_statuses = {"Completed", "Cancelled", "Pending"}
    assert set(df_ord["status"].unique()) == expected_statuses

    order_dt = pd.to_datetime(df_ord["order_date"])
    delivery_dt = pd.to_datetime(df_ord["delivery_date"])
    assert (delivery_dt >= order_dt).all()

    pending_mask = df_ord["status"] == "Pending"
    pending_dates = pd.to_datetime(df_ord.loc[pending_mask, "order_date"])
    assert ((pending_dates.dt.year == 2026) & (pending_dates.dt.month == 12)).all()

    dec_2026_mask = (order_dt.dt.year == 2026) & (order_dt.dt.month == 12)
    assert dec_2026_mask.any(), "No hay órdenes en diciembre de 2026"
    pending_rate_dec26 = pending_mask[dec_2026_mask].mean()
    assert 0.005 <= pending_rate_dec26 <= 0.05

    non_pending = df_ord.loc[~pending_mask, "status"]
    completed_rate = (non_pending == "Completed").mean()
    cancelled_rate = (non_pending == "Cancelled").mean()

    assert completed_rate == pytest.approx(0.95, abs=0.02)
    assert cancelled_rate == pytest.approx(0.05, abs=0.02)


def test_line_invariants_and_financial_reconciliation(sales_data):
    df_ord, df_lines = sales_data

    assert (df_lines["quantity"] > 0).all()
    assert (df_lines["unit_cost"] > 0).all()
    assert (df_lines["unit_price"] >= 0).all()
    assert ((df_lines["discount_rate"] >= 0.0) & (df_lines["discount_rate"] <= 1.0)).all()

    expected_subtotal = (
        df_lines["quantity"] * df_lines["unit_price"] * (1.0 - df_lines["discount_rate"])
    ).round(2)
    expected_cost = (df_lines["quantity"] * df_lines["unit_cost"]).round(2)

    assert (df_lines["line_subtotal"] - expected_subtotal).abs().max() <= 0.01 + 1e-6
    assert (df_lines["line_cost_total"] - expected_cost).abs().max() <= 0.01 + 1e-6

    grouped = df_lines.groupby("order_id").agg({
        "line_subtotal": "sum",
        "line_cost_total": "sum",
        "line_id": "count"
    }).reset_index()

    merged = pd.merge(df_ord, grouped, on="order_id")
    assert (merged["total_lines"] == merged["line_id"]).all()

    abs_diff_amount = round(float((merged["total_amount"] - merged["line_subtotal"]).abs().sum()), 2)
    abs_diff_cost = round(float((merged["total_cost"] - merged["line_cost_total"]).abs().sum()), 2)

    assert abs_diff_amount == 0.0
    assert abs_diff_cost == 0.0


def test_reproducibility_with_seed(sales_data):
    df_ord_1, df_lines_1 = sales_data
    df_ord_2, df_lines_2 = generate_sales_data()

    pd.testing.assert_frame_equal(df_ord_1, df_ord_2)
    pd.testing.assert_frame_equal(df_lines_1, df_lines_2)


if __name__ == "__main__":
    sys.exit(pytest.main(["-v", __file__]))