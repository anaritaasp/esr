import json
from socket import *
import threading
import sys
import re
from Controller import Controller
from Neighbours import Neighbours

CONTROLLER_IP = sys.argv[1]
CONTROLLER_PORT = 12345

class Node:
    def __init__(self, name, ip_address, port):
        self.name = name # nome do nodo
        self.ip_address = ip_address
        self.port = port
        self.neighbors = []  # Lista de vizinhos
        self.parent = None  # Nó pai na árvore

    # initiates a node by connecting it to the controller
    def initiate_node(self):
        bootstrapper_socket = socket(AF_INET, SOCK_STREAM)
        bootstrapper_socket.connect((CONTROLLER_IP, CONTROLLER_PORT))
        
        request = f"GET_INFO {self.node_id}"
        bootstrapper_socket.send(request.encode())
        
        node_info = bootstrapper_socket.recv(1024).decode()
        
        self.update_info(json.loads(node_info))

        bootstrapper_socket.close()
        print(f"Node {self.node_id} connected to Bootstrapper and updated its info.")
    
    def update_info(self, node_info):
        # Atualiza as informações do Node com base nos dados fornecidos
        if self.node_id in node_info['Nodos']:
            node_data = node_info['Nodos'][self.name]
            self.ip_address = node_data    
        
    def is_ip(argument):
        # Regular expression to check if the argument is an IP address
        ip_pattern = re.compile(r'^(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.'
                            '(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.'
                            '(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.'
                            '(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)$')

        return bool(ip_pattern.match(argument))

    if __name__ == "__main__":
        if len(sys.argv) == 2:
            argumento = sys.argv[1]
            if argumento == "start": #se o arg é o start -> esse nodo passa a ser o bootstrapper e dá arranque ao controller
                controller = Controller()
                controller_handler = threading.Thread(target=controller.run())
                controller_handler.start()
            elif is_ip(argumento):
                print("bom dia")
              # o argumento é o ip do bootstrapper
              #sendo uma conexão tcp - ele sabe o ip do nodo que mandou
              #e depois retorna a lista dos seus vizinhoos
                neighbours = Neighbours(argumento)#temos de pedir ao nodo bootsrapper que nos envie a info dos nossos vizinhos
                n_handler = threading.Thread(target=neighbours.run())
                n_handler.start()
            else:
                print("Erro nos argumentos")
    else:
            print("Erro no número de argumentos")


