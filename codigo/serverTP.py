import socket
import threading

def manejar_cliente(conn, addr, lista_clientes):
    print(f"\n[NUEVA CONEXIÓN] {addr} conectado.")
    
    conectado = True
    while conectado:
        try:
            mensaje = conn.recv(1024).decode('utf-8')
            if not mensaje:
                break
            
            print(f"[{addr}] dice: {mensaje}")
            conn.send(f"Eco: {mensaje}".encode('utf-8'))
            
        except ConnectionResetError:
            break

    conn.close()
    lista_clientes.remove(conn)
    print(f"\n[DESCONEXIÓN] {addr} se ha ido.")
    print(f"[CLIENTES ACTIVOS] {len(lista_clientes)}")

def iniciar_servidor():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', 5050))
    server.listen()
    
    clientes_activos = []
    print("[INICIO] Servidor escuchando en el puerto 5050...")

    while True:
        conn, addr = server.accept()
        clientes_activos.append(conn)
        
        hilo = threading.Thread(target=manejar_cliente, args=(conn, addr, clientes_activos))
        hilo.start()
        print(f"[CLIENTES ACTIVOS] {len(clientes_activos)}")

if __name__ == "__main__":
    iniciar_servidor()