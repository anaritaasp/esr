from Neighbours import Neighbours
import socket
from globalvars import UDP_PORT
from threading import Thread
import pickle


class Node:
    # controla a forma como os pedidos são tratados
    # cada nodo vai redirecionar conteúdo
    def __init__(self, bootstrapper_ip) :
        self.node , self.neighbours =  Neighbours(bootstrapper_ip).run()  #nodos vizinhos do nosso nodo

    def send_to_neighbours(self, udp_socket, data, client_address):
        previous_path = data['path']
        new_path = previous_path.append(self.node)
        packet = {'request':'tree', 'path':new_path}
        for _,values in self.neighbours:  #vão ser ips
            if client_address[0] not in values:
                for addr in values:
                    udp_socket.sendto(pickle.dumps(packet), addr)

            

    def handle_tree_request(self,udp_socket, data, client_address):
        if self.node == 'RP':
            None ## TODO
        else:
            self.send_to_neighbours(udp_socket, data, client_address)

    def handle_request(self,udp_socket, data, client_address):
        deserialized_data = pickle.loads(data)
        if(deserialized_data['request'] == 'tree'):
            self.handle_tree_request(udp_socket, data, client_address)
        else:
            None # TODO    


    

    def run(self):
        print('Node started...')
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #abre socket

        # Bind the socket to a specific address and port
        server_address = ('localhost', UDP_PORT)
        udp_socket.bind(server_address)

        while True:
            with udp_socket.recvfrom(1024) as (data, client_address):
                request_handler = Thread(target=self.handle_request,args=(self,udp_socket, data, client_address))
                request_handler.start()

            

    

    # Um nodo envia pedido á procura do RP
    # Manda para os nodos vizinhos
    # Nodos vizinhos reenviam se não encontrarem RP
    # else fazem traceback do caminho
        