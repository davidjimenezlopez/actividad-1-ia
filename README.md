# Biblio-IA

Biblio-IA es un sistema web moderno de reservas de libros, construido con Python, Flask, Flask-SQLAlchemy y estilizado con Tailwind CSS. Permite a los usuarios registrarse, explorar un catálogo de libros y hacer reservas, mientras que los administradores pueden añadir nueva literatura al inventario.

## Requisitos Previos
Para levantar este proyecto, debes tener instalado en tu sistema local:
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Instalación y Despliegue

1. Clona este repositorio o entra al directorio raíz del proyecto.
2. Abre una terminal en la raíz del proyecto y ejecuta el siguiente comando:

   ```bash
   docker-compose up -d --build
   ```

3. ¡Listo! Docker descargará las dependencias, creará la imagen e inicializará el contenedor en segundo plano.

> **Nota importante:** La base de datos es gestionada automáticamente. La primera vez que levantes el contenedor, el sistema ejecutará un script de población (seed) que creará de forma automatizada todas las tablas e inyectará un catálogo de libros y los usuarios.

## Credenciales de Acceso

**Usuario Administrador:**
- **Nombre de usuario:** `admin`
- **Contraseña:** `admin`

**Usuario Estándar (No admin):**
- **Nombre de usuario:** `tales`
- **Contraseña:** `tales`

## Interacción con la App

Una vez que el contenedor esté corriendo sin problemas, puedes acceder al sistema localmente empleando tu navegador preferido:

**URL de acceso local:** [http://localhost:5000](http://localhost:5000)