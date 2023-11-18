import pickle
import sys, socket

from random import randint
import sys, traceback, threading, socket

from VideoStream import VideoStream
from RtpPacket import RtpPacket
from oNode import Node

class Servidor(Node):
    def __init__(self, name, addr, port, metrica, content, estado):
        super().__init__(name, addr, port)
        self.content = content # conteudo que o server tem
        self.metrica = metrica  # a sua latencia
        self.estado = estado  # estado do server -> possivelmente none no inicio?


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
            print(f"Received from client {client_addr[0]}:{client_addr[1]}: {received_message}")
            if received_message.lower() == "exit":
                print(f"Client {client_addr[0]}:{client_addr[1]} requested to exit.")
                break
            response = input(f"Send to Client {client_addr[0]}:{client_addr[1]}: ") # the server requests for a response to the client
            client_socket.send(response.encode()) # the response is encoded in bytes in order to be sent to the client
        client_socket.close() # the client's connection is closed - therefore the server closes the client's socket

    # Server starter function
    def initiate_server(self):
        # creates the server socket
        # 1st parameter indicates that the underlying network is using IPv4
        # 2nd parameter indicates 
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        try:
            server.bind((self.ip_address, self.port))
            server.listen(5)
            print(f"Server listening on {self.ip_address}:{self.port}")

            while True:
                client_sock, client_addr = server.accept()
                print(f"Connection accepted from {client_addr[0]}:{client_addr[1]}")
                client_handler = threading.Thread(target=self.handle_client, args=(client_sock, client_addr))
                client_handler.start()

        except Exception as e:
            print(f"Error: {e}")
            server.close()
    
    # fica a espera que algum cliente se conecte e responde a pedidos de streaming        
    def serve_client(self):
            print(f"Server running at {self.addr}:{self.port}")

            while True:
                client_socket, client_addr = self.server_socket.accept()
                print(f"Connection established with {client_addr}")

                data = client_socket.recv(1024)
                data = pickle.loads(data)

                request = data.get("request")
                content = data.get("content")

                if request == "stream":
                    if content == self.content:
                        response = {"error": False, "message": f"Streaming {self.content}"}
                    else:
                        response = {"error": True, "message": "Content not found"}

                    client_socket.send(pickle.dumps(response))
                elif request == "close":
                    client_socket.close()
                    print(f"Connection closed with {client_addr}")
                    break