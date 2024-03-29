from tkinter import *
import tkinter.messagebox
from PIL import Image, ImageTk
import socket, threading, os
from globalvars import RTP_PORT
from Node import Node
from Packet import Packet

from RtpPacket import RtpPacket

CACHE_FILE_NAME = "cache-"
CACHE_FILE_EXT = ".jpg"

class ClienteGUI:
	
	
	# Initiation..
	def __init__(self, master, bootstrapper_ip):
		self.node = Node(bootstrapper_ip, None) #vamos buscar os seus vizinhos
		threading.Thread(target=self.node.run, args=()).start()
		self.master = master
		self.master.protocol("WM_DELETE_WINDOW", self.handler)
		self.createWidgets()
		self.addr = '0.0.0.0'
		self.port = RTP_PORT
		self.rtspSeq = 0
		self.sessionId = 0
		self.requestSent = -1
		self.teardownAcked = 0
		
		self.request_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		packet = Packet('request_stream',[],[],None,'movie.Mjpeg')
		self.node.start_dissemination(self.request_socket,packet,'movie.Mjpeg')
		#request_socket.shutdown(socket.SHUT_RDWR)
		#request_socket.close()

		

		self.openRtpPort()
		self.playMovie()
		self.frameNbr = 0
		
	def createWidgets(self):
		"""Build GUI."""
		# Create Setup button
		self.setup = Button(self.master, width=20, padx=3, pady=3)
		self.setup["text"] = "Setup"
		self.setup["command"] = self.setupMovie
		self.setup.grid(row=1, column=0, padx=2, pady=2)
		
		# Create Play button		
		self.start = Button(self.master, width=20, padx=3, pady=3)
		self.start["text"] = "Play"
		self.start["command"] = self.playMovie
		self.start.grid(row=1, column=1, padx=2, pady=2)
		
		# Create Pause button			
		self.pause = Button(self.master, width=20, padx=3, pady=3)
		self.pause["text"] = "Pause"
		self.pause["command"] = self.pauseMovie
		self.pause.grid(row=1, column=2, padx=2, pady=2)
		
		# Create Teardown button
		self.teardown = Button(self.master, width=20, padx=3, pady=3)
		self.teardown["text"] = "Teardown"
		self.teardown["command"] =  self.exitClient
		self.teardown.grid(row=1, column=3, padx=2, pady=2)
		
		# Create a label to display the movie
		self.label = Label(self.master, height=19)
		self.label.grid(row=0, column=0, columnspan=4, sticky=W+E+N+S, padx=5, pady=5) 
	
	def setupMovie(self):
		"""Setup button handler."""
		print("Not implemented...")
	
	def exitClient(self):
		"""Teardown button handler."""
		self.master.destroy() # Close the gui window
		# Close stream
		try:
			packet = Packet('close_stream',[],[],None,'movie.Mjpeg')
			self.node.start_dissemination(self.request_socket,packet,'movie.Mjpeg')
		finally:	
			self.request_socket.shutdown(socket.SHUT_RDWR)
			self.request_socket.close()
		os.remove(CACHE_FILE_NAME + str(self.sessionId) + CACHE_FILE_EXT) # Delete the cache image from video

	def pauseMovie(self):
		"""Pause button handler."""
		self.playEvent.set()
	
	def playMovie(self):
		"""Play button handler."""
		self.playEvent = threading.Event()
		# Create a new thread to listen for RTP packets
		threading.Thread(target=self.listenRtp).start()
		self.playEvent.clear()
	
	def listenRtp(self):		
		"""Listen for RTP packets."""
		while True:
			try:
				# Stop listening upon requesting PAUSE or TEARDOWN
				if self.playEvent.isSet(): 
					break
 
				data = self.rtpSocket.recv(20480)
				if data:
					rtpPacket = RtpPacket()
					rtpPacket.decode(data)
					
					currFrameNbr = rtpPacket.seqNum()
					print("Current Seq Num: " + str(currFrameNbr))
	
					if currFrameNbr > self.frameNbr: # Discard the late packet
						self.frameNbr = currFrameNbr
						self.updateMovie(self.writeFrame(rtpPacket.getPayload()))
			except:
				# Stop listening upon requesting PAUSE or TEARDOWN
				if self.playEvent.isSet(): 
					break
				
				self.rtpSocket.shutdown(socket.SHUT_RDWR)
				self.rtpSocket.close()
				break
				
	
	def writeFrame(self, data):
		"""Write the received frame to a temp image file. Return the image file."""
		cachename = CACHE_FILE_NAME + str(self.sessionId) + CACHE_FILE_EXT
		file = open(cachename, "wb")
		file.write(data)
		file.close()
		
		return cachename
	
	def updateMovie(self, imageFile):
		"""Update the image file as video frame in the GUI."""
		try:
			photo = ImageTk.PhotoImage(Image.open(imageFile))
			self.label.configure(image = photo, height=288) 
			self.label.image = photo
		except OSError as e:
			# Log the error
			print(f"Error loading image: {e}")
			# Optionally, provide a default image or skip processing
		
	
	def openRtpPort(self):
		"""Open RTP socket binded to a specified port."""
		# Create a new datagram socket to receive RTP packets from the server
		self.rtpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		
		# Set the timeout value of the socket to 0.5sec
		self.rtpSocket.settimeout(15)
		print("Waiting for stream... 15 second timeout")
		
		try:
			# Bind the socket to the address using the RTP port
			self.rtpSocket.bind((self.addr, self.port))
			print('\nBind \n')
		except:
			tkinter.messagebox.messagebox.showwarning('Unable to Bind', 'Unable to bind PORT=%d' %self.rtpPort)

	def handler(self):
		"""Handler on explicitly closing the GUI window."""
		self.pauseMovie()
		if tkinter.messagebox.messagebox.askokcancel("Quit?", "Are you sure you want to quit?"):
			self.exitClient()
		else: # When the user presses cancel, resume playing.
			self.playMovie()