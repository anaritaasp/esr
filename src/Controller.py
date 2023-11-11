import json
from threading import Thread
import socket
import pickle

SERVER_HOST = '0.0.0.0'  # Listen on all available network interfaces
SERVER_PORT = 60000  # Choose a port number
STREAM={'movie.Mjpeg':61000}
#temos de definir porta para bootstrap
#temos de definir portas para streaming

class Controller:
    
    def __init__(self):
        # abrimos o ficheiro JSON
        f= open('neighbours.json')
        # devolvemos os objetos do JSON como um dicionário
        neighbours = json.load(f)
        self.nodos = neighbours.get('Nodos') #dicionário com os nodos
        self.vizinhos = neighbours.get('Adjacentes') #dicionário com os vizinhos
       # self.address = default_ip_address
    

    def return_node_name(self):
        list=[]
        for node, addresses in self.nodos.items():
            list.append(node)
        return list

    def check_if_its_server(self):
        return [elem for elem in self.return_node_name() if elem.startswith('s') or elem.startswith('S')]

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

    # se um dado nodo tiver uma dada vizinhança pretendemos obter um dicionário com o match de ips da sua vizinhança associada a cada nodo
    # ex: se a vizinhança de N2 for  ["N1","N3"] queremos ter um dicionário tipo {N1:[10.0.0.1,10.0.0.2], N3:[10.0.0.3,10.0.0.4]}
    def get_the_vizinhanca_ips(self, none_name):
        dict_final = {}
        lista_vizinhos= self.get_vizinhanca(none_name)
        for elem in lista_vizinhos:
            list=self.get_the_ips(elem)
            dict_final.add(elem,list)
        return dict_final

    def handle_request(self, client_socket, client_address):
        node_name = None

        # Receive and process data from the client
        data = client_socket.recv(1024).decode('utf-8')
        print(f"Received data: {data}")

        # Verifies if request's ip is valid in the overlay network
        node_name = self.get_the_node_name(client_address)
        if(node_name):
            # Responds with node's adjacents
            data = self.get_the_vizinhanca_ips(node_name)
            serialized_data = pickle.dumps(data)
            # Send a response back to the client
            client_socket.send(serialized_data)
        
        # else ignores request
        # Close the client socket
        client_socket.close()


    def run(self):
        print ("Starting the Bootstrap")
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



            
            

if __name__ == '__main__':
    Controller().run()
        