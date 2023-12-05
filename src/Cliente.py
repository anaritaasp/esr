import sys
from tkinter import Tk
from ClienteGUI import ClienteGUI

if __name__ == "__main__":
	try:
		bootstrapper_ip = sys.argv[1] 
		#content = sys.argv[2]
	except:
		print("[Usage: Cliente.py <bootstrapper_ip>]\n")	
	
	root = Tk()
	# Create a new client
	app = ClienteGUI(root, bootstrapper_ip) # trata dos pacotes RTP e abrirá a janela de streaming
	app.master.title("Client Request")	
	root.mainloop()