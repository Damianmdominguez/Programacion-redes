import socket
import threading

def recibir_mensajes(s):
    """Escucha en segundo plano todo lo que envía el servidor."""
    while True:
        try:
            msg = s.recv(1024).decode('utf-8')
            if not msg:
                print("\n[Desconectado del servidor]")
                break
            print(msg)
        except:
            break

def funcion_cliente():
    host = "127.0.0.1"
    port = 5050
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        s.connect((host, port))
        print("Conectado al servidor.")

        # Iniciamos el hilo que escucha al servidor
        hilo = threading.Thread(target=recibir_mensajes, args=(s,))
        hilo.daemon = True
        hilo.start()

        # Bucle principal para escribir desde el teclado
        while True:
            msg = input()
            s.send(msg.encode('utf-8'))
            if msg.strip().lower() == "/adios":
                break

    except ConnectionRefusedError:
        print("No se pudo conectar al servidor.")
    except OSError:
        pass
    finally:
        s.close()
        print("Conexión cerrada.")

if __name__ == "__main__":
    funcion_cliente()