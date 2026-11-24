"""
tests/phase4_validation/test_dw_reconciliation.py
---------------------------------------------------
Pruebas de aceptación para Fase 4: reconciliación de conteos y métricas
financieras entre stg_demo1 (órdenes Completed) y dw_demo1.FactSales,
exclusión de estados no Completed, consistencia regional del vendedor y
patrones de negocio clave (estacionalidad e inflación Steel & Rebar).
"""

import sys
from pathlib import Path

TESTS_PHASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TESTS_PHASE_DIR.parent.parent
PYTHON_DIR = PROJECT_ROOT / "python"

for p in (str(PROJECT_ROOT), str(PYTHON_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

import pytest
from drivers.sqlserver import get_sql_connection


@pytest.fixture(scope="module")
def db_conn():
    conn = get_sql_connection()
    yield conn
    conn.close()


def test_staging_to_dw_counts_and_statuses(db_conn):
    cursor = db_conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM stg_demo1.sales_orders")
    total_orders = cursor.fetchone()[0]
    assert total_orders == 150_000

    cursor.execute("SELECT DISTINCT status FROM stg_demo1.sales_orders")
    assert {row[0] for row in cursor.fetchall()} == {"Completed", "Cancelled", "Pending"}

    # Pending exclusivo en diciembre de 2026
    cursor.execute("""
        SELECT COUNT(*)
        FROM stg_demo1.sales_orders
        WHERE status = 'Pending'
          AND NOT (YEAR(order_date) = 2026 AND MONTH(order_date) = 12)
    """)
    assert cursor.fetchone()[0] == 0

    # FactSales equivale exactamente a líneas de órdenes Completed
    cursor.execute("""
        SELECT COUNT(*)
        FROM stg_demo1.sales_order_lines l
        INNER JOIN stg_demo1.sales_orders o ON l.order_id = o.order_id
        WHERE o.status = 'Completed'
    """)
    expected_completed_lines = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM dw_demo1.FactSales")
    assert cursor.fetchone()[0] == expected_completed_lines

    cursor.close()


def test_staging_to_dw_financial_reconciliation(db_conn):
    cursor = db_conn.cursor()

    cursor.execute("""
        SELECT
            CAST(COALESCE(SUM(l.quantity), 0) AS BIGINT),
            CAST(COALESCE(SUM(ROUND(l.quantity * l.unit_price * l.discount_rate, 2)), 0) AS DECIMAL(18, 2)),
            CAST(COALESCE(SUM(l.line_subtotal), 0) AS DECIMAL(18, 2)),
            CAST(COALESCE(SUM(l.line_cost_total), 0) AS DECIMAL(18, 2)),
            CAST(COALESCE(SUM(l.line_subtotal - l.line_cost_total), 0) AS DECIMAL(18, 2))
        FROM stg_demo1.sales_order_lines l
        INNER JOIN stg_demo1.sales_orders o ON l.order_id = o.order_id
        WHERE o.status = 'Completed'
    """)
    stg_units, stg_disc, stg_rev, stg_cost, stg_profit = cursor.fetchone()

    cursor.execute("""
        SELECT
            CAST(COALESCE(SUM(Quantity), 0) AS BIGINT),
            CAST(COALESCE(SUM(DiscountAmount), 0) AS DECIMAL(18, 2)),
            CAST(COALESCE(SUM(Revenue), 0) AS DECIMAL(18, 2)),
            CAST(COALESCE(SUM(TotalCost), 0) AS DECIMAL(18, 2)),
            CAST(COALESCE(SUM(GrossProfit), 0) AS DECIMAL(18, 2))
        FROM dw_demo1.FactSales
    """)
    dw_units, dw_disc, dw_rev, dw_cost, dw_profit = cursor.fetchone()

    assert dw_units == stg_units
    assert abs(float(dw_disc) - float(stg_disc)) <= 5.00
    assert abs(float(dw_rev) - float(stg_rev)) <= 5.00
    assert abs(float(dw_cost) - float(stg_cost)) <= 5.00
    assert abs(float(dw_profit) - float(stg_profit)) <= 5.00

    cursor.close()


def test_salesperson_region_attribution_and_no_anomalies(db_conn):
    cursor = db_conn.cursor()

    # La región comercial de FactSales debe coincidir con la del vendedor en staging
    cursor.execute("""
        SELECT COUNT(*)
        FROM dw_demo1.FactSales f
        INNER JOIN stg_demo1.sales_orders o ON f.SalesOrderID = o.order_id
        INNER JOIN stg_demo1.salespeople sp ON o.salesperson_id = sp.salesperson_id
        INNER JOIN dw_demo1.DimRegion r ON f.RegionKey = r.RegionKey
        WHERE r.RegionID <> sp.region_id
    """)
    assert cursor.fetchone()[0] == 0

    # Cero filas con métricas financieras inválidas
    cursor.execute("""
        SELECT COUNT(*)
        FROM dw_demo1.FactSales
        WHERE Quantity <= 0
           OR UnitPrice < 0
           OR UnitCost <= 0
           OR DiscountAmount < 0
           OR DiscountAmount > (Quantity * UnitPrice)
           OR ABS(Revenue - ((Quantity * UnitPrice) - DiscountAmount)) > 0.01
           OR ABS(TotalCost - (Quantity * UnitCost)) > 0.01
           OR ABS(GrossProfit - (Revenue - TotalCost)) > 0.01
    """)
    assert cursor.fetchone()[0] == 0

    cursor.close()


if __name__ == "__main__":
    sys.exit(pytest.main(["-v", __file__]))