"""
tests/phase2_staging/test_staging_load.py
-----------------------------------------
Pruebas de aceptación para Fase 2: estructura, conteos, unicidad/nulos,
integridad referencial lógica, estados y conciliación en stg_demo1.
"""

import csv
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
from drivers.sqlserver import get_sql_connection


@pytest.fixture(scope="module")
def db_conn():
    conn = get_sql_connection()
    yield conn
    conn.close()


def _read_csv_header_and_count(csv_path: Path) -> tuple[list[str], int]:
    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        header = next(reader, [])
        row_count = sum(1 for _ in reader)
    return header, row_count


def test_schemas_tables_and_columns(db_conn):
    cursor = db_conn.cursor()

    cursor.execute("""
        SELECT SCHEMA_NAME
        FROM INFORMATION_SCHEMA.SCHEMATA
        WHERE SCHEMA_NAME IN ('stg_demo1', 'dw_demo1')
    """)
    assert {row[0] for row in cursor.fetchall()} == {"stg_demo1", "dw_demo1"}

    expected_tables = {
        "regions",
        "warehouses",
        "salespeople",
        "suppliers",
        "products",
        "customers",
        "sales_orders",
        "sales_order_lines",
    }
    cursor.execute("""
        SELECT TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = 'stg_demo1'
    """)
    tables = {row[0] for row in cursor.fetchall()}
    assert expected_tables.issubset(tables)

    expected_columns = {
        "regions": {"region_id", "region_name", "country"},
        "warehouses": {"warehouse_id", "warehouse_name", "region_id"},
        "customers": {
            "customer_id",
            "company_name",
            "contact_name",
            "contact_email",
            "tax_id",
            "customer_segment",
            "region_id",
            "registration_date",
        },
        "salespeople": {"salesperson_id", "salesperson_name", "region_id"},
        "suppliers": {
            "supplier_id",
            "supplier_name",
            "contact_name",
            "contact_email",
            "country",
            "primary_category",
        },
        "products": {
            "product_id",
            "product_sku",
            "product_name",
            "category",
            "unit_base_cost",
            "unit_base_price",
            "supplier_id",
        },
        "sales_orders": {
            "order_id",
            "order_date",
            "delivery_date",
            "customer_id",
            "salesperson_id",
            "region_id",
            "warehouse_id",
            "total_lines",
            "total_amount",
            "total_cost",
            "status",
        },
        "sales_order_lines": {
            "line_id",
            "order_id",
            "product_id",
            "quantity",
            "unit_cost",
            "unit_price",
            "discount_rate",
            "line_subtotal",
            "line_cost_total",
        },
    }

    for tbl, req_cols in expected_columns.items():
        cursor.execute(
            """
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = 'stg_demo1' AND TABLE_NAME = ?
            """,
            (tbl,),
        )
        db_cols = {row[0] for row in cursor.fetchall()}
        assert req_cols.issubset(db_cols), f"Faltan columnas en stg_demo1.{tbl}: {req_cols - db_cols}"

    data_dir = config.OUTPUT_DIR
    csv_map = [
        ("salespeople.csv", "salespeople"),
        ("suppliers.csv", "suppliers"),
        ("products.csv", "products"),
        ("customers.csv", "customers"),
        ("sales_orders.csv", "sales_orders"),
        ("order_lines.csv", "sales_order_lines"),
    ]
    for csv_name, tbl in csv_map:
        csv_file = data_dir / csv_name
        assert csv_file.exists(), f"No existe {csv_file}"
        header, _ = _read_csv_header_and_count(csv_file)
        assert len(header) == len(set(header)), f"Columnas duplicadas en {csv_name}"
        cursor.execute(
            """
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = 'stg_demo1' AND TABLE_NAME = ?
            """,
            (tbl,),
        )
        db_cols = {row[0] for row in cursor.fetchall()}
        assert set(header) == db_cols, f"Encabezados de {csv_name} no coinciden con stg_demo1.{tbl}"

    cursor.close()


def test_staging_row_counts(db_conn):
    cursor = db_conn.cursor()
    data_dir = config.OUTPUT_DIR

    csv_table_pairs = [
        ("salespeople.csv", "stg_demo1.salespeople"),
        ("suppliers.csv", "stg_demo1.suppliers"),
        ("products.csv", "stg_demo1.products"),
        ("customers.csv", "stg_demo1.customers"),
        ("sales_orders.csv", "stg_demo1.sales_orders"),
        ("order_lines.csv", "stg_demo1.sales_order_lines"),
    ]

    for csv_name, table_fqn in csv_table_pairs:
        _, expected_rows = _read_csv_header_and_count(data_dir / csv_name)
        cursor.execute(f"SELECT COUNT(*) FROM {table_fqn}")
        actual_rows = cursor.fetchone()[0]
        assert actual_rows == expected_rows, f"Mismatch en {table_fqn}: {actual_rows} vs {expected_rows}"

    cursor.execute("SELECT COUNT(*) FROM stg_demo1.regions")
    assert cursor.fetchone()[0] == len(config.REGIONS)

    cursor.execute("SELECT COUNT(*) FROM stg_demo1.warehouses")
    assert cursor.fetchone()[0] == len(config.WAREHOUSES)

    cursor.close()


def test_staging_keys_nulls_and_uniqueness(db_conn):
    cursor = db_conn.cursor()

    key_checks = [
        ("stg_demo1.regions", "region_id"),
        ("stg_demo1.warehouses", "warehouse_id"),
        ("stg_demo1.salespeople", "salesperson_id"),
        ("stg_demo1.suppliers", "supplier_id"),
        ("stg_demo1.products", "product_id"),
        ("stg_demo1.customers", "customer_id"),
        ("stg_demo1.sales_orders", "order_id"),
        ("stg_demo1.sales_order_lines", "line_id"),
    ]

    for table_fqn, pk_col in key_checks:
        cursor.execute(f"SELECT COUNT(*) FROM {table_fqn} WHERE {pk_col} IS NULL")
        assert cursor.fetchone()[0] == 0, f"Nulos en {table_fqn}.{pk_col}"

        cursor.execute(f"SELECT COUNT(*) - COUNT(DISTINCT {pk_col}) FROM {table_fqn}")
        assert cursor.fetchone()[0] == 0, f"Duplicados en {table_fqn}.{pk_col}"

    cursor.close()


def test_staging_logical_referential_integrity(db_conn):
    cursor = db_conn.cursor()

    fk_queries = [
        """
        SELECT COUNT(*)
        FROM stg_demo1.sales_order_lines l
        LEFT JOIN stg_demo1.sales_orders o ON l.order_id = o.order_id
        WHERE o.order_id IS NULL
        """,
        """
        SELECT COUNT(*)
        FROM stg_demo1.sales_order_lines l
        LEFT JOIN stg_demo1.products p ON l.product_id = p.product_id
        WHERE p.product_id IS NULL
        """,
        """
        SELECT COUNT(*)
        FROM stg_demo1.sales_orders o
        LEFT JOIN stg_demo1.customers c ON o.customer_id = c.customer_id
        WHERE c.customer_id IS NULL
        """,
        """
        SELECT COUNT(*)
        FROM stg_demo1.sales_orders o
        LEFT JOIN stg_demo1.salespeople sp ON o.salesperson_id = sp.salesperson_id
        WHERE sp.salesperson_id IS NULL
        """,
        """
        SELECT COUNT(*)
        FROM stg_demo1.sales_orders o
        LEFT JOIN stg_demo1.warehouses w ON o.warehouse_id = w.warehouse_id
        WHERE w.warehouse_id IS NULL
        """,
        """
        SELECT COUNT(*)
        FROM stg_demo1.sales_orders o
        LEFT JOIN stg_demo1.regions r ON o.region_id = r.region_id
        WHERE r.region_id IS NULL
        """,
        """
        SELECT COUNT(*)
        FROM stg_demo1.products p
        LEFT JOIN stg_demo1.suppliers s ON p.supplier_id = s.supplier_id
        WHERE s.supplier_id IS NULL
        """,
        """
        SELECT COUNT(*)
        FROM stg_demo1.salespeople sp
        LEFT JOIN stg_demo1.regions r ON sp.region_id = r.region_id
        WHERE r.region_id IS NULL
        """,
        """
        SELECT COUNT(*)
        FROM stg_demo1.customers c
        LEFT JOIN stg_demo1.regions r ON c.region_id = r.region_id
        WHERE r.region_id IS NULL
        """,
        """
        SELECT COUNT(*)
        FROM stg_demo1.warehouses w
        LEFT JOIN stg_demo1.regions r ON w.region_id = r.region_id
        WHERE r.region_id IS NULL
        """,
    ]

    for query in fk_queries:
        cursor.execute(query)
        assert cursor.fetchone()[0] == 0

    cursor.close()


def test_staging_statuses_and_header_line_reconciliation(db_conn):
    cursor = db_conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM stg_demo1.sales_orders WHERE status IS NULL")
    assert cursor.fetchone()[0] == 0

    cursor.execute("SELECT DISTINCT status FROM stg_demo1.sales_orders")
    assert {row[0] for row in cursor.fetchall()} == {"Completed", "Cancelled", "Pending"}

    cursor.execute("SELECT COUNT(*) FROM stg_demo1.sales_orders WHERE delivery_date < order_date")
    assert cursor.fetchone()[0] == 0

    cursor.execute("""
        WITH line_agg AS (
            SELECT
                order_id,
                COUNT(*) AS calc_lines,
                CAST(SUM(line_subtotal) AS DECIMAL(14, 2)) AS calc_amount,
                CAST(SUM(line_cost_total) AS DECIMAL(14, 2)) AS calc_cost
            FROM stg_demo1.sales_order_lines
            GROUP BY order_id
        )
        SELECT COUNT(*)
        FROM stg_demo1.sales_orders o
        LEFT JOIN line_agg a ON o.order_id = a.order_id
        WHERE a.order_id IS NULL
           OR o.total_lines <> a.calc_lines
           OR ABS(o.total_amount - a.calc_amount) > 0.05
           OR ABS(o.total_cost - a.calc_cost) > 0.05
    """)
    assert cursor.fetchone()[0] == 0

    cursor.close()


if __name__ == "__main__":
    sys.exit(pytest.main(["-v", __file__]))