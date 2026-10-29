import socket
import threading

def manejar_cliente(conn, addr, lista_clientes):
    print(f"\n[NUEVA CONEXIÓN] {addr} conectado.")
    
    # Se envía un mensaje inicial al cliente
    conn.send("Conectado. Comandos: /users para ver conectados, /adios para salir.\n".encode('utf-8'))
    
    conectado = True
    while conectado:
        try:
            # Recibe el mensaje
            mensaje = conn.recv(1024).decode('utf-8').strip()
            if not mensaje:
                break
            
            print(f"[{addr}] dice: {mensaje}")
            
            # Condición 1: El cliente envía /adios
            if mensaje == "/adios":
                conn.send("Desconectando... ¡Adiós!".encode('utf-8'))
                conectado = False # Rompe el ciclo para terminar el hilo
                
            # Condición 2: El cliente envía /users
            elif mensaje == "/users":
                # Armamos un string con todos los usuarios en la lista
                respuesta = f"\n--- Usuarios conectados ({len(lista_clientes)}) ---\n"
                for cliente_socket in lista_clientes:
                    try:
                        # getpeername() nos da la (IP, Puerto) asociada a ese socket
                        direccion_cliente = cliente_socket.getpeername()
                        respuesta += f"- {direccion_cliente}\n"
                    except:
                        pass
                conn.send(respuesta.encode('utf-8'))
                
            # Condición 3: Eco (devuelve el mensaje al cliente)
            else:
                conn.send(f"Eco: {mensaje}".encode('utf-8'))
            
        except ConnectionResetError:
            break

    # Al terminar la conexión
    conn.close()
    if conn in lista_clientes:
        lista_clientes.remove(conn) # Se elimina al cliente de la lista
        
    print(f"\n[DESCONEXIÓN] {addr} se ha ido.")
    print(f"[CLIENTES ACTIVOS] {len(lista_clientes)}")

def iniciar_servidor():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 5050)) # la privada del servidor o localhost(127.0.0.1)[cite: 2]
    server.listen()
    
    clientes_activos = []
    print("[INICIO] Servidor escuchando en el puerto 5050...")

    while True:
        conn, addr = server.accept()
        clientes_activos.append(conn)
        
        # Crear hilo para el nuevo cliente[cite: 2]
        # target: declarando cuáles son las funciones target de los hilos[cite: 3]
        hilo = threading.Thread(target=manejar_cliente, args=(conn, addr, clientes_activos))
        
        # Iniciamos los hilos con .start(). Esto le dice al Sistema Operativo que empiece a ejecutarlos en paralelo[cite: 5]
        hilo.start()
        
        print(f"[CLIENTES ACTIVOS] {len(clientes_activos)}")

if __name__ == "__main__":
    iniciar_servidor()