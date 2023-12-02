class socketHandler:
    def __init__(self) :
        self.ips_list = []
        self.socket = None
    
    def __str__(self):
        return "ips->" + self.ips_list + "socket->" + self.socket

    def add_socket(self,socket):
        self.socket = socket

    