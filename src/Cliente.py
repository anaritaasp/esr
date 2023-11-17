import pickle
import socket
import sys
from tkinter import Tk
from ClienteGUI import ClienteGUI

if __name__ == "__main__":
	try:
		addr = '127.0.0.1'
		port = 25000
	except:
		print("[Usage: Cliente.py]\n")	
	
	root = Tk()
	
	# Create a new client
	app = ClienteGUI(root, addr, port)
	app.master.title("Cliente Exemplo")	
	root.mainloop()
	
# client wants to stream so it has to notify the rp so it can give a list of the servers with the content the client asked for
def send_request_rp(self, content):
    # get the rp ip
	rp_ip = self.get_the_RP()
	# create a socket
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# connect to the rp
	sock.connect((rp_ip, self.port))
	# send the request
	sock.send(pickle.dumps({'request': 'stream', 'content': content}))
	# receive the response
	data = sock.recv(1024)
	# close the socket
	sock.close()
	# return the response
	return pickle.loads(data)