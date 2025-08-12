import os, time, psycopg2
from psycopg2.extras import execute_values

def get_conn():
    host = os.getenv("PGHOST", "postgres_kb")
    port = int(os.getenv("PGPORT", "5432"))
    db   = os.getenv("PGDATABASE")
    user = os.getenv("PGUSER")
    pwd  = os.getenv("PGPASSWORD")
    for i in range(10):
        try:
            conn = psycopg2.connect(host=host, port=port, dbname=db, user=user, password=pwd)
            conn.autocommit = False
            return conn
        except Exception as e:
            print(f"[DB] Intento {i+1}/10 - esperando DB... ({e})")
            time.sleep(3)
    raise RuntimeError("No se pudo conectar a Postgres.")

def ensure_schemas_and_tables(conn):
    ddl = """
    CREATE SCHEMA IF NOT EXISTS log;
    CREATE TABLE IF NOT EXISTS log.log_lotes (
        lote_key        SERIAL PRIMARY KEY,
        lote_descripcion VARCHAR(255),
        lote_esquema     VARCHAR(255),
        lote_origen      VARCHAR(255)
    );
    CREATE TABLE IF NOT EXISTS log.log_procesos (
        proceso_key              SERIAL PRIMARY KEY,
        lote_key                 INT,
        fecha_inicio_proceso     TIMESTAMP,
        fecha_fin_proceso        TIMESTAMP,
        estado_procesamiento_key INT
    );
    """
    with conn.cursor() as cur:
        cur.execute(ddl)
    conn.commit()

def upsert_lotes(conn, lotes):
    with conn.cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO log.log_lotes (lote_key, lote_descripcion, lote_esquema, lote_origen)
            VALUES %s
            ON CONFLICT (lote_key) DO UPDATE
            SET lote_descripcion = EXCLUDED.lote_descripcion,
                lote_esquema     = EXCLUDED.lote_esquema,
                lote_origen      = EXCLUDED.lote_origen;
            """,
            [(l["lote_key"], l.get("lote_descripcion"), l.get("lote_esquema"), l.get("lote_origen")) for l in lotes]
        )
    conn.commit()

# ---- PROCESOS ---------------------------------------------------------------

def start_proceso(conn, lote_key):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO log.log_procesos (lote_key, fecha_inicio_proceso, estado_procesamiento_key)
            VALUES (%s, NOW(), 0)
            RETURNING proceso_key;
        """, (lote_key,))
        pk = cur.fetchone()[0]
    conn.commit()
    return pk

def finish_proceso(conn, proceso_key, estado):
    # estado: 2 = OK, 8 = ERROR (usa NOW() como fin)
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE log.log_procesos
               SET estado_procesamiento_key = %s,
                   fecha_fin_proceso = NOW()
             WHERE proceso_key = %s;
        """, (estado, proceso_key))
    conn.commit()
