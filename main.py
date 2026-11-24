#!/usr/bin/env python3
"""
main.py
-------
Orquestador central de Sales & Business Performance (B2B Analytics).
Permite ejecutar de forma secuencial o aislada cada fase previa a Power BI / DAX.
"""

import sys
import argparse
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
PYTHON_DIR = ROOT_DIR / "python"
for p in (str(ROOT_DIR), str(PYTHON_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

from phase1_generate import run_phase_1
from phase2_staging import run_phase_2
from phase3_dw import run_phase_3
from phase4_validate import run_phase_4


def main():
    parser = argparse.ArgumentParser(
        description="Sales & Business Performance - Orquestador de Fases",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "--phase",
        type=int,
        choices=[1, 2, 3, 4],
        help=(
            "Ejecuta una fase específica:\n"
            "  1: Generación de datos en Python (CSV con SEED=42).\n"
            "  2: Creación de tablas e ingesta a Staging (stg_demo1).\n"
            "  3: Construcción de Dimensiones y FactSales (dw_demo1).\n"
            "  4: Validación SQL y conciliación previa a Power BI / DAX."
        )
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Ejecuta secuencialmente las fases 1 -> 2 -> 3 -> 4."
    )

    args = parser.parse_args()

    print("==================================================================")
    print("  SALES & BUSINESS PERFORMANCE — ORQUESTADOR POR FASE")
    print("==================================================================")

    if args.all:
        print("\n🚀 Ejecutando pipeline completo (Fases 1 a 4)...")
        run_phase_1()
        run_phase_2()
        run_phase_3()
        run_phase_4()
        print("\n🎉 ¡Fases 1 a 4 completadas! Revisa la evidencia antes de DAX.")
        return

    if args.phase == 1:
        run_phase_1()
    elif args.phase == 2:
        run_phase_2()
    elif args.phase == 3:
        run_phase_3()
    elif args.phase == 4:
        run_phase_4()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()