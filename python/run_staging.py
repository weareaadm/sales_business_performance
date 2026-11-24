"""
python/run_staging.py
---------------------
Utilidades de ejecución SQL e ingesta transaccional por lotes de CSVs
hacia el esquema stg_demo1 en SQL Server.
"""

import csv
import re
from datetime import date
from decimal import Decimal
from pathlib import Path


def execute_sql_file(cursor, conn, file_path: Path, commit: bool = True) -> None:
    """
    Ejecuta un archivo SQL dividido por lotes 'GO'.
    Nota: Sentencias DDL (CREATE/DROP SCHEMA/TABLE) en SQL Server no siempre
    participan de un ROLLBACK transaccional estándar como DML.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"El archivo SQL no existe: {file_path}")

    print(f"\n-> Ejecutando script: {file_path.name}")

    with open(file_path, "r", encoding="utf-8-sig") as f:
        sql_content = f.read()

    batches = re.split(r"^\s*GO\s*$", sql_content, flags=re.IGNORECASE | re.MULTILINE)

    for i, batch in enumerate(batches):
        clean_batch = batch.strip()
        if not clean_batch:
            continue
        try:
            cursor.execute(clean_batch)
            if cursor.messages:
                for msg in cursor.messages:
                    print(f"   [SQL Server]: {msg[1]}")
        except Exception as e:
            print(f"✖ Error en el lote #{i + 1} de {file_path.name}")
            raise e

    if commit:
        conn.commit()
    print(f"✓ Script {file_path.name} completado.")


def _get_table_columns_info(
    cursor, schema_name: str, table_name: str
) -> list[tuple[str, str]]:
    cursor.execute(
        """
        SELECT COLUMN_NAME, DATA_TYPE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = ? AND TABLE_NAME = ?
        ORDER BY ORDINAL_POSITION
        """,
        (schema_name, table_name),
    )
    cols = [(row[0], row[1].lower()) for row in cursor.fetchall()]
    if not cols:
        raise RuntimeError(
            f"No se encontraron columnas para la tabla {schema_name}.{table_name}"
        )
    return cols


def _cast_value(
    val: str | None,
    data_type: str,
    csv_name: str,
    table_name: str,
    row_idx: int,
    col_name: str,
):
    if val is None or val == "":
        return None
    try:
        if data_type in ("int", "bigint", "smallint", "tinyint"):
            return int(val)
        if data_type in ("decimal", "numeric", "float", "real", "money", "smallmoney"):
            return Decimal(val)
        if data_type == "date":
            return date.fromisoformat(val[:10])
        return val
    except Exception as exc:
        raise ValueError(
            f"Error de tipo en {csv_name} -> {table_name}, fila {row_idx}, "
            f"columna '{col_name}' (tipo SQL '{data_type}', valor '{val}'): {exc}"
        ) from exc


def load_csv_to_table(
    cursor,
    conn,
    csv_path: Path,
    table_name: str,
    batch_size: int = 1000,
    commit: bool = True,
) -> int:
    """
    Valida estructura/filas de un CSV (UTF-8 / UTF-8 BOM) y carga sus registros
    en 'schema.table' usando inserciones parametrizadas por lotes con tipado explícito.
    """
    if not csv_path.exists():
        raise FileNotFoundError(f"No se encontró el archivo CSV: {csv_path}")

    if "." not in table_name:
        raise ValueError(
            f"Nombre de tabla inválido (debe ser esquema.tabla): {table_name}"
        )

    schema_name, tbl_name = table_name.split(".", 1)
    cols_info = _get_table_columns_info(cursor, schema_name, tbl_name)
    expected_cols = [col for col, _ in cols_info]
    col_type_map = dict(cols_info)

    print(f"\n-> Ingestando CSV {csv_path.name} en la tabla {table_name}...")

    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        header = next(reader, None)

        if not header:
            raise ValueError(
                f"El archivo CSV '{csv_path.name}' está vacío o sin encabezado."
            )

        if len(header) != len(set(header)):
            dups = [col for col in header if header.count(col) > 1]
            raise ValueError(
                f"El archivo CSV '{csv_path.name}' contiene columnas duplicadas: "
                f"{sorted(set(dups))}"
            )

        if set(header) != set(expected_cols):
            missing = sorted(set(expected_cols) - set(header))
            extra = sorted(set(header) - set(expected_cols))
            raise ValueError(
                f"Desajuste de columnas entre '{csv_path.name}' y '{table_name}'. "
                f"Faltantes: {missing} | Sobrantes: {extra}"
            )

        expected_len = len(header)
        cursor.execute(f"TRUNCATE TABLE [{schema_name}].[{tbl_name}]")

        placeholders = ", ".join(["?"] * expected_len)
        columns_sql = ", ".join([f"[{col}]" for col in header])
        query = (
            f"INSERT INTO [{schema_name}].[{tbl_name}] ({columns_sql}) "
            f"VALUES ({placeholders})"
        )

        # Se mantiene fast_executemany desactivado para evitar inferencia corta de búfer
        # en columnas DECIMAL/numéricas en pyodbc + ODBC Driver 18.
        cursor.fast_executemany = False

        batch_data = []
        total_inserted = 0

        for row_idx, row in enumerate(reader, start=2):
            if len(row) != expected_len:
                raise ValueError(
                    f"Error en {csv_path.name} -> {table_name}, fila {row_idx}: "
                    f"se esperaban {expected_len} columnas y se encontraron {len(row)}."
                )

            normalized_row = [
                _cast_value(
                    val,
                    col_type_map[col_name],
                    csv_path.name,
                    table_name,
                    row_idx,
                    col_name,
                )
                for col_name, val in zip(header, row)
            ]
            batch_data.append(normalized_row)

            if len(batch_data) >= batch_size:
                try:
                    cursor.executemany(query, batch_data)
                except Exception as exc:
                    raise RuntimeError(
                        f"Error insertando lote en {csv_path.name} -> {table_name} "
                        f"(alrededor de fila {row_idx}): {exc}"
                    ) from exc
                total_inserted += len(batch_data)
                batch_data = []

        if batch_data:
            try:
                cursor.executemany(query, batch_data)
            except Exception as exc:
                raise RuntimeError(
                    f"Error insertando lote final en {csv_path.name} -> {table_name}: {exc}"
                ) from exc
            total_inserted += len(batch_data)

    if commit:
        conn.commit()
    print(
        f"✓ Tabla {table_name} poblada exitosamente ({total_inserted:,} filas) "
        f"desde {csv_path.name}."
    )
    return total_inserted