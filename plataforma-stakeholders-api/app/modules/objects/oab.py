class OAB:
    def __init__(self, numero, tipo, uf):
        self.__numero = numero
        self.__tipo = tipo
        self.__uf = uf

    def __repr__(self):
        return f"OAB(numero={self.__numero}, tipo='{self.__tipo}', uf='{self.__uf}')"
    
    @property
    def numero(self):
        return self.__numero
    
    @property
    def tipo(self):
        return self.__tipo
    
    @property
    def uf(self):
        return self.__uf