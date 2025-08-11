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




# Probar interfaz grafica Open WebUI con modelo Llama3
## 1.Iniciar contenedores de Open WebUI y Ollama
docker compose up -d openwebui ollama

## 2. Descargar el modelo manualmente (por el momento se hace asi, luego se optimiza desde docker)
# Descargar Llama 3
docker-compose exec ollama ollama pull llama3:8b-instruct-q4_0

# Verificar que se descargó
docker-compose exec ollama ollama list

## 3.Verificar conectividad desde Open WebUI
# Probar si Open WebUI puede ver Ollama
docker-compose exec openwebui curl http://ollama:11434/api/tags


## 4. Refrescar Open WebUI
Ve a http://localhost:3000
Recarga la página (F5)
Busca en "Selecciona un modelo" - ahora debería aparecer llama3:8b-instruct-q4_0

