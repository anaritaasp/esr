from Neighbours import Neighbours
import socket
from globalvars import UDP_PORT, RTP_PORT
import threading
import pickle
from Packet import Packet
import sys
import subprocess
from Controller import Controller
from ListHandler import ListHandler as LH
import threading
from socketHandler import socketHandler
import subprocess
import re
import netifaces
from concurrent.futures import ThreadPoolExecutor




#classe onde tratamos das funções auxiliares aos pedidos do cliente e entrega de conteúdo
class Node:

    # controla a forma como os pedidos são tratados
    # cada nodo vai redirecionar conteúdo
    def __init__(self, bootstrapper_ip, server_stream) :
        if bootstrapper_ip == 'start':
            controller = Controller()
            controller_handler = threading.Thread(target=controller.run,args=())
            controller_handler.start()
            try:
                addresses = netifaces.ifaddresses('eth0')
                bootstrapper_ip = addresses[netifaces.AF_INET][0]['addr']
            except (KeyError, ValueError, IndexError):
                print(f"Error getting IP address for interface eth0")
                bootstrapper_ip = 'localhost'  # Return 'localhost' as a default value

        self.node , self.neighbours, self.own_content, self.servers =  Neighbours(bootstrapper_ip).run()  # nodos vizinhos do nosso nodo
        self.instream = None
        self.streaming = {}
        self.content = "movie.Mjpeg"
        self.server_stream = server_stream
        self.packet_ids = LH()
        self.executor = ThreadPoolExecutor(max_workers=10) # pool de threads para melhorar o controlo de fluxo
        # Define a lock for synchronization
        self.streaming_lock = threading.Lock()


    # verificamos se existe um pacote com o mesmo id, se não existe ele adiciona à lista de ids e continua o processo de pedir
    def control_ids(self, id):
        if self.packet_ids.check_if_id_exists(id) == False:
            self.packet_ids.add_request_id(id) # se não existir adicionamos à lista
            return True
        else: return False # caso contrário, já não faz o pedido

    # função para iniciar um pedido
    def start_dissemination(self, socket, data, content):
        self.send_to_neighbours(socket, data, ('localhost', UDP_PORT),content)

    #função responsável por encaminhar o pedido do cliente até encontrar o neighbour que tem o content
    def send_to_neighbours(self, socket, data, client_address, content): # enquanto não encontrarmos o rp, vamos enviar o pacote de nodo a nodo
        previous_path = data.path
        if(previous_path is None): previous_path = []
        previous_path.append(self.node) # adiciona o nodo à rota
        packet = Packet(data.request,previous_path, [],None,content)
        print('Sending to neighbours')
        for node,values in self.neighbours.items():  # vão ser ips
            if client_address[0] not in values:
                print('Sending to', node)
                for addr in values:
                    addr2 = (addr, UDP_PORT)
                    #print(addr2)
                    socket.sendto(pickle.dumps(packet), addr2)

    
    # função que confirma com o cliente que ele aceita a conexão para envio de conteúdo
    def handle_response_stream(self, socket, data, client_addr):
        #hop a hop de volta ao cliente
        # temos o path que é o caminho que foi feito do cliente até ao nodo que possui o stream ou até ao rp
        # com isso vamos dando pop de cada elemento para fazer o traceback
        if (len(data.path) > 0): # enquanto não chegarmos ao cliente
            next_node = data.path.pop()
            next_node_ips = self.neighbours[next_node]
            data.reverse_path.append(self.node) 
            packet = Packet('response_stream', data.path, data.reverse_path, data.error, data.content)
            print("Sending ", packet.request, " to ", next_node)
            for addr in next_node_ips:
                socket.sendto(pickle.dumps(packet), (addr,UDP_PORT))
        elif (len(data.path) == 0): #chegamos ao cliente
            #perguntamos se aceita a conexão do nodo que possui o conteúdo
            next_node = data.reverse_path.pop()
            next_node_ips = self.neighbours[next_node]
            data.path.append(self.node)
            packet = Packet('stream_confirm', data.path, data.reverse_path, data.error, data.content)
            print("Sending ", packet.request, " to ", next_node)
            for addr in next_node_ips:
                socket.sendto(pickle.dumps(packet), (addr,UDP_PORT))
                
                
    def handle_stream_confirm(self, socket, data, client_addr):
        self.streaming_lock.acquire()
        try:
            stream_info = self.streaming.get(data.content, None)
            if stream_info is None:
                self.streaming[data.content] = socketHandler()
            if client_addr[0] not in [t[0] for t in self.streaming[data.content].ips_list]:
                self.streaming[data.content].ips_list.append((client_addr[0],RTP_PORT))
        finally:
            self.streaming_lock.release()        
         # o cliente já recebeu o pedido de stream e manda hop a hop até ao servidor a sua confirmação
        if len(data.reverse_path) > 0: # o caminho do cliente até ao nodo que tem o conteúdo para streamar
            next_node = data.reverse_path.pop()
            next_node_ips = self.neighbours[next_node]
            data.path.append(self.node) 
            packet = Packet('stream_confirm', data.path, data.reverse_path, data.error, data.content)
            print("Sending ", packet.request, " to ", next_node)
            for addr in next_node_ips:
                socket.sendto(pickle.dumps(packet), (addr,UDP_PORT))
        
        elif len(data.reverse_path) == 0: # chegamos ao nodo com o conteúdo para streamar
            next_node = data.path.pop()
            next_node_ips = self.neighbours[next_node]
            packet = Packet('stream',data.path, data.reverse_path, data.error, data.content)
            print("Sending ", packet.request, " to ", next_node)
            for addr in next_node_ips:
                socket.sendto(pickle.dumps(packet), (addr,UDP_PORT))
            self.redirect_stream(data)

    # já chegou a confirmação ao nodo que tem a stream e ele responde com tá tudo pronto para streamar   
    def handle_stream(self, socket_, data):
        # confirmamos o pedido de stream e vamos abrir a porta para iniciar o stream
        if len(data.path) > 0: # o caminho do cliente até ao nodo que tem o conteúdo para streamar
            next_node = data.path.pop()
            next_node_ips = self.neighbours[next_node]
            packet = Packet('stream', data.path, data.reverse_path, data.error, data.content)
            print("Sending ", packet.request, " to ", next_node)
            for addr in next_node_ips:
                socket_.sendto(pickle.dumps(packet), (addr,UDP_PORT))
            self.redirect_stream(data)
           

    def redirect_stream(self, data):
        # abrimos uma porta para iniciar o stream ---
        stream_info = self.streaming.get(data.content, None)
        if stream_info:    
            if stream_info.socket is None:
                self.streaming[data.content].socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.streaming[data.content].socket.bind(('0.0.0.0', RTP_PORT))
                print('RTP socket open - ', self.streaming[data.content].socket.getsockname())

                rtp_socket = self.streaming[data.content].socket
                
                _, addr = rtp_socket.recvfrom(20480)
                self.streaming_lock.acquire()
                if self.instream is None:
                    self.instream = addr[0]
                self.streaming_lock.release()
                # temos que redirecionar os pacotes
                while True:
                    try:
                    # como len é > 0 ainda nao tamos no cliente
                        rtp_packet, addr = rtp_socket.recvfrom(20480)
                        #print(rtp_packet)
                        self.streaming_lock.acquire()
                        if rtp_packet and self.instream == addr[0]:
                            #print(self.streaming[data.content])
                            for ip in self.streaming[data.content].ips_list:
                                self.streaming[data.content].socket.sendto(rtp_packet, ip)
                    finally:
                        self.streaming_lock.release()

    
    def handle_close_stream(self, socket, data, addr):
        #print(self.server_stream)
        if self.server_stream is not None:
            self.server_stream.stop_stream()
        else:      
            self.streaming_lock.acquire()
            # in case node is streaming, close corresponding content's stream
            curr_content_streaming = self.streaming.get(data.content,None)
            
            if curr_content_streaming and (addr[0], RTP_PORT) in curr_content_streaming.ips_list:
                #print(curr_content_streaming.ips_list)
                index = [t[0] for t in curr_content_streaming.ips_list].index(addr[0])
                #print(index)
                curr_content_streaming.ips_list.pop(index)
                #print(curr_content_streaming.ips_list)\
                # if no clients to stream to, close stream and warn other nodes
                if len(curr_content_streaming.ips_list) == 0:
                    self.send_to_neighbours(socket, data, addr, data.content)
                    self.instream = None
                    if self.node == 'RP':
                        # if RP, send to server a request to stop the stream
                        _, sv_addr = curr_content_streaming.socket.recvfrom(20480)
                        packet = Packet('close_stream', [], [], data.error, data.content)
                        print("Sending ", packet.request, " to ", sv_addr)
                        socket.sendto(pickle.dumps(packet), (sv_addr[0],UDP_PORT))
                    try:
                        curr_content_streaming.socket.shutdown(socket.SHUT_RDWR)
                        curr_content_streaming.socket.close()
                    except socket.error as e:
                        print(f"Error while closing the socket: {e}")  
            self.streaming_lock.release()
            
        
    # o rp tem de ter a lista dos ips dos servidores
    # o rp vai mandar request para todos os servidores
    # e depois só os que tiverem o conteúdo é que respondem
    def content_request(self, socket, data, chosen_server):
        packet = Packet('content_request', None, None, data.error,data.content)
        #print("Sending ", packet.request, " to servers")
        #for elem in self.servers:
        print("Sending ", packet.request, " to ", chosen_server)
        socket.sendto(pickle.dumps(packet), (chosen_server,UDP_PORT))
    
    # pedido de stream ao servidor escolhido pelo rp
    def handle_content_request(self, data, rp_addr):
        if data.content in self.own_content:
            # start streaming to rp
            print("Starting stream to ", rp_addr[0])
            self.server_stream.run_stream(rp_addr[0], RTP_PORT)

    def check_if_is_client(self):
        if self.node.startswith('C'):
            return True
        else: return False 

    def ping_server(self,server):
        try:
            # Run the ping command and capture the output
            result = subprocess.run(['ping', '-c', '4', server], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10)
            
            # Check if the ping was successful
            if result.returncode == 0:
                # Extract and return the average latency from the ping output
                match = re.search(r'rtt min/avg/max/mdev = [\d.]+/([\d.]+)/[\d.]+/[\d.]+ ms', result.stdout)
                if match:
                    return float(match.group(1))
        except subprocess.TimeoutExpired:
            print(f"Timeout: Could not ping {server}")
        except Exception as e:
            print(f"Error pinging {server}: {e}")

        return sys.maxsize  # Return a large value for servers that couldn't be pinged
           
    def handle_request_stream(self,socket, data, client_address):
        # if found content, reply with path to accept?
        self.streaming_lock.acquire()
        if data.content in self.streaming.keys():
            self.streaming_lock.release()
            # we've found the content
            # must reply to the client with the 
            self.handle_response_stream(socket, data, client_address)
        else: 
            self.streaming_lock.release()
            if self.node == 'RP':
                # we get the servers from the bootstrap
                servers_ip_list = self.servers.copy()
                # Select server with content
                #mandamos ping para todos os ips na lista de ips com conteudo e guardamos o 
                #chosen_server= servers_ip_list.pop()
                best_latency= sys.maxsize
                for ip in servers_ip_list:
                    latency = self.ping_server(ip)
                    if latency < best_latency:
                        best_latency = latency
                        chosen_server = ip
                
                # send content request to server
                self.streaming_lock.acquire()
                if data.content not in self.streaming.keys() and self.instream is None:
                    self.streaming_lock.release()
                    self.content_request(socket, data, chosen_server)
                else: self.streaming_lock.release()
                #once we have the ip address
                # confirm path with client
                next_node = data.path.pop()
                next_node_ips = self.neighbours[next_node]
                data.reverse_path.append(self.node) 
                packet = Packet('response_stream', data.path, data.reverse_path, data.error, data.content)
                print("Sending ", packet.request, " to ", next_node)
                for addr in next_node_ips:
                    socket.sendto(pickle.dumps(packet), (addr,UDP_PORT))
            # if its not a server nor rp
            else: 
                # it won't have content
                # forward the message to it's neighbours
                self.send_to_neighbours(socket,data, client_address, data.content)

    def handle_request(self,socket, data, client_address):
        deserialized_data = pickle.loads(data)
        if self.control_ids(deserialized_data.id):
            print("-----\nPacket received from ", client_address, " -> ",deserialized_data, "\n-----")
            if deserialized_data.request == 'request_stream':
                self.handle_request_stream(socket, deserialized_data, client_address) # pedido cliente
            elif deserialized_data.request == 'response_stream':
                self.handle_response_stream(socket, deserialized_data, client_address) # tem o conteudo devolve ao cliente hop a hop
            elif deserialized_data.request == 'stream_confirm':
                self.handle_stream_confirm(socket, deserialized_data,client_address) # cliente confirma o caminho
            elif deserialized_data.request == 'stream':
                self.handle_stream(socket,deserialized_data) # 
            elif deserialized_data.request == 'content_request':
                self.handle_content_request(deserialized_data, client_address)
            elif deserialized_data.request == 'close_stream':
                self.handle_close_stream(socket, deserialized_data, client_address)
            else:
                None # TODO 
        sys.stdout.flush()   

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
            print("Received packet from ", client_address)
            # Utilização do ThreadPoolExecutor para processar solicitações
            self.executor.submit(self.handle_request, socket_, data, client_address)
            #request_handler = Thread(target=self.handle_request,args=(socket_, data, client_address))
            #request_handler.start()


if __name__ == "__main__":
    bootstrapper_ip = None
    try:
        bootstrapper_ip = sys.argv[1] 
        #content = sys.argv[2]
    except:
        print("[Usage: Node.py <bootstrapper_ip>]\n")	
    
    if bootstrapper_ip:
        (Node(bootstrapper_ip, None)).run()
    
