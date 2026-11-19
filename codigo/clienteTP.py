import socket

def funcion_cliente():
    host = "127.0.0.1"
    port = 5050
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host, port))
        print("Conectado al servidor")

        while True:
            msg = input("> ")
            s.send(msg.encode('utf-8'))
            if msg.strip().lower() == "/adios":
                break
            respuesta = s.recv(1024).decode('utf-8')
            print(respuesta)

    except ConnectionRefusedError:
        print("No se pudo conectar al servidor.")
    finally:
        s.close()
        print("Conexión cerrada.")

if __name__ == "__main__":
    funcion_cliente()