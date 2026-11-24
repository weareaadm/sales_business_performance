# Business Case, Case Study & Power BI Specification
## Sales & Business Performance — B2B Construction Materials Enterprise Analytics

**Repositorio:** `02_sales_business_performance`  
**Versión del documento:** 1.0  
**Dominio:** Distribución mayorista B2B de materiales de construcción  
**Periodo analítico:** 2024-01-01 a 2026-12-31  
**Moneda de análisis:** USD  
**Fuente analítica:** SQL Server — `dw_demo1`  
**Estado:** Especificación funcional para construir el modelo semántico, las medidas DAX y los dashboards Power BI.

---

# 1. Business Case

## 1.1 Contexto del negocio

La empresa del caso es una distribuidora mayorista ficticia de materiales de construcción e insumos industriales, con operación comercial en Lima, Perú.

Atiende cuatro segmentos:

- **Contractor:** contratistas de obras medianas y remodelaciones.
- **Construction Company:** empresas de infraestructura y construcción de gran escala.
- **Retailer:** ferreterías y cadenas minoristas.
- **Individual:** compradores individuales y compras ocasionales.

La operación cuenta con ocho regiones comerciales, 50 vendedores, ocho almacenes, 50 proveedores, 500 productos y 2,000 clientes.

El histórico sintético cubre tres años completos, desde enero de 2024 hasta diciembre de 2026. La generación de datos utiliza `SEED = 42` para que los resultados puedan reproducirse.

## 1.2 Problema de negocio

La dirección necesita una visión integrada de las ventas y la rentabilidad para responder preguntas que no se resuelven observando únicamente el importe facturado:

- ¿Cómo evolucionan las ventas y la utilidad bruta?
- ¿Qué regiones generan más ingresos y cuáles tienen mejores márgenes?
- ¿Qué segmentos y clientes aportan más valor?
- ¿Qué categorías y productos son más rentables?
- ¿Cómo se comporta el equipo comercial?
- ¿Qué cambios temporales o eventos del mercado afectan los márgenes?

El análisis debe permitir distinguir entre crecimiento de facturación y crecimiento rentable. Una región puede vender mucho y, al mismo tiempo, tener un margen inferior por su mezcla de productos y descuentos.

## 1.3 Objetivo del proyecto

Construir una solución de Business Intelligence que transforme los datos transaccionales en información confiable para monitorear:

1. Ventas netas y descuentos.
2. Costos y utilidad bruta.
3. Porcentaje de margen bruto.
4. Desempeño por tiempo, región y vendedor.
5. Comportamiento y concentración de clientes.
6. Rentabilidad por categoría y producto.

El resultado esperado es un dashboard ejecutivo y un conjunto de páginas de análisis que permitan explorar los resultados con filtros consistentes.

## 1.4 Alcance

### Incluido en este proyecto

- Ventas completadas (`Completed`).
- Revenue, Gross Revenue, descuentos, costos y Gross Profit.
- Análisis temporal entre 2024 y 2026.
- Análisis por región comercial, vendedor y almacén.
- Análisis por cliente y segmento.
- Análisis por producto, subcategoría y categoría.
- Comparación de ventas y margen entre periodos.
- Concentración de ingresos por cliente (Pareto).
- Conciliación de métricas SQL Server ↔ DAX.

### Fuera del alcance actual

- Inventario disponible y valorización de existencias.
- Rotación de inventario y días de inventario.
- Quiebres de stock.
- Fulfillment rate y cumplimiento real de entregas.
- Capacidad y productividad operativa de almacenes.
- Gastos operativos, marketing, distribución y utilidad neta.
- Comisiones reales de vendedores.

Estos temas pueden formar parte de una futura solución **Operations & Supply Chain**, pero no deben simularse con las tablas actuales.

## 1.5 Usuarios y decisiones

| Usuario | Necesidad | Decisiones que debe facilitar el dashboard |
|---|---|---|
| CEO / Gerencia General | Visión consolidada del negocio | Evaluar crecimiento, ventas y rentabilidad |
| Gerencia Comercial | Desempeño por región y vendedor | Identificar oportunidades y brechas comerciales |
| Finanzas | Ingresos, descuentos, costos y utilidad | Monitorear rentabilidad y presión sobre márgenes |
| Gestión de Clientes | Segmentos y concentración | Priorizar clientes y detectar dependencia comercial |
| Gestión de Producto | Categorías y productos | Identificar productos que aportan ingresos y utilidad |

## 1.6 Criterios de éxito

El dashboard será aceptado cuando:

- Las métricas financieras estén definidas con las fórmulas de este documento.
- Los importes y conteos principales concilien con SQL Server bajo los mismos filtros.
- Los filtros de fecha, región, segmento, vendedor y producto funcionen de forma coherente.
- Los indicadores de margen se calculen como razón entre importes agregados, no como promedio simple de porcentajes por fila.
- Las páginas respondan las preguntas de negocio descritas en esta especificación.
- Se documenten las limitaciones del dataset sintético y de las tablas disponibles.

---

# 2. Case Study

## 2.1 Escenario

La dirección comercial observa diferencias entre regiones: algunas generan un volumen alto de facturación, mientras otras muestran mejores porcentajes de margen. También existen cambios de costos en determinadas categorías que pueden afectar temporalmente la rentabilidad.

El equipo de Analytics debe construir una vista única de ventas completadas y explicar qué factores están detrás de los resultados: tiempo, mezcla de productos, segmentos de clientes, región comercial y desempeño de vendedores.

## 2.2 Flujo comercial

```text
Customer
   |
   v
Salesperson
   |
   v
Sales Order (cabecera y estado)
   |
   v
Sales Order Lines (producto, cantidad, precio, costo y descuento)
   |
   v
Revenue / Total Cost / Gross Profit
```

Cada línea de orden representa una combinación transaccional de producto, cantidad, precio, costo y descuento. La tabla de hechos conserva ese nivel de detalle.

## 2.3 Preguntas que debe resolver el análisis

### Ventas y evolución

- ¿Cuál es el Revenue total del periodo?
- ¿Cómo evolucionan Revenue, Gross Profit y unidades por mes?
- ¿Qué años, trimestres o meses presentan mayor crecimiento?
- ¿Cuál es el valor promedio de una orden (AOV)?

### Rentabilidad

- ¿Qué regiones, categorías y productos generan mayor Gross Profit?
- ¿Dónde se observa un margen bruto menor?
- ¿Qué relación existe entre descuentos y margen?
- ¿Cómo cambia el margen cuando aumenta el costo de una categoría?

### Clientes

- ¿Qué segmentos generan más Revenue y Gross Profit?
- ¿Qué clientes concentran la mayor parte de los ingresos?
- ¿Cuántos clientes activos compraron en el periodo filtrado?
- ¿Cuál es el Revenue promedio por cliente activo?

### Región y equipo comercial

- ¿Qué regiones comerciales lideran en ventas y margen?
- ¿Qué vendedores generan mayor Revenue y Gross Profit?
- ¿La región con mayor facturación es también la de mejor margen?
- ¿Cómo se distribuye el desempeño entre vendedores?

### Productos

- ¿Qué categorías y subcategorías generan más ventas?
- ¿Qué productos aportan más utilidad bruta?
- ¿Qué productos tienen alta facturación pero menor margen?
- ¿Qué efecto tuvo el incremento de costos de Steel & Rebar en 2025?

## 2.4 Patrones de negocio que deben investigarse

El dataset incorpora patrones sintéticos intencionados. Deben tratarse como hipótesis analíticas que el dashboard permite comprobar, no como conclusiones que se deban mostrar como hechos sin validación.

### A. Diferencia regional de mezcla y margen

- **Norte:** mayor ponderación de Steel & Rebar vendido a Construction Company. Se espera una facturación elevada y presión sobre el margen por el menor margen base de la categoría y los descuentos corporativos.
- **Sur:** mayor ponderación de Tools & Equipment y Paints & Finishes vendido a Contractor. Se espera un porcentaje de margen superior, aunque el volumen de facturación pueda ser menor.

La región comercial de la venta se deriva del vendedor asignado. No debe confundirse con la región base del cliente ni con la ubicación física del almacén.

### B. Incremento de costos de Steel & Rebar en 2025

Entre agosto y octubre de 2025, el costo transaccional de Steel & Rebar aumenta un 14%.

- Agosto de 2025: el precio de venta permanece en el nivel base, por lo que se espera una contracción del margen.
- Septiembre y octubre de 2025: el precio de venta incorpora el incremento, por lo que se espera una recuperación del margen.
- Desde noviembre de 2025: costos y precios regresan a sus niveles base.

El análisis debe permitir comparar la evolución mensual de Revenue, Total Cost, Gross Profit y Gross Margin % para Steel & Rebar y contrastarla con otras categorías.

### C. Estacionalidad

El diseño del dataset concentra aproximadamente el 45% del volumen anual de órdenes entre junio y octubre. El dashboard debe permitir comprobar la distribución mensual de ventas y unidades.

## 2.5 Interpretación correcta de la geografía

Existen perspectivas geográficas distintas:

1. **Región comercial de la venta:** región asignada al vendedor. Es la perspectiva oficial para analizar desempeño regional de ventas y corresponde a `FactSales.RegionKey`.
2. **Región base del cliente:** atributo descriptivo de `DimCustomer`. Sirve para segmentar la cartera de clientes, pero no es la región comercial de la venta.
3. **Región física del almacén:** `DimWarehouse[RegionName]`. Describe la ubicación del almacén asociado a la transacción.

No se deben intercambiar estas perspectivas ni presentar `DimCustomer[RegionName]` como si fuera `FactSales.RegionKey`.

---

# 3. Fuente de datos y arquitectura analítica

## 3.1 Pipeline

```text
Especificaciones y reglas de negocio
          |
          v
Python — generación sintética reproducible (SEED = 42)
          |
          v
CSV en data/generated/
          |
          v
SQL Server — Staging (stg_demo1)
          |
          v
SQL Server — Data Warehouse (dw_demo1)
          |
          v
Validación y conciliación SQL
          |
          v
Power BI — Modelo semántico + DAX
          |
          v
Dashboards de Sales & Business Performance
```

## 3.2 Fuente recomendada para Power BI

Conectar Power BI a SQL Server y consumir las tablas del esquema `dw_demo1`.

**Tabla de hechos:**

- `dw_demo1.FactSales`

**Dimensiones:**

- `dw_demo1.DimDate`
- `dw_demo1.DimRegion`
- `dw_demo1.DimWarehouse`
- `dw_demo1.DimCustomer`
- `dw_demo1.DimSalesperson`
- `dw_demo1.DimProduct`

No conectar los CSV directamente al modelo semántico para el dashboard final si el Data Warehouse ya está cargado y validado. Los CSV y `stg_demo1` son capas de generación, ingesta y auditoría.

## 3.3 Grano de la tabla de hechos

`FactSales` tiene una fila por línea de orden de venta (`SalesOrderLineID`).

Por tanto:

- `COUNTROWS(FactSales)` representa líneas de orden, no órdenes.
- Una orden puede tener varias líneas.
- Para contar órdenes se debe usar `DISTINCTCOUNT(FactSales[SalesOrderID])`.
- Para contar clientes compradores se debe usar `DISTINCTCOUNT(FactSales[CustomerKey])`.

## 3.4 Regla de inclusión de ventas

`FactSales` incluye exclusivamente líneas pertenecientes a órdenes cuyo estado es `Completed`.

Las órdenes `Cancelled` y `Pending` permanecen en Staging, pero no contribuyen a los indicadores financieros del dashboard actual.

Por este motivo, el dashboard basado únicamente en `FactSales` representa ventas completadas. No debe utilizarse para calcular tasas de cancelación o pendientes: para ello se necesitaría un modelo operativo adicional basado en las cabeceras de órdenes de Staging.

## 3.5 Modelo dimensional y relaciones

Usar un esquema en estrella con relaciones de uno a muchos desde las dimensiones hacia `FactSales`.

| Dimensión | Clave en dimensión | Clave en FactSales | Cardinalidad |
|---|---|---|---|
| DimDate | `DateKey` | `DateKey` | 1:* |
| DimCustomer | `CustomerKey` | `CustomerKey` | 1:* |
| DimProduct | `ProductKey` | `ProductKey` | 1:* |
| DimSalesperson | `SalespersonKey` | `SalespersonKey` | 1:* |
| DimRegion | `RegionKey` | `RegionKey` | 1:* |
| DimWarehouse | `WarehouseKey` | `WarehouseKey` | 1:* |

Configuración recomendada:

- Relaciones activas.
- Dirección de filtro simple: dimensión → hecho.
- No crear relaciones entre dimensiones si no son necesarias.
- No relacionar `DimCustomer[RegionName]` directamente con `DimRegion`.
- Marcar `DimDate` como tabla de fechas usando `DimDate[FullDate]`.
- Ordenar `DimDate[MonthName]` por `DimDate[Month]`.
- Ordenar `DimDate[QuarterName]` por `DimDate[Quarter]`.
- Usar las claves subrogadas para las relaciones.

## 3.6 Campos disponibles en las dimensiones

### `DimDate`

`DateKey`, `FullDate`, `Year`, `Quarter`, `QuarterName`, `Month`, `MonthName`, `DayOfWeek`, `DayOfWeekName`, `IsWeekend`.

### `DimRegion`

`RegionKey`, `RegionID`, `RegionName`, `Country`.

Representa la región comercial de la venta cuando filtra `FactSales`.

### `DimWarehouse`

`WarehouseKey`, `WarehouseID`, `WarehouseName`, `RegionName`.

Representa el almacén de despacho asociado a la línea de venta.

### `DimCustomer`

`CustomerKey`, `CustomerID`, `CustomerName`, `Segment`, `RegionName`, `RegistrationDate`.

`RegionName` es la región base del cliente.

### `DimSalesperson`

`SalespersonKey`, `SalespersonID`, `SalespersonName`, `RegionName`.

`RegionName` corresponde a la región asignada al vendedor.

### `DimProduct`

`ProductKey`, `ProductID`, `ProductName`, `Category`, `Subcategory`, `SupplierName`, `ListPrice`, `UnitCost`.

`ListPrice` y `UnitCost` son atributos del catálogo; para calcular la rentabilidad histórica se deben utilizar `FactSales[UnitPrice]` y `FactSales[UnitCost]`, que corresponden a los valores transaccionales.

### `FactSales`

`SalesOrderLineID`, `SalesOrderID`, `DateKey`, `CustomerKey`, `ProductKey`, `SalespersonKey`, `RegionKey`, `WarehouseKey`, `Quantity`, `UnitPrice`, `UnitCost`, `DiscountAmount`, `Revenue`, `TotalCost`, `GrossProfit`.

`Revenue`, `TotalCost` y `GrossProfit` son columnas calculadas persistidas en SQL Server.

---

# 4. Definiciones de negocio y métricas

Las medidas deben respetar estas definiciones. No crear fórmulas alternativas con nombres similares sin documentar la diferencia.

| Métrica | Definición | Fórmula |
|---|---|---|
| Gross Revenue | Venta antes de descuentos | `Quantity × UnitPrice` |
| Total Discount | Descuento monetario acumulado | `SUM(DiscountAmount)` |
| Total Revenue | Venta neta | `(Quantity × UnitPrice) - DiscountAmount` |
| Total Cost | Costo de venta | `Quantity × UnitCost` |
| Total Gross Profit | Utilidad bruta | `Revenue - TotalCost` |
| Gross Margin % | Utilidad bruta sobre venta neta | `GrossProfit / Revenue` |
| Total Units | Unidades vendidas | `SUM(Quantity)` |
| Total Orders | Órdenes distintas | `DISTINCTCOUNT(SalesOrderID)` |
| Total Order Lines | Líneas de orden | `COUNTROWS(FactSales)` |
| Active Customers | Clientes con ventas en el contexto actual | `DISTINCTCOUNT(CustomerKey)` |
| AOV | Venta neta promedio por orden | `Revenue / Total Orders` |
| Avg Revenue per Customer | Venta neta promedio por cliente activo | `Revenue / Active Customers` |
| Discount Rate % | Descuento sobre venta bruta | `Total Discount / Gross Revenue` |

**Regla de agregación:** Gross Margin % y Discount Rate % deben calcularse dividiendo los importes agregados del contexto actual. No utilizar `AVERAGE` sobre porcentajes calculados por línea.

## 4.1 Medidas DAX base

Las siguientes medidas reflejan las definiciones existentes en `dax/measures.md` del repositorio:

```dax
Gross Revenue =
SUMX (
    FactSales,
    FactSales[Quantity] * FactSales[UnitPrice]
)

Total Discount =
SUM ( FactSales[DiscountAmount] )

Total Revenue =
SUM ( FactSales[Revenue] )

Total Cost =
SUM ( FactSales[TotalCost] )

Total Gross Profit =
SUM ( FactSales[GrossProfit] )

Total Units =
SUM ( FactSales[Quantity] )

Total Orders =
DISTINCTCOUNT ( FactSales[SalesOrderID] )

Total Order Lines =
COUNTROWS ( FactSales )

Active Customers =
DISTINCTCOUNT ( FactSales[CustomerKey] )
```

## 4.2 Medidas DAX de rentabilidad y promedios

```dax
Gross Margin % =
DIVIDE ( [Total Gross Profit], [Total Revenue], 0 )

Discount Rate % =
DIVIDE ( [Total Discount], [Gross Revenue], 0 )

Avg Order Value (AOV) =
DIVIDE ( [Total Revenue], [Total Orders], 0 )

Avg Units per Order =
DIVIDE ( [Total Units], [Total Orders], 0 )

Avg Revenue per Customer =
DIVIDE ( [Total Revenue], [Active Customers], 0 )
```

## 4.3 Inteligencia de tiempo

Requiere que `DimDate[FullDate]` esté marcada como Date Table y que la relación con `FactSales` esté activa.

```dax
Revenue YTD =
TOTALYTD ( [Total Revenue], DimDate[FullDate] )

Gross Profit YTD =
TOTALYTD ( [Total Gross Profit], DimDate[FullDate] )

Revenue PY =
CALCULATE (
    [Total Revenue],
    SAMEPERIODLASTYEAR ( DimDate[FullDate] )
)

Revenue YoY =
[Total Revenue] - [Revenue PY]

Revenue YoY % =
DIVIDE ( [Revenue YoY], [Revenue PY] )

Gross Margin % PY =
CALCULATE (
    [Gross Margin %],
    SAMEPERIODLASTYEAR ( DimDate[FullDate] )
)

Gross Margin % YoY (bps) =
( [Gross Margin %] - [Gross Margin % PY] ) * 10000
```

## 4.4 Concentración de clientes — Pareto

```dax
Customer Revenue Rank =
RANKX (
    ALLSELECTED ( DimCustomer[CustomerName] ),
    [Total Revenue],
    ,
    DESC,
    Dense
)

Cumulative Customer Revenue =
VAR CurrentRev = [Total Revenue]
RETURN
    CALCULATE (
        [Total Revenue],
        FILTER (
            ALLSELECTED ( DimCustomer[CustomerName] ),
            [Total Revenue] >= CurrentRev
        )
    )

Cumulative Customer Revenue % =
DIVIDE (
    [Cumulative Customer Revenue],
    CALCULATE (
        [Total Revenue],
        ALLSELECTED ( DimCustomer[CustomerName] )
    ),
    0
)
```

La medida acumulada debe probarse con el orden descendente por Revenue y con los filtros de página. Si existen empates de Revenue, varios clientes pueden compartir rango y el acumulado puede avanzar por grupos empatados.

## 4.5 Formato recomendado

| Tipo de medida | Formato |
|---|---|
| Revenue, Gross Revenue, Cost, Gross Profit, Discount, AOV | Moneda USD, 2 decimales |
| Gross Margin %, Discount Rate %, Revenue YoY % | Porcentaje, 1–2 decimales |
| Gross Margin % YoY (bps) | Número entero con sufijo `bps` |
| Total Units, Total Orders, Total Order Lines, Active Customers | Entero con separador de miles |
| Revenue Rank | Entero |

---

# 5. Power BI Specification

## 5.1 Objetivo de diseño

Construir un reporte ejecutivo, claro y navegable. La primera página debe responder rápidamente cómo está funcionando el negocio. Las páginas siguientes deben permitir explicar los resultados por tiempo, clientes, productos y equipo comercial.

El diseño debe priorizar:

- Jerarquía visual clara.
- Pocos KPI principales por página.
- Comparaciones temporales legibles.
- Títulos dinámicos cuando los filtros cambien.
- Formatos numéricos consistentes.
- Tooltips útiles y drill-through cuando aporten valor.
- Ausencia de gráficos decorativos que no respondan preguntas de negocio.

## 5.2 Navegación propuesta

Se proponen cinco páginas:

1. Executive Overview
2. Sales Trends
3. Customer Analysis
4. Product Profitability
5. Regional & Sales Performance

La estructura aprovecha las áreas analíticas del proyecto y amplía el análisis temporal y comercial. Si se desea mantener un reporte más compacto, las páginas 2 y 5 pueden integrarse.

## 5.3 Filtros globales

Incluir, cuando corresponda:

- Year
- Quarter
- Month
- Region (región comercial de la venta)
- Customer Segment
- Product Category
- Salesperson

Reglas:

- Los filtros deben sincronizarse entre páginas cuando tengan el mismo significado.
- Evitar mezclar región comercial, región del cliente y región del almacén en un único slicer llamado simplemente `Region`.
- Si se necesita analizar región del cliente, etiquetar el filtro como `Customer Region`.
- Ofrecer un botón para limpiar filtros.
- Mostrar el periodo seleccionado en el encabezado o subtítulo.

## 5.4 Página 1 — Executive Overview

**Objetivo:** presentar el estado general de ventas y rentabilidad.

### KPI cards

- Total Revenue
- Total Gross Profit
- Gross Margin %
- Total Orders
- Total Units
- Avg Order Value (AOV)

### Visuales

| Visual | Campos / medidas | Pregunta |
|---|---|---|
| Línea mensual | `DimDate[FullDate]`, Total Revenue, Total Gross Profit | ¿Cómo evolucionan ventas y utilidad? |
| Barras por región | `DimRegion[RegionName]`, Total Revenue | ¿Qué regiones aportan más ingresos? |
| Barras por categoría | `DimProduct[Category]`, Total Revenue | ¿Qué categorías impulsan las ventas? |
| Segmentos de clientes | `DimCustomer[Segment]`, Total Revenue | ¿Qué segmentos contribuyen más? |
| Tabla de resumen | Región, Revenue, Gross Profit, Gross Margin % | ¿Qué regiones combinan volumen y rentabilidad? |

### Diseño sugerido

- Parte superior: título, periodo y filtros principales.
- Primera fila: KPI cards.
- Zona central: tendencia mensual y Revenue por región.
- Zona inferior: contribución por categoría y segmento.

### Insight esperado

Identificar si el crecimiento de ventas está acompañado por crecimiento de utilidad y qué regiones o categorías explican el resultado.

## 5.5 Página 2 — Sales Trends

**Objetivo:** analizar la evolución temporal de las ventas y sus variaciones.

### KPI cards

- Total Revenue
- Revenue YoY %
- Revenue YTD
- Gross Profit YTD
- Total Orders

### Visuales

| Visual | Campos / medidas | Pregunta |
|---|---|---|
| Línea mensual | Revenue y Gross Profit por FullDate | ¿Cuál es la tendencia mensual? |
| Columnas por año | Total Revenue por Year | ¿Cómo cambia la facturación anual? |
| Matriz Año × Mes | Revenue, Gross Profit, Gross Margin % | ¿Qué meses explican los cambios? |
| Línea de margen | Gross Margin % por mes | ¿En qué periodos se comprime el margen? |
| Unidades por mes | Total Units por FullDate | ¿La evolución del volumen acompaña a la venta? |

### Análisis requerido

- Comparar 2024, 2025 y 2026.
- Identificar estacionalidad entre junio y octubre.
- Revisar la variación interanual.
- Analizar el periodo agosto–octubre de 2025 para Steel & Rebar.

El año 2026 debe interpretarse como parte del dataset sintético cerrado, no como información real ni como pronóstico.

## 5.6 Página 3 — Customer Analysis

**Objetivo:** entender la contribución, el valor y la concentración de los clientes.

### KPI cards

- Active Customers
- Total Revenue
- Avg Revenue per Customer
- Avg Order Value (AOV)

### Visuales

| Visual | Campos / medidas | Pregunta |
|---|---|---|
| Barras por segmento | Segment, Revenue | ¿Qué segmentos aportan más ventas? |
| Barras por segmento | Segment, Gross Profit y Gross Margin % | ¿Qué segmentos son más rentables? |
| Top 10 clientes | CustomerName, Revenue | ¿Quiénes son los principales clientes? |
| Pareto de clientes | Customer Revenue Rank, Cumulative Customer Revenue % | ¿Qué tan concentrados están los ingresos? |
| Tabla de clientes | CustomerName, Segment, Revenue, Orders, AOV, Gross Profit, Margin % | ¿Qué clientes combinan valor y rentabilidad? |

### Interacciones

- Seleccionar un segmento debe filtrar el ranking de clientes.
- Permitir drill-through a una página de detalle de cliente si se implementa.
- Mostrar el ranking según Revenue del contexto filtrado.

### Insight esperado

Detectar dependencia de pocos clientes y diferencias entre segmentos en volumen, valor promedio y margen.

## 5.7 Página 4 — Product Profitability

**Objetivo:** analizar la contribución económica de categorías, subcategorías y productos.

### KPI cards

- Total Revenue
- Total Cost
- Total Gross Profit
- Gross Margin %
- Total Discount

### Visuales

| Visual | Campos / medidas | Pregunta |
|---|---|---|
| Barras por categoría | Category, Revenue | ¿Qué categorías venden más? |
| Barras por categoría | Category, Gross Profit | ¿Qué categorías aportan más utilidad? |
| Dispersión | Revenue y Gross Margin % por producto | ¿Qué productos combinan volumen y margen? |
| Top / Bottom productos | ProductName, Revenue, Gross Profit, Margin % | ¿Qué productos destacan o requieren atención? |
| Tendencia Steel & Rebar | Mes, Revenue, Total Cost, Gross Profit, Gross Margin % | ¿Qué ocurrió durante el incremento de costos de 2025? |
| Matriz de producto | Category, Subcategory, ProductName, Revenue, Cost, Gross Profit, Margin % | ¿Dónde se genera la rentabilidad? |

### Reglas

- La rentabilidad histórica debe usar el costo transaccional de `FactSales[UnitCost]`, no `DimProduct[UnitCost]`.
- No interpretar `ListPrice` como precio de venta real de cada transacción.
- Permitir analizar descuentos y margen conjuntamente.
- No presentar margen negativo como error automáticamente: el caso de Steel & Rebar en agosto de 2025 contempla una compresión temporal del margen.

## 5.8 Página 5 — Regional & Sales Performance

**Objetivo:** comparar regiones comerciales y desempeño de vendedores.

### KPI cards

- Total Revenue
- Total Gross Profit
- Gross Margin %
- Total Orders
- Active Customers

### Visuales

| Visual | Campos / medidas | Pregunta |
|---|---|---|
| Ranking de regiones | RegionName, Revenue | ¿Qué regiones venden más? |
| Comparación regional | RegionName, Gross Profit y Gross Margin % | ¿Qué regiones son más rentables? |
| Ranking de vendedores | SalespersonName, Revenue, Gross Profit, Margin % | ¿Quiénes contribuyen más? |
| Dispersión de vendedores | Revenue vs Gross Margin %, detalle SalespersonName | ¿Quién combina volumen y rentabilidad? |
| Matriz región-vendedor | RegionName, SalespersonName, Revenue, Orders, Gross Profit | ¿Cómo se distribuye el resultado comercial? |
| Tendencia por región | FullDate, Revenue, leyenda RegionName | ¿Cómo evoluciona cada territorio? |

### Reglas

- La región de esta página debe ser `DimRegion[RegionName]`, que filtra por `FactSales[RegionKey]`.
- `DimSalesperson[RegionName]` debe ser consistente con la región comercial asignada al vendedor.
- No sumar resultados de regiones diferentes como si fueran almacenes.
- No inferir comisiones, cuotas o cumplimiento de objetivos porque esos datos no forman parte del modelo actual.

---

# 6. Interacciones, UX y navegación

## 6.1 Interacciones

- Los gráficos deben filtrar o resaltar otros visuales solo cuando la relación analítica sea clara.
- Los KPI cards deben responder a los filtros de página y reporte.
- Los títulos deben indicar el contexto seleccionado cuando sea útil.
- Los tooltips deben mostrar Revenue, Gross Profit, Gross Margin %, Orders y Units según el visual.
- Incorporar drill-through para detalle de cliente, producto o vendedor si mejora la exploración.

## 6.2 Tooltips sugeridos

**Tooltip de región:**
- Total Revenue
- Total Gross Profit
- Gross Margin %
- Total Orders
- Active Customers

**Tooltip de producto:**
- Total Revenue
- Total Cost
- Total Gross Profit
- Gross Margin %
- Total Units
- Total Discount

**Tooltip de cliente:**
- Segment
- Total Revenue
- Total Orders
- Avg Order Value
- Total Gross Profit
- Gross Margin %

## 6.3 Formato y accesibilidad

- Usar USD como moneda de presentación.
- Mantener dos decimales en importes cuando el espacio lo permita.
- Utilizar porcentajes para márgenes y tasas.
- Evitar depender únicamente del color para expresar resultados.
- Mantener escalas y formatos consistentes entre páginas.
- Incluir títulos claros, unidades y periodos.
- Evitar exceso de visuales, bordes y etiquetas.

---

# 7. Validación y conciliación SQL ↔ DAX

La exactitud de las medidas es un criterio obligatorio. SQL Server es la referencia de validación de los datos procesados en el Data Warehouse; Power BI presenta y permite explorar esos mismos resultados.

## 7.1 Reglas de conciliación

Para cada medida principal:

1. Ejecutar la agregación equivalente en SQL sobre `dw_demo1.FactSales`.
2. Ejecutar la medida DAX en Power BI con exactamente el mismo periodo y filtros.
3. Comparar los resultados.
4. Documentar la diferencia y explicar cualquier discrepancia.
5. No publicar el reporte como validado si existen diferencias no explicadas.

## 7.2 Matriz mínima de pruebas

| Prueba | SQL de referencia | Medida DAX | Resultado esperado |
|---|---|---|---|
| Revenue total | `SUM(Revenue)` | `[Total Revenue]` | Igualdad |
| Gross Revenue | `SUM(Quantity * UnitPrice)` | `[Gross Revenue]` | Igualdad |
| Discount | `SUM(DiscountAmount)` | `[Total Discount]` | Igualdad |
| Total Cost | `SUM(TotalCost)` | `[Total Cost]` | Igualdad |
| Gross Profit | `SUM(GrossProfit)` | `[Total Gross Profit]` | Igualdad |
| Units | `SUM(Quantity)` | `[Total Units]` | Igualdad |
| Orders | `COUNT(DISTINCT SalesOrderID)` | `[Total Orders]` | Igualdad |
| Order Lines | `COUNT(*)` | `[Total Order Lines]` | Igualdad |
| Customers | `COUNT(DISTINCT CustomerKey)` | `[Active Customers]` | Igualdad |
| Gross Margin % | `SUM(GrossProfit) / SUM(Revenue)` | `[Gross Margin %]` | Igualdad dentro de tolerancia |

Para importes monetarios, definir una tolerancia máxima de USD 0.01 cuando la precisión o el formato de presentación lo requieran. Los conteos deben coincidir exactamente. Los porcentajes deben compararse con una precisión acordada y sobre los mismos importes base.

## 7.3 Pruebas de filtros

Repetir las conciliaciones al menos para:

- Año.
- Mes.
- Región comercial.
- Segmento de cliente.
- Categoría de producto.
- Vendedor.

También comprobar que la selección de un vendedor filtre la región comercial correspondiente y que los filtros de cliente y almacén no alteren accidentalmente el significado de la región comercial.

## 7.4 Validación de inteligencia de tiempo

- Confirmar que `DimDate` contiene el calendario necesario para el periodo analítico.
- Confirmar que `FullDate` es única y está marcada como Date Table.
- Verificar que Revenue PY compare el mismo periodo del año anterior.
- Verificar YTD con el mismo contexto de fechas.
- Probar los límites entre años y meses.
- No mostrar variaciones YoY como cero cuando el periodo comparable no existe; evaluar si corresponde devolver BLANK.

## 7.5 Evidencia

Guardar los resultados de validación en el repositorio, por ejemplo:

```text
02_sales_business_performance/
├── dax/
│   ├── measures.md
│   └── reconciliation_results.md
└── dashboard/
    ├── dashboard_link.md
    ├── screenshots/
    └── validation/
```

La evidencia debe incluir fecha de ejecución, filtros aplicados, consulta SQL, medida DAX, resultado de ambos lados y estado `PASS` o `FAIL`.

---

# 8. Entregables

## 8.1 Entregables Power BI

- Archivo `.pbix` del proyecto.
- Modelo semántico con relaciones documentadas.
- Medidas DAX organizadas por carpetas de visualización.
- Cinco páginas del reporte según esta especificación (o una consolidación documentada).
- Tooltips e interacciones configurados.
- Formatos y nombres de medidas consistentes.

## 8.2 Entregables de documentación

- `dax/measures.md`: catálogo completo de medidas, fórmulas y formatos.
- `dashboard/dashboard_link.md`: enlace al reporte publicado, si aplica.
- `dashboard/screenshots/`: capturas finales por página.
- `dax/reconciliation_results.md`: evidencia de conciliación SQL ↔ DAX.
- Actualización del `README.md` con alcance y entregables.

## 8.3 Criterios de aceptación final

- [ ] El modelo Power BI utiliza `dw_demo1` como fuente del reporte.
- [ ] El modelo respeta el grano de una fila por línea de orden.
- [ ] Las seis relaciones dimensión-hecho están activas y correctamente configuradas.
- [ ] `DimDate` está marcada como tabla de fechas.
- [ ] Las medidas financieras siguen las definiciones de negocio.
- [ ] Las medidas principales concilian con SQL.
- [ ] Los filtros funcionan correctamente en todas las páginas.
- [ ] La región comercial no se confunde con la región del cliente ni con la región del almacén.
- [ ] El reporte no presenta indicadores de inventario, fulfillment, cancelaciones o comisiones que no estén soportados por el modelo.
- [ ] Las cinco páginas (o la estructura consolidada documentada) responden las preguntas de negocio.
- [ ] Se guardaron capturas y evidencia de validación.
- [ ] Se documentaron limitaciones y supuestos del dataset sintético.

---

# 9. Limitaciones y supuestos

1. Los datos son sintéticos y reproducibles; no representan transacciones reales de una empresa.
2. El periodo 2024–2026 es un dataset cerrado de tres años completos.
3. `FactSales` solo incluye órdenes `Completed`.
4. No es posible calcular cancelaciones, pendientes ni conversión de órdenes usando únicamente `FactSales`.
5. No existen tablas de inventario, existencias, costos de almacenamiento ni entregas reales.
6. Gross Profit es utilidad bruta antes de gastos operativos, financieros, comerciales y tributarios.
7. No existen cuotas comerciales ni objetivos por vendedor; por ello, no se debe mostrar attainment o cumplimiento de cuota.
8. La región comercial se asigna por el vendedor; la región del cliente y la ubicación del almacén son atributos distintos.
9. El incremento de costos y los patrones regionales son eventos incorporados deliberadamente en los datos sintéticos.
10. Los resultados exactos deben obtenerse de la ejecución reproducible y de las consultas de validación, no estimarse a partir de los objetivos de generación.

---

# 10. Referencias internas del repositorio

Este documento se alinea con los siguientes archivos:

- `README.md`
- `case_study/business_case.md`
- `data_specification/business_rules.md`
- `data_specification/data_dictionary.md`
- `data_specification/data_generation_spec.md`
- `data_specification/source_to_target_mapping.md`
- `sql/01_create_schema_and_tables.sql`
- `sql/02_dimensions.sql`
- `sql/03_facts.sql`
- `sql/04_analysis.sql`
- `dax/measures.md`
- `tests/phase3_dw/`
- `tests/phase4_validation/`

**Principio rector:** SQL valida la consistencia de los datos y las reglas de negocio; DAX implementa las métricas del modelo semántico; Power BI comunica los resultados mediante una experiencia interactiva. Los tres niveles deben utilizar las mismas definiciones.