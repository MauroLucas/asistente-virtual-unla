FROM python:3.11-slim

# Evita buffering y permite logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencias del sistema para psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Instalar requirements
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY app/ /app/app

# DATA_DIR viene montado por volumen (ver docker-compose)
ENV DATA_DIR=/app/data

# Comando por defecto
CMD ["python", "-m", "app.main"]
