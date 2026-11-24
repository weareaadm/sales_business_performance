"""
generate_salespeople.py
-----------------------
Genera el catálogo maestro de 50 vendedores asignados a las regiones de Lima, Perú.
"""

import sys
from pathlib import Path
from faker import Faker
import pandas as pd

PYTHON_DIR = Path(__file__).resolve().parent
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

import config

def generate_salespeople() -> pd.DataFrame:
    fake = Faker('es_ES')
    Faker.seed(config.SEED)
    
    salespeople = []
    salesperson_id_counter = 1
    
    for r_id, count in config.REGION_SALESPERSON_COUNTS.items():
        for _ in range(count):
            salespeople.append({
                "salesperson_id": salesperson_id_counter,
                "salesperson_name": fake.name(),
                "region_id": r_id
            })
            salesperson_id_counter += 1
            
    return pd.DataFrame(salespeople)

if __name__ == "__main__":
    df = generate_salespeople()
    out_path = config.OUTPUT_DIR / "salespeople.csv"
    df.to_csv(out_path, index=False)
    print(f"✓ Generados {len(df)} vendedores exitosamente en: {out_path}")