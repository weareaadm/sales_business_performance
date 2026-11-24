# Análisis de Ventas y Rendimiento Comercial (Sales & Business Performance)
## Solución Analytics End-to-End para Empresa B2B de Materiales de Construcción (Lima, Perú)

**Python · SQL Server · Data Warehouse · Star Schema · PyTest · DAX · Power BI**

---

Este proyecto forma parte de un portafolio público de *Data Analytics / Business Intelligence* y modela un flujo *End-to-End* sobre datos sintéticos reproducibles (`SEED = 42`) para una distribuidora B2B de materiales de construcción que opera en 8 zonas de Lima, Perú, durante el período **2024-01-01 a 2026-12-31**.

```text
Requerimientos y Reglas de Negocio
  ↓
Generación Sintética Determinista en Python (SEED = 42 -> data/generated/*.csv)
  ↓
Capa Staging en SQL Server (stg_demo1) + Pruebas PyTest
  ↓
Data Warehouse Dimensional en SQL Server (dw_demo1: Dim* y FactSales) + Pruebas PyTest
  ↓
Validación y Conciliación SQL (04_analysis.sql + tests/phase4_validation)
  ↓
Modelo Semántico y Medidas DAX en Power BI (dax/measures.md)
  ↓
Dashboard Ejecutivo y Documentación Final
```

---

## 1. Alcance y Reglas de Negocio

* **Período transaccional:** `2024-01-01` a `2026-12-31` (`150,000` órdenes en `sales_orders.csv` con `40,000` en 2024, `48,000` en 2025 y `62,000` en 2026).
* **Líneas por orden:** Distribución de Poisson ($\lambda = 3.3$) acotada entre `1` y `10` líneas por orden; cantidad por línea entre `1` y `20` unidades.
* **Estados de orden:** `Completed`, `Cancelled` y `Pending` (`Pending` restringido a diciembre de 2026).
* **Regla de `FactSales`:** Solo se cargan líneas de órdenes con `status = 'Completed'`. Las órdenes `Cancelled` y `Pending` permanecen en `stg_demo1` para auditoría y control operativo.
* **Atribución comercial:** `FactSales.RegionKey` se deriva de la región asignada al vendedor (`salespeople.region_id` $\rightarrow$ `DimRegion.RegionID`).
* **Métricas financieras (`dw_demo1.FactSales`):**
  * $\text{Revenue} = (\text{Quantity} \times \text{UnitPrice}) - \text{DiscountAmount}$
  * $\text{TotalCost} = \text{Quantity} \times \text{UnitCost}$
  * $\text{GrossProfit} = \text{Revenue} - \text{TotalCost}$
  * $\text{Gross Margin \%} = \frac{\text{GrossProfit}}{\text{Revenue}}$
* **Patrones incorporados en el generador:**
  * **Estacionalidad:** Mayor peso mensual entre junio y octubre (`9.0%` mensual) frente al resto del año.
  * **Inflación *Steel & Rebar* (2025):** Multiplicador de costo `1.14x` en agosto, septiembre y octubre de 2025, con traslado al precio (`1.14x`) a partir de septiembre de 2025.

---

## 2. Catálogos Configurados (`python/config.py`)

### 2.1 Regiones, Almacenes y Fuerza de Ventas (50 vendedores)

| Region ID | Región | Almacén | Vendedores |
| :---: | :--- | :--- | :---: |
| `1` | Lima Norte | `WH-LimaNorte-01` | 12 |
| `2` | Lima Sur | `WH-LimaSur-01` | 10 |
| `3` | Lima Este | `WH-LimaEste-01` | 9 |
| `4` | Lima Centro | `WH-LimaCentro-01` | 8 |
| `5` | Lima Moderna | `WH-LimaModerna-01` | 5 |
| `6` | Callao | `WH-Callao-01` | 3 |
| `7` | Lima Balnearios | `WH-Balnearios-01` | 2 |
| `8` | Lima Periurbana | `WH-Periurbana-01` | 1 |

### 2.2 Productos (500) y Proveedores (50)

| Categoría | Productos | Rango Costo Base (USD) | Margen Objetivo | Proveedores |
| :--- | :---: | :---: | :---: | :---: |
| `Steel & Rebar` | 120 | `$150.0` – `$1,200.0` | 22% | 12 |
| `Structural & Piping` | 100 | `$80.0` – `$850.0` | 25% | 10 |
| `Electrical & Industrial` | 110 | `$25.0` – `$450.0` | 30% | 11 |
| `Heavy Equipment & Tools` | 90 | `$200.0` – `$3,500.0` | 28% | 9 |
| `Safety & Maintenance` | 80 | `$10.0` – `$180.0` | 35% | 8 |

### 2.3 Segmentos de Clientes (2,000 clientes)

| Segmento | Peso | Prob. Máx. Descuento | Tasa Máx. Descuento |
| :--- | :---: | :---: | :---: |
| `Enterprise` | 15% | 60% | 15% |
| `Mid-Market` | 35% | 40% | 10% |
| `SMB` | 50% | 20% | 5% |

---

## 3. Configuración del Entorno (`.env`) y Requisitos

Crea un archivo `.env` en la raíz del repositorio (sin subir credenciales reales a Git) con la configuración de conexión:

```env
# SQL Server
MSSQL_SERVER=localhost
MSSQL_PORT=1433
MSSQL_DATABASE=SAbupe
MSSQL_USER=sa
MSSQL_SA_PASSWORD=TU_CONTRASEÑA_AQUI

# PostgreSQL (si aplica a otros módulos del repositorio)
POSTGRES_USER=TU_USUARIO_POSTGRES
POSTGRES_PASSWORD=TU_CONTRASEÑA_POSTGRES
POSTGRES_DB=postgres
POSTGRES_PORT=5432
```

* **Dependencias Python:** Instala los paquetes de `requirements.txt` (incluyendo `pyodbc`, `pandas`, `numpy`, `faker`, `python-dotenv`, `pytest`) y asegúrate de tener instalado **ODBC Driver 18 for SQL Server** en el sistema.
* Si la base de datos configurada en `MSSQL_DATABASE` (por defecto `SAbupe`) no existe aún, `python/drivers/sqlserver.py` la crea automáticamente antes de conectar.

---

## 4. Estructura del Proyecto

```text
02_sales_business_performance/
├── main.py                         # Orquestador CLI (--phase 1..4 o --all)
├── README.md
├── case_study/
│   └── business_case.md
├── dashboard/
│   ├── dashboard_link.md
│   ├── demo sales.jpeg
│   └── screenshots/
├── data/
│   └── generated/                  # CSVs generados (customers, suppliers, products, salespeople, sales_orders, order_lines)
├── data_model/
│   └── star_schema.png
├── data_specification/
│   ├── business_rules.md
│   ├── data_dictionary.md
│   ├── data_generation_spec.md
│   └── source_to_target_mapping.md
├── dax/
│   └── measures.md
├── images/
│   └── demo_dashboard.jpeg
├── python/
│   ├── config.py
│   ├── drivers/sqlserver.py
│   ├── generate/
│   │   ├── generate_customers.py
│   │   ├── generate_products.py
│   │   ├── generate_salespeople.py
│   │   └── generate_sales.py
│   ├── phase1_generate.py
│   ├── phase2_staging.py
│   ├── phase3_dw.py
│   ├── phase4_validate.py
│   ├── run_staging.py
│   └── test_runner.py
├── sql/
│   ├── 01_create_schema_and_tables.sql
│   ├── 01_staging.sql
│   ├── 02_dimensions.sql
│   ├── 03_facts.sql
│   └── 04_analysis.sql
└── tests/
    ├── phase1_generate/
    ├── phase2_staging/
    ├── phase3_dw/
    └── phase4_validation/
```

---

## 5. Ejecución por Fases y Estado

Puedes ejecutar cada fase de forma independiente o correr las fases 1 a 4 en secuencia desde la raíz del repositorio:

```bash
# Fase 1: Generación de CSVs en data/generated/ + tests/phase1_generate
python3 02_sales_business_performance/main.py --phase 1

# Fase 2: DDL y carga a stg_demo1 + tests/phase2_staging
python3 02_sales_business_performance/main.py --phase 2

# Fase 3: Poblado de dimensiones y FactSales en dw_demo1 + tests/phase3_dw
python3 02_sales_business_performance/main.py --phase 3

# Fase 4: Validación y conciliación SQL + tests/phase4_validation
python3 02_sales_business_performance/main.py --phase 4

# Ejecución secuencial de Fases 1 -> 2 -> 3 -> 4
python3 02_sales_business_performance/main.py --all
```

### Estado de validación del proyecto

| Fase | Descripción | Estado | Notas |
| :---: | :--- | :---: | :--- |
| **Fase 1** | Generación determinista (`SEED=42`) y pruebas unitarias | Validado en entorno del autor | 6 CSVs y suites en `tests/phase1_generate` |
| **Fase 2** | Esquemas/tablas e ingesta en `stg_demo1` | Validado en entorno del autor | 8 tablas en `stg_demo1` y `tests/phase2_staging` |
| **Fase 3** | Modelo dimensional (`Dim*` y `FactSales`) en `dw_demo1` | Validado en entorno del autor | `02_dimensions.sql`, `03_facts.sql` y `tests/phase3_dw` |
| **Fase 4** | Conciliación Staging $\leftrightarrow$ DW y controles de calidad | Validado en entorno del autor | `04_analysis.sql` y `tests/phase4_validation` |


