# Data Dictionary — DW Ventas y Rentabilidad

**Proyecto:** B2B Construction Materials Enterprise Analytics  
**Versión:** 2.0 
**Motor:** SQL Server / Azure SQL Database  
**Esquemas:** `stg_demo1` (Staging Layer) | `dw_demo1` (Data Warehouse Layer)  

---

## Índice
1. [Capa de Staging (`stg_demo1`)](#1-capa-de-staging-stg_demo1)
   - [1.1 `stg_demo1.regions`](#11-stg_demo1regions)
   - [1.2 `stg_demo1.warehouses`](#12-stg_demo1warehouses)
   - [1.3 `stg_demo1.customers`](#13-stg_demo1customers)
   - [1.4 `stg_demo1.salespeople`](#14-stg_demo1salespeople)
   - [1.5 `stg_demo1.suppliers`](#15-stg_demo1suppliers)
   - [1.6 `stg_demo1.products`](#16-stg_demo1products)
   - [1.7 `stg_demo1.sales_orders`](#17-stg_demo1sales_orders)
   - [1.8 `stg_demo1.sales_order_lines`](#18-stg_demo1sales_order_lines)
2. [Capa de Data Warehouse (`dw_demo1`)](#2-capa-de-data-warehouse-dw_demo1)
   - [2.1 `dw_demo1.DimRegion`](#21-dw_demo1dimregion)
   - [2.2 `dw_demo1.DimWarehouse`](#22-dw_demo1dimwarehouse)
   - [2.3 `dw_demo1.DimCustomer`](#23-dw_demo1dimcustomer)
   - [2.4 `dw_demo1.DimSalesperson`](#24-dw_demo1dimsalesperson)
   - [2.5 `dw_demo1.DimProduct`](#25-dw_demo1dimproduct)
   - [2.6 `dw_demo1.DimDate`](#26-dw_demo1dimdate)
   - [2.7 `dw_demo1.FactSales`](#27-dw_demo1factsales)

---

## 1. Capa de Staging (`stg_demo1`)

La capa de staging contiene las tablas réplica del sistema transaccional de origen (OLTP). Los datos ingresan planos, sin surrogar claves y reflejando las transacciones de negocio operativas.

### 1.1 `stg_demo1.regions`
Almacena el catálogo maestro de regiones geográficas/comerciales de la compañía.

| Nombre Columna | Tipo de Dato | Nulabilidad | Restricciones / Reglas | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| `region_id` | `INT` | `NOT NULL` | Clave natural (`1` a `8`). | Identificador único de la región. |
| `region_name` | `VARCHAR(100)` | `NOT NULL` | Único por región. | Nombre de la región geográfica (ej. *North*, *South*, *East*). |
| `country` | `VARCHAR(100)` | `NOT NULL` | Texto plano. | País al que pertenece la región. |

---

### 1.2 `stg_demo1.warehouses`
Catálogo de almacenes/centros de distribución desde donde se despacha la mercancía.

| Nombre Columna | Tipo de Dato | Nulabilidad | Restricciones / Reglas | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| `warehouse_id` | `INT` | `NOT NULL` | Clave natural (`1` a `8`). | Identificador único del almacén. |
| `warehouse_name` | `VARCHAR(100)` | `NOT NULL` | Texto plano. | Nombre operativo del centro de distribución. |
| `region_id` | `INT` | `NOT NULL` | FK virtual a `stg_demo1.regions`. | Región donde está físicamente ubicado el almacén. |

---

### 1.3 `stg_demo1.customers`
Maestro de clientes registrados en la plataforma transaccional.

| Nombre Columna | Tipo de Dato | Nulabilidad | Restricciones / Reglas | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| `customer_id` | `INT` | `NOT NULL` | Clave natural (`1` a `2000`). | Identificador único del cliente. |
| `customer_name` | `VARCHAR(150)` | `NOT NULL` | Razón social o nombre. | Nombre del cliente o empresa contratante. |
| `segment` | `VARCHAR(50)` | `NOT NULL` | `Contractor`, `Construction Company`, `Retailer`, `Individual`. | Segmento comercial del cliente. |
| `region_id` | `INT` | `NOT NULL` | FK virtual a `stg_demo1.regions`. | Región base asignada al cliente. |
| `registration_date` | `DATE` | `NOT NULL` | Formato `YYYY-MM-DD` (`<= 2026-12-31`). | Fecha de alta del cliente en el sistema. |

---

### 1.4 `stg_demo1.salespeople`
Maestro de la fuerza de ventas asignada por región.

| Nombre Columna | Tipo de Dato | Nulabilidad | Restricciones / Reglas | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| `salesperson_id` | `INT` | `NOT NULL` | Clave natural (`1` a `50`). | Identificador único del vendedor. |
| `salesperson_name` | `VARCHAR(150)` | `NOT NULL` | Texto plano. | Nombre completo del ejecutivo de ventas. |
| `region_id` | `INT` | `NOT NULL` | FK virtual a `stg_demo1.regions`. | Región comercial asignada al vendedor. |

---

### 1.5 `stg_demo1.suppliers`
Catálogo de proveedores de materiales y suministros de construcción.

| Nombre Columna | Tipo de Dato | Nulabilidad | Restricciones / Reglas | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| `supplier_id` | `INT` | `NOT NULL` | Clave natural (`1` a `50`). | Identificador único del proveedor. |
| `supplier_name` | `VARCHAR(150)` | `NOT NULL` | Texto plano. | Razon social o nombre comercial del proveedor. |

---

### 1.6 `stg_demo1.products`
Catálogo maestro de productos con precios y costos de lista.

| Nombre Columna | Tipo de Dato | Nulabilidad | Restricciones / Reglas | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| `product_id` | `INT` | `NOT NULL` | Clave natural (`1` a `500`). | Identificador único del producto. |
| `product_name` | `VARCHAR(150)` | `NOT NULL` | Texto plano. | Nombre descriptivo del producto comercial. |
| `category` | `VARCHAR(100)` | `NOT NULL` | Ej. *Cement & Concrete*, *Steel & Rebar*. | Categoría principal del producto. |
| `subcategory` | `VARCHAR(100)` | `NOT NULL` | Texto plano. | Subcategoría específica del producto. |
| `supplier_id` | `INT` | `NOT NULL` | FK virtual a `stg_demo1.suppliers`. | Proveedor principal del producto. |
| `list_price` | `DECIMAL(12,2)` | `NOT NULL` | `CHK_stg_product_price_valid`: `list_price >= unit_cost` | Precio base de lista sugerido al público (USD). |
| `unit_cost` | `DECIMAL(12,2)` | `NOT NULL` | `CHK_stg_product_cost_positive`: `unit_cost > 0` | Costo unitario base de adquisición/fabricación (USD). |

---

### 1.7 `stg_demo1.sales_orders`
Cabeceras de órdenes de compra transaccionales.

| Nombre Columna | Tipo de Dato | Nulabilidad | Restricciones / Reglas | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| `order_id` | `BIGINT` | `NOT NULL` | Clave primaria (`1` a `150000`). | Identificador único de la cabecera de orden. |
| `order_date` | `DATE` | `NOT NULL` | `2024-01-01` a `2026-12-31`. | Fecha en que se emite la orden. |
| `requested_delivery_date` | `DATE` | `NOT NULL` | `CHK_stg_delivery_date`: `>= order_date` | Fecha solicitada para la entrega del pedido. |
| `customer_id` | `INT` | `NOT NULL` | FK virtual a `stg_demo1.customers`. | Cliente que efectúa la compra. |
| `salesperson_id` | `INT` | `NOT NULL` | FK virtual a `stg_demo1.salespeople`. | Vendedor asignado a la transacción. |
| `warehouse_id` | `INT` | `NOT NULL` | FK virtual a `stg_demo1.warehouses`. | Almacén asignado para el despacho del pedido. |
| `status` | `VARCHAR(30)` | `NOT NULL` | `Completed`, `Cancelled`, `Pending`. | Estado operativo de la orden. |

---

### 1.8 `stg_demo1.sales_order_lines`
Detalle de productos incluidos en cada orden de compra (líneas de orden).

| Nombre Columna | Tipo de Dato | Nulabilidad | Restricciones / Reglas | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| `order_line_id` | `BIGINT` | `NOT NULL` | Clave primaria (`1` a `500000`). | Identificador único de la línea de orden. |
| `order_id` | `BIGINT` | `NOT NULL` | FK virtual a `stg_demo1.sales_orders`. | Identificador de la orden cabecera. |
| `product_id` | `INT` | `NOT NULL` | FK virtual a `stg_demo1.products`. | Producto vendido. |
| `quantity` | `INT` | `NOT NULL` | `CHK_stg_quantity_positive`: `quantity > 0` | Unidades vendidas en la línea. |
| `unit_price` | `DECIMAL(12,2)` | `NOT NULL` | `CHK_stg_unit_price_nonnegative`: `unit_price >= 0` | Precio de venta unitario aplicado (USD). |
| `unit_cost` | `DECIMAL(12,2)` | `NOT NULL` | `CHK_stg_unit_cost_positive`: `unit_cost > 0` | Costo unitario registrado en la venta (USD). |
| `discount_amount` | `DECIMAL(12,2)` | `NOT NULL` | `CHK_stg_discount_nonnegative`: `>= 0`<br>`CHK_stg_discount_not_exceed_gross`: `<= quantity * unit_price` | Monto total de descuento en dólares otorgado a la línea. |

---

## 2. Capa de Data Warehouse (`dw_demo1`)

Capa modelada bajo esquema en estrella (Star Schema) para consumo analítico, optimizada con claves subrogadas (`IDENTITY`), relaciones explícitas (FK) y métricas precalculadas.

### 2.1 `dw_demo1.DimRegion`
Dimensión de geografía comercial.

| Nombre Columna | Tipo de Dato | Nulabilidad | Restricciones / Reglas | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| `RegionKey` | `INT` | `NOT NULL` | `PK`, `IDENTITY(1,1)` | Clave subrogada de la dimensión. |
| `RegionID` | `INT` | `NOT NULL` | `UQ_DimRegion_RegionID` | Clave de negocio (Business Key de `stg_demo1.regions`). |
| `RegionName` | `VARCHAR(100)` | `NOT NULL` | Texto plano. | Nombre descriptivo de la región comercial. |
| `Country` | `VARCHAR(100)` | `NOT NULL` | Texto plano. | País al que pertenece la región. |

---

### 2.2 `dw_demo1.DimWarehouse`
Dimensión de almacenes y centros logísticos.

| Nombre Columna | Tipo de Dato | Nulabilidad | Restricciones / Reglas | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| `WarehouseKey` | `INT` | `NOT NULL` | `PK`, `IDENTITY(1,1)` | Clave subrogada de la dimensión. |
| `WarehouseID` | `INT` | `NOT NULL` | `UQ_DimWarehouse_WarehouseID` | Clave de negocio (Business Key de `stg_demo1.warehouses`). |
| `WarehouseName` | `VARCHAR(100)` | `NOT NULL` | Texto plano. | Nombre del centro logístico. |
| `RegionName` | `VARCHAR(100)` | `NOT NULL` | Denormalizado desde `stg_demo1.regions`. | Región física donde se ubica el almacén. |

---

### 2.3 `dw_demo1.DimCustomer`
Dimensión de clientes de la empresa.

| Nombre Columna | Tipo de Dato | Nulabilidad | Restricciones / Reglas | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| `CustomerKey` | `INT` | `NOT NULL` | `PK`, `IDENTITY(1,1)` | Clave subrogada de la dimensión. |
| `CustomerID` | `INT` | `NOT NULL` | `UQ_DimCustomer_CustomerID` | Clave de negocio (Business Key de `stg_demo1.customers`). |
| `CustomerName` | `VARCHAR(150)` | `NOT NULL` | Texto plano. | Nombre o razón social del cliente. |
| `Segment` | `VARCHAR(50)` | `NOT NULL` | `Contractor`, `Construction Company`, `Retailer`, `Individual`. | Segmentación comercial. |
| `RegionName` | `VARCHAR(100)` | `NOT NULL` | Denormalizado desde `stg_demo1.regions`. | Región base del cliente. |
| `RegistrationDate` | `DATE` | `NOT NULL` | Formato `YYYY-MM-DD`. | Fecha original de alta en el sistema. |

---

### 2.4 `dw_demo1.DimSalesperson`
Dimensión de la fuerza de ventas.

| Nombre Columna | Tipo de Dato | Nulabilidad | Restricciones / Reglas | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| `SalespersonKey` | `INT` | `NOT NULL` | `PK`, `IDENTITY(1,1)` | Clave subrogada de la dimensión. |
| `SalespersonID` | `INT` | `NOT NULL` | `UQ_DimSalesperson_SalespersonID` | Clave de negocio (Business Key de `stg_demo1.salespeople`). |
| `SalespersonName` | `VARCHAR(150)` | `NOT NULL` | Texto plano. | Nombre del vendedor. |
| `RegionName` | `VARCHAR(100)` | `NOT NULL` | Denormalizado desde `stg_demo1.regions`. | Región comercial asignada al vendedor. |

---

### 2.5 `dw_demo1.DimProduct`
Dimensión de productos de catálogo.

| Nombre Columna | Tipo de Dato | Nulabilidad | Restricciones / Reglas | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| `ProductKey` | `INT` | `NOT NULL` | `PK`, `IDENTITY(1,1)` | Clave subrogada de la dimensión. |
| `ProductID` | `INT` | `NOT NULL` | `UQ_DimProduct_ProductID` | Clave de negocio (Business Key de `stg_demo1.products`). |
| `ProductName` | `VARCHAR(150)` | `NOT NULL` | Texto plano. | Nombre comercial del producto. |
| `Category` | `VARCHAR(100)` | `NOT NULL` | Texto plano. | Categoría superior. |
| `Subcategory` | `VARCHAR(100)` | `NOT NULL` | Texto plano. | Subcategoría técnica. |
| `SupplierName` | `VARCHAR(150)` | `NOT NULL` | Denormalizado desde `stg_demo1.suppliers`. | Nombre del proveedor principal. |
| `ListPrice` | `DECIMAL(12,2)` | `NOT NULL` | `>= UnitCost` | Precio de lista base actual (USD). |
| `UnitCost` | `DECIMAL(12,2)` | `NOT NULL` | `> 0` | Costo unitario base actual (USD). |

---

### 2.6 `dw_demo1.DimDate`
Dimensión de tiempo estándar para análisis multidimensional.

| Nombre Columna | Tipo de Dato | Nulabilidad | Restricciones / Reglas | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| `DateKey` | `INT` | `NOT NULL` | `PK`, Formato entero `YYYYMMDD`. | Clave sustituta de fecha (ej. `20240115`). |
| `FullDate` | `DATE` | `NOT NULL` | Único, Formato `YYYY-MM-DD`. | Fecha completa en tipo `DATE`. |
| `Year` | `INT` | `NOT NULL` | Ej. `2024`, `2025`, `2026`. | Año numérico de 4 dígitos. |
| `Quarter` | `INT` | `NOT NULL` | `1` a `4`. | Trimestre del año. |
| `QuarterName` | `VARCHAR(10)` | `NOT NULL` | Ej. `Q1`, `Q2`, `Q3`, `Q4`. | Etiqueta corta del trimestre. |
| `Month` | `INT` | `NOT NULL` | `1` a `12`. | Mes numérico. |
| `MonthName` | `VARCHAR(20)` | `NOT NULL` | Ej. `January`, `February`, etc. | Nombre completo del mes. |
| `DayOfWeek` | `INT` | `NOT NULL` | `1` a `7`. | Día numérico de la semana. |
| `DayOfWeekName` | `VARCHAR(20)` | `NOT NULL` | Ej. `Monday`, `Tuesday`, etc. | Nombre del día de la semana. |
| `IsWeekend` | `BIT` | `NOT NULL` | `1` si es Sábado/Domingo, `0` en otro caso. | Indicador de fin de semana. |

---

### 2.7 `dw_demo1.FactSales`
Tabla de hechos principal del Data Warehouse. Su **grano** es de **una fila por cada línea de orden de venta (`SalesOrderLineID`)**.

| Nombre Columna | Tipo de Dato | Nulabilidad | Restricciones / Reglas | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| `SalesOrderLineID` | `BIGINT` | `NOT NULL` | `PK_FactSales` | Clave primaria del hecho (proviene de `order_line_id`). |
| `SalesOrderID` | `BIGINT` | `NOT NULL` | Clave transaccional. | Identificador de la cabecera de orden (`order_id`). |
| `DateKey` | `INT` | `NOT NULL` | `FK_FactSales_DimDate` | Relación con la dimensión de tiempo (derivado de `order_date`). |
| `CustomerKey` | `INT` | `NOT NULL` | `FK_FactSales_DimCustomer` | Relación con el cliente comprador. |
| `ProductKey` | `INT` | `NOT NULL` | `FK_FactSales_DimProduct` | Relación con el producto vendido. |
| `SalespersonKey` | `INT` | `NOT NULL` | `FK_FactSales_DimSalesperson` | Relación con el vendedor asignado. |
| `RegionKey` | `INT` | `NOT NULL` | `FK_FactSales_DimRegion` | **Región Comercial**: Derivada de la región del vendedor (`SalespersonKey`). |
| `WarehouseKey` | `INT` | `NOT NULL` | `FK_FactSales_DimWarehouse` | Relación con el almacén de despacho. |
| `Quantity` | `INT` | `NOT NULL` | `CHK_FactSales_Quantity`: `Quantity > 0` | Cantidad de unidades vendidas. |
| `UnitPrice` | `DECIMAL(12,2)` | `NOT NULL` | `CHK_FactSales_UnitPrice`: `UnitPrice >= 0` | Precio transaccional cobrado por unidad (USD). |
| `UnitCost` | `DECIMAL(12,2)` | `NOT NULL` | `CHK_FactSales_UnitCost`: `UnitCost > 0` | Costo transaccional unitario registrado (USD). |
| `DiscountAmount` | `DECIMAL(12,2)` | `NOT NULL` | `CHK_FactSales_Discount`: `>= 0`<br>`CHK_FactSales_DiscountNotExceedGross`: `<= Quantity * UnitPrice` | Monto total de descuento otorgado en la línea (USD). |
| `Revenue` | `DECIMAL(12,2)` | `NULL` (Calculado) | **Columna calculada persistida:**<br>`(Quantity * UnitPrice) - DiscountAmount` | Venta Neta o Ingreso computable generado por la línea (USD). |
| `TotalCost` | `DECIMAL(12,2)` | `NULL` (Calculado) | **Columna calculada persistida:**<br>`Quantity * UnitCost` | Costo total transaccional acumulado de la línea (USD). |
| `GrossProfit` | `DECIMAL(12,2)` | `NULL` (Calculado) | **Columna calculada persistida:**<br>`Revenue - TotalCost` | Ganancia o Utilidad Bruta generada por la línea (USD). |