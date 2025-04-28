class Processo:
    def __init__(self, **kwargs):
        self.__ano_inicio = kwargs.get('ano_inicio', None)
        self.__data_inicio = kwargs.get('data_inicio', None)
        self.__descricao = kwargs.get('descricao', None)
        self.__arquivado = kwargs.get('arquivado', None)
        self.__assunto = kwargs.get('assunto', None)
        self.__classe = kwargs.get('classe', None)
        self.__data_arquivamento = kwargs.get('data_arquivamento', None)
        self.__data_distribuicao = kwargs.get('data_distribuicao', None)
        self.__informacoes_complementares = kwargs.get('informacoes_complementares', None)

    def __repr__(self):
        return f"Processo(ano_inicio={self.__ano_inicio}, data_inicio={self.__data_inicio}, " \
               f"descricao={self.__descricao}, arquivado={self.__arquivado}, assunto={self.__assunto}, " \
               f"classe={self.__classe}, data_arquivamento={self.__data_arquivamento}, " \
               f"data_distribuicao={self.__data_distribuicao}, " \
               f"informacoes_complementares={self.__informacoes_complementares})"
    
    @property
    def ano_inicio(self):
        return self.__ano_inicio
    
    @property
    def data_inicio(self):
        return self.__data_inicio
    
    @property
    def descricao(self):
        return self.__descricao
    
    @property
    def arquivado(self):
        return self.__arquivado
    
    @property
    def assunto(self):
        return self.__assunto
    
    @property
    def classe(self):
        return self.__classe
    
    @property
    def data_arquivamento(self):
        return self.__data_arquivamento
    
    @property
    def data_distribuicao(self):
        return self.__data_distribuicao
    
    @property
    def informacoes_complementares(self):
        return self.__informacoes_complementares