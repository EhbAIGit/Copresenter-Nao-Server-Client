import socket
import threading

# Server configuration
HOST = socket.gethostname()  # Get the hostname of the machine
PORT = 5000                  # Port to listen on

def handle_client(client_socket, address):
    """Handle incoming client connection and send commands."""
    print(f"Connection established with {address}")
    try:
        while True:
            # Prompt user for input to send to the client
            command = input("Enter a command to send to the client (or type 'exit' to close the connection): ")
            if command.lower() == "exit":
                print("Closing connection with the client...")
                break
            # Send the command to the client
            client_socket.send(command.encode())
            # Wait for the client's response
            response = client_socket.recv(1024).decode()
            print(f"Response from client: {response}")
    except (socket.error, Exception) as e:
        print(f"Connection error: {e}")
    finally:
        client_socket.close()
        print(f"Connection with {address} closed.")

def start_server():
    """Start the server and listen for incoming connections."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)  # Allow up to 5 queued connections
    print(f"Server is listening on {HOST}:{PORT}...")

    while True:
        try:
            client_socket, address = server_socket.accept()
            # Handle each client in a separate thread
            client_thread = threading.Thread(target=handle_client, args=(client_socket, address))
            client_thread.start()
        except KeyboardInterrupt:
            print("Shutting down the server...")
            break
        except Exception as e:
            print(f"Server error: {e}")
    server_socket.close()

if __name__ == "__main__":
    start_server()
