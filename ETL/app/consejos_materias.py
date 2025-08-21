import os
import pandas as pd
from .db import start_proceso, finish_proceso

EXPECTED = ["Carrera", "Plan", "Materia", "Consejo"]

def ensure_table(conn):
    ddl = """
    CREATE SCHEMA IF NOT EXISTS data;

    CREATE TABLE IF NOT EXISTS data.consejos_materias_sistemas (
        "Carrera"  TEXT,
        "Plan"     TEXT,
        "Materia"  TEXT,
        "Consejo"  TEXT
    );
    """
    with conn.cursor() as cur:
        cur.execute(ddl)

def _ensure_xlsx_suffix(filename: str) -> str:
    # Acepta nombre con o sin extensión .xlsx
    return filename if filename.lower().endswith(".xlsx") else f"{filename}.xlsx"

def load_excel_to_table(conn, xlsx_path):
    df = pd.read_excel(xlsx_path, engine="openpyxl")

    # Validación de columnas
    for col in EXPECTED:
        if col not in df.columns:
            raise ValueError(f"Falta la columna '{col}' en {xlsx_path}")

    # Mantener solo las columnas necesarias y convertir a string/None
    df = df[EXPECTED]
    for col in EXPECTED:
        df[col] = df[col].apply(
            lambda x: None if (pd.isna(x) or str(x).strip() == "") else str(x).strip()
        )

    rows = [tuple(r) for r in df.to_numpy()]

    with conn.cursor() as cur:
        cur.execute('TRUNCATE TABLE data.consejos_materias_sistemas;')
        from psycopg2.extras import execute_values
        execute_values(
            cur,
            'INSERT INTO data.consejos_materias_sistemas ("Carrera","Plan","Materia","Consejo") VALUES %s',
            rows
        )

def run(conn, data_dir):
    LOTE_KEY = 2  # Carga Excel Consejos de Materias
    proceso_key = start_proceso(conn, LOTE_KEY)  # estado = 0

    try:
        ensure_table(conn)

        base_dir = data_dir or "/app/data"
        filename = _ensure_xlsx_suffix("consejos_materias_sistemas")
        xlsx = os.path.join(base_dir, filename)

        if not os.path.exists(xlsx):
            raise FileNotFoundError(f"No se encontró el archivo: {xlsx}")

        load_excel_to_table(conn, xlsx)
        conn.commit()
        finish_proceso(conn, proceso_key, 2)   # OK
        print("✅ Carga de data.consejos_materias_sistemas completada.")
    except Exception:
        conn.rollback()
        finish_proceso(conn, proceso_key, 8)   # ERROR
        raise
