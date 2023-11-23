# precisamos de uma classe os campos que vai armazenar o conteúdo do pacote
import uuid
class Packet:

    def __init__(self, request, path, error, content):
        self.id = uuid.uuid4() #id unico para cada pacote
        self.request = request #pedido do cliente
        self.path = path   #caminho percorrido até si
        self.error = error #se implementarmos correção de erros 
        self.content = content #conteúdo que o cliente pede
        
    def __str__(self):
        return f"ID={str(self.id)},request={self.request},path={self.path},error={self.error},content={self.content}"
