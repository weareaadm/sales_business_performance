"""
tests/phase3_dw/test_dw_star_schema.py
---------------------------------------
Pruebas de aceptación para Fase 3: dimensiones, FactSales, exclusión de
órdenes no Completed, métricas financieras e idempotencia en dw_demo1.
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
import config
from drivers.sqlserver import get_sql_connection
from run_staging import execute_sql_file


@pytest.fixture(scope="module")
def db_conn():
    conn = get_sql_connection()
    yield conn
    conn.close()


def test_dw_tables_exist_and_dimensions_populated(db_conn):
    cursor = db_conn.cursor()

    expected_dw = {
        "DimDate",
        "DimRegion",
        "DimWarehouse",
        "DimCustomer",
        "DimSalesperson",
        "DimProduct",
        "FactSales",
    }
    cursor.execute("""
        SELECT TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = 'dw_demo1'
    """)
    assert expected_dw.issubset({row[0] for row in cursor.fetchall()})

    cursor.execute("SELECT COUNT(*) FROM dw_demo1.DimRegion")
    assert cursor.fetchone()[0] == len(config.REGIONS)

    cursor.execute("SELECT COUNT(*) FROM dw_demo1.DimWarehouse")
    assert cursor.fetchone()[0] == len(config.WAREHOUSES)

    cursor.execute("SELECT COUNT(*) FROM dw_demo1.DimCustomer")
    assert cursor.fetchone()[0] == config.TOTAL_CUSTOMERS

    cursor.execute("SELECT COUNT(*) FROM dw_demo1.DimSalesperson")
    assert cursor.fetchone()[0] == config.TOTAL_SALESPEOPLE

    cursor.execute("SELECT COUNT(*) FROM dw_demo1.DimProduct")
    assert cursor.fetchone()[0] == config.TOTAL_PRODUCTS

    cursor.execute("SELECT COUNT(*) FROM dw_demo1.DimDate WHERE FullDate BETWEEN '2024-01-01' AND '2026-12-31'")
    assert cursor.fetchone()[0] == 1096

    cursor.close()


def test_dw_keys_uniqueness_and_completed_only_filter(db_conn):
    cursor = db_conn.cursor()

    pk_checks = [
        ("dw_demo1.DimRegion", "RegionKey", "RegionID"),
        ("dw_demo1.DimWarehouse", "WarehouseKey", "WarehouseID"),
        ("dw_demo1.DimCustomer", "CustomerKey", "CustomerID"),
        ("dw_demo1.DimSalesperson", "SalespersonKey", "SalespersonID"),
        ("dw_demo1.DimProduct", "ProductKey", "ProductID"),
        ("dw_demo1.DimDate", "DateKey", "FullDate"),
        ("dw_demo1.FactSales", "SalesOrderLineID", "SalesOrderLineID"),
    ]
    for tbl, sk, bk in pk_checks:
        cursor.execute(f"SELECT COUNT(*) FROM {tbl} WHERE {sk} IS NULL OR {bk} IS NULL")
        assert cursor.fetchone()[0] == 0

        cursor.execute(f"SELECT COUNT(*) - COUNT(DISTINCT {sk}) FROM {tbl}")
        assert cursor.fetchone()[0] == 0

        cursor.execute(f"SELECT COUNT(*) - COUNT(DISTINCT {bk}) FROM {tbl}")
        assert cursor.fetchone()[0] == 0

    cursor.execute("""
        SELECT COUNT(*)
        FROM stg_demo1.sales_order_lines l
        INNER JOIN stg_demo1.sales_orders o ON l.order_id = o.order_id
        WHERE o.status = 'Completed'
    """)
    expected_completed_lines = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM dw_demo1.FactSales")
    assert cursor.fetchone()[0] == expected_completed_lines

    cursor.execute("""
        SELECT COUNT(*)
        FROM dw_demo1.FactSales f
        INNER JOIN stg_demo1.sales_orders o ON f.SalesOrderID = o.order_id
        WHERE o.status <> 'Completed'
    """)
    assert cursor.fetchone()[0] == 0

    cursor.close()


def test_dw_fact_referential_integrity_and_financial_formulas(db_conn):
    cursor = db_conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM dw_demo1.FactSales f
        LEFT JOIN dw_demo1.DimDate d ON f.DateKey = d.DateKey
        LEFT JOIN dw_demo1.DimCustomer c ON f.CustomerKey = c.CustomerKey
        LEFT JOIN dw_demo1.DimProduct p ON f.ProductKey = p.ProductKey
        LEFT JOIN dw_demo1.DimSalesperson sp ON f.SalespersonKey = sp.SalespersonKey
        LEFT JOIN dw_demo1.DimRegion r ON f.RegionKey = r.RegionKey
        LEFT JOIN dw_demo1.DimWarehouse w ON f.WarehouseKey = w.WarehouseKey
        WHERE d.DateKey IS NULL
           OR c.CustomerKey IS NULL
           OR p.ProductKey IS NULL
           OR sp.SalespersonKey IS NULL
           OR r.RegionKey IS NULL
           OR w.WarehouseKey IS NULL
    """)
    assert cursor.fetchone()[0] == 0

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


def test_dw_idempotency_on_rerun():
    conn = get_sql_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM dw_demo1.FactSales")
        before_fact = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM dw_demo1.DimCustomer")
        before_cust = cursor.fetchone()[0]

        sql_dir = PROJECT_ROOT / "sql"
        prev_auto = conn.autocommit
        conn.autocommit = False
        try:
            execute_sql_file(cursor, conn, sql_dir / "02_dimensions.sql", commit=False)
            execute_sql_file(cursor, conn, sql_dir / "03_facts.sql", commit=False)
            conn.commit()
        except Exception:
            try:
                conn.rollback()
            except Exception:
                pass
            raise
        finally:
            try:
                conn.autocommit = prev_auto
            except Exception:
                pass

        cursor.execute("SELECT COUNT(*) FROM dw_demo1.FactSales")
        assert cursor.fetchone()[0] == before_fact
        cursor.execute("SELECT COUNT(*) FROM dw_demo1.DimCustomer")
        assert cursor.fetchone()[0] == before_cust
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    sys.exit(pytest.main(["-v", __file__]))