import os
from .db import get_conn, ensure_schemas_and_tables, upsert_lotes
from .lotes import get_lotes_config
from . import consejos_materias, materias_sistemas_plan_2024, v_materias


def main():
    print("🔌 Conectando a Postgres...")
    conn = get_conn()
    try:
        print("🧱 Verificando esquemas/tablas base...")
        ensure_schemas_and_tables(conn)

        print("🗂️  Registrando lotes...")
        upsert_lotes(conn, get_lotes_config())

        print("📥 Ejecutando lote Materias Sistemas Plan 2024...")
        materias_sistemas_plan_2024.run(conn, data_dir=os.getenv("DATA_DIR", "/app/data"))

        print("🏗️ Generando vista materializada v_materias...")
        v_materias.run(conn)

        print("📥 Ejecutando lote Consejos de Materias...")
        consejos_materias.run(conn, data_dir=os.getenv("DATA_DIR", "/app/data"))

        print("✅ ETL finalizado.")
    finally:
        conn.close()

if __name__ == "__main__":
    main()

