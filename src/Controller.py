import json
from threading import Thread
import socket
import pickle

SERVER_HOST = '0.0.0.0'  # Listen on all available network interfaces
SERVER_PORT = 60000  # Choose a port number

#temos de definir porta para bootstrap
#temos de definir portas para streaming

class Controller:
    
    def __init__(self, default_ip_address):
        # abrimos o ficheiro JSON
        f= open('neighbours.json')
        # devolvemos os objetos do JSON como um dicionário
        neighbours = json.load(f)
        self.nodos = neighbours.get('Nodos') #dicionário com os nodos
        self.vizinhos = neighbours.get('Adjacentes') #dicionário com os vizinhos
        self.address = default_ip_address

    #dado um IP quero saber o nome do seu nodo. 
    # ex: "10.2.3.1" representa o nodo N2
    # retorna string

    def get_the_node_name(self, ip_address):
        nodo_name = None
        for nodo, addresses in  self.nodos.items(): 
                if ip_address in addresses:
                    nodo_name = nodo 
                    return nodo_name


    # dado um nome de um nodo quero saber a lista dos seus IPS
    # ex: dado o nodo N2 providenciamos a lista dos seus ips ["10.2.3.1"]
    # retorna uma lista de strings

    def get_the_ips(self, node_name):
        lista_enderecos = []
        for nodo, addresses in self.nodos.items():
            if node_name == nodo:
                lista_enderecos = addresses
        return lista_enderecos
    
    # devolve uma lista com os nodos vizinhos do nodo que providenciamos
    # ex: dado o N2 devolvemos a sua vizinhança como ["N1","N3"]
    def get_vizinhanca(self, node_name):
        lista_vizinhos = []
        for node, neighbours in self.vizinhos.items():
            if node_name == node:
                lista_vizinhos = neighbours
        return lista_vizinhos


    def run(self):
        
        # Criamos o socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((SERVER_HOST, SERVER_PORT))
        server_socket.listen(5) # 5 clients in queue
        # Espera pela conexão e pedidos dos servidores autorizados
        while(True):
            node_name = None
             # Aceitamos conexões 
            client_socket, client_address = server_socket.accept()
            print(f"Accepted connection from {client_address}")

            # Recebemos and process data from the client
            data = client_socket.recv(1024).decode('utf-8')
            print(f"Received data: {data}")

            # Verifies if request's ip is valid in the overlay network
            node_name = self.get_the_node_name(client_address)
            if(node_name):
                # Responds with node's adjacents
                
                # Send a response back to the client
                response = "Hello, client! I received your message."
                client_socket.send(response.encode('utf-8'))

            
            # else ignores request
            # Close the client socket
            client_socket.close()
            


        