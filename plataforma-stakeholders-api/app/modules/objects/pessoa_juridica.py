from app.modules.utils import format_cnpj
from app.modules.objects.advogado import Advogado

class PessoaJuridica:
    """
    Representa uma pessoa jurídica (empresa), contendo informações sobre a empresa e seus sócios.

    Atributos:
        cnpj (str): O CNPJ da empresa.
        razao_social (str): A razão social da empresa.
        cnae_codigo (str): O código CNAE da atividade econômica principal da empresa.
        cnae_descricao (str): A descrição do CNAE da atividade econômica principal.
        data_fundacao (str): A data de fundação da empresa.
        situacao_cadastral (str): A situação cadastral da empresa (ex: ativa, inativa).
        codigo_natureza_juridica (int): O código representando a natureza jurídica da empresa.
        natureza_juridica_descricao (str): A descrição da natureza jurídica da empresa.
        natureza_juridica_tipo (str): O tipo da natureza jurídica da empresa.
        faixa_funcionarios (str): A faixa de número de funcionários da empresa (ex: 1-10, 11-50).
        quantidade_funcionarios (int): O número total de funcionários da empresa.
        faixa_faturamento (str): A faixa de faturamento anual da empresa (ex: até 1M, 1M-5M).
        matriz (bool): Indica se a empresa é a matriz (True) ou uma filial (False).
        orgao_publico (str): Informação sobre o órgão público associado, se aplicável.
        ramo (str): O ramo de atuação da empresa (ex: tecnologia, construção).
        tipo_empresa (str): O tipo de empresa (ex: privada, pública).
        ultima_atualizacao_pj (str): A data da última atualização de informações da empresa no cadastro.
        porte (str): O porte da empresa (ex: microempresa, pequena, média, grande).
        telefones (list): Lista de telefones associados à empresa.
        enderecos (list): Lista de endereços da empresa.
        emails (list): Lista de emails da empresa.
        socios (list): Lista de sócios, representados por objetos PessoaFisica.
    """

    def __init__(self, **kwargs) -> None:
        """
        Inicializa a classe PessoaJuridica com os dados fornecidos.

        Parâmetros:
            **kwargs: Um dicionário contendo os atributos da empresa. As chaves possíveis são:
                - cnpj (str): O CNPJ da empresa.
                - razaoSocial (str): A razão social da empresa.
                - nomeFantasia (str): Nome fantasia da empresa.
                - cnaeCodigo (str): O código CNAE da empresa.
                - cnaeDescricao (str): A descrição do CNAE da empresa.
                - dataFundacao (str): A data de fundação da empresa.
                - situacaoCadastral (str): A situação cadastral da empresa (ex: ativa, inativa).
                - naturezaJuridicaCodigo (int): O código representando a natureza jurídica da empresa.
                - naturezaJuridicaDescricao (str): A descrição da natureza jurídica da empresa.
                - naturezaJuridicaTipo (str): O tipo da natureza jurídica da empresa.
                - faixaFuncionarios (str): A faixa de número de funcionários da empresa (ex: 1-10, 11-50).
                - quantidadeFuncionarios (int): O número total de funcionários da empresa.
                - faixaFaturamento (str): A faixa de faturamento anual da empresa (ex: até 1M, 1M-5M).
                - matriz (bool): Indica se a empresa é a matriz (True) ou uma filial (False).
                - orgaoPublico (str): Informação sobre o órgão público associado, se aplicável.
                - ramo (str): O ramo de atuação da empresa (ex: tecnologia, construção).
                - tipoempresa (str): O tipo de empresa (ex: privada, pública).
                - ultimaAtualizacaoPJ (str): A data da última atualização de informações da empresa no cadastro.
                - porte (str): O porte da empresa (micro, pequena, média, grande).
                - telefones (list): Lista de telefones (strings) associados à empresa.
                - enderecos (list): Lista de endereços (strings) associados à empresa.
                - emails (list): Lista de emails (strings) associados à empresa.
                - socios (list): Lista de sócios, que são instâncias de PessoaFisica associadas à empresa.
        """
        self.__cnpj = kwargs.get('cnpj', None)
        self.__razao_social = kwargs.get('razaoSocial', None)
        self.__nome_fantasia = kwargs.get('nomeFantasia', None)
        self.__cnae_codigo = kwargs.get('cnaeCodigo', None)
        self.__cnae_descricao = kwargs.get('cnaeDescricao', None)
        self.__data_fundacao = kwargs.get('dataFundacao', None)
        self.__situacao_cadastral = kwargs.get('situacaoCadastral', None)
        self.__codigo_natureza_juridica = kwargs.get('naturezaJuridicaCodigo', None)
        self.__natureza_juridica_descricao = kwargs.get('naturezaJuridicaDescricao', None)
        self.__natureza_juridica_tipo = kwargs.get('naturezaJuridicaTipo', None)
        self.__faixa_funcionarios = kwargs.get('faixaFuncionarios', None)
        self.__quantidade_funcionarios = kwargs.get('quantidadeFuncionarios', None)
        self.__faixa_faturamento = kwargs.get('faixaFaturamento', None)
        self.__matriz = kwargs.get('matriz', None)
        self.__orgao_publico = kwargs.get('orgaoPublico', None)
        self.__ramo = kwargs.get('ramo', None)
        self.__tipo_empresa = kwargs.get('tipoempresa', None)
        self.__ultima_atualizacao_pj = kwargs.get('ultimaAtualizacaoPJ', None)
        self.__porte = kwargs.get('porte', None)
        self.__telefones = kwargs.get('telefones', None)
        self.__enderecos = kwargs.get('enderecos', None)
        self.__emails = kwargs.get('emails', None)
        self.__socios = kwargs.get('socios', None)
        self.__advogados = kwargs.get('advogados', list())
        self.__cnae_secundario = kwargs.get('cnaEsSecundarios', list())

    def __repr__(self):
        """
        Retorna uma representação string da empresa, mostrando o CNPJ e a razão social.

        Retorno:
            str: Uma representação simplificada da empresa (CNPJ e razão social).
        """
        return f"PessoaJuridica(cnpj={self.__cnpj}, razao_social={self.__razao_social})"

    def __eq__(self, other):
        """
        Compara duas instâncias de PessoaJuridica verificando se seus CNPJs são iguais.

        Parâmetros:
            other (PessoaJuridica): Outra instância de PessoaJuridica.

        Retorno:
            bool: Retorna True se os CNPJs forem iguais, caso contrário, False.
        """
        if isinstance(other, PessoaJuridica):
            return self.cnpj == other.cnpj
        return False

    def __hash__(self):
        """
        Retorna o hash baseado no CNPJ da empresa.

        Retorno:
            int: O valor do hash da instância com base no CNPJ.
        """
        return hash(self.cnpj)

    @property
    def cnpj(self):
        """Retorna o CNPJ da empresa."""
        return format_cnpj(self.__cnpj)

    @property
    def razao_social(self):
        """Retorna a razão social da empresa."""
        return self.__razao_social

    @property
    def nome_fantasia(self):
        return self.__nome_fantasia

    @property
    def cnae_codigo(self):
        """Retorna o código CNAE da atividade econômica principal da empresa."""
        return self.__cnae_codigo

    @property
    def cnae_descricao(self):
        """Retorna a descrição do CNAE da atividade econômica principal da empresa."""
        return self.__cnae_descricao
    
    @property
    def data_fundacao(self):
        """Retorna a data de fundação da empresa."""
        return self.__data_fundacao
    
    @property
    def situacao_cadastral(self):
        """Retorna a situação cadastral da empresa"""
        return self.__situacao_cadastral
    
    @property
    def codigo_natureza_juridica(self):
        """Retorna o código da natureza jurídica."""
        return self.__codigo_natureza_juridica

    @property
    def natureza_juridica_descricao(self):
        """Retorna a descrição da natureza jurídica."""
        return self.__natureza_juridica_descricao

    @property
    def natureza_juridica_tipo(self):
        """Retorna o tipo da natureza jurídica."""
        return self.__natureza_juridica_tipo

    @property
    def faixa_funcionarios(self):
        """Retorna a faixa de funcionários."""
        return self.__faixa_funcionarios

    @property
    def quantidade_funcionarios(self):
        """Retorna a quantidade de funcionários."""
        return self.__quantidade_funcionarios

    @property
    def faixa_faturamento(self):
        """Retorna a faixa de faturamento."""
        return self.__faixa_faturamento

    @property
    def matriz(self):
        """Retorna se a empresa é matriz (True/False)."""
        return self.__matriz

    @property
    def orgao_publico(self):
        """Retorna o órgão público, se aplicável."""
        return self.__orgao_publico

    @property
    def ramo(self):
        """Retorna o ramo da empresa."""
        return self.__ramo

    @property
    def tipo_empresa(self):
        """Retorna o tipo da empresa."""
        return self.__tipo_empresa

    @property
    def ultima_atualizacao_pj(self):
        """Retorna a última atualização PJ."""
        return self.__ultima_atualizacao_pj

    @property
    def porte(self):
        """Retorna o porte da empresa (micro, pequena, média, grande)."""
        return self.__porte

    @property
    def telefones(self):
        """Retorna uma lista de números de telefone associados à empresa."""
        return self.__telefones

    @property
    def enderecos(self):
        """Retorna uma lista de endereços associados à empresa."""
        return self.__enderecos

    @property
    def emails(self):
        """Retorna uma lista de emails associados à empresa."""
        return self.__emails

    @property
    def socios(self):
        """Retorna uma lista de sócios (instâncias de PessoaFisica) associados à empresa."""
        return self.__socios

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

    def to_dict(self):
        """
        Transforma as propriedades da instância em um dicionário.

        Retorno:
            dict: Dicionário contendo os atributos da empresa.
        """
        return {
            'cnpj': self.cnpj,
            'razao_social': self.razao_social,
            'nome_fantasia': self.nome_fantasia,
            'data_fundacao': self.__data_fundacao,
            'situacao_cadastral': self.__situacao_cadastral,
            'codigo_natureza_juridica': self.codigo_natureza_juridica,
            'natureza_juridica_descricao': self.natureza_juridica_descricao,
            'natureza_juridica_tipo': self.natureza_juridica_tipo,
            'faixa_funcionarios': self.faixa_funcionarios,
            'quantidade_funcionarios': self.quantidade_funcionarios,
            'faixa_faturamento': self.faixa_faturamento,
            'matriz': self.matriz,
            'orgao_publico': self.orgao_publico,
            'ramo': self.ramo,
            'tipo_empresa': self.tipo_empresa,
            'ultima_atualizacao_pj': self.ultima_atualizacao_pj
        }
