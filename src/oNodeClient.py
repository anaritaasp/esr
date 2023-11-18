import pickle
import socket
import sys
from tkinter import Tk
from ClienteGUI import ClienteGUI
from oNode import Node

class Cliente(Node):
    def __init__(self, ip, porta):
        super().__init__(ip, porta)
        
    # Client's starter function
    def initiate_client(self):
        server_host = "10.0.0.10" # aqui para iniciar o cliente teria de se ligar ao bootstrapper certo?
        server_port = 1234
        client = socket(socket.AF_INET, socket.SOCK_STREAM)
        client.bind((self.ip_address, self.port))

        try:
            print(f"Connecting to server at {server_host}:{server_port}")
            client.connect((server_host, server_port))
            print("Connection successful!")

            while True:
                message = input("Send to server: ")
                client.send(message.encode())
                print("Message sent to server.")

                response = client.recv(1024)
                if not response:
                    print("Server closed the connection.")
                    break

                print(f"Received from the server: {response.decode()}")

        except ConnectionRefusedError:
            print(f"Error: Connection to {server_host}:{server_port} refused. Is the server running?")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            client.close()