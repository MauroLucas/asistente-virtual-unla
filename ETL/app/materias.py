import os, json, math, pandas as pd
from psycopg2.extras import execute_values, Json
from .db import start_proceso, finish_proceso

EXPECTED = [
    "Carrera", "Plan", "Materia", "Correlativas",
    "cuatrimestre", "Carga Horaria Semanal", "Carga Horaria Total", "Area"
]

def _norm(s: str) -> str:
    # normaliza para mapear columnas sin importar mayúsculas/espacios
    import unicodedata, re
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = s.strip().lower()
    s = re.sub(r"\s+", " ", s)
    return s

def _build_colmap(df_cols):
    # mapea columnas del Excel a las esperadas
    wanted = {_norm(c): c for c in EXPECTED}
    found = {}
    for c in df_cols:
        n = _norm(c)
        if n in wanted:
            found[wanted[n]] = c
    missing = [c for c in EXPECTED if c not in found]
    if missing:
        raise ValueError(f"Faltan columnas en Excel: {missing}")
    return found

def _parse_correlativas(val):
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return None
    if isinstance(val, (list, dict)):
        return val
    if isinstance(val, (int, float)):
        return [val]
    s = str(val).strip()
    if not s:
        return None
    # si ya parece JSON, intentar cargar
    if (s.startswith("{") and s.endswith("}")) or (s.startswith("[") and s.endswith("]")):
        try:
            return json.loads(s)
        except Exception:
            pass
    # fallback: lista separada por coma/;/
    parts = [p.strip() for p in re_split(s) if p.strip()]
    return parts if parts else None

def re_split(s):
    import re
    return re.split(r"[;,/|]+", s)

def ensure_table(conn):
    ddl = """
    CREATE SCHEMA IF NOT EXISTS data;

    CREATE TABLE IF NOT EXISTS data.materias (
        "Carrera"                 TEXT,
        "Plan"                    TEXT,
        "Materia"                 TEXT,
        "Correlativas"            JSON,
        "cuatrimestre"            TEXT,
        "Carga Horaria Semanal"   TEXT,
        "Carga Horaria Total"     TEXT,
        "Area"                    TEXT
    );
    """
    with conn.cursor() as cur:
        cur.execute(ddl)

def load_excel_to_table(conn, xlsx_path):
    df = pd.read_excel(xlsx_path, engine="openpyxl")
    colmap = _build_colmap(df.columns)

    # renombra DataFrame a las columnas esperadas exactamente
    df = df.rename(columns={v: k for k, v in colmap.items()})
    df = df[EXPECTED]  # orden

    # parseos/casts
    df["Correlativas"] = df["Correlativas"].apply(_parse_correlativas)

    # todo como str o None para los TEXT
    for c in ["Carrera","Plan","Materia","cuatrimestre","Carga Horaria Semanal","Carga Horaria Total","Area"]:
        df[c] = df[c].apply(lambda x: None if (pd.isna(x) if not isinstance(x, str) else x.strip()== "") else str(x))

    rows = []
    for _, r in df.iterrows():
        rows.append((
            r["Carrera"], r["Plan"], r["Materia"],
            Json(r["Correlativas"]) if r["Correlativas"] is not None else None,
            r["cuatrimestre"], r["Carga Horaria Semanal"], r["Carga Horaria Total"], r["Area"]
        ))

    with conn.cursor() as cur:
        # carga full-refresh
        cur.execute('TRUNCATE TABLE data.materias;')
        execute_values(
            cur,
            """
            INSERT INTO data.materias
            ("Carrera","Plan","Materia","Correlativas","cuatrimestre",
             "Carga Horaria Semanal","Carga Horaria Total","Area")
            VALUES %s
            """,
            rows
        )

def run(conn, data_dir):
    LOTE_KEY = 1  # Carga Excel Materias
    proceso_key = start_proceso(conn, LOTE_KEY)  # estado = 0

    try:
        ensure_table(conn)
        xlsx = os.path.join(data_dir or "/app/data", "materias.xlsx")
        if not os.path.exists(xlsx):
            raise FileNotFoundError(f"No se encontró el archivo: {xlsx}")

        load_excel_to_table(conn, xlsx)
        conn.commit()
        finish_proceso(conn, proceso_key, 2)   # OK
        print("✅ Carga de data.materias completada.")
    except Exception as e:
        conn.rollback()
        finish_proceso(conn, proceso_key, 8)   # ERROR
        raise
