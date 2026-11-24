"""
generate_sales.py
-----------------
Genera el motor transaccional comercial (2024-2026) creando dos dataframes:
1. sales_orders.csv (150,000 órdenes de encabezado con columna status)
2. order_lines.csv (~500,000 líneas de detalle con lógica de precios y costos)
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

PYTHON_DIR = Path(__file__).resolve().parent
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

import config
from generate_customers import generate_customers
from generate_products import generate_suppliers_and_products


def _assign_order_status(order_date: datetime, rng: np.random.Generator) -> str:
    """
    Asigna estado de orden:
    - 'Pending': ~2% exclusivo en diciembre de 2026.
    - Resto: ~95% 'Completed' y ~5% 'Cancelled'.
    """
    if order_date.year == 2026 and order_date.month == 12 and rng.random() < 0.02:
        return "Pending"
    return "Completed" if rng.random() < 0.95 else "Cancelled"


def generate_sales_data():
    rng = np.random.default_rng(config.SEED)

    # 1. Cargar o Generar Dimensiones Base
    df_cust = generate_customers()
    _, df_prod = generate_suppliers_and_products()

    cust_region_map = dict(zip(df_cust["customer_id"], df_cust["region_id"]))
    cust_segment_map = dict(zip(df_cust["customer_id"], df_cust["customer_segment"]))

    prod_category_map = dict(zip(df_prod["product_id"], df_prod["category"]))
    prod_cost_map = dict(zip(df_prod["product_id"], df_prod["unit_base_cost"]))
    prod_price_map = dict(zip(df_prod["product_id"], df_prod["unit_base_price"]))

    # Estructura de Vendedores por Región de Lima
    salespeople_by_region = {}
    sp_id_counter = 1
    for r_id, sp_count in config.REGION_SALESPERSON_COUNTS.items():
        salespeople_by_region[r_id] = list(range(sp_id_counter, sp_id_counter + sp_count))
        sp_id_counter += sp_count

    # 2. Pre-calcular Distribución de Órdenes por Mes
    dates_list = []
    month_weights_list = []

    for year, annual_target in config.ANNUAL_ORDER_TARGETS.items():
        for month in range(1, 13):
            if month in [1, 3, 5, 7, 8, 10, 12]:
                days_in_month = 31
            elif month in [4, 6, 9, 11]:
                days_in_month = 30
            else:
                days_in_month = 29 if (year % 4 == 0) else 28

            m_weight = config.MONTHLY_WEIGHTS[month]
            daily_weight = (m_weight * annual_target) / days_in_month

            for day in range(1, days_in_month + 1):
                dates_list.append(datetime(year, month, day))
                month_weights_list.append(daily_weight)

    month_weights_list = np.array(month_weights_list)
    date_probs = month_weights_list / month_weights_list.sum()

    chosen_dates = rng.choice(dates_list, size=config.TOTAL_ORDERS, p=date_probs)
    chosen_dates.sort()

    # 3. Generar Órdenes y Líneas de Detalle
    orders = []
    order_lines = []

    order_id_counter = 1
    line_id_counter = 1

    customer_ids = df_cust["customer_id"].values
    product_ids = df_prod["product_id"].values

    delivery_options = [1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 15]
    delivery_probs = [0.23, 0.24, 0.23, 0.07, 0.06, 0.06, 0.06, 0.01, 0.02, 0.01, 0.01]

    for order_date in chosen_dates:
        cust_id = int(rng.choice(customer_ids))
        reg_id = cust_region_map[cust_id]
        segment = cust_segment_map[cust_id]

        sp_id = int(rng.choice(salespeople_by_region[reg_id]))
        wh_id = reg_id

        days_to_deliver = int(rng.choice(delivery_options, p=delivery_probs))
        delivery_date = order_date + timedelta(days=days_to_deliver)
        status = _assign_order_status(order_date, rng)

        num_lines = int(rng.poisson(lam=config.POISSON_LAMBDA))
        num_lines = max(config.MIN_LINES_PER_ORDER, min(config.MAX_LINES_PER_ORDER, num_lines))

        chosen_products = rng.choice(product_ids, size=num_lines, replace=False)

        order_total_amount = 0.0
        order_total_cost = 0.0

        o_year, o_month = order_date.year, order_date.month

        for p_id in chosen_products:
            cat = prod_category_map[p_id]
            base_cost = prod_cost_map[p_id]
            base_price = prod_price_map[p_id]

            cost_mult = 1.0
            price_mult = 1.0
            if cat == config.STEEL_INFLATION_EVENT["category"]:
                if (o_year, o_month) in config.STEEL_INFLATION_EVENT["cost_affected_months"]:
                    cost_mult = config.STEEL_INFLATION_EVENT["cost_multiplier"]
                if (o_year, o_month) in config.STEEL_INFLATION_EVENT["price_affected_months"]:
                    price_mult = config.STEEL_INFLATION_EVENT["price_multiplier"]

            unit_cost = round(base_cost * cost_mult, 2)
            unit_price = round(base_price * price_mult, 2)

            quantity = int(rng.integers(1, 21))

            seg_info = config.CUSTOMER_SEGMENTS[segment]
            has_discount = rng.random() < seg_info["max_discount_prob"]
            if has_discount:
                discount_rate = round(float(rng.uniform(0.01, seg_info["max_discount_rate"])), 4)
            else:
                discount_rate = 0.0

            line_subtotal = round(quantity * unit_price * (1.0 - discount_rate), 2)
            line_cost_total = round(quantity * unit_cost, 2)

            order_lines.append({
                "line_id": line_id_counter,
                "order_id": order_id_counter,
                "product_id": int(p_id),
                "quantity": quantity,
                "unit_cost": unit_cost,
                "unit_price": unit_price,
                "discount_rate": discount_rate,
                "line_subtotal": line_subtotal,
                "line_cost_total": line_cost_total
            })

            order_total_amount += line_subtotal
            order_total_cost += line_cost_total
            line_id_counter += 1

        orders.append({
            "order_id": order_id_counter,
            "order_date": order_date.strftime("%Y-%m-%d"),
            "delivery_date": delivery_date.strftime("%Y-%m-%d"),
            "customer_id": cust_id,
            "salesperson_id": sp_id,
            "region_id": reg_id,
            "warehouse_id": wh_id,
            "total_lines": num_lines,
            "total_amount": round(order_total_amount, 2),
            "total_cost": round(order_total_cost, 2),
            "status": status
        })
        order_id_counter += 1

    df_orders = pd.DataFrame(orders)
    df_order_lines = pd.DataFrame(order_lines)

    return df_orders, df_order_lines


if __name__ == "__main__":
    print("Iniciando la generación de ventas (150,000 órdenes)...")
    df_ord, df_lines = generate_sales_data()

    ord_path = config.OUTPUT_DIR / "sales_orders.csv"
    lines_path = config.OUTPUT_DIR / "order_lines.csv"

    df_ord.to_csv(ord_path, index=False)
    df_lines.to_csv(lines_path, index=False)

    print(f"✓ Generadas {len(df_ord):,} órdenes exitosamente en: {ord_path}")
    print(f"✓ Generadas {len(df_lines):,} líneas de detalle en: {lines_path}")