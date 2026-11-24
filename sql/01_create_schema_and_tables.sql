-- ============================================================================
-- PROYECTO: B2B Construction Materials Enterprise Analytics
-- ESQUEMAS: stg_demo1 (Staging) | dw_demo1 (Data Warehouse)
-- MOTOR: SQL Server / Azure SQL Database
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 0. LIMPIEZA PREVIA (Idempotencia para re-ejecuciones seguras)
-- ----------------------------------------------------------------------------

-- Eliminar tablas de Data Warehouse en orden inverso por dependencias de FK
IF OBJECT_ID('dw_demo1.FactSales', 'U') IS NOT NULL DROP TABLE dw_demo1.FactSales;
IF OBJECT_ID('dw_demo1.DimCustomer', 'U') IS NOT NULL DROP TABLE dw_demo1.DimCustomer;
IF OBJECT_ID('dw_demo1.DimProduct', 'U') IS NOT NULL DROP TABLE dw_demo1.DimProduct;
IF OBJECT_ID('dw_demo1.DimSalesperson', 'U') IS NOT NULL DROP TABLE dw_demo1.DimSalesperson;
IF OBJECT_ID('dw_demo1.DimWarehouse', 'U') IS NOT NULL DROP TABLE dw_demo1.DimWarehouse;
IF OBJECT_ID('dw_demo1.DimRegion', 'U') IS NOT NULL DROP TABLE dw_demo1.DimRegion;
IF OBJECT_ID('dw_demo1.DimDate', 'U') IS NOT NULL DROP TABLE dw_demo1.DimDate;

-- Eliminar tablas de Staging
IF OBJECT_ID('stg_demo1.sales_order_lines', 'U') IS NOT NULL DROP TABLE stg_demo1.sales_order_lines;
IF OBJECT_ID('stg_demo1.sales_orders', 'U') IS NOT NULL DROP TABLE stg_demo1.sales_orders;
IF OBJECT_ID('stg_demo1.products', 'U') IS NOT NULL DROP TABLE stg_demo1.products;
IF OBJECT_ID('stg_demo1.suppliers', 'U') IS NOT NULL DROP TABLE stg_demo1.suppliers;
IF OBJECT_ID('stg_demo1.salespeople', 'U') IS NOT NULL DROP TABLE stg_demo1.salespeople;
IF OBJECT_ID('stg_demo1.customers', 'U') IS NOT NULL DROP TABLE stg_demo1.customers;
IF OBJECT_ID('stg_demo1.warehouses', 'U') IS NOT NULL DROP TABLE stg_demo1.warehouses;
IF OBJECT_ID('stg_demo1.regions', 'U') IS NOT NULL DROP TABLE stg_demo1.regions;
GO

-- Eliminar esquemas si existen
DROP SCHEMA IF EXISTS dw_demo1;
DROP SCHEMA IF EXISTS stg_demo1;
GO

-- ----------------------------------------------------------------------------
-- 1. CREACIÓN DE ESQUEMAS
-- ----------------------------------------------------------------------------
CREATE SCHEMA stg_demo1;
GO
CREATE SCHEMA dw_demo1;
GO

-- ----------------------------------------------------------------------------
-- 2. CAPA DE STAGING (stg_demo1)
-- ----------------------------------------------------------------------------

-- Tablas maestras / dimensiones de staging
CREATE TABLE stg_demo1.regions (
    region_id INT NOT NULL,
    region_name VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL
);

CREATE TABLE stg_demo1.warehouses (
    warehouse_id INT NOT NULL,
    warehouse_name VARCHAR(100) NOT NULL,
    region_id INT NOT NULL
);

CREATE TABLE stg_demo1.customers (
    customer_id INT NOT NULL,
    company_name VARCHAR(200) NOT NULL,
    contact_name VARCHAR(150) NULL,
    contact_email VARCHAR(150) NULL,
    tax_id VARCHAR(50) NULL,
    customer_segment VARCHAR(50) NOT NULL,
    region_id INT NOT NULL,
    registration_date DATE NOT NULL
);


CREATE TABLE stg_demo1.salespeople (
    salesperson_id INT NOT NULL,
    salesperson_name VARCHAR(150) NOT NULL,
    region_id INT NOT NULL
);

CREATE TABLE stg_demo1.suppliers (
    supplier_id INT NOT NULL,
    supplier_name VARCHAR(150) NOT NULL,
    contact_name VARCHAR(150) NULL,
    contact_email VARCHAR(150) NULL,
    country VARCHAR(100) NULL,
    primary_category VARCHAR(100) NULL
);

CREATE TABLE stg_demo1.products (
    product_id INT NOT NULL,
    product_sku VARCHAR(50) NOT NULL,
    product_name VARCHAR(150) NOT NULL,
    category VARCHAR(100) NOT NULL,
    unit_base_cost DECIMAL(12,2) NOT NULL,
    unit_base_price DECIMAL(12,2) NOT NULL,
    supplier_id INT NOT NULL,

    -- Validaciones de precios y costos del catálogo
    CONSTRAINT CHK_stg_product_cost_positive
        CHECK (unit_base_cost > 0),
    CONSTRAINT CHK_stg_product_price_valid
        CHECK (unit_base_price >= unit_base_cost)
);

-- Tablas transaccionales de staging
CREATE TABLE stg_demo1.sales_orders (
    order_id BIGINT NOT NULL,
    order_date DATE NOT NULL,
    delivery_date DATE NOT NULL,
    customer_id INT NOT NULL,
    salesperson_id INT NOT NULL,
    region_id INT NOT NULL,
    warehouse_id INT NOT NULL,
    total_lines INT NOT NULL,
    total_amount DECIMAL(12,2) NOT NULL,
    total_cost DECIMAL(12,2) NOT NULL,
    status VARCHAR(30) NULL, --
    
    CONSTRAINT CHK_stg_delivery_date 
        CHECK (delivery_date >= order_date)
);


CREATE TABLE stg_demo1.sales_order_lines (
    line_id BIGINT NOT NULL,
    order_id BIGINT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_cost DECIMAL(12,2) NOT NULL,
    unit_price DECIMAL(12,2) NOT NULL,
    discount_rate DECIMAL(5,4) DEFAULT 0.0000 NOT NULL,
    line_subtotal DECIMAL(12,2) NOT NULL,
    line_cost_total DECIMAL(12,2) NOT NULL,

    -- Validaciones de valores de línea
    CONSTRAINT CHK_stg_quantity_positive 
        CHECK (quantity > 0),
    CONSTRAINT CHK_stg_unit_price_nonnegative
        CHECK (unit_price >= 0),
    CONSTRAINT CHK_stg_unit_cost_positive
        CHECK (unit_cost > 0)
);

GO

-- ----------------------------------------------------------------------------
-- 3. CAPA DE DATA WAREHOUSE (dw_demo1)
-- ----------------------------------------------------------------------------

-- DimRegion
CREATE TABLE dw_demo1.DimRegion (
    RegionKey INT IDENTITY(1,1) NOT NULL,
    RegionID INT NOT NULL,
    RegionName VARCHAR(100) NOT NULL,
    Country VARCHAR(100) NOT NULL,
    CONSTRAINT PK_DimRegion PRIMARY KEY (RegionKey),
    CONSTRAINT UQ_DimRegion_RegionID UNIQUE (RegionID)
);

-- DimWarehouse
CREATE TABLE dw_demo1.DimWarehouse (
    WarehouseKey INT IDENTITY(1,1) NOT NULL,
    WarehouseID INT NOT NULL,
    WarehouseName VARCHAR(100) NOT NULL,
    RegionName VARCHAR(100) NOT NULL,
    CONSTRAINT PK_DimWarehouse PRIMARY KEY (WarehouseKey),
    CONSTRAINT UQ_DimWarehouse_WarehouseID UNIQUE (WarehouseID)
);

-- DimCustomer
CREATE TABLE dw_demo1.DimCustomer (
    CustomerKey INT IDENTITY(1,1) NOT NULL,
    CustomerID INT NOT NULL,
    CustomerName VARCHAR(150) NOT NULL,
    Segment VARCHAR(50) NOT NULL,
    RegionName VARCHAR(100) NOT NULL,
    RegistrationDate DATE NOT NULL,
    CONSTRAINT PK_DimCustomer PRIMARY KEY (CustomerKey),
    CONSTRAINT UQ_DimCustomer_CustomerID UNIQUE (CustomerID)
);

-- DimSalesperson
CREATE TABLE dw_demo1.DimSalesperson (
    SalespersonKey INT IDENTITY(1,1) NOT NULL,
    SalespersonID INT NOT NULL,
    SalespersonName VARCHAR(150) NOT NULL,
    RegionName VARCHAR(100) NOT NULL,
    CONSTRAINT PK_DimSalesperson PRIMARY KEY (SalespersonKey),
    CONSTRAINT UQ_DimSalesperson_SalespersonID UNIQUE (SalespersonID)
);

-- DimProduct
CREATE TABLE dw_demo1.DimProduct (
    ProductKey INT IDENTITY(1,1) NOT NULL,
    ProductID INT NOT NULL,
    ProductName VARCHAR(150) NOT NULL,
    Category VARCHAR(100) NOT NULL,
    Subcategory VARCHAR(100) NOT NULL,
    SupplierName VARCHAR(150) NOT NULL,
    ListPrice DECIMAL(12,2) NOT NULL,
    UnitCost DECIMAL(12,2) NOT NULL,
    CONSTRAINT PK_DimProduct PRIMARY KEY (ProductKey),
    CONSTRAINT UQ_DimProduct_ProductID UNIQUE (ProductID)
);

-- DimDate
CREATE TABLE dw_demo1.DimDate (
    DateKey INT NOT NULL, -- Formato YYYYMMDD
    FullDate DATE UNIQUE NOT NULL,
    Year INT NOT NULL,
    Quarter INT NOT NULL,
    QuarterName VARCHAR(10) NOT NULL,
    Month INT NOT NULL,
    MonthName VARCHAR(20) NOT NULL,
    DayOfWeek INT NOT NULL,
    DayOfWeekName VARCHAR(20) NOT NULL,
    IsWeekend BIT NOT NULL,
    CONSTRAINT PK_DimDate PRIMARY KEY (DateKey)
);

-- FactSales
CREATE TABLE dw_demo1.FactSales (
    SalesOrderLineID BIGINT NOT NULL,
    SalesOrderID BIGINT NOT NULL,
    
    -- Foreign Keys a Dimensiones
    DateKey INT NOT NULL,
    CustomerKey INT NOT NULL,
    ProductKey INT NOT NULL,
    SalespersonKey INT NOT NULL,
    RegionKey INT NOT NULL,    -- Región Comercial (derivada de Salesperson)
    WarehouseKey INT NOT NULL,

    -- Métricas Operativas Directas
    Quantity INT NOT NULL,
    UnitPrice DECIMAL(12,2) NOT NULL,
    UnitCost DECIMAL(12,2) NOT NULL,
    DiscountAmount DECIMAL(12,2) NOT NULL,

    -- Columnas Calculadas Persistidas
    Revenue AS (CAST((Quantity * UnitPrice) - DiscountAmount AS DECIMAL(12,2))) PERSISTED,
    TotalCost AS (CAST(Quantity * UnitCost AS DECIMAL(12,2))) PERSISTED,
    GrossProfit AS (CAST(((Quantity * UnitPrice) - DiscountAmount) - (Quantity * UnitCost) AS DECIMAL(12,2))) PERSISTED,

    -- Primary Key
    CONSTRAINT PK_FactSales PRIMARY KEY (SalesOrderLineID),
    
    -- Foreign Keys
    CONSTRAINT FK_FactSales_DimDate FOREIGN KEY (DateKey) 
        REFERENCES dw_demo1.DimDate(DateKey),
    CONSTRAINT FK_FactSales_DimCustomer FOREIGN KEY (CustomerKey) 
        REFERENCES dw_demo1.DimCustomer(CustomerKey),
    CONSTRAINT FK_FactSales_DimProduct FOREIGN KEY (ProductKey) 
        REFERENCES dw_demo1.DimProduct(ProductKey),
    CONSTRAINT FK_FactSales_DimSalesperson FOREIGN KEY (SalespersonKey) 
        REFERENCES dw_demo1.DimSalesperson(SalespersonKey),
    CONSTRAINT FK_FactSales_DimRegion FOREIGN KEY (RegionKey) 
        REFERENCES dw_demo1.DimRegion(RegionKey),
    CONSTRAINT FK_FactSales_DimWarehouse FOREIGN KEY (WarehouseKey) 
        REFERENCES dw_demo1.DimWarehouse(WarehouseKey),

    -- Constraints de Calidad e Invariantes de Negocio (DW-level)
    CONSTRAINT CHK_FactSales_Quantity 
        CHECK (Quantity > 0),
    CONSTRAINT CHK_FactSales_UnitPrice 
        CHECK (UnitPrice >= 0),
    CONSTRAINT CHK_FactSales_UnitCost 
        CHECK (UnitCost > 0),
    CONSTRAINT CHK_FactSales_Discount 
        CHECK (DiscountAmount >= 0),
    CONSTRAINT CHK_FactSales_DiscountNotExceedGross 
        CHECK (DiscountAmount <= (Quantity * UnitPrice))
);
GO

-- ----------------------------------------------------------------------------
-- 4. ÍNDICES NO AGRUPADOS PARA OPTIMIZACIÓN DE CRUCES EN DW
-- ----------------------------------------------------------------------------
CREATE INDEX IX_FactSales_DateKey        ON dw_demo1.FactSales(DateKey);
CREATE INDEX IX_FactSales_CustomerKey    ON dw_demo1.FactSales(CustomerKey);
CREATE INDEX IX_FactSales_ProductKey     ON dw_demo1.FactSales(ProductKey);
CREATE INDEX IX_FactSales_SalespersonKey ON dw_demo1.FactSales(SalespersonKey);
CREATE INDEX IX_FactSales_RegionKey      ON dw_demo1.FactSales(RegionKey);
CREATE INDEX IX_FactSales_WarehouseKey   ON dw_demo1.FactSales(WarehouseKey);
GO