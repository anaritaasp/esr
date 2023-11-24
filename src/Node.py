from Neighbours import Neighbours
import socket
from globalvars import UDP_PORT
from threading import Thread
import pickle
from Arvore import Arvore
from Packet import Packet


#classe onde tratamos das funções auxiliares aos pedidos do cliente e entrega de conteúdo
class Node:
   
    # controla a forma como os pedidos são tratados
    # cada nodo vai redirecionar conteúdo
    def __init__(self, bootstrapper_ip) :
        self.node , self.neighbours, self.own_content, self.servers =  Neighbours(bootstrapper_ip).run()  # nodos vizinhos do nosso nodo
        self.streaming = {}
        self.content = "movie.Mjpeg"
        

    # função para iniciar um pedido
    def start_dissemination(self, socket, data, content):
        self.send_to_neighbours(socket, data, ('localhost', UDP_PORT),content)

    #função responsável por encaminhar o pedido do cliente até encontrar o neighbour que tem o content
    def send_to_neighbours(self, socket, data, client_address, content): # enquanto não encontrarmos o rp, vamos enviar o pacote de nodo a nodo
        previous_path = data.path
        if(previous_path is None): previous_path = []
        previous_path.append(self.node) # adiciona o nodo à rota
        packet = Packet(data.request,previous_path,None,content)
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
            packet = Packet('tree_response', data.path, data.error, data.content)
            print(packet) #para efeitos de debug
            for addr in next_node_ips:
                print(addr)
                socket.sendto(pickle.dumps(packet), (addr,UDP_PORT))
        else:
            print('Info reached RP.')        

    def handle_response_stream(self, socket, data):
        #hop a hop de volta ao cliente

         # Verifica se o nodo atual possui o conteúdo para streaming
        if self.content == data.content:
            # Se possui o conteúdo, começa o streaming de volta ao cliente
            print(f"Initiating streaming of {data.content} to client {data.path[0]}.")

            # Obtém o caminho de retorno (traceback) do pacote de dados
            traceback_path = data.path[::-1]  # Reverte o caminho para enviar hop a hop de volta ao cliente

            # Envia o streaming hop a hop de volta ao cliente
            return_path = []
            for node in traceback_path:
                if node not in return_path:
                    # Cria um pacote com informações de streaming de volta ao cliente
                    return_path.append(node)
                    packet = Packet('response_stream', return_path, None, data.content)
                    # Envia o pacote para o próximo nodo na rota de retorno
                    socket.sendto(pickle.dumps(packet), (node, UDP_PORT))
            print("Streaming response sent to client.")
        else:
            print("Content not found in the current node.")
        
    

    def handle_request_stream(self,socket, data, client_address):
        # Se o conteúdo está presente no streaming local
        if data.content in self.streaming.values():
            # Encontramos o conteúdo, responder ao cliente com o caminho para aceitar
            self.handle_response_stream(socket, data)
        # Se não encontrou o conteúdo localmente
        else: 
            # Se for o ponto de referência (RP)
            if self.node == 'RP':
                # Obtemos a lista de servidores do bootstrap
                servers_ip_list = self.servers
                
                # Selecionamos um servidor com o conteúdo (por enquanto, use o primeiro)
                chosen_server = servers_ip_list.pop() if servers_ip_list else None
                
                if chosen_server:
                    # Confirmamos o caminho com o cliente
                    self.handle_response_stream(socket, data)
            else:
                # Se não for um servidor nem o ponto de referência (RP)
                # Encaminhamos a mensagem para os vizinhos
                self.send_to_neighbours(socket, data, client_address)
                

    def handle_request(self,socket, data, client_address):
        deserialized_data = pickle.loads(data)
        print(deserialized_data)
        if deserialized_data.request == 'request_stream':
            self.handle_request_stream(socket, deserialized_data, client_address)
        elif deserialized_data.request == 'response_stream':
            self.handle_response_stream(socket, data)
        else:
            None # TODO: handle other requests
               


    

    def run(self):
        print('Node started...')
        socket_ = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #abre socket

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

            

    

    # Um nodo envia pedido à procura do RP
    # Manda para os nodos vizinhos
    # Nodos vizinhos reenviam se não encontrarem RP
    # else fazem traceback do caminho