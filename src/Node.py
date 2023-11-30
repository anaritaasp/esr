from Neighbours import Neighbours
import socket
from globalvars import UDP_PORT, RTP_PORT
from threading import Thread
import pickle
from Arvore import Arvore
from Packet import Packet
import sys
import subprocess
from Controller import Controller

import threading


#classe onde tratamos das funções auxiliares aos pedidos do cliente e entrega de conteúdo
class Node:
   
    # controla a forma como os pedidos são tratados
    # cada nodo vai redirecionar conteúdo
    def __init__(self, bootstrapper_ip, server_stream) :
        if bootstrapper_ip == 'start':
            controller = Controller()
            controller_handler = threading.Thread(target=controller.run())
            controller_handler.start()
            bootstrapper_ip = 'localhost'
        self.node , self.neighbours, self.own_content, servers =  Neighbours(bootstrapper_ip).run()  # nodos vizinhos do nosso nodo
        self.servers = servers.copy() if servers else []
        self.streaming = {}
        self.content = "movie.Mjpeg"
        self.server_stream = server_stream
        

    # função para iniciar um pedido
    def start_dissemination(self, socket, data, content):
        self.send_to_neighbours(socket, data, ('localhost', UDP_PORT),content)

    #função responsável por encaminhar o pedido do cliente até encontrar o neighbour que tem o content
    def send_to_neighbours(self, socket, data, client_address, content): # enquanto não encontrarmos o rp, vamos enviar o pacote de nodo a nodo
        previous_path = data.path
        if(previous_path is None): previous_path = []
        previous_path.append(self.node) # adiciona o nodo à rota
        packet = Packet(data.request,previous_path, [],None,content)
        print(packet)
        for _,values in self.neighbours.items():  # vão ser ips
            if client_address[0] not in values:
                for addr in values:
                    addr2 = (addr, UDP_PORT)
                    print(addr2)
                    socket.sendto(pickle.dumps(packet), addr2)

    
    # quando chega ao rp - temos o caminho que foi feito da origem do request até ao rp e depois fazemos o traceback de volta
    # basicamente entrega o conteúdoo ao cliente - se chegou ao rp
    def handle_tree_response(self,socket, data):  
        print(data.path)
        next_node = data.path.pop()
        next_node_ips = self.neighbours[next_node]
        if data.path is not None and data.path != []:
            #packet = {'request':'tree_response','path':data['path']}
            packet = Packet('tree_response', data.path, data.reverse_path, data.error, data.content)
            print(packet) #para efeitos de debug
            for addr in next_node_ips:
                #print(addr)
                socket.sendto(pickle.dumps(packet), (addr,UDP_PORT))
        else:
            print('Info reached RP.')        

    # função que confirma com o cliente que ele aceita a conexão para envio de conteúdo
    def handle_response_stream(self, socket, data):
        #hop a hop de volta ao cliente
        # temos o path que é o caminho que foi feito do cliente até ao nodo que possui o stream ou até ao rp
        # com isso vamos dando pop de cada elemento para fazer o traceback
        if (len(data.path) > 0): # enquanto não chegarmos ao cliente
            next_node = data.path.pop()
            next_node_ips = self.neighbours[next_node]
            data.reverse_path.append(self.node) 
            packet = Packet('response_stream', data.path, data.reverse_path, data.error, data.content)
            for addr in next_node_ips:
                socket.sendto(pickle.dumps(packet), (addr,UDP_PORT))
        elif (len(data.path) == 0): #chegamos ao cliente
            #perguntamos se aceita a conexão do nodo que possui o conteúdo
            packet = Packet('stream_confirm', data.path, data.reverse_path, data.error, data.content)
            next_node = data.reverse_path.pop()
            next_node_ips = self.neighbours[next_node]
            data.path.append(self.node)
            for addr in next_node_ips:
                socket.sendto(pickle.dumps(packet), (addr,UDP_PORT))
                
                
    def handle_stream_confirm(self, socket, data):
         # o cliente já recebeu o pedido de stream e manda hop a hop até ao servidor a sua confirmação
        if len(data.reverse_path) > 0: # o caminho do cliente até ao nodo que tem o conteúdo para streamar
            next_node = data.reverse_path.pop()
            next_node_ips = self.neighbours[next_node]
            data.path.append(self.node) 
            packet = Packet('stream_confirm', data.path, data.reverse_path, data.error, data.content)
            for addr in next_node_ips:
                socket.sendto(pickle.dumps(packet), (addr,UDP_PORT))
        
        elif len(data.reverse_path) == 0: # chegamos ao nodo com o conteúdo para streamar
            next_node = data.path.pop()
            next_node_ips = self.neighbours[next_node]
            packet = Packet('stream',data.path, data.reverse_path, data.error, data.content)
            for addr in next_node_ips:
                socket.sendto(pickle.dumps(packet), (addr,UDP_PORT))
                
    def handle_stream(self, socket, data):
        # confirmamos o pedido de stream e vamos abrir a porta para iniciar o stream
        if len(data.path) > 0: # o caminho do cliente até ao nodo que tem o conteúdo para streamar
            next_node = data.path.pop()
            next_node_ips = self.neighbours[next_node]
            packet = Packet('stream', data.path, data.reverse_path, data.error, data.content)
            for addr in next_node_ips:
                socket.sendto(pickle.dumps(packet), (addr,UDP_PORT))
                
        # abrimos uma porta para iniciar o stream ---
        # ! para já só uma porta
        stream_port = RTP_PORT
        rtp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        rtp_socket.bind((socket.gethostname(), stream_port))
        # TODO receive and send RTP packets to client

    # o rp tem de ter a lista dos ips dos servidores
    # o rp vai mandar request para todos os servidores
    # e depois só os que tiverem o conteúdo é que respondem
    def content_request(self, socket, data):
        packet = Packet('content_request', None, None, data.error,data.content)
        for elem in self.servers:
            socket.sendto(pickle.dumps(packet), (elem,UDP_PORT))
    
    # pedido de stream ao servidor escolhido pelo rp
    def handle_content_request(self, socket, data, rp_addr):
        from Servidor import Servidor
        if data.content in self.own_content:
            # start streaming to rp
            self.server_stream.run_stream(rp_addr[0], RTP_PORT)

    def check_if_is_client(self):
        if self.node.startswith('C'):
            return True
        else: return False 
                
    def handle_request_stream(self,socket, data, client_address):
        # if found content, reply with path to accept?
        if data.content in self.streaming.values():
            # we've found the content
            # must reply to the client with the 
            self.handle_response_stream(socket, data)
       
        #    None
        # else redirect
    
        # if is RP
        elif self.node == 'RP':
            # we get the servers from the bootstrap
            print('name: ', self.node)
            print("servers: ", self.servers)
            servers_ip_list = self.servers
            # Select server with content
            #!------------------- FOR NOW USE THE FIRST ONE - for streaming tests purpose ------------------------------------------------------------------------------
            chosen_server= servers_ip_list.pop()
            #once we have the ip address
            # confirm path with client
            self.content_request(socket, data)
        # if its not a server nor rp
        else: 
            # it won't have content
            # forward the message to it's neighbours
            self.send_to_neighbours(socket,data, client_address, data.content)

    def handle_request(self,socket, data, client_address):
        deserialized_data = pickle.loads(data)
        print(deserialized_data)
        if deserialized_data.request == 'request_stream':
            self.handle_request_stream(socket, deserialized_data, client_address)
        elif deserialized_data.request == 'response_stream':
            self.handle_response_stream(socket, deserialized_data)
        elif deserialized_data.request == 'stream_confirm':
            self.handle_stream_confirm(socket, deserialized_data)
        elif deserialized_data.request == 'stream':
            self.handle_stream(socket,deserialized_data)
        elif deserialized_data.request == 'content_request':
            self.handle_content_request(socket, deserialized_data, client_address)
        else:
            None # TODO    

    def run(self): 
        print('Node started...')
        socket_ = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # abre socket

        # Bind the socket to a specific address and port
        server_address = ('0.0.0.0', UDP_PORT)
        socket_.bind(server_address)

        # SEND REQUEST - TEST
        
        #self.start_dissemination(socket, 'tree')
        # ----------------




        while True:
            data, client_address = socket_.recvfrom(1024)
            print(client_address)
            request_handler = Thread(target=self.handle_request,args=(socket_, data, client_address))
            request_handler.start()





if __name__ == "__main__":
    bootstrapper_ip = None
    try:
        bootstrapper_ip = sys.argv[1] 
        #content = sys.argv[2]
    except:
        print("[Usage: Node.py <bootstrapper_ip>]\n")	
    
    if bootstrapper_ip:
        (Node(bootstrapper_ip, None)).run()
    


    

    # Um nodo envia pedido à procura do RP
    # Manda para os nodos vizinhos
    # Nodos vizinhos reenviam se não encontrarem RP
    # else fazem traceback do caminho