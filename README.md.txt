# TP Integrador - Programación sobre Redes

Aplicación Cliente-Servidor concurrente en Python usando sockets TCP, hilos (`threading`), base de datos MySQL, encriptación SHA-256 (`hashlib`) y la API pública de GitHub (`requests`).

## Contenido del Repositorio
* `server.py`: Servidor TCP concurrente (puerto `5050`) que autentica usuarios contra MySQL, gestiona el chat y procesa comandos.
* `cliente.py`: Cliente TCP con hilo secundario para recibir mensajes del servidor en tiempo real sin bloquear el envío.
* `requirements.txt`: Librerías externas necesarias para ejecutar el proyecto.
* `.gitignore`: Exclusión del entorno virtual (`venv/`) y archivos temporales (`__pycache__/`).

## Requisitos Previos
1. Python 3 instalado.
2. Servidor MySQL activo (ej. XAMPP o MariaDB).
3. Crear la base de datos `db_github_api` con las tablas `usuarios`, `repositorios` y `followers`.
4. Insertar un usuario de prueba en `usuarios` con la contraseña cifrada en SHA-256 (por ejemplo, `admin` / `1234`).

## Instalación y Uso

1. Clonar el repositorio y abrir la carpeta del proyecto.
2. Crear y activar el entorno virtual:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate

Instalar dependencias:

1) PowerShell
pip install -r requirements.txt
Iniciar el servidor en una terminal:

2) PowerShell
python server.py
Iniciar uno o más clientes en otras terminales:

3) PowerShell
python cliente.py

4) Ingresar usuario y contraseña cuando el servidor los solicite.


Comandos Disponibles
/repos <usuario>: Consulta los repositorios públicos de GitHub del usuario indicado y los guarda en la tabla repositorios.

/followers <usuario>: Consulta los seguidores de GitHub del usuario indicado y los guarda en la tabla followers.

/hora: Devuelve la hora actual del servidor.

/todos <mensaje>: Envía un mensaje global a todos los clientes conectados.

/usuarios: Lista todos los usuarios conectados actualmente.

/adios: Envía un mensaje de despedida y cierra la conexión.