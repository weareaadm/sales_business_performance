-- ============================================================================
-- SCRIPT: 02_dimensions.sql
-- DESCRIPCIÓN: Poblado idempotente (full refresh ordenado) de dimensiones en dw_demo1
-- ============================================================================

DELETE FROM dw_demo1.FactSales;
DELETE FROM dw_demo1.DimCustomer;
DELETE FROM dw_demo1.DimProduct;
DELETE FROM dw_demo1.DimSalesperson;
DELETE FROM dw_demo1.DimWarehouse;
DELETE FROM dw_demo1.DimRegion;
DELETE FROM dw_demo1.DimDate;
GO

-- 1. DimRegion
SET IDENTITY_INSERT dw_demo1.DimRegion ON;
INSERT INTO dw_demo1.DimRegion (RegionKey, RegionID, RegionName, Country)
SELECT region_id, region_id, region_name, country
FROM stg_demo1.regions;
SET IDENTITY_INSERT dw_demo1.DimRegion OFF;
GO

-- 2. DimDate (2024-01-01 a 2026-12-31 -> 1,096 días)
WITH DateSeries AS (
    SELECT CAST('2024-01-01' AS DATE) AS FullDate
    UNION ALL
    SELECT DATEADD(DAY, 1, FullDate)
    FROM DateSeries
    WHERE FullDate < CAST('2026-12-31' AS DATE)
)
INSERT INTO dw_demo1.DimDate (
    DateKey, FullDate, Year, Quarter, QuarterName,
    Month, MonthName, DayOfWeek, DayOfWeekName, IsWeekend
)
SELECT
    CAST(CONVERT(VARCHAR(8), FullDate, 112) AS INT) AS DateKey,
    FullDate,
    YEAR(FullDate) AS [Year],
    DATEPART(QUARTER, FullDate) AS [Quarter],
    'Q' + CAST(DATEPART(QUARTER, FullDate) AS VARCHAR(1)) AS QuarterName,
    MONTH(FullDate) AS [Month],
    DATENAME(MONTH, FullDate) AS MonthName,
    ((DATEPART(WEEKDAY, FullDate) + @@DATEFIRST - 2) % 7) + 1 AS DayOfWeek,
    DATENAME(WEEKDAY, FullDate) AS DayOfWeekName,
    CASE
        WHEN ((DATEPART(WEEKDAY, FullDate) + @@DATEFIRST - 2) % 7) + 1 IN (6, 7) THEN 1
        ELSE 0
    END AS IsWeekend
FROM DateSeries
OPTION (MAXRECURSION 2000);
GO

-- 3. DimWarehouse
INSERT INTO dw_demo1.DimWarehouse (WarehouseID, WarehouseName, RegionName)
SELECT w.warehouse_id, w.warehouse_name, r.region_name
FROM stg_demo1.warehouses w
INNER JOIN stg_demo1.regions r ON w.region_id = r.region_id;
GO

-- 4. DimCustomer
INSERT INTO dw_demo1.DimCustomer (CustomerID, CustomerName, Segment, RegionName, RegistrationDate)
SELECT c.customer_id, c.company_name, c.customer_segment, r.region_name, c.registration_date
FROM stg_demo1.customers c
INNER JOIN stg_demo1.regions r ON c.region_id = r.region_id;
GO

-- 5. DimSalesperson
INSERT INTO dw_demo1.DimSalesperson (SalespersonID, SalespersonName, RegionName)
SELECT sp.salesperson_id, sp.salesperson_name, r.region_name
FROM stg_demo1.salespeople sp
INNER JOIN stg_demo1.regions r ON sp.region_id = r.region_id;
GO

-- 6. DimProduct
INSERT INTO dw_demo1.DimProduct (ProductID, ProductName, Category, Subcategory, SupplierName, ListPrice, UnitCost)
SELECT
    p.product_id,
    p.product_name,
    p.category,
    p.category,
    s.supplier_name,
    p.unit_base_price,
    p.unit_base_cost
FROM stg_demo1.products p
INNER JOIN stg_demo1.suppliers s ON p.supplier_id = s.supplier_id;
GO