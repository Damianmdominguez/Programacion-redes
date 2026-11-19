import socket
import threading
import mysql.connector
import hashlib

# Configuración de la base de datos MySQL
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "db_github_api"
}

def connect_db():
    """Establece la conexión con la base de datos MySQL."""
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Error al conectar a MySQL: {err}")
        return None

def encriptar_password(password):
    """Convierte una contraseña en texto plano a un hash SHA-256."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def manejar_cliente(conn, addr, clientes_activos):
    """Maneja el ciclo de vida de cada cliente conectado en un hilo independiente."""
    print(f"\n[NUEVA CONEXIÓN] {addr} conectado.")
    db = connect_db()
    
    if not db:
        conn.send("Error interno de base de datos. Cerrando conexión.".encode('utf-8'))
        conn.close()
        return

    cursor = db.cursor()
    usuario = ""

    try:
        # 1. Pedir usuario y contraseña
        conn.send("Ingrese usuario: ".encode('utf-8'))
        usuario = conn.recv(1024).decode('utf-8').strip()

        conn.send("Ingrese contraseña: ".encode('utf-8'))
        password = conn.recv(1024).decode('utf-8').strip()

        # 2. Encriptar la contraseña recibida y validar en MySQL
        password_hash = encriptar_password(password)
        query = "SELECT id FROM usuarios WHERE username = %s AND password = %s"
        cursor.execute(query, (usuario, password_hash))
        resultado = cursor.fetchone()

        # 3. Si es incorrecto, informar y cortar conexión a la primera
        if not resultado:
            conn.send("Usuario o contraseña incorrectos. Cerrando sesión.".encode('utf-8'))
            print(f"[LOGIN FALLIDO] {addr} intentó ingresar como '{usuario}'.")
            return

        # 4. Si es válido, dar bienvenida y registrar en clientes activos
        clientes_activos[conn] = usuario
        conn.send(f"¡Bienvenido al servidor, {usuario}!".encode('utf-8'))
        print(f"[LOGIN EXITOSO] {usuario} ({addr}) conectado. Activos: {len(clientes_activos)}")

        # 5. Bucle de chat básico (Eco)
        while True:
            mensaje = conn.recv(1024).decode('utf-8').strip()
            if not mensaje or mensaje.lower() == "/adios":
                conn.send("¡Adiós! Desconectando...".encode('utf-8'))
                break
            
            print(f"[{usuario}] dice: {mensaje}")
            conn.send(f"Eco: {mensaje}".encode('utf-8'))

    except ConnectionResetError:
        pass
    finally:
        # Limpieza al desconectar
        if conn in clientes_activos:
            del clientes_activos[conn]
        cursor.close()
        db.close()
        conn.close()
        print(f"[DESCONEXIÓN] {usuario if usuario else addr} se ha ido. Activos: {len(clientes_activos)}")

def iniciar_servidor():
    """Inicia el servidor TCP concurrente en el puerto 5050."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', 5050))
    server.listen()
    
    # Usamos diccionario {socket: nombre_usuario} para saber quién es cada cliente
    clientes_activos = {}
    print("[INICIO] Servidor escuchando en 127.0.0.1:5050...")

    while True:
        conn, addr = server.accept()
        hilo = threading.Thread(target=manejar_cliente, args=(conn, addr, clientes_activos))
        hilo.start()

if __name__ == "__main__":
    iniciar_servidor()