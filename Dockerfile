# Usa una imagen base de Python
FROM python:3.11-slim-bullseye

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema (para psycopg2)
RUN apt-get update \
    && apt-get -y install gcc libpq-dev \
    && apt-get clean

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Exponer el puerto
EXPOSE 8000
