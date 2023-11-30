import threading

class ListHandler:
    def __init__(self):
        self.packet_ids = []
        self.lock = threading.Lock()
    # função que identifica um pedido com um determinado id
    # uma vez que o mesmo nodo tem várias interfaces ocorre o cenário em que temos o mesmo pedido a ser pedido várias vezes
    # de forma a garantir que tal nao acontece, adicionamos um id a cada pedido
    def add_request_id(self, id):
        self.lock.acquire()
        try:
            self.packet_ids.append(id)
        finally:
            self.lock.release()

    # função que remove um pedido do inicio da lista
    def remove_request_id(self):
        self.lock.acquire()
        try:
            self.packet_ids.pop(0)
        finally:
            self.lock.release()

    def check_if_id_exists(self, id):
        self.lock.acquire()
        try:
            if id in self.packet_ids:
                return True
            else: return False
        finally:
            self.lock.release()
        