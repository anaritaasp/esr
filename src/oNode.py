import json
from socket import *
import threading
import sys
from Controller import Controller

    
controller_instance = Controller()

class Node:
    def __init__(self, ip_address):
        self.ip_address = ip_address
        self.adjacent_nodes = []

    def load_from_bootstrap(self):
        node_name = controller_instance.get_the_node_name(self.ip_address)
        self.adjacent_nodes = controller_instance.get_the_vizinhanca_ips(node_name)


    def get_ip_address(self):
        return self.ip_address

    def get_adjacent_nodes(self):
        return self.adjacent_nodes


# function that handles client functions
# receives the client's socket 
def handle_client(client_socket, client_addr):
    while True: # as long as there's an active connection to the client
        clientmessage = client_socket.recv(1024) #receives the data from the client (maximum 1024 bytes from the client)
        if not clientmessage: #checks if the client didn't close the connection (if the message is empty)
            break
        # if the server received client's data, it's printed on the screen
        # the decode fucntion converts binary data into a readable string 
        received_message = clientmessage.decode()
        print(f"Received from client {client_addr[0]}:{client_addr[1]}: {received_message}")
        if received_message.lower() == "exit":
            print(f"Client {client_addr[0]}:{client_addr[1]} requested to exit.")
            break
        response = input(f"Send to Client {client_addr[0]}:{client_addr[1]}: ") # the server requests for a response to the client
        client_socket.send(response.encode()) # the response is encoded in bytes in order to be sent to the client
    client_socket.close() # the client's connection is closed - therefore the server closes the client's socket


# Server starter function
def initiate_server():
    server_host = "10.0.0.10"  # Escuta em todas as interfaces
    server_port = 1234
    # creates the server socket
    # 1st parameter indicates that the underlying network is using IPv4
    # 2nd parameter indicates 
    server = socket(AF_INET, SOCK_STREAM) 
    try:
        server.bind((server_host, server_port))
        server.listen(5)
        print(f"Server listening on {server_host}:{server_port}")

        while True:
            client_sock, client_addr = server.accept()
            print(f"Connection accepted from {client_addr[0]}:{client_addr[1]}")
            client_handler = threading.Thread(target=handle_client, args=(client_sock, client_addr))
            client_handler.start()

    except Exception as e:
        print(f"Error: {e}")
        server.close()

# Client's starter function
def initiate_client():
    server_host = "10.0.0.10"
    server_port = 1234
    client = socket(AF_INET, SOCK_STREAM)

    try:
        print(f"Connecting to server at {server_host}:{server_port}")
        client.connect((server_host, server_port))
        print("Connection successful!")

        while True:
            message = input("Send to server: ")
            client.send(message.encode())
            print("Message sent to server.")

            response = client.recv(1024)
            if not response:
                print("Server closed the connection.")
                break

            print(f"Received from the server: {response.decode()}")

    except ConnectionRefusedError:
        print(f"Error: Connection to {server_host}:{server_port} refused. Is the server running?")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()
    


if __name__ == "__main__":
   if len(sys.argv) == 2:
        if sys.argv[1] == "servidor":
            initiate_server()
        elif sys.argv[1] in controller_instance.check_if_its_server():
            initiate_server()
        elif sys.argv[1] == "cliente":
            initiate_client()
        elif sys.argv[1] in controller_instance.return_node_name():
            initiate_client()
        else:
            print("Erro nos argumentos")
   else:
        print("Erro no número de argumentos")
