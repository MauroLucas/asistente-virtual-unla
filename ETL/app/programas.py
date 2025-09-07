# ETL/app/programas.py
import os
import subprocess
import shutil
from pathlib import Path
from psycopg2.extras import execute_values
from .db import start_proceso, finish_proceso
from docx import Document  # librería python-docx

CARRERA_FIJA = "Lic. Sistemas"

def _ensure_table(conn):
    ddl = """
    CREATE SCHEMA IF NOT EXISTS data;

    CREATE TABLE IF NOT EXISTS data.programas_contenidos (
        "Carrera"  TEXT,
        "Programa" TEXT,
        "Contenido" TEXT
    );
    """
    with conn.cursor() as cur:
        cur.execute(ddl)

def _extract_text_from_docx(path: Path) -> str:
    doc = Document(str(path))
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())

def _download_from_drive(folder_url: str, dest_dir: Path):
    if dest_dir.exists():
        shutil.rmtree(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(["gdown", "--folder", "-O", str(dest_dir), folder_url], check=True)

def run(conn):
    LOTE_KEY = 3
    proceso_key = start_proceso(conn, LOTE_KEY)
    try:
        _ensure_table(conn)

        folder_url = os.getenv("WORD_FOLDER_PROGRAMAS_URL")
        if not folder_url:
            raise ValueError("Falta WORD_FOLDER_PROGRAMAS_URL en .env")

        tmp_dir = Path("/app/tmp_word")
        _download_from_drive(folder_url, tmp_dir)

        rows = []
        for f in tmp_dir.rglob("*.docx"):
            contenido = _extract_text_from_docx(f)
            programa = f.stem  # nombre sin extensión
            rows.append((CARRERA_FIJA, programa, contenido))

        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE data.programas_contenidos;")
            if rows:
                execute_values(
                    cur,
                    """
                    INSERT INTO data.programas_contenidos
                    ("Carrera","Programa","Contenido")
                    VALUES %s
                    """,
                    rows
                )

        conn.commit()
        finish_proceso(conn, proceso_key, 2)
        print("✅ Programas cargados en data.programas_contenidos")
    except Exception:
        conn.rollback()
        finish_proceso(conn, proceso_key, 8)
        raise


