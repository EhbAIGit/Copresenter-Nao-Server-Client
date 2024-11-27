import socket

default_host = socket.gethostname()
default_port = 5000

# Socket connection related functions
def create_server_socket(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print("Server socket created and listening on IP {}:{} -- Waiting for the client...".format(socket.gethostbyname(host), port))
    return server_socket

def accept_connection(server_socket):
    conn, address = server_socket.accept()
    print("Client connected from: " + str(address))
    return conn, address

def close_server_connection(conn):
    conn.close()
    print("Server connection closed.")

def receive_message(conn):
    return conn.recv(1024).decode()

def send_response(conn, message):
    conn.send(message.encode())
    print(f"Sent response to client: {message}")


def initialize_socket_connection(host=default_host, port=default_port):
    server_socket = create_server_socket(host, port)
    conn, address = accept_connection(server_socket)
    return server_socket, conn, address