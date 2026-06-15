# Usamos una imagen de Python ligera y eficiente
FROM python:3.11-slim

# Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiamos primero el archivo de requisitos para aprovechar el caché de Docker
COPY src/requirements.txt .

# Instalamos las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos todo el resto del código fuente a la carpeta /app
COPY src/ .

# Exponemos el puerto 5000 (el predeterminado de Flask)
EXPOSE 5000

# Definimos variables de entorno necesarias para Flask
ENV FLASK_APP=app.py
ENV FLASK_ENV=development

# Ejecutamos primero el seeder y luego levantamos el servidor Flask abierto a la red de Docker
CMD ["sh", "-c", "python seed.py && flask run --host=0.0.0.0"]