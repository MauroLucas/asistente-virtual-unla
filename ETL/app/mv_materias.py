# v_materias.py
# Crea la vista materializada data.v_materias uniendo 2024 (con Area) y 2014 (sin Area).

def run(conn):
    print("🏗️ Creando vista materializada data.mv_materias ...")
    ddl = """
    CREATE SCHEMA IF NOT EXISTS data;

    DROP MATERIALIZED VIEW IF EXISTS data.mv_materias;

    CREATE MATERIALIZED VIEW data.mv_materias AS
    SELECT
        "Carrera",
        "Plan",
        "Materia",
        "Correlativas",
        "cuatrimestre",
        "Carga Horaria Semanal",
        "Carga Horaria Total",
        "Area"                      -- 2024 trae su Area
    FROM data.materias_sistemas_plan_2024

    UNION ALL

    SELECT
        "Carrera",
        "Plan",
        "Materia",
        "Correlativas",
        "cuatrimestre",
        "Carga Horaria Semanal",
        "Carga Horaria Total",
        NULL::TEXT AS "Area"        -- 2014 no tiene Area
    FROM data.materias_sistemas_plan_2014
    WITH DATA;
    """
    with conn.cursor() as cur:
        cur.execute(ddl)
    conn.commit()
    print("✅ Vista materializada data.v_materias creada.")

