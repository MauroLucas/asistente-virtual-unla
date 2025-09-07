import os
from .db import get_conn, ensure_schemas_and_tables, upsert_lotes
from .lotes import get_lotes_config
from . import (
    consejos_materias,
    materias_sistemas_plan_2024,
    materias_sistemas_plan_2014,  
    mv_materias,
    programas
)

def main():
    print("🔌 Conectando a Postgres...")
    conn = get_conn()
    try:
        print("🧱 Verificando esquemas/tablas base...")
        ensure_schemas_and_tables(conn)

        print("🗂️  Registrando lotes...")
        upsert_lotes(conn, get_lotes_config())

        data_dir = os.getenv("DATA_DIR", "/app/data")

        print("📥 Ejecutando lote Materias Sistemas Plan 2024...")
        materias_sistemas_plan_2024.run(conn, data_dir=data_dir)

        print("📥 Ejecutando lote Materias Sistemas Plan 2014...")
        materias_sistemas_plan_2014.run(conn, data_dir=data_dir)

        print("🏗️ Generando vista materializada mv_materias...")
        mv_materias.run(conn)

        print("📥 Ejecutando lote Consejos de Materias...")
        consejos_materias.run(conn, data_dir=data_dir)


        print("📄 Ejecutando lote Programas/Contenidos (Word/Drive)...")
        programas.run(conn)  # ← nuevo

        print("✅ ETL finalizado.")
    finally:
        conn.close()

if __name__ == "__main__":
    main()

