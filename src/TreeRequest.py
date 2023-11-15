from socket import *
import threading
import sys

class TreeRequest: 
    
    def send_request(self, client_socket, client_address):
        node_name = None

        # Recebe e processa dados do cliente
        data = client_socket.recv(1024).decode('utf-8')
        print(f"Received data: {data}")

        # Verifica se o request's ip é valido na overlay network
        node_name = self.get_the_node_name(client_address)
        if(node_name):
            # Responde com os nodos adjacentes
            data = self.get_the_vizinhanca_ips(node_name)
            print(data)
            serialized_data = pickle.dumps(data) 
            # Envia a resposta de volta ao cliente
            client_socket.send(serialized_data)
        
        # caso ignore o request
        # fecha o client socket
        client_socket.close()
    
    
    def run(self):
        print ("Connecting to the Bootstrap")
        # Criamos o socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((SERVER_HOST, SERVER_PORT))
        server_socket.listen(5) # 5 clients in queue
        # Espera pela conexão e pedidos dos servidores autorizados
        while(True):
            client_sock, client_addr = server_socket.accept()
            print(f"Connection accepted from {client_addr[0]}:{client_addr[1]}")
            client_handler = Thread(target=self.handle_request, args=(client_sock, client_addr))
            client_handler.start()
            