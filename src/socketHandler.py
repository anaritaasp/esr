class socketHandler:
    def __init__(self) :
        self.ips_list = []
        self.socket = None
    
    def add_socket(self,socket):
        self.socket = socket

    def __str__(self):
        return "ips->" + self.ips_list + "socket->" + self.socket