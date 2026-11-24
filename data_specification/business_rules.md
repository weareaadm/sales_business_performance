# BUSINESS RULES & DATA QUALITY SPECIFICATION

**Proyecto:** B2B Construction Materials Enterprise Analytics  
**Versión:** 2.0 
**Esquemas de Aplicación:** `stg_demo1` (Staging) | `dw_demo1` (Data Warehouse)  
**Período de Cobertura:** 2024-01-01 a 2026-12-31  

---

## 1. Métricas Financieras y Fórmulas de Negocio

En la capa analítica del Data Warehouse (`dw_demo1.FactSales`), las métricas clave del negocio se modelan para garantizar consistencia entre reportes de Power BI, consultas de Business Intelligence y análisis de ingeniería de datos.

### 1.1 Fórmulas Base

* **Gross Revenue (Monto Bruto Total):**  
  $$\text{Gross Revenue} = \text{Quantity} \times \text{UnitPrice}$$
  *Representa la venta teórica antes de aplicar cualquier tipo de descuento.*

* **Discount Amount (Monto de Descuento):**  
  $$\text{Discount Amount} \ge 0.00$$
  *Monto monetario absoluto descontado sobre el valor total de la línea de la orden.*

* **Revenue / Net Sales (Venta Neta):**  
  $$\text{Revenue} = (\text{Quantity} \times \text{UnitPrice}) - \text{DiscountAmount}$$
  *Métrica primaria de facturación real del negocio.*

* **Total Cost (Costo Total de Ventas):**  
  $$\text{Total Cost} = \text{Quantity} \times \text{UnitCost}$$
  *Costo de los bienes vendidos (COGS) valorizado al costo unitario al momento del registro de la transacción.*

* **Gross Profit (Utilidad Bruta / Margen Bruto):**  
  $$\text{Gross Profit} = \text{Revenue} - \text{TotalCost} = \big((\text{Quantity} \times \text{UnitPrice}) - \text{DiscountAmount}\big) - (\text{Quantity} \times \text{UnitCost})$$
  *Contribución marginal antes de gastos operacionales, de distribución y marketing.*

### 1.2 Implementación Técnica en SQL Server / Azure SQL
Las métricas `Revenue`, `TotalCost` y `GrossProfit` están definidas como **Columnas Calculadas Persistidas** (*Persisted Computed Columns*) directamente en la tabla de hechos `dw_demo1.FactSales`, garantizando cero discrepancias por redondeo o fórmulas inconsistentes entre herramientas cliente.

---

## 2. Reglas de Invariante y Calidad de Datos

Para asegurar un dataset realista y consistente, se aplican las siguientes reglas de validación en la generación de datos en Python y en la carga de ETL.

### 2.1 Precios, Costos y Descuentos

1. **Garantía de Costo Positivo:**  
   `unit_cost > 0.00`  
   Aplica de forma estricta tanto para el maestro de productos (`stg_demo1.products`) como para el histórico transaccional (`stg_demo1.sales_order_lines`).

2. **Garantía de Precio de Lista Base:**  
   `list_price >= unit_cost`  
   En el catálogo de productos, el precio de lista nunca se define por debajo del costo unitario base.

3. **No Negatividad de Precios Transaccionales:**  
   `unit_price >= 0.00`  
   Permite transacciones a precio $0.00 (ej. muestras o bonificaciones autorizadas), pero no montos negativos.

4. **Límite Operacional de Descuentos:**  
   `0.00 <= discount_amount <= (quantity * unit_price)`  
   El descuento acumulado por línea no puede superar la venta bruta de dicha línea (no se admiten ventas netas negativas por descuentos excesivos).

---

## 3. Reglas Operacionales y Flujos de Trabajo

### 3.1 Entrega Solicitada (`requested_delivery_date`)
La fecha solicitada de entrega se calcula siempre con respecto a la fecha de emisión de la orden (`order_date`), añadiendo una distribución de días hábiles posterior:

* **70% de las órdenes:** `order_date` + (1 a 3 días hábiles)
* **25% de las órdenes:** `order_date` + (4 a 7 días hábiles)
* **5% de las órdenes:** `order_date` + (8 a 15 días hábiles)

`requested_delivery_date >= order_date`

### 3.2 Estados de las Órdenes (`status`)
Las órdenes se clasifican bajo tres estados operacionales:

1. **`Completed` (~92% - 94%):** Órdenes despachadas y facturadas satisfactoriamente.
2. **`Cancelled` (~5% - 6%):** Órdenes canceladas o devueltas. Distribuidas a lo largo de los 3 años de histórico para reflejar transacciones anuladas en staging.
3. **`Pending` (~2% general):** Órdenes en proceso. **Regla de Exclusividad Temporal:** Solo se presentan en órdenes cuya `order_date` corresponda al último mes del histórico (diciembre de 2026). No existen órdenes pendientes en períodos pasados.

### 3.3 Carga de FactSales

Solo las órdenes con status = 'Completed' son elegibles para ingresar a
dw_demo1.FactSales.

Las órdenes con status = 'Cancelled' o 'Pending' permanecen disponibles
en la capa de staging para controles de calidad y análisis operacional,
pero no generan registros en FactSales.

Por lo tanto:

- stg_demo1.sales_orders: contiene Completed, Cancelled y Pending.
- stg_demo1.sales_order_lines: puede contener líneas asociadas a los tres estados.
- dw_demo1.FactSales: contiene únicamente líneas pertenecientes a órdenes Completed.


### 3.4 Asignación Territorial y Consistencia Comercial
* La atribuibilidad comercial de una venta se define mediante la estructura organizativa de ventas.
* La Región Comercial (`dw_demo1.FactSales.RegionKey`) en el Star Schema se deriva de la región asignada al **Vendedor** (`salesperson_id`), independientemente de la ubicación física del almacén de despacho o del cliente.
* Esto garantiza una atribución limpia para el cálculo de comisiones, evaluación de fuerza de ventas y presupuestos regionales.

---

## 4. Patrones de Negocio Incorporados (Business Insights)

El dataset sintético incluye anomalías y patrones reales intencionados para ser descubiertos durante la exploración de datos en SQL y la construcción del dashboard en Power BI:

1. **Asimetría Regional de Margen:**
   * **Región Norte:** Muestra un alto volumen de ventas (*Revenue*) impulsado por la categoría *Steel & Rebar*, pero obtiene un porcentaje de Margen Bruto (*Gross Profit %*) más bajo debido a negociaciones corporativas con altos descuentos a *Construction Companies*.
   * **Región Sur:** Genera un menor volumen total, pero mantiene un *Gross Margin %* elevado impulsado por ventas recurrentes de *Tools & Equipment* y *Paints & Finishes* a segmentos *Contractor*.

2. **Pic de Inflación de Proveedores (Q3 2025):**
   * Entre agosto de 2025 y octubre de 2025, el `unit_cost` de la categoría *Steel & Rebar* sufre un incremento del 14% en la capa transaccional.
   * El `unit_price` cobrado al cliente se ajusta con un desfase (lag) de 30 días, provocando una contracción temporal en la utilidad bruta durante dicho trimestre.

3. **Estacionalidad de la Industria de Construcción:**
   * El período de junio a octubre concentrará aproximadamente el **45% del volumen anual de órdenes**, reflejando la temporada alta de ejecución de obras.