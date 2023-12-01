import pickle
import socket
import sys
from tkinter import Tk
from ClienteGUI import ClienteGUI
from Node import Node
import threading

if __name__ == "__main__":
	try:
		bootstrapper_ip = sys.argv[1] 
		#content = sys.argv[2]
	except:
		print("[Usage: Cliente.py <bootstrapper_ip>]\n")	
	
	root = Tk()
	# Create a new client
	#node = Node(bootstrapper_ip, content) #vamos buscar os seus vizinhos
	app = ClienteGUI(root, bootstrapper_ip) # trata dos pacotes RTP e abrirá a janela de streaming
	#node.add_client(app)
	app.master.title("Client Request")	
	#threading.Thread(target=root.mainloop, args=()).start()
	root.mainloop()