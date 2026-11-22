# Multi-stage / Production Dockerfile para Transcriptor Maestro Backend
FROM python:3.11-slim

# Metadatos del contenedor
LABEL maintainer="Daniel Felipe Castro Lizarazo <FelipeCastro5>"
LABEL description="Backend API FastAPI para Transcriptor Maestro"

# Variables de entorno para Python y optimización en contenedor
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    APP_HOME=/app

# Instalar dependencias mínimas de sistema (curl para HEALTHCHECK)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Hardening: Crear usuario y grupo sin privilegios (Principio de Menor Privilegio)
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/bash -m appuser

WORKDIR $APP_HOME

# Copiar e instalar dependencias primero para optimizar la caché UnionFS de Docker
COPY requirements-prod.txt .
RUN pip install --no-cache-dir -r requirements-prod.txt

# Copiar código fuente y migración DDL canónica
COPY app/ ./app
COPY db/ ./db
COPY scripts/ ./scripts

# Crear directorios de almacenamiento temporal y asignar permisos a appuser
RUN mkdir -p storage/audios_temp storage/salidas && \
    chown -R appuser:appgroup $APP_HOME

# Cambiar a usuario sin privilegios
USER appuser

# Exponer puerto de servicio
EXPOSE 8000

# Verificación de salud nativa de Docker
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando de inicio
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
