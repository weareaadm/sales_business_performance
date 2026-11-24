# SOURCE TO TARGET MAPPING SPECIFICATION

**Proyecto:** B2B Construction Materials Enterprise Analytics  
**Versión:** 2.0 
**Esquema Origen (Staging):** `stg_demo1`  
**Esquema Destino (Data Warehouse):** `dw_demo1`  
**Período de Carga:** 2024-01-01 a 2026-12-31  

---

## 1. Mapeo de Tablas de Dimensión

### 1.1 `dw_demo1.DimRegion`
* **Origen principal:** `stg_demo1.regions`
* **Estrategia de Carga:** Carga directa de catálogo con generación de Key subrogada (`RegionKey IDENTITY`).

| Campo Destino (DW) | Tipo Dato DW | Campo Origen (Staging) | Tipo Dato Staging | Regla de Transformación / Lógica |
| :--- | :--- | :--- | :--- | :--- |
| `RegionKey` | `INT` | N/A | N/A | Clave primaria subrogada (`IDENTITY(1,1)`). |
| `RegionID` | `INT` | `region_id` | `INT` | Clave de negocio (Natural Key). Mapeo directo. |
| `RegionName` | `VARCHAR(100)` | `region_name` | `VARCHAR(100)` | Mapeo directo. |
| `Country` | `VARCHAR(100)` | `country` | `VARCHAR(100)` | Mapeo directo. |

---

### 1.2 `dw_demo1.DimWarehouse`
* **Origen principal:** `stg_demo1.warehouses`
* **Origen complementario:** `stg_demo1.regions`

| Campo Destino (DW) | Tipo Dato DW | Campo Origen (Staging) | Tipo Dato Staging | Regla de Transformación / Lógica |
| :--- | :--- | :--- | :--- | :--- |
| `WarehouseKey` | `INT` | N/A | N/A | Clave primaria subrogada (`IDENTITY(1,1)`). |
| `WarehouseID` | `INT` | `warehouses.warehouse_id` | `INT` | Clave de negocio (Natural Key). Mapeo directo. |
| `WarehouseName` | `VARCHAR(100)` | `warehouses.warehouse_name` | `VARCHAR(100)` | Mapeo directo. |
| `RegionName` | `VARCHAR(100)` | `regions.region_name` | `VARCHAR(100)` | `JOIN stg_demo1.regions ON warehouses.region_id = regions.region_id`. Denormalización de la región del almacén. |

---

### 1.3 `dw_demo1.DimCustomer`
* **Origen principal:** `stg_demo1.customers`
* **Origen complementario:** `stg_demo1.regions`

| Campo Destino (DW) | Tipo Dato DW | Campo Origen (Staging) | Tipo Dato Staging | Regla de Transformación / Lógica |
| :--- | :--- | :--- | :--- | :--- |
| `CustomerKey` | `INT` | N/A | N/A | Clave primaria subrogada (`IDENTITY(1,1)`). |
| `CustomerID` | `INT` | `customers.customer_id` | `INT` | Clave de negocio (Natural Key). Mapeo directo. |
| `CustomerName` | `VARCHAR(150)` | `customers.customer_name` | `VARCHAR(150)` | Mapeo directo. |
| `Segment` | `VARCHAR(50)` | `customers.segment` | `VARCHAR(50)` | Mapeo directo (Contractor, Construction Company, Retailer, Individual). |
| `RegionName` | `VARCHAR(100)` | `regions.region_name` | `VARCHAR(100)` | `JOIN stg_demo1.regions ON customers.region_id = regions.region_id`. Denormalización de región base del cliente. |
| `RegistrationDate` | `DATE` | `customers.registration_date` | `DATE` | Mapeo directo. |

---

### 1.4 `dw_demo1.DimSalesperson`
* **Origen principal:** `stg_demo1.salespeople`
* **Origen complementario:** `stg_demo1.regions`

| Campo Destino (DW) | Tipo Dato DW | Campo Origen (Staging) | Tipo Dato Staging | Regla de Transformación / Lógica |
| :--- | :--- | :--- | :--- | :--- |
| `SalespersonKey` | `INT` | N/A | N/A | Clave primaria subrogada (`IDENTITY(1,1)`). |
| `SalespersonID` | `INT` | `salespeople.salesperson_id` | `INT` | Clave de negocio (Natural Key). Mapeo directo. |
| `SalespersonName` | `VARCHAR(150)` | `salespeople.salesperson_name` | `VARCHAR(150)` | Mapeo directo. |
| `RegionName` | `VARCHAR(100)` | `regions.region_name` | `VARCHAR(100)` | `JOIN stg_demo1.regions ON salespeople.region_id = regions.region_id`. Denormalización de la región del vendedor. |

---

### 1.5 `dw_demo1.DimProduct`
* **Origen principal:** `stg_demo1.products`
* **Origen complementario:** `stg_demo1.suppliers`

| Campo Destino (DW) | Tipo Dato DW | Campo Origen (Staging) | Tipo Dato Staging | Regla de Transformación / Lógica |
| :--- | :--- | :--- | :--- | :--- |
| `ProductKey` | `INT` | N/A | N/A | Clave primaria subrogada (`IDENTITY(1,1)`). |
| `ProductID` | `INT` | `products.product_id` | `INT` | Clave de negocio (Natural Key). Mapeo directo. |
| `ProductName` | `VARCHAR(150)` | `products.product_name` | `VARCHAR(150)` | Mapeo directo. |
| `Category` | `VARCHAR(100)` | `products.category` | `VARCHAR(100)` | Mapeo directo. |
| `Subcategory` | `VARCHAR(100)` | `products.subcategory` | `VARCHAR(100)` | Mapeo directo. |
| `SupplierName` | `VARCHAR(150)` | `suppliers.supplier_name` | `VARCHAR(150)` | `JOIN stg_demo1.suppliers ON products.supplier_id = suppliers.supplier_id`. Denormalización del proveedor. |
| `ListPrice` | `DECIMAL(12,2)` | `products.list_price` | `DECIMAL(12,2)` | Mapeo directo (Precio de lista actual). |
| `UnitCost` | `DECIMAL(12,2)` | `products.unit_cost` | `DECIMAL(12,2)` | Mapeo directo (Costo unitario actual). |

---

### 1.6 `dw_demo1.DimDate`
* **Origen:** Generación mediante Script de Calendario SQL / Python.
* **Rango de Fechas:** `2024-01-01` a `2026-12-31`.

| Campo Destino (DW) | Tipo Dato DW | Campo Origen / Fuente | Regla de Transformación / Lógica |
| :--- | :--- | :--- | :--- |
| `DateKey` | `INT` | Generado | Formato de clave numérico `YYYYMMDD` (ej. `20250815`). |
| `FullDate` | `DATE` | Generado | Fecha real completa (`YYYY-MM-DD`). |
| `Year` | `INT` | Generado | Año extraído (`YEAR(FullDate)`). |
| `Quarter` | `INT` | Generado | Trimestre del año (`1` al `4`). |
| `QuarterName` | `VARCHAR(10)` | Generado | Nombre del trimestre (`'Q1'`, `'Q2'`, `'Q3'`, `'Q4'`). |
| `Month` | `INT` | Generado | Número del mes (`1` al `12`). |
| `MonthName` | `VARCHAR(20)` | Generado | Nombre completo del mes en inglés (`'January'`, `'February'`, `'March'`, etc.). |
| `DayOfWeek` | `INT` | Generado | Día de la semana (`1` - Lunes a `7` - Domingo). |
| `DayOfWeekName` | `VARCHAR(20)` | Generado | Nombre del día en inglés (`'Monday'`, `'Tuesday'`, `'Wednesday'`, etc.). |
| `IsWeekend` | `BIT` | Generado | `1` si es Sábado o Domingo, `0` en caso contrario. |

---

## 2. Mapeo de Tabla de Hechos (`dw_demo1.FactSales`)

* **Origen Principal:** `stg_demo1.sales_order_lines` (Granularidad base)
* **Origen Encabezado:** `stg_demo1.sales_orders`
* **Origen Atribución:** `stg_demo1.salespeople`

### Regla de Elegibilidad y Filtrado ETL
Solo las líneas pertenecientes a órdenes con:
```sql
sales_orders.status = 'Completed'
```
son cargadas en `dw_demo1.FactSales`. Las líneas asociadas a órdenes `'Cancelled'` o `'Pending'` permanecen exclusivamente en staging y no se insertan en el hecho.

| Campo Destino (DW) | Tipo Dato DW | Campo Origen (Staging) | Regla de Transformación / Búsqueda (Lookup) |
| :--- | :--- | :--- | :--- |
| `SalesOrderLineID` | `BIGINT` | `sales_order_lines.order_line_id` | Clave primaria del hecho. Mapeo directo y preservación de ID original. |
| `SalesOrderID` | `BIGINT` | `sales_order_lines.order_id` | Mapeo directo. ID de la orden de venta. |
| `DateKey` | `INT` | `sales_orders.order_date` | `JOIN stg_demo1.sales_orders ON sales_order_lines.order_id = sales_orders.order_id`. Transformación a formato `YYYYMMDD` en tipo `INT`. |
| `CustomerKey` | `INT` | `sales_orders.customer_id` | Lookup en `dw_demo1.DimCustomer` comparando `CustomerID = sales_orders.customer_id`. |
| `ProductKey` | `INT` | `sales_order_lines.product_id` | Lookup en `dw_demo1.DimProduct` comparando `ProductID = sales_order_lines.product_id`. |
| `SalespersonKey` | `INT` | `sales_orders.salesperson_id` | Lookup en `dw_demo1.DimSalesperson` comparando `SalespersonID = sales_orders.salesperson_id`. |
| `RegionKey` | `INT` | `salespeople.region_id` | **Atribución Comercial:** Se obtiene `region_id` de `stg_demo1.salespeople` ligado al vendedor. Lookup en `dw_demo1.DimRegion` comparando `RegionID = salespeople.region_id`. |
| `WarehouseKey` | `INT` | `sales_orders.warehouse_id` | Lookup en `dw_demo1.DimWarehouse` comparando `WarehouseID = sales_orders.warehouse_id`. |
| `Quantity` | `INT` | `sales_order_lines.quantity` | Mapeo directo de unidades vendidas. |
| `UnitPrice` | `DECIMAL(12,2)` | `sales_order_lines.unit_price` | Mapeo directo de precio unitario real cobrado. |
| `UnitCost` | `DECIMAL(12,2)` | `sales_order_lines.unit_cost` | Mapeo directo del costo unitario al momento de la venta. |
| `DiscountAmount` | `DECIMAL(12,2)` | `sales_order_lines.discount_amount` | Mapeo directo del descuento total en la línea. |
| `Revenue` | `DECIMAL(12,2)` | *(Columna Calculada)* | `AS (CAST((Quantity * UnitPrice) - DiscountAmount AS DECIMAL(12,2))) PERSISTED` |
| `TotalCost` | `DECIMAL(12,2)` | *(Columna Calculada)* | `AS (CAST(Quantity * UnitCost AS DECIMAL(12,2))) PERSISTED` |
| `GrossProfit` | `DECIMAL(12,2)` | *(Columna Calculada)* | `AS (CAST(((Quantity * UnitPrice) - DiscountAmount) - (Quantity * UnitCost) AS DECIMAL(12,2))) PERSISTED` |

---

## 3. Resumen de Flujo ETL y Dependencias de Carga

```plaintext
1. Carga de Dimensiones Independientes
   ├── dw_demo1.DimDate          (Generado dinámicamente con nombres de días/meses en inglés)
   └── dw_demo1.DimRegion        (stg_demo1.regions)

2. Carga de Dimensiones Denormalizadas con Lookup
   ├── dw_demo1.DimWarehouse     (stg_demo1.warehouses JOIN stg_demo1.regions)
   ├── dw_demo1.DimCustomer      (stg_demo1.customers JOIN stg_demo1.regions)
   ├── dw_demo1.DimSalesperson   (stg_demo1.salespeople JOIN stg_demo1.regions)
   └── dw_demo1.DimProduct       (stg_demo1.products JOIN stg_demo1.suppliers)

3. Carga de Tabla de Hechos
   └── dw_demo1.FactSales        (stg_demo1.sales_order_lines 
                                  JOIN stg_demo1.sales_orders (WHERE status = 'Completed')
                                  JOIN stg_demo1.salespeople 
                                  + Lookups a todas las Dimensiones)
```

---

## 4. DDL de Implementación (SQL Server / Azure SQL Database)

```sql
-- ============================================================================
-- PROYECTO: B2B Construction Materials Enterprise Analytics
-- ESQUEMAS: stg_demo1 (Staging) | dw_demo1 (Data Warehouse)
-- MOTOR: SQL Server / Azure SQL Database
-- ============================================================================

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
    customer_name VARCHAR(150) NOT NULL,
    segment VARCHAR(50) NOT NULL,
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
    supplier_name VARCHAR(150) NOT NULL
);

CREATE TABLE stg_demo1.products (
    product_id INT NOT NULL,
    product_name VARCHAR(150) NOT NULL,
    category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100) NOT NULL,
    supplier_id INT NOT NULL,
    list_price DECIMAL(12,2) NOT NULL,
    unit_cost DECIMAL(12,2) NOT NULL,

    -- Validaciones de precios y costos del catálogo
    CONSTRAINT CHK_stg_product_cost_positive
        CHECK (unit_cost > 0),
    CONSTRAINT CHK_stg_product_price_valid
        CHECK (list_price >= unit_cost)
);

-- Tablas transaccionales de staging
CREATE TABLE stg_demo1.sales_orders (
    order_id BIGINT NOT NULL,
    order_date DATE NOT NULL,
    requested_delivery_date DATE NOT NULL,
    customer_id INT NOT NULL,
    salesperson_id INT NOT NULL,
    warehouse_id INT NOT NULL,
    status VARCHAR(30) NOT NULL,
    
    CONSTRAINT CHK_stg_delivery_date 
        CHECK (requested_delivery_date >= order_date)
);

CREATE TABLE stg_demo1.sales_order_lines (
    order_line_id BIGINT NOT NULL,
    order_id BIGINT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(12,2) NOT NULL,
    unit_cost DECIMAL(12,2) NOT NULL,
    discount_amount DECIMAL(12,2) DEFAULT 0.00 NOT NULL,

    -- Validaciones de valores de línea
    CONSTRAINT CHK_stg_quantity_positive 
        CHECK (quantity > 0),
    CONSTRAINT CHK_stg_unit_price_nonnegative
        CHECK (unit_price >= 0),
    CONSTRAINT CHK_stg_unit_cost_positive
        CHECK (unit_cost > 0),
    CONSTRAINT CHK_stg_discount_nonnegative 
        CHECK (discount_amount >= 0),
    CONSTRAINT CHK_stg_discount_not_exceed_gross 
        CHECK (discount_amount <= (quantity * unit_price))
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
```