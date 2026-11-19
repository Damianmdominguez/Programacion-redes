import socket
import threading
import mysql.connector
import hashlib
import datetime
import requests

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

def guardar_repos(conn_socket, cursor, db, usuario_git):
    """Consulta los repositorios de un usuario en la API de GitHub y los guarda en MySQL."""
    url = f"https://api.github.com/users/{usuario_git}/repos"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            repositorios = response.json()
            for repo in repositorios:
                query = "INSERT INTO repositorios (name, html_url) VALUES (%s, %s)"
                cursor.execute(query, (repo['name'], repo['html_url']))
            db.commit()
            conn_socket.send(f"Se guardaron {len(repositorios)} repositorios de '{usuario_git}' en la BD.".encode('utf-8'))
        else:
            conn_socket.send(f"No se encontró el usuario '{usuario_git}' en GitHub.".encode('utf-8'))
    except Exception as e:
        conn_socket.send(f"Error al consultar GitHub: {e}".encode('utf-8'))

def guardar_followers(conn_socket, cursor, db, usuario_git):
    """Consulta los followers de un usuario en la API de GitHub y los guarda en MySQL."""
    url = f"https://api.github.com/users/{usuario_git}/followers"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            followers = response.json()
            for foll in followers:
                query = "INSERT INTO followers (follower_name, follower_url) VALUES (%s, %s)"
                cursor.execute(query, (foll['login'], foll['html_url']))
            db.commit()
            conn_socket.send(f"Se guardaron {len(followers)} followers de '{usuario_git}' en la BD.".encode('utf-8'))
        else:
            conn_socket.send(f"No se encontró el usuario '{usuario_git}' en GitHub.".encode('utf-8'))
    except Exception as e:
        conn_socket.send(f"Error al consultar GitHub: {e}".encode('utf-8'))

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
        # 1. Fase de Login
        conn.send("Ingrese usuario: ".encode('utf-8'))
        usuario = conn.recv(1024).decode('utf-8').strip()

        conn.send("Ingrese contraseña: ".encode('utf-8'))
        password = conn.recv(1024).decode('utf-8').strip()

        password_hash = encriptar_password(password)
        query = "SELECT id FROM usuarios WHERE username = %s AND password = %s"
        cursor.execute(query, (usuario, password_hash))
        resultado = cursor.fetchone()

        if not resultado:
            conn.send("Usuario o contraseña incorrectos. Cerrando sesión.".encode('utf-8'))
            print(f"[LOGIN FALLIDO] {addr} intentó ingresar como '{usuario}'.")
            return

        # 2. Login exitoso
        clientes_activos[conn] = usuario
        conn.send(f"¡Bienvenido al servidor, {usuario}! Comandos: /repos, /followers, /hora, /todos, /usuarios, /adios".encode('utf-8'))
        print(f"[LOGIN EXITOSO] {usuario} ({addr}) conectado. Activos: {len(clientes_activos)}")

        # 3. Bucle de Chat y Comandos
        while True:
            mensaje = conn.recv(1024).decode('utf-8').strip()
            if not mensaje:
                break
            
            print(f"[{usuario}] dice: {mensaje}")

            # Si empieza con "/" es un comando
            if mensaje.startswith("/"):
                partes = mensaje.split(" ", 1) # Separa el comando del resto del texto
                comando = partes[0].lower()

                if comando == "/adios":
                    conn.send("¡Adiós! Desconectando...".encode('utf-8'))
                    break

                elif comando == "/hora":
                    hora = datetime.datetime.now().strftime("%H:%M:%S")
                    conn.send(f"Hora actual del servidor: {hora}".encode('utf-8'))

                elif comando == "/usuarios":
                    lista = "Usuarios conectados:\n"
                    for u in clientes_activos.values():
                        lista += f"- {u}\n"
                    conn.send(lista.encode('utf-8'))

                elif comando == "/todos":
                    if len(partes) > 1:
                        texto = partes[1]
                        for cliente_sock in clientes_activos.keys():
                            if cliente_sock != conn: # No se lo reenvía al que lo mandó
                                try:
                                    cliente_sock.send(f"[Mensaje global de {usuario}]: {texto}".encode('utf-8'))
                                except:
                                    pass
                        conn.send("Mensaje enviado a todos los usuarios.".encode('utf-8'))
                    else:
                        conn.send("Uso correcto: /todos tu mensaje".encode('utf-8'))

                elif comando == "/repos":
                    if len(partes) > 1:
                        guardar_repos(conn, cursor, db, partes[1].strip())
                    else:
                        conn.send("Uso correcto: /repos usuario_github".encode('utf-8'))

                elif comando == "/followers":
                    if len(partes) > 1:
                        guardar_followers(conn, cursor, db, partes[1].strip())
                    else:
                        conn.send("Uso correcto: /followers usuario_github".encode('utf-8'))

                else:
                    conn.send("Comando no reconocido.".encode('utf-8'))
            else:
                # Chat normal (Eco)
                conn.send(f"Servidor recibió: {mensaje}".encode('utf-8'))

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
    
    clientes_activos = {}
    print("[INICIO] Servidor escuchando en 127.0.0.1:5050...")

    while True:
        conn, addr = server.accept()
        hilo = threading.Thread(target=manejar_cliente, args=(conn, addr, clientes_activos))
        hilo.start()

if __name__ == "__main__":
    iniciar_servidor()