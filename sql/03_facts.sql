-- ============================================================================
-- SCRIPT: 03_facts.sql
-- DESCRIPCIÓN: Poblado idempotente de dw_demo1.FactSales solo para órdenes Completed
-- ============================================================================

DELETE FROM dw_demo1.FactSales;
GO

INSERT INTO dw_demo1.FactSales (
    SalesOrderLineID,
    SalesOrderID,
    DateKey,
    CustomerKey,
    ProductKey,
    SalespersonKey,
    RegionKey,
    WarehouseKey,
    Quantity,
    UnitPrice,
    UnitCost,
    DiscountAmount
)
SELECT
    l.line_id AS SalesOrderLineID,
    l.order_id AS SalesOrderID,
    dd.DateKey,
    cu.CustomerKey,
    pr.ProductKey,
    sp.SalespersonKey,
    rg.RegionKey,
    wh.WarehouseKey,
    l.quantity AS Quantity,
    l.unit_price AS UnitPrice,
    l.unit_cost AS UnitCost,
    CASE
        WHEN CAST(l.quantity * l.unit_price * l.discount_rate AS DECIMAL(12,2)) < 0
            THEN CAST(0.00 AS DECIMAL(12,2))
        WHEN CAST(l.quantity * l.unit_price * l.discount_rate AS DECIMAL(12,2)) > CAST(l.quantity * l.unit_price AS DECIMAL(12,2))
            THEN CAST(l.quantity * l.unit_price AS DECIMAL(12,2))
        ELSE CAST(l.quantity * l.unit_price * l.discount_rate AS DECIMAL(12,2))
    END AS DiscountAmount
FROM stg_demo1.sales_order_lines l
INNER JOIN stg_demo1.sales_orders o
    ON l.order_id = o.order_id
INNER JOIN dw_demo1.DimDate dd
    ON dd.DateKey = CAST(CONVERT(VARCHAR(8), o.order_date, 112) AS INT)
INNER JOIN stg_demo1.salespeople s
    ON o.salesperson_id = s.salesperson_id
INNER JOIN dw_demo1.DimCustomer cu
    ON o.customer_id = cu.CustomerID
INNER JOIN dw_demo1.DimProduct pr
    ON l.product_id = pr.ProductID
INNER JOIN dw_demo1.DimSalesperson sp
    ON o.salesperson_id = sp.SalespersonID
INNER JOIN dw_demo1.DimRegion rg
    ON s.region_id = rg.RegionID
INNER JOIN dw_demo1.DimWarehouse wh
    ON o.warehouse_id = wh.WarehouseID
WHERE o.status = 'Completed';
GO