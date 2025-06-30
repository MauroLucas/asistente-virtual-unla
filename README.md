# Asistente Virtual - Stack Docker

Entorno para desarrollo de asistente virtual con Ollama, n8n y PostgreSQL.

## Requisitos previos
- Docker
- Docker Compose
- 8GB+ RAM recomendado

## Instalación rápida
```bash
# 1. Iniciar contenedores
docker-compose up -d

# 2. Instalar modelo de lenguaje (ejecutar después de iniciar)
docker-compose exec ollama /bin/ollama pull llama3:8b-instruct-q4_0

# 3. Regla clave: 
Dentro de flujos n8n, siempre usar nombres de servicio (ollama, postgres) en lugar de localhost