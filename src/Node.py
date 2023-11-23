from Neighbours import Neighbours
import socket
from globalvars import UDP_PORT
from threading import Thread
import pickle
from Arvore import Arvore

#classe onde tratamos das funções auxiliares à criação da árvore
class Node:
    
    # controla a forma como os pedidos são tratados
    # cada nodo vai redirecionar conteúdo
    def __init__(self, bootstrapper_ip) :
        self.node , self.neighbours =  Neighbours(bootstrapper_ip).run()  # nodos vizinhos do nosso nodo
        print(self.node)
        if self.node == 'RP': # a árvore é iniciada quando estivermos no 'rp'
            self.tree = Arvore()

    def start_dissemination(self, socket, request):
        self.send_to_neighbours(socket, {'request':request}, ('localhost', UDP_PORT))


    def send_to_neighbours(self, socket, data, client_address): # enquanto não encontrarmos o rp, vamos enviar o pacote de nodo a nodo
        previous_path = data['path']
        if(previous_path is None): previous_path = []
        previous_path.append(self.node) # adiciona o nodo à rota
        packet = {'request':data['request'], 'path':previous_path}
        print(packet)
        for _,values in self.neighbours.items():  # vão ser ips
            if client_address[0] not in values:
                for addr in values:
                    addr2 = (addr, UDP_PORT)
                    print(addr2)
                    socket.sendto(pickle.dumps(packet), addr2)

    
    # quando chega ao rp - temos o caminho que foi feito da origem do request até ao rp e depois fazemos o traceback de volta
    # basicamente 
    def handle_tree_response(self,socket, data):  
        print(data['path'])
        next_node = data['path'].pop()
        next_node_ips = self.neighbours[next_node]
        if data['path'] is not None and data['path'] != []:
            packet = {'request':'tree_response','path':data['path']}
            print(packet)
            for addr in next_node_ips:
                print(addr)
                socket.sendto(pickle.dumps(packet), (addr,UDP_PORT))
        else:
            print('Info reached RP.')        

    # trata do pedido até ao rp
    def handle_tree_request(self,socket, data, client_address):
        print("in")
        print(self.node)
        if self.node == 'RP':
            # Add route to tree with the full list of the path
            path_copy = list(data['path'])
            self.tree.route_to_rp(path_copy, self.node)
            print(self.tree.tree)
            print(data)
            self.handle_tree_response(socket, data)
            
        else:
            self.send_to_neighbours(socket, data, client_address)

    
    def handle_stream_request(self,socket, data, client_address):
        # if found content, reply with path to accept?
        #if :
        #    None
        # else redirect
        #else:
            self.send_to_neighbours(socket,data, client_address)

    def handle_request(self,socket, data, client_address):
        deserialized_data = pickle.loads(data)
        print(deserialized_data)
        if(deserialized_data['request'] == 'tree'):
            self.handle_tree_request(socket, deserialized_data, client_address)
        elif deserialized_data['request'] == 'tree_response':
            self.handle_tree_response(socket, deserialized_data)
        elif deserialized_data['request'] == 'stream':
            self.handle_stream_request(socket, deserialized_data, client_address)
        else:
            None # TODO    


    

    def run(self):
        print('Node started...')
        socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #abre socket

        # Bind the socket to a specific address and port
        server_address = ('0.0.0.0', UDP_PORT)
        socket.bind(server_address)

        # SEND REQUEST - TEST
        self.start_dissemination(socket, 'tree')
        # ----------------


        while True:
            data, client_address = socket.recvfrom(1024)
            print(client_address)
            request_handler = Thread(target=self.handle_request,args=(socket, data, client_address))
            request_handler.start()

            

    

    # Um nodo envia pedido à procura do RP
    # Manda para os nodos vizinhos
    # Nodos vizinhos reenviam se não encontrarem RP
    # else fazem traceback do caminho