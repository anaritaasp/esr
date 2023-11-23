#classe onde criamos a estrutura da árvore
class Arvore:
    # só o rp é que tem esta info
    # para saber a localização dos servers

    def __init__ (self):
        self.tree= {}

    # adiciona um nó e um dos seus vizinhos - cujo caminho é mais proximo para o rp
    def route_to_rp(self, path_until_rp, current_node):
        while path_until_rp != []: #enquanto houver nodos no caminho
            node_before_current = path_until_rp.pop()
            self.tree[node_before_current]= current_node # dos filhos para o rp

if __name__ == "__main__":
    minha_arvore = Arvore()
