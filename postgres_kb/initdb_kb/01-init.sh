#!/usr/bin/env bash
set -e

# Corre como $POSTGRES_USER sobre $POSTGRES_DB (prueba_ia)
# Crea esquemas/roles en prueba_ia y además crea n8n_user + n8n_db para n8n.

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL

-- ====== Esquemas en prueba_ia ======
CREATE SCHEMA IF NOT EXISTS data;
CREATE SCHEMA IF NOT EXISTS log;

-- ====== Roles (app_ro, etl, n8n_user) ======
DO \$\$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '${APP_RO_USER}') THEN
    CREATE ROLE ${APP_RO_USER} LOGIN PASSWORD '${APP_RO_PASSWORD}';
  END IF;

  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '${ETL_USER}') THEN
    CREATE ROLE ${ETL_USER} LOGIN PASSWORD '${ETL_PASSWORD}';
  END IF;

  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '${N8N_USER}') THEN
    CREATE ROLE ${N8N_USER} LOGIN PASSWORD '${N8N_PASSWORD}';
  END IF;
END
\$\$;

-- Conexión a prueba_ia
GRANT CONNECT ON DATABASE ${POSTGRES_DB} TO ${APP_RO_USER}, ${ETL_USER};

-- Permisos en esquemas de negocio
GRANT USAGE ON SCHEMA data TO ${APP_RO_USER}, ${ETL_USER};
GRANT USAGE ON SCHEMA log  TO ${ETL_USER};
GRANT CREATE ON SCHEMA data, log TO ${ETL_USER};

-- Endurecer esquema public de prueba_ia
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
GRANT CREATE ON SCHEMA public TO ${POSTGRES_USER}, ${ETL_USER};

-- Permisos sobre objetos existentes en data/log
GRANT SELECT ON ALL TABLES    IN SCHEMA data TO ${APP_RO_USER};
GRANT SELECT ON ALL SEQUENCES IN SCHEMA data TO ${APP_RO_USER};

GRANT ALL PRIVILEGES ON ALL TABLES    IN SCHEMA data, log TO ${ETL_USER};
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA data, log TO ${ETL_USER};

-- Permisos por defecto para futuros objetos creados por ETL en data
ALTER DEFAULT PRIVILEGES FOR ROLE ${ETL_USER} IN SCHEMA data
  GRANT SELECT ON TABLES TO ${APP_RO_USER};
ALTER DEFAULT PRIVILEGES FOR ROLE ${ETL_USER} IN SCHEMA data
  GRANT SELECT ON SEQUENCES TO ${APP_RO_USER};

-- ====== Crear base de n8n (dueño: n8n_user) ======
-- Crear la DB solo si no existe (usa \gexec para ejecutar el resultado)
SELECT 'CREATE DATABASE ' || quote_ident('${N8N_DB}') || ' OWNER ${N8N_USER}'
WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname='${N8N_DB}')
\gexec

EOSQL

# Endurecer el esquema public y asegurar privilegios dentro de n8n_db
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$N8N_DB" <<-EOSQL
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
GRANT CREATE ON SCHEMA public TO ${POSTGRES_USER}, ${N8N_USER};

GRANT CONNECT ON DATABASE ${N8N_DB} TO ${N8N_USER};
GRANT ALL PRIVILEGES ON DATABASE ${N8N_DB} TO ${N8N_USER};
-- Que n8n_user sea dueño de lo que cree y tenga permisos totales
ALTER DEFAULT PRIVILEGES FOR ROLE ${N8N_USER} IN SCHEMA public
  GRANT ALL ON TABLES TO ${N8N_USER};
ALTER DEFAULT PRIVILEGES FOR ROLE ${N8N_USER} IN SCHEMA public
  GRANT ALL ON SEQUENCES TO ${N8N_USER};
EOSQL



