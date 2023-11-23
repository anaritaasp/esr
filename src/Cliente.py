import pickle
import socket
import sys
from tkinter import Tk
from ClienteGUI import ClienteGUI´
from Node import Node

# este cliente funciona localmente apenas (!!!!!)

if __name__ == "__main__":
	try:
		bootstrapper_ip = sys.argv[1]
	except:
		print("[Usage: Cliente.py <bootstrapper_ip>]\n")	
	
	root = Tk()
	
	# Create a new client
	node = Node(bootstrapper_ip)
	app = ClienteGUI(root, node)
	app.master.title("Cliente TEST")	
	root.mainloop()
	