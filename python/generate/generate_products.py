"""
generate_products.py
--------------------
Genera el catálogo de 50 proveedores y 500 productos agrupados por las
5 categorías comerciales definidas en config.py.
"""

import sys
from pathlib import Path
from faker import Faker
import pandas as pd
import numpy as np

# Garantizar importación de config desde la misma carpeta python/
PYTHON_DIR = Path(__file__).resolve().parent
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

import config

def generate_suppliers_and_products():
    fake = Faker('es_ES')
    Faker.seed(config.SEED)
    rng = np.random.default_rng(config.SEED)
    
    suppliers = []
    products = []
    
    supplier_id_counter = 1
    product_id_counter = 1
    
    # 1. Generar 50 Proveedores asignados a categorías
    for cat_name, cat_info in config.PRODUCT_CATEGORIES.items():
        sup_count = cat_info["primary_supplier_count"]
        
        for _ in range(sup_count):
            suppliers.append({
                "supplier_id": supplier_id_counter,
                "supplier_name": f"Proveedor {fake.company()}",
                "contact_name": fake.name(),
                "contact_email": fake.company_email(),
                "country": "Peru",
                "primary_category": cat_name
            })
            supplier_id_counter += 1
            
    df_suppliers = pd.DataFrame(suppliers)
    
    # 2. Generar 500 Productos catalogados
    for cat_name, cat_info in config.PRODUCT_CATEGORIES.items():
        prod_count = cat_info["product_count"]
        min_cost, max_cost = cat_info["base_cost_range"]
        target_margin = cat_info["target_margin"]
        
        # Filtrar proveedores de esta categoría
        cat_suppliers = df_suppliers[df_suppliers["primary_category"] == cat_name]["supplier_id"].tolist()
        
        for i in range(1, prod_count + 1):
            base_cost = round(float(rng.uniform(min_cost, max_cost)), 2)
            base_price = round(base_cost / (1.0 - target_margin), 2)
            supplier_id = int(rng.choice(cat_suppliers))
            
            products.append({
                "product_id": product_id_counter,
                "product_sku": f"PRD-{cat_name[:3].upper()}-{product_id_counter:04d}",
                "product_name": f"Producto {cat_name} Grade-{i}",
                "category": cat_name,
                "unit_base_cost": base_cost,
                "unit_base_price": base_price,
                "supplier_id": supplier_id
            })
            product_id_counter += 1
            
    df_products = pd.DataFrame(products)
    return df_suppliers, df_products

if __name__ == "__main__":
    df_sup, df_prod = generate_suppliers_and_products()
    
    sup_path = config.OUTPUT_DIR / "suppliers.csv"
    prod_path = config.OUTPUT_DIR / "products.csv"
    
    df_sup.to_csv(sup_path, index=False)
    df_prod.to_csv(prod_path, index=False)
    
    print(f"✓ Generados {len(df_sup)} proveedores en: {sup_path}")
    print(f"✓ Generados {len(df_prod)} productos en: {prod_path}")