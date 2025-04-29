from app.modules.utils import format_cpf
from app.modules.objects.advogado import Advogado
from decimal import Decimal


class PessoaFisica:
    """
    Representa uma pessoa física, contendo informações pessoais e relacionamentos.

    Atributos:
        cpf (str): O CPF da pessoa física.
        nome (str): O nome completo da pessoa física.
        sexo (str): O sexo da pessoa física.
        data_nascimento (str): A data de nascimento da pessoa física.
        nome_mae (str): O nome da mãe da pessoa física.
        idade (int): A idade da pessoa física.
        signo (str): O signo da pessoa física.
        obito (bool): Indica se a pessoa está registrada como falecida (True) ou não (False).
        data_obito (str): A data do óbito da pessoa, caso aplicável.
        renda_estimada (float): A renda estimada da pessoa.
        pep (bool): Indica se a pessoa é uma Pessoa Exposta Politicamente (PEP).
        parentescos (list): Lista de pessoas físicas que têm algum grau de parentesco com essa pessoa.
        sociedades (list): Lista de empresas (PessoaJuridica) nas quais a pessoa tem algum tipo de sociedade.
        telefones (list): Lista de telefones da pessoa física.
        enderecos (list): Lista de endereços da pessoa física.
        emails (list): Lista de emails da pessoa física.
    """

    def __init__(self, **kwargs) -> None:
        """
        Inicializa a classe PessoaFisica com os dados fornecidos.

        Parâmetros:
            **kwargs: Um dicionário contendo os atributos da pessoa física. As chaves possíveis são:
                - cpf (str): O CPF da pessoa física.
                - nome (str): O nome completo da pessoa física.
                - sexo (str): O sexo da pessoa física.
                - dataNascimento (str): A data de nascimento da pessoa física.
                - nomeMae (str): O nome da mãe da pessoa física.
                - idade (int): A idade da pessoa física.
                - signo (str): O signo da pessoa física.
                - isObito (bool): Indica se a pessoa está registrada como falecida (True) ou não (False).
                - dataObito (str): A data do óbito da pessoa, caso aplicável.
                - rendaEstimada (float): A renda estimada da pessoa.
                - isPEP (bool): Indica se a pessoa é uma Pessoa Exposta Politicamente (PEP).
                - parentescos (list): Lista de parentes (objetos `PessoaFisica`) que têm relação de parentesco com essa pessoa.
                - sociedades (list): Lista de empresas (objetos `PessoaJuridica`) em que a pessoa tem sociedade.
                - telefones (list): Lista de telefones (strings) associados à pessoa física.
                - enderecos (list): Lista de endereços (strings) associados à pessoa física.
                - emails (list): Lista de endereços de email (strings) associados à pessoa física.
        """
        self.__cpf = kwargs.get('cpf', None)
        self.__nome = kwargs.get('nome', None)
        self.__sexo = kwargs.get('sexo', None)
        self.__data_nascimento = kwargs.get('dataNascimento', None)
        self.__nome_mae = kwargs.get('nomeMae', None)
        self.__idade = kwargs.get('idade', None)
        self.__signo = kwargs.get('signo', None)
        self.__obito = kwargs.get('isObito', None)
        self.__data_obito = kwargs.get('dataObito', None)
        self.__renda_estimada = kwargs.get('rendaEstimada', None)
        self.__pep = kwargs.get('isPEP')
        self.__parentescos = kwargs.get('parentescos', None)
        self.__sociedades = kwargs.get('sociedades', None)
        self.__telefones = kwargs.get('telefones', None)
        self.__enderecos = kwargs.get('enderecos', None)
        self.__emails = kwargs.get('emails', None)
        self.__advogados = kwargs.get('advogados', list())
        
    def __repr__(self):
        """
        Retorna uma representação string da pessoa física, mostrando o CPF e nome.

        Retorno:
            str: Uma representação simplificada da pessoa física (CPF e nome).
        """
        return f"PessoaFisica(cpf={self.__cpf}, nome={self.__nome})"

    def __eq__(self, other):
        """
        Compara duas instâncias de PessoaFisica verificando se seus CPFs são iguais.

        Parâmetros:
            other (PessoaFisica): Outra instância de PessoaFisica.

        Retorno:
            bool: Retorna True se os CPFs forem iguais, caso contrário, False.
        """
        if isinstance(other, PessoaFisica):
            return self.cpf == other.cpf
        return False

    def __hash__(self):
        """
        Retorna o hash baseado no CPF da pessoa física.

        Retorno:
            int: O valor do hash da instância com base no CPF.
        """
        return hash(self.cpf)

    @property
    def cpf(self):
        """Retorna o CPF da pessoa física."""
        return format_cpf(self.__cpf)

    @property
    def nome(self):
        """Retorna o nome completo da pessoa física."""
        return self.__nome

    @property
    def sexo(self):
        """Retorna o sexo da pessoa física."""
        return self.__sexo

    @property
    def data_nascimento(self):
        """Retorna a data de nascimento da pessoa física."""
        return self.__data_nascimento

    @property
    def nome_mae(self):
        """Retorna o nome da mãe da pessoa física."""
        return self.__nome_mae

    @property
    def idade(self):
        """Retorna a idade da pessoa física."""
        return self.__idade
    
    @property
    def signo(self):
        """Retorna o signo da pessoa física."""
        return self.__signo
    
    @property
    def obito(self):
        """Retorna o obito da pessoa física."""
        return self.__obito
    
    @property
    def data_obito(self):
        """Retorna a data de obito da pessoa física."""
        return self.__data_obito
    
    @property
    def renda_estimada(self):
        """Retorna a renda estimada da pessoa física."""
        return self.__renda_estimada
    
    @property
    def pep(self):
        """Retorna o pep da pessoa física."""
        return self.__pep

    @property
    def parentescos(self):
        """Retorna uma lista de parentescos, que são outras instâncias de PessoaFisica associadas a essa pessoa."""
        return self.__parentescos

    @property
    def sociedades(self):
        """Retorna uma lista de sociedades, que são instâncias de PessoaJuridica em que a pessoa física tem participação."""
        return self.__sociedades

    @property
    def telefones(self):
        """Retorna uma lista de números de telefone associados à pessoa física."""
        return self.__telefones

    @property
    def enderecos(self):
        """Retorna uma lista de endereços associados à pessoa física."""
        return self.__enderecos

    @property
    def emails(self):
        """Retorna uma lista de endereços de email associados à pessoa física."""
        return self.__emails

    @property
    def advogados(self):
        return self.__advogados

    @advogados.setter
    def advogados(self, advogados):
        if type(advogados) != list:
            return

        for advogado in advogados:
            if not isinstance(advogado, Advogado):
                return

        self.__advogados = advogados
        
    def format_renda(self):
        """
        Converte um valor de renda de string para um formato numérico adequado sem modificar o atributo original.
        """
        if isinstance(self.__renda_estimada, str):
            renda_formatada = self.__renda_estimada.replace('.', '').replace(',', '.')  
            try:
                return Decimal(renda_formatada)  
            except ValueError:
                return None  
        return self.__renda_estimada 
    
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
            'cpf': self.cpf,
            'firstname': firstname,
            'lastname': lastname,
            'sexo': self.sexo,
            'data_nascimento': self.data_nascimento,
            'nome_mae': self.nome_mae,
            'idade': self.idade,
            'signo': self.signo,
            'obito': self.obito,
            'data_obito': self.data_obito,
            'renda_estimada': self.format_renda(),  
            'pep': self.pep
        }
