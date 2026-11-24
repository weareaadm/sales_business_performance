"""
generate_customers.py
---------------------
Genera el catálogo de 2,000 clientes con asignación determinista por cuota
de mercado en las 8 regiones de Lima, Perú.
"""

import math
import sys
from pathlib import Path
from faker import Faker
import pandas as pd

# Garantizar importación de config desde la misma carpeta python/
PYTHON_DIR = Path(__file__).resolve().parent
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

import config

def generate_customers() -> pd.DataFrame:
    fake = Faker('es_ES')
    Faker.seed(config.SEED)
    
    customers = []
    customer_id_counter = 1
    
    # Repartir 2,000 clientes según el market_weight de cada región
    total_customers_target = config.TOTAL_CUSTOMERS
    
    # Calcular cuotas por región garantizando suma exacta a 2000
    region_allocations = {}
    allocated_sum = 0
    
    for r in config.REGIONS[:-1]:
        count = math.floor(total_customers_target * r["market_weight"])
        region_allocations[r["region_id"]] = count
        allocated_sum += count
    
    # Asignar el remanente a la última región
    last_region_id = config.REGIONS[-1]["region_id"]
    region_allocations[last_region_id] = total_customers_target - allocated_sum
    
    # Segmentos de cliente
    segments = list(config.CUSTOMER_SEGMENTS.keys())
    
    for region in config.REGIONS:
        r_id = region["region_id"]
        count = region_allocations[r_id]
        
        for _ in range(count):
            segment = fake.random_element(elements=segments)
            
            # RUC de 11 dígitos para empresas en Perú (inicia con 20 + 9 dígitos)
            tax_id = f"20{fake.numerify('#########')}"
            
            # Fecha de registro entre 2021 y 2023
            reg_date = fake.date_between(start_date='-3y', end_date='-1d').strftime('%Y-%m-%d')
            company_name = f"{fake.company()} {fake.company_suffix()}"
            
            customers.append({
                "customer_id": customer_id_counter,
                "company_name": company_name,
                "contact_name": fake.name(),
                "contact_email": fake.company_email(),
                "tax_id": tax_id,
                "customer_segment": segment,
                "region_id": r_id,
                "registration_date": reg_date
            })
            customer_id_counter += 1
            
    df_customers = pd.DataFrame(customers)
    return df_customers

if __name__ == "__main__":
    df = generate_customers()
    out_path = config.OUTPUT_DIR / "customers.csv"
    df.to_csv(out_path, index=False)
    print(f"✓ Generados {len(df)} clientes exitosamente en: {out_path}")