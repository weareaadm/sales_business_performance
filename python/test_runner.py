import os
import subprocess
import sys
from pathlib import Path


def run_phase_tests(phase_test_dir: str) -> None:
    """
    Ejecuta pytest sobre la carpeta de pruebas correspondiente a la fase.
    Lanza RuntimeError si algún test falla.
    """
    project_root = Path(__file__).resolve().parent.parent
    python_dir = project_root / "python"
    test_path = project_root / "tests" / phase_test_dir

    print(f"\n🧪 Ejecutando tests de fase en: tests/{phase_test_dir} ...")

    if not test_path.exists() or not any(test_path.glob("test_*.py")):
        print(f"⚠️ No se encontraron archivos test_*.py en tests/{phase_test_dir} (se omite).")
        return

    env = os.environ.copy()
    existing_pp = env.get("PYTHONPATH", "")
    paths_to_add = [str(project_root), str(python_dir)]
    if existing_pp:
        paths_to_add.append(existing_pp)
    env["PYTHONPATH"] = os.pathsep.join(paths_to_add)

    cmd = [sys.executable, "-m", "pytest", "-v", str(test_path)]
    result = subprocess.run(cmd, cwd=str(project_root), env=env)

    if result.returncode != 0:
        raise RuntimeError(
            f"❌ Fallaron los tests de la fase ({phase_test_dir}) con código {result.returncode}."
        )

    print(f"✅ Todos los tests de tests/{phase_test_dir} pasaron.")