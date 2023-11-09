from socket import *
import threading
import sys


# function that handles client functions
# receives the client's socket 
def handle_client(client_socket, client_addr):
    while True: # as long as there's an active connection to the client
        clientmessage = client_socket.recv(1024) #receives the data from the client (maximum 1024 bytes from the client)
        if not clientmessage: #checks if the client didn't close the connection (if the message is empty)
            break
        # if the server received client's data, it's printed on the screen
        # the decode fucntion converts binary data into a readable string 
        received_message= clientmessage.decode()
        print(f"Received from client: {received_message}")
        if received_message.lower() == "exit":
            print(f"Client {client_addr[0]}:{client_addr[1]} requested to exit.")
            break
        response = input("Send to Client: ") # the server requests for a response to the client
        client_socket.send(response.encode()) # the response is encoded in bytes in order to be sent to the client
    client_socket.close() # the client's connection is closed - therefore the server closes the client's socket

# Server starter function
def initiate_server():
    server_host = "0.0.0.0"  # Escuta em todas as interfaces
    server_port = 12346
    # creates the server socket
    # 1st parameter indicates that the underlying network is using IPv4
    # 2nd parameter indicates 
    server = socket(AF_INET, SOCK_STREAM) 
    server.bind((server_host, server_port))
    server.listen(5)
    print(f"Server listening in {server_host}:{server_port}")

    while True:
        client_sock, client_addr = server.accept()
        print(f"Connection accepeted from {client_addr[0]}:{client_addr[1]}")
        client_handler = threading.Thread(target=handle_client, args=(client_sock,client_addr))
        client_handler.start()

# Client's starter function
def initiate_client():
    client_host = "10.0.1.20"
    client_port = 12346
    client = socket(AF_INET, SOCK_STREAM)
    client.connect((client_host, client_port))

    while True:
        message = input("Send to server: ")
        client.send(message.encode())
        response = client.recv(1024)
        print(f"Received from the server: {response.decode()}")

if __name__ == "__main__":
   if len(sys.argv) == 2:
        if sys.argv[1] == "servidor":
            initiate_server()
        elif sys.argv[1] == "cliente":
            initiate_client()
        else:
            print("Erro nos argumentos")
   else:
        print("Erro no número de argumentos")
