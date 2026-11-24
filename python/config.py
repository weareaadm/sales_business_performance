"""
config.py
---------
Configuración centralizada y única fuente de verdad técnica para la generación
del dataset comercial (2024-2026) enfocado en Lima, Perú.
"""

from pathlib import Path

# ==========================================
# 1. Semilla Central y Rutas
# ==========================================
SEED = 42
BASE_DIR = Path(__file__).resolve().parent.parent

OUTPUT_DIR = BASE_DIR / "data" / "generated"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ==========================================
# 2. Rangos de Fechas y Cuotas de Órdenes
# ==========================================
START_YEAR = 2024
END_YEAR = 2026

ANNUAL_ORDER_TARGETS = {
    2024: 40_000,
    2025: 48_000,
    2026: 62_000
}

TOTAL_ORDERS = sum(ANNUAL_ORDER_TARGETS.values())  # 150,000

# Ponderación mensual (Temporada alta Jun-Oct: 9.0% c/u; Temporada regular: ~7.857% c/u)
MONTHLY_WEIGHTS = {
    1: 0.078571, 2: 0.078571, 3: 0.078571, 4: 0.078571, 5: 0.078571,
    6: 0.090000, 7: 0.090000, 8: 0.090000, 9: 0.090000, 10: 0.090000,
    11: 0.078571, 12: 0.078575  # Ajuste decimal para sumar exactamente 1.0
}

# ==========================================
# 3. Distribución de Líneas por Orden
# ==========================================
POISSON_LAMBDA = 3.3
MIN_LINES_PER_ORDER = 1
MAX_LINES_PER_ORDER = 10

# ==========================================
# 4. Dimensiones y Catálogos Fijos (Lima, Perú)
# ==========================================
REGIONS = [
    {"region_id": 1, "region_name": "Lima Norte", "country": "Peru", "market_weight": 0.25},
    {"region_id": 2, "region_name": "Lima Sur", "country": "Peru", "market_weight": 0.20},
    {"region_id": 3, "region_name": "Lima Este", "country": "Peru", "market_weight": 0.18},
    {"region_id": 4, "region_name": "Lima Centro", "country": "Peru", "market_weight": 0.15},
    {"region_id": 5, "region_name": "Lima Moderna", "country": "Peru", "market_weight": 0.10},
    {"region_id": 6, "region_name": "Callao", "country": "Peru", "market_weight": 0.05},
    {"region_id": 7, "region_name": "Lima Balnearios", "country": "Peru", "market_weight": 0.04},
    {"region_id": 8, "region_name": "Lima Periurbana", "country": "Peru", "market_weight": 0.03}
]

WAREHOUSES = [
    {"warehouse_id": 1, "warehouse_name": "WH-LimaNorte-01", "region_id": 1, "city": "Los Olivos"},
    {"warehouse_id": 2, "warehouse_name": "WH-LimaSur-01", "region_id": 2, "city": "Villa El Salvador"},
    {"warehouse_id": 3, "warehouse_name": "WH-LimaEste-01", "region_id": 3, "city": "Ate"},
    {"warehouse_id": 4, "warehouse_name": "WH-LimaCentro-01", "region_id": 4, "city": "Cercado de Lima"},
    {"warehouse_id": 5, "warehouse_name": "WH-LimaModerna-01", "region_id": 5, "city": "Surquillo"},
    {"warehouse_id": 6, "warehouse_name": "WH-Callao-01", "region_id": 6, "city": "Callao"},
    {"warehouse_id": 7, "warehouse_name": "WH-Balnearios-01", "region_id": 7, "city": "Lurín"},
    {"warehouse_id": 8, "warehouse_name": "WH-Periurbana-01", "region_id": 8, "city": "Chosica"}
]

TOTAL_CUSTOMERS = 2000
TOTAL_SUPPLIERS = 50
TOTAL_PRODUCTS = 500
TOTAL_SALESPEOPLE = 50

# Asignación exacta de cuotas de vendedores por región en Lima (Suma 50)
REGION_SALESPERSON_COUNTS = {
    1: 12, # Lima Norte
    2: 10, # Lima Sur
    3: 9,  # Lima Este
    4: 8,  # Lima Centro
    5: 5,  # Lima Moderna
    6: 3,  # Callao
    7: 2,  # Lima Balnearios
    8: 1   # Lima Periurbana
}

# ==========================================
# 5. Definición de Categorías de Producto
# ==========================================
PRODUCT_CATEGORIES = {
    "Steel & Rebar": {
        "product_count": 120,
        "base_cost_range": (150.0, 1200.0),
        "target_margin": 0.22,
        "primary_supplier_count": 12
    },
    "Structural & Piping": {
        "product_count": 100,
        "base_cost_range": (80.0, 850.0),
        "target_margin": 0.25,
        "primary_supplier_count": 10
    },
    "Electrical & Industrial": {
        "product_count": 110,
        "base_cost_range": (25.0, 450.0),
        "target_margin": 0.30,
        "primary_supplier_count": 11
    },
    "Heavy Equipment & Tools": {
        "product_count": 90,
        "base_cost_range": (200.0, 3500.0),
        "target_margin": 0.28,
        "primary_supplier_count": 9
    },
    "Safety & Maintenance": {
        "product_count": 80,
        "base_cost_range": (10.0, 180.0),
        "target_margin": 0.35,
        "primary_supplier_count": 8
    }
}

# Segmentos de Cliente y Distribución de Descuentos
CUSTOMER_SEGMENTS = {
    "Enterprise": {"weight": 0.15, "max_discount_prob": 0.60, "max_discount_rate": 0.15},
    "Mid-Market": {"weight": 0.35, "max_discount_prob": 0.40, "max_discount_rate": 0.10},
    "SMB":        {"weight": 0.50, "max_discount_prob": 0.20, "max_discount_rate": 0.05}
}

# Probabilidades de tiempo de entrega (días hábiles)
DELIVERY_DAYS_PROBABILITIES = {
    (1, 3): 0.70,
    (4, 7): 0.25,
    (8, 15): 0.05
}

# Evento Especial: Inflación de Steel & Rebar en 2025
STEEL_INFLATION_EVENT = {
    "category": "Steel & Rebar",
    "cost_multiplier": 1.14,
    "price_multiplier": 1.14,
    "cost_affected_months": [(2025, 8), (2025, 9), (2025, 10)],
    "price_affected_months": [(2025, 9), (2025, 10)]
}