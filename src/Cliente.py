import pickle
import socket
import sys
from tkinter import Tk
from ClienteGUI import ClienteGUI
from Node import Node

#arrancamos o cliente com o ip do bootstrapper e o nome do conteúdo que quer pedir (ex:Movie.jpeg)

if __name__ == "__main__":
	try:
		bootstrapper_ip = sys.argv[1] 
		#content = sys.argv[2]
	except:
		print("[Usage: Cliente.py <bootstrapper_ip>]\n")	
	
	root = Tk()
	
	# Create a new client
	#node = Node(bootstrapper_ip, content) #vamos buscar os seus vizinhos
	node = Node(bootstrapper_ip, None) #vamos buscar os seus vizinhos
	app = ClienteGUI(root, node) #trata dos pacotes RTP e abrirá a janela de streaming
	app.master.title("Cliente Request")	
	root.mainloop()
	