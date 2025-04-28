from app.modules.objects.oab import OAB
from app.modules.utils import format_cpf

class Advogado:
    def __init__(self, **kwargs):
        self.__cnpj = kwargs.get("cnpj", None)
        self.__cpf = kwargs.get("cpf", None)
        self.__nome = kwargs.get("nome", None)
        self.__oabs = [OAB(**oab) for oab in kwargs.get("oabs", list())]
        self.__quantidade_processos = kwargs.get("quantidade_processos", None)
        self.__sufixo = kwargs.get("sufixo", None)
        self.__tipo = kwargs.get("tipo", None)
        self.__tipo_normalizado = kwargs.get("tipo_normalizado", None)
        self.__tipo_pessoa = kwargs.get("tipo_pessoa", None)
        self.__envolvidos = kwargs.get("envolvidos", None)
        self.__stakeholder = kwargs.get("stakeholder", False)
        self.__polo = kwargs.get("polo", None)
        self.__prefixo = kwargs.get("prefixo", None)

    def __repr__(self):
        return (f"Advogado(cnpj={self.cnpj}, cpf={self.cpf}, nome='{self.nome}', "
                f"oabs={self.oabs}, polo='{self.polo}', prefixo={self.prefixo}, "
                f"quantidade_processos={self.quantidade_processos}, sufixo={self.sufixo}, "
                f"tipo='{self.tipo}', tipo_normalizado='{self.tipo_normalizado}', tipo_pessoa='{self.tipo_pessoa}')")
    
    @property
    def cnpj(self):
        return self.__cnpj
    
    @property
    def cpf(self):
        return self.__cpf
    
    @property
    def nome(self):
        return self.__nome
    
    @property
    def oabs(self):
        return self.__oabs
    
    @property
    def polo(self):
        return self.__polo
    
    @property
    def prefixo(self):
        return self.__prefixo
    
    @property
    def quantidade_processos(self):
        return self.__quantidade_processos
    
    @property
    def sufixo(self):
        return self.__sufixo
    
    @property
    def tipo(self):
        return self.__tipo
    
    @property
    def tipo_normalizado(self):
        return self.__tipo_normalizado
    
    @property
    def tipo_pessoa(self):
        return self.__tipo_pessoa

    @property
    def envolvidos(self):
        return self.__envolvidos

    @envolvidos.setter
    def envolvidos(self, envolvidos):
        from app.modules.objects.pessoa_fisica import PessoaFisica
        from app.modules.objects.pessoa_juridica import PessoaJuridica

        if type(envolvidos) != list:
            return

        for envolvido in envolvidos:
            if (not isinstance(envolvido, PessoaFisica) and
                    not isinstance(envolvido, PessoaJuridica)):
                return

        self.__envolvidos = envolvidos
    
    def to_dict(self):
        """
        Transforma as propriedades da instância em um dicionário.

        Retorno:
            dict: Dicionário contendo os atributos da pessoa física.
        """
        nomes = str(self.nome).split(" ")
        firstname = nomes[0]
        lastname = " ".join(nomes[1:]) if len(nomes) > 1 else ""

        return {
            'oab': self.oabs[0].numero,
            'firstname': firstname,
            'lastname': lastname,
            'cpf': self.__cpf,
            'stakeholder': self.__stakeholder
            # 'sexo': self.sexo,
            # 'data_nascimento': self.data_nascimento,
            # 'nome_mae': self.nome_mae,
            # 'idade': self.idade
        }