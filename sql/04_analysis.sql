-- ============================================================================
-- SCRIPT: 04_analysis.sql
-- DESCRIPCIÓN: Validación, calidad de datos y reconciliación Staging <-> DW
-- ============================================================================

-- 1. Reconciliación de conteos (Staging vs FactSales solo órdenes Completed)
SELECT
    (SELECT COUNT(*) FROM stg_demo1.sales_orders) AS stg_total_orders,
    (SELECT COUNT(*) FROM stg_demo1.sales_orders WHERE status = 'Completed') AS stg_completed_orders,
    (SELECT COUNT(*) FROM stg_demo1.sales_orders WHERE status = 'Cancelled') AS stg_cancelled_orders,
    (SELECT COUNT(*) FROM stg_demo1.sales_orders WHERE status = 'Pending') AS stg_pending_orders,
    (SELECT COUNT(*) FROM stg_demo1.sales_order_lines) AS stg_total_lines,
    (
        SELECT COUNT(*)
        FROM stg_demo1.sales_order_lines l
        INNER JOIN stg_demo1.sales_orders o ON l.order_id = o.order_id
        WHERE o.status = 'Completed'
    ) AS expected_completed_lines,
    (SELECT COUNT(*) FROM dw_demo1.FactSales) AS dw_fact_sales_rows;
GO

-- 2. Conciliación financiera (líneas de órdenes Completed en Staging vs FactSales)
WITH stg_completed AS (
    SELECT
        COUNT(*) AS line_count,
        COUNT(DISTINCT l.order_id) AS order_count,
        SUM(CAST(l.quantity AS BIGINT)) AS total_units,
        SUM(CAST(ROUND(l.quantity * l.unit_price * l.discount_rate, 2) AS DECIMAL(18,2))) AS total_discount,
        SUM(CAST(l.line_subtotal AS DECIMAL(18,2))) AS total_revenue,
        SUM(CAST(l.line_cost_total AS DECIMAL(18,2))) AS total_cost,
        SUM(CAST(l.line_subtotal - l.line_cost_total AS DECIMAL(18,2))) AS total_gross_profit
    FROM stg_demo1.sales_order_lines l
    INNER JOIN stg_demo1.sales_orders o ON l.order_id = o.order_id
    WHERE o.status = 'Completed'
),
dw_fact AS (
    SELECT
        COUNT(*) AS line_count,
        COUNT(DISTINCT SalesOrderID) AS order_count,
        SUM(CAST(Quantity AS BIGINT)) AS total_units,
        SUM(CAST(DiscountAmount AS DECIMAL(18,2))) AS total_discount,
        SUM(CAST(Revenue AS DECIMAL(18,2))) AS total_revenue,
        SUM(CAST(TotalCost AS DECIMAL(18,2))) AS total_cost,
        SUM(CAST(GrossProfit AS DECIMAL(18,2))) AS total_gross_profit
    FROM dw_demo1.FactSales
)
SELECT
    'LineCount' AS metric_name,
    CAST(s.line_count AS DECIMAL(18,2)) AS stg_completed_val,
    CAST(f.line_count AS DECIMAL(18,2)) AS dw_fact_val,
    CAST(f.line_count - s.line_count AS DECIMAL(18,2)) AS diff
FROM stg_completed s CROSS JOIN dw_fact f
UNION ALL
SELECT
    'OrderCount',
    CAST(s.order_count AS DECIMAL(18,2)),
    CAST(f.order_count AS DECIMAL(18,2)),
    CAST(f.order_count - s.order_count AS DECIMAL(18,2))
FROM stg_completed s CROSS JOIN dw_fact f
UNION ALL
SELECT
    'TotalUnits',
    CAST(s.total_units AS DECIMAL(18,2)),
    CAST(f.total_units AS DECIMAL(18,2)),
    CAST(f.total_units - s.total_units AS DECIMAL(18,2))
FROM stg_completed s CROSS JOIN dw_fact f
UNION ALL
SELECT
    'DiscountAmount',
    s.total_discount,
    f.total_discount,
    f.total_discount - s.total_discount
FROM stg_completed s CROSS JOIN dw_fact f
UNION ALL
SELECT
    'Revenue',
    s.total_revenue,
    f.total_revenue,
    f.total_revenue - s.total_revenue
FROM stg_completed s CROSS JOIN dw_fact f
UNION ALL
SELECT
    'TotalCost',
    s.total_cost,
    f.total_cost,
    f.total_cost - s.total_cost
FROM stg_completed s CROSS JOIN dw_fact f
UNION ALL
SELECT
    'GrossProfit',
    s.total_gross_profit,
    f.total_gross_profit,
    f.total_gross_profit - s.total_gross_profit
FROM stg_completed s CROSS JOIN dw_fact f;
GO

-- 3. Auditoría de anomalías e integridad en FactSales (debe retornar 0 filas anómalas)
SELECT
    SUM(CASE WHEN Quantity <= 0 THEN 1 ELSE 0 END) AS invalid_quantity,
    SUM(CASE WHEN UnitPrice < 0 THEN 1 ELSE 0 END) AS invalid_unit_price,
    SUM(CASE WHEN UnitCost <= 0 THEN 1 ELSE 0 END) AS invalid_unit_cost,
    SUM(CASE WHEN DiscountAmount < 0 THEN 1 ELSE 0 END) AS negative_discount,
    SUM(CASE WHEN DiscountAmount > (Quantity * UnitPrice) THEN 1 ELSE 0 END) AS discount_exceeds_gross,
    SUM(CASE WHEN ABS(Revenue - ((Quantity * UnitPrice) - DiscountAmount)) > 0.01 THEN 1 ELSE 0 END) AS revenue_mismatch,
    SUM(CASE WHEN ABS(TotalCost - (Quantity * UnitCost)) > 0.01 THEN 1 ELSE 0 END) AS cost_mismatch,
    SUM(CASE WHEN ABS(GrossProfit - (Revenue - TotalCost)) > 0.01 THEN 1 ELSE 0 END) AS profit_mismatch
FROM dw_demo1.FactSales;
GO