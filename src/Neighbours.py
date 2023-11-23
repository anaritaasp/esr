from socket import *
import threading
import sys
import json
from threading import Thread
import socket
import pickle
import subprocess
import time
from Controller import Controller
from globalvars import BOOTSTRAP_PORT

#classe usada para um dado nodo pedir ao bootstrapper o dicionário dos seus vizinhos
class Neighbours: 
    
    def __init__(self, bootstrapper_ip):
        self.bootstrapper_ip = bootstrapper_ip
        #self.my_neighbours={} #dicionário dos vizinhos do nodo
    
    def run(self):
        print("Connecting to the Bootstrap")
        # Criamos o socket
        cli_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #conecta-se com o bootstrapper 
        cli_socket.connect((self.bootstrapper_ip, BOOTSTRAP_PORT))
        #o node que precisa requer que o bootstrapper lhe providencie os ips dos nodos vizinhos
        message = "Give me my neighbours"
        cli_socket.send(pickle.dumps(message))
        response = cli_socket.recv(1024)
        #faz a serialização - passa a info a bits
        deserialized_data = pickle.loads(response)
        if deserialized_data['error'] == True: #
            print("ERROR -  couldn't obtain info from bootstrap") 
            exit(-1)
        else:
            ### the dictionary is inside the data part of the handle request
            return (deserialized_data['node'],deserialized_data['data'])  

            