# ESPECIFICACIÓN DE GENERACIÓN DE DATOS

**Proyecto:** B2B Construction Materials Enterprise Analytics  
**Versión:** 2.1  
**Semilla Aleatoria (Seed):** `42`  
**Entorno Destino:** Python (`Faker`, `NumPy`, `Pandas`)  
**Período de Generación:** `2024-01-01` a `2026-12-31` (3 años completos)  

---

## 1. Target Volume Summary & Scope Clarification.

| Entidad / Tabla | Esquema Staging | Volumen Objetivo | Rango de IDs | Notas de Dominio |
| :--- | :--- | :--- | :--- | :--- |
| **Regions** | `stg_demo1.regions` | 8 regiones | `1` a `8` | Regiones comerciales operativas. |
| **Warehouses** | `stg_demo1.warehouses` | 8 almacenes | `1` a `8` | Relación 1:1 inicial con regiones. |
| **Salespeople** | `stg_demo1.salespeople` | 50 vendedores | `1` a `50` | Asignación fija por región. |
| **Suppliers** | `stg_demo1.suppliers` | 50 proveedores | `1` a `50` | Proveedores de materiales por categoría. |
| **Products** | `stg_demo1.products` | 500 productos | `1` a `500` | Distribuidos en 6 categorías industriales. |
| **Customers** | `stg_demo1.customers` | 2,000 clientes | `1` a `2000` | Distribuidos en 4 segmentos de negocio. |
| **Sales Orders** | `stg_demo1.sales_orders` | 150,000 órdenes (exactas) | `1` a `150000` | Encabezados transaccionales en staging. |
| **Sales Order Lines** | `stg_demo1.sales_order_lines` | ~500,000 líneas (estimado) | `1` a `~500000` | Resultado stocástico de la distribución en staging. |

> **Aclaración de Alcance Staging vs. DW & Volumen Objetivo:**  
> * **Volumen de Líneas Staging:** El objetivo de ~500,000 líneas es una estimación basada en la distribución de Poisson ($\lambda = 3.3$, acotada en `[1, 10]`). El volumen exacto de líneas producidas será el resultado determinista de la ejecución con `SEED = 42`.
> * **Filtrado FactSales:** En el Modelo Dimensional, `FactSales` incluirá exclusivamente las órdenes con `status = 'Completed'`. Las órdenes `Cancelled` y `Pending` permanecerán en staging y no contribuirán al Revenue de ventas cerradas. La cantidad exacta final de líneas en `FactSales` se determinará tras ejecutar la generación con `SEED = 42`.

---

## 2. Catalog & Entity Parameters

### 2.1 Regiones y Fuerza de Ventas
Distribuido de forma fija a través de las 8 regiones comerciales:

| Region_ID | Nombre Región | Almacén Asignado | Cantidad de Vendedores | IDs de Vendedores |
| :---: | :--- | :--- | :---: | :---: |
| `1` | Norte | Warehouse Norte | 8 | `1` – `8` |
| `2` | Sur | Warehouse Sur | 7 | `9` – `15` |
| `3` | Centro | Warehouse Centro | 9 | `16` – `24` |
| `4` | Este | Warehouse Este | 6 | `25` – `30` |
| `5` | Oeste | Warehouse Oeste | 5 | `31` – `35` |
| `6` | Metropolitano | Warehouse Metro | 8 | `36` – `43` |
| `7` | Costa | Warehouse Costa | 4 | `44` – `47` |
| `8` | Sierra | Warehouse Sierra | 3 | `48` – `50` |

### 2.1.1 Proveedores y Asignación por Categoría

Se generan exactamente 50 proveedores, con una categoría principal asignada de forma determinística. Cada proveedor pertenece a una única categoría principal.

| Rango Supplier_ID | Categoría Principal | N° Proveedores |
| :--- | :--- | :---: |
| `1` – `8` | Cement & Concrete | 8 |
| `9` – `16` | Steel & Rebar | 8 |
| `17` – `26` | Plumbing & Pipes | 10 |
| `27` – `36` | Tools & Equipment | 10 |
| `37` – `43` | Electrical & Lighting | 7 |
| `44` – `50` | Paints & Finishes | 7 |
| **Total** | | **50** |

**Reglas de asignación:**

* Cada proveedor tiene exactamente una categoría principal.
* Cada producto se asigna a un proveedor cuya categoría principal coincide con la categoría del producto.
* La asignación de productos a proveedores es determinística bajo `SEED = 42`.
* Cada proveedor debe tener al menos un producto asignado.
* La relación `product.supplier_id → suppliers.supplier_id` debe ser válida para el 100% del catálogo.

### 2.2 Segmentos de Clientes (`stg_demo1.customers`)
Un total de 2,000 clientes con asignación fija de segmento y distribución de fechas de registro progresivas entre `2023-06-01` y `2026-11-30`.

| Segmento | % Total | N° Clientes | Frecuencia | Cantidad / Línea (U) | Sensibilidad / Tipo Descuento |
| :--- | :---: | :---: | :--- | :--- | :--- |
| **Contractor** | 40% | 800 | Alta | Uniforme(5, 50) | Estándar (5% - 12%) |
| **Construction Company** | 25% | 500 | Media-Baja | Uniforme(10, 200) | Corporativo / Volumen (15% - 25%) |
| **Retailer** | 20% | 400 | Recurrente | Uniforme(5, 50) | Estándar (5% - 12%) |
| **Individual** | 15% | 300 | Ocasional | Uniforme(1, 10) | Nula (0% Descuento) |

### 2.2.1 Distribución Regional de Clientes

Los 2,000 clientes se distribuyen entre las 8 regiones mediante cuotas regionales exactas.

| Region_ID | Región | % Clientes | N° Clientes |
| :---: | :--- | :---: | :---: |
| `1` | Norte | 16% | 320 |
| `2` | Sur | 14% | 280 |
| `3` | Centro | 18% | 360 |
| `4` | Este | 12% | 240 |
| `5` | Oeste | 10% | 200 |
| `6` | Metropolitano | 16% | 320 |
| `7` | Costa | 8% | 160 |
| `8` | Sierra | 6% | 120 |
| **Total** | | **100%** | **2,000** |

**Reglas de asignación:**

* Las cuotas regionales son exactas y deben sumar 2,000 clientes.
* La asignación individual de clientes a regiones debe ser determinística bajo `SEED = 42`.
* `customers.region_id` representa la región base/comercial del cliente.
* La región del cliente **no determina** la región del vendedor asignado a una orden.
* La región del cliente y la región comercial de la venta constituyen perspectivas geográficas independientes.

**Relación conceptual:**

Customer Region → análisis geográfico del cliente.

Salesperson Region → región comercial de la venta → `FactSales.RegionKey`.

### 2.3 Categorías del Catálogo de Productos (`stg_demo1.products`)
Catálogo de 500 productos con margen de lista sobre costo calculado con la fórmula de margen sobre venta:

`list_price = round(unit_cost / (1 - target_margin), 2)`

| Categoría | % Catálogo | N° Items | Rango `unit_cost` ($) | Target Gross Margin (%) |
| :--- | :---: | :---: | :---: | :---: |
| **Cement & Concrete** | 15% | 75 | $10.00 – $45.00 | 15% – 22% |
| **Steel & Rebar** | 15% | 75 | $120.00 – $1,100.00 | 12% – 18% |
| **Plumbing & Pipes** | 20% | 100 | $4.00 – $180.00 | 25% – 35% |
| **Tools & Equipment** | 20% | 100 | $40.00 – $1,200.00 | 35% – 50% |
| **Electrical & Lighting** | 15% | 75 | $8.00 – $280.00 | 30% – 40% |
| **Paints & Finishes** | 15% | 75 | $15.00 – $350.00 | 28% – 38% |

---

## 3. Order Generation Parameters

### 3.1 Crecimiento Anual, Estacionalidad y Asignación de Residuos
El volumen se fija en **150,000 órdenes exactas** distribuidas en 3 años con crecimiento interanual y estacionalidad del sector construcción:

#### Distribución Determinista por Año:
* **2024:** 40,000 órdenes (26.67%)
* **2025:** 48,000 órdenes (32.00%)
* **2026:** 62,000 órdenes (41.33%)

#### Ponderación Mensual Teórica (Estacionalidad):
* **Temporada Alta (Junio a Octubre - 5 meses):** Concentra el **45%** del volumen anual (`9.00% por mes`).
* **Temporada Regular (Enero a Mayo, Noviembre, Diciembre - 7 meses):** Concentra el **55%** del volumen anual (`55% / 7 ≈ 7.857142857% por mes`).

#### Método de Cuota Entera (Largest Remainder Method):
Para garantizar que la suma de órdenes mensuales coincida exactamente con la cuota fija anual (40k, 48k y 62k):
1. Calcular la cuota flotante ideal por mes multiplicando el total anual por el porcentaje del mes.
2. Tomar la parte entera de cada cuota como el número base de órdenes para el mes.
3. Asignar las órdenes sobrantes de 1 en 1 entre los meses ordenados de mayor a menor según su parte decimal (residuo). En caso de empate en la parte decimal, resolver la prioridad por orden cronológico del mes.

### 3.2 Estructura de Encabezados, Líneas y Jerarquía de Estados (`status`)
* **Líneas por Orden:** Distribución de Poisson con $\lambda = 3.3$, acotada (*clamped*) en el rango `[1, 10]`. El promedio realizado resultará de aplicar el acotamiento y el `SEED = 42`.
* **Regla Jerárquica de Asignación de Estado (`status`):**  
  Para evitar incompatibilidades o sumas inconsistentes de distribución:
  1. **Evaluación de 'Pending' (Override Exclusivo Diciembre 2026):** Si la orden pertenece a Diciembre de 2026, tiene una probabilidad independiente del **2%** de asignarse como `Pending`.
  2. **Distribución Principal (Órdenes Restantes):** Todas las órdenes que no hayan sido marcadas como `Pending` (incluyendo el 98% restante de Diciembre 2026 y el 100% de los meses anteriores) se distribuyen bajo el esquema:
     * `Completed`: ~95%
     * `Cancelled`: ~5%
  3. **Documentación Post-Ejecución:** La proporción observada final de estados será registrada en la documentación técnica una vez fijada con `SEED = 42`.

### 3.3 Matriz Condicional de Descuentos (`discount_amount`)
La probabilidad de aplicación de descuento se evalúa a nivel de línea en función del segmento del cliente:

| Segmento Cliente | Probabilidad 0% Desc. | Probabilidad Desc. Estándar (5% - 12%) | Probabilidad Desc. Corporativo (15% - 25%) |
| :--- | :---: | :---: | :---: |
| **Contractor** | 65% | 35% | 0% |
| **Retailer** | 65% | 35% | 0% |
| **Construction Company** | 50% | 0% | 50% |
| **Individual** | 100% | 0% | 0% |

`discount_amount = round(quantity * unit_price * rate, 2)`

> **Nota sobre el Revenue Neto:** `unit_price` es el precio de venta bruto unitario antes de aplicar el descuento. El descuento se almacena en `discount_amount` y se deduce para obtener la venta neta (`net_revenue = (quantity * unit_price) - discount_amount`). Por ende, el otorgamiento de un descuento elevado puede reducir la venta neta por debajo del costo transaccional en líneas específicas sin invalidar la regla `unit_price >= unit_cost`.

---

## 4. Built-in Business Patterns (Patrones BI para Descubrimiento)

### 4.1 Asimetría Regional de Margen

Los patrones regionales se aplican sobre la región comercial de la venta, determinada por el `region_id` del vendedor asignado a la orden. Esta dimensión se materializa en `FactSales.RegionKey`.

* **Región Norte (`region_id = 1`):**  
  Ponderación aumentada (3.5x) para la combinación de categoría *Steel & Rebar* y segmento de cliente *Construction Company*.  
  **Efecto BI esperado:** Alto *Revenue* bruto y una presión significativa sobre *Gross Margin %* debido a la combinación de márgenes base relativamente bajos en *Steel & Rebar* y descuentos corporativos elevados (15%–25%) aplicados a *Construction Company*.

* **Región Sur (`region_id = 2`):**  
  Ponderación aumentada (3.0x) para las categorías *Tools & Equipment* y *Paints & Finishes* cuando son vendidas a clientes del segmento *Contractor*.  
  **Efecto BI esperado:** Volumen de ventas relativamente menor, acompañado de un *Gross Margin %* superior debido al mayor margen base de estas categorías y a la menor intensidad de descuentos corporativos.

> **Nota:** `customers.region_id` representa la región geográfica/base del cliente y no determina la región comercial de la venta. La región comercial utilizada para este patrón se deriva exclusivamente de `salespeople.region_id`.

### 4.2 Impacto Inflacionario de Proveedores con Desfase (Ago-Oct 2025)
Aplica exclusivamente a la categoría **Steel & Rebar**:
1. **Período de Increm. de Costo (`2025-08-01` a `2025-10-31`):**  
   `unit_cost_transaccional = base_unit_cost * 1.14`
2. **Desfase de Ajuste de Precio al Cliente (Lag de 30 días):**  
   * **`2025-08-01` a `2025-08-31`:** `unit_price` se mantiene en el precio normal de lista (`base_list_price`).  
   * **`2025-09-01` a `2025-10-31`:** `unit_price` se incrementa reflejando el traspaso al cliente:  
     `unit_price_ajustado = base_list_price * 1.14`  
   * **A partir de `2025-11-01`:** Tanto `unit_cost` como `unit_price` retornan a sus niveles base prepico.  
3. **Efecto BI:** Contracción severa del *Gross Margin %* durante agosto de 2025, seguida de una recuperación hacia niveles cercanos al margen base a partir de septiembre, una vez trasladado el incremento de costos al precio de venta.

---

## 5. Reglas de Validación Post-generación (`validate_generated_data.py`)

Cualquier conjunto de archivos generado debe superar el 100% de estas pruebas automatizadas:

1. **Volumen Determinista de Encabezados:**  
   `len(sales_orders) = 150000`
2. **Integridad Referencial Estricta e Invariantes por Orden:**  
   * Zero huérfanos en `sales_order_lines.order_id` -> `sales_orders.order_id`.
   * Unicidad estricta de `order_line_id` como clave primaria en la tabla de detalles.
   * `product_id` en cada línea debe mapear a una clave válida en `stg_demo1.products`.
   * **Límites por Orden:** Todo `order_id` en `sales_orders` debe poseer entre 1 y 10 líneas asociadas en `sales_order_lines`.
   * Claves de referencia válidas para clientes, vendedores y almacenes; la región comercial de cada orden debe derivarse consistentemente del vendedor asignado mediante salespeople.region_id.
3. **Invariante Temporal del Cliente:**  
   `sales_orders.order_date >= customers.registration_date`
4. **Consistencia Regional del Vendedor:**  
   `salespeople.region_id = sales_orders -> salesperson_id -> region_id`
5. **Invariantes Financieros y de Precios:**  
   * **Catálogo (`stg_demo1.products`):**  
     `unit_cost > 0 y list_price >= unit_cost`
   * **Transacciones (`stg_demo1.sales_order_lines`):**  
     `unit_cost > 0 y unit_price >= unit_cost`  
   * **Excepción Controlada de Precio Bruto:** Para *Steel & Rebar* entre `2025-08-01` y `2025-08-31`, `unit_price` puede ser inferior a `unit_cost` debido al *lag* de 30 días de traslado del incremento de costo.
6. **Invariante de Descuentos y Venta Bruta:**  
   `0 <= discount_amount <= (quantity * unit_price)`
7. **Desglose Fechas de Entrega:**  
   `requested_delivery_date >= order_date`
8. **Restricción de Estado 'Pending':**  
   `IF status = 'Pending' THEN order_date >= '2026-12-01'`
9. **Regla de Redondeo Financiero:** Todos los montos monetarios (`unit_cost`, `unit_price`, `discount_amount`) deben estar redondeados estrictamente a 2 decimales.
10. **Criterio de Reproducibilidad:** La ejecución del script con `SEED = 42` debe producir exactamente los mismos valores, filas y orden de filas. El hash se calculará sobre una serialización determinista de cada archivo generado, manteniendo columnas, tipos/formato, orden de filas y codificación constantes.
11. Dominio de Estado:
   `status` debe pertenecer exclusivamente al conjunto:
   {'Completed', 'Cancelled', 'Pending'}.
12. **Integridad de Proveedores y Categorías:**  
    * Todos los `products.supplier_id` deben corresponder a un `supplier_id` válido en `stg_demo1.suppliers`.
    * Cada proveedor debe tener al menos un producto asignado.
    * Cada producto debe estar asignado a un proveedor cuya categoría principal coincida con la categoría del producto:  
      `products.category = supplier.primary_category`
    * La asignación proveedor -> categoría debe ser determinística bajo `SEED = 42`.
    * El catálogo debe contener exactamente 500 productos y los 50 proveedores deben estar representados al menos una vez.