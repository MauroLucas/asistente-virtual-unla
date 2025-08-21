# v_materias.py
# Crea la vista materializada data.v_materias de forma simple.

def run(conn):
    print("🏗️ Creando vista materializada data.v_materias ...")
    ddl = """
    CREATE SCHEMA IF NOT EXISTS data;

    DROP MATERIALIZED VIEW IF EXISTS data.v_materias;

    CREATE MATERIALIZED VIEW data.v_materias AS
    SELECT
        "Carrera",
        "Plan",
        "Materia",
        "Correlativas",
        "cuatrimestre",
        "Carga Horaria Semanal",
        "Carga Horaria Total",
        "Area"
    FROM data.materias_sistemas_plan_2024
    WITH DATA;
    """
    with conn.cursor() as cur:
        cur.execute(ddl)
    conn.commit()
    print("✅ Vista materializada data.v_materias creada.")
