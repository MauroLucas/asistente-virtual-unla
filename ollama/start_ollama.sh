#!/bin/bash

echo "🚀 Iniciando Ollama..."
docker-compose up -d ollama

echo "⏳ Esperando a que Ollama esté listo..."
sleep 10

echo "⏳ Descargando modelo llama3.1:8b-instruct-q4_0..."
docker exec ollama ollama pull llama3.1:8b-instruct-q4_0

echo "Verificando que el modelo se descargó..."
if docker exec ollama ollama list | grep -q "llama3.1:8b-instruct-q4_0"; then
    echo "✅ Modelo descargado exitosamente"
else
    echo "Error: No se pudo descargar el modelo"
    exit 1
fi

echo ""
echo "🚀 Iniciando todos los servicios..."
docker-compose up -d

echo ""
echo "✅ Todos los servicios están corriendo"
