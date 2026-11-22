# Multi-stage Build para Transcriptor Maestro Frontend (Angular 19 + Nginx)

# Etapa 1: Compilación de la aplicación Angular
FROM node:20-alpine AS build

WORKDIR /app

# Copiar manifiestos e instalar dependencias
COPY package*.json ./
RUN npm ci || npm install

# Copiar código fuente y compilar bundle optimizado para producción
COPY . .
RUN npm run build -- --configuration production

# Etapa 2: Servidor Web Nginx ligero para producción
FROM nginx:1.25-alpine AS runtime

LABEL maintainer="Daniel Felipe Castro Lizarazo <FelipeCastro5>"
LABEL description="Frontend Angular 19 servido por Nginx para Transcriptor Maestro"

# Limpiar configuración por defecto y copiar bundle estático
RUN rm -rf /usr/share/nginx/html/*
COPY --from=build /app/dist/frontend-angular/browser /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Exponer puerto 80 HTTP
EXPOSE 80

# Verificación de salud nativa
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
    CMD wget -q -O /dev/null http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
