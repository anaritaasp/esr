import json
from threading import Thread
import socket
import pickle
import subprocess
import time

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
        self.latency={}
       # self.address = default_ip_address
    
    #retorna os nomes de todos os nodos. ex:[N1,N2,N3]
    def return_node_name(self):
        list=[]
        for node, addresses in self.nodos.items():
            list.append(node)
        return list

    #retorna os nodos que são servidores (começam com a letra s)
    def check_if_its_server(self):
        return [elem for elem in self.return_node_name() if elem.startswith('s') or elem.startswith('S')]

    #retorna os ips associados ao RP
    def get_the_RP(self):
        rp_info = self.nodos.get("RP", {})
        rp_ips = rp_info.get("ip", [])
        return rp_ips
        
    #dado um IP quero saber o nome do seu nodo. 
    # ex: "10.2.3.1" representa o nodo N2
    # retorna string

    def get_the_node_name(self, ip_address):
        nodo_name = None
        for nodo, info in self.nodos.items():
            addresses = info.get("ip", [])
            if ip_address in addresses:
                nodo_name = nodo
                return nodo_name
        return nodo_name


    # dado um nome de um nodo quero saber a lista dos seus IPS
    # ex: dado o nodo N2 providenciamos a lista dos seus ips ["10.2.3.1"]
    # retorna uma lista de strings

    def get_the_ips(self, node_name):
        lista_enderecos = self.nodos.get(node_name, {}).get("ip", [])
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
    def get_the_vizinhanca_ips(self, node_name):
        dict_final = {}
        lista_vizinhos= self.get_vizinhanca(node_name)
        for elem in lista_vizinhos:
            list=self.get_the_ips(elem)
            dict_final.add(elem,list)
        return dict_final




    def measure_latency(self, server_ip):
        try:
            # Corre o ping command e captura o output
            # corre o echo request do ICMP para enviar
            # o 4 significa que o ping command vai mandar 4 packets para o destino especificado
            # desta forma conseguimos obter resultados de rtt mais fiávies
            result = subprocess.run(['ping', '-c', '4', server_ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # Verifica se o ping foi bem sucedido
            if result.returncode == 0:
                # Extrai e faz parse do round-trip time do output
                lines = result.stdout.split('\n')
                if len(lines) >= 3:
                    rtt_line = lines[2].split('=')
                    if len(rtt_line) >= 2:
                        rtt_str = rtt_line[1].split()[0]
                        rtt_ms = float(rtt_str)
                        return rtt_ms
        except Exception as e:
            print(f"Error measuring latency: {e}")

        # Return None if there was an error or if the ping was unsuccessful
        return None

    def periodic_latency_checks(self):
        while True:
            rp_ip = self.get_the_RP()
            if rp_ip:
                for server_name in self.check_if_its_server():
                    server_ip = self.get_the_ips(server_name)[0]  # Assuming one IP per server
                    latency = self.measure_latency(server_ip)

                    threshold = 50  # Example threshold in milliseconds

                    if latency is not None and latency > threshold:
                        print(f"Latency to {server_name} exceeds threshold. Re-establishing connection...")
                        # Implement your re-establishment logic here

                # Print the latency data dictionary
                print("Latency data:", self.latency)

                time.sleep(60)  # Example: Check every 60 seconds
            else:
                print("RP not found. Retrying...")
                time.sleep(10)

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
        