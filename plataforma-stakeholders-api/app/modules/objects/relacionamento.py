class Relacionamento:
    def __init__(self, entidade_1, entidade_2, tipo_relacionamento):
        """
        Representa um relacionamento entre duas entidades (PessoaFisica ou PessoaJuridica).
        :param entidade_1: A primeira entidade (PessoaFisica ou PessoaJuridica)
        :param entidade_2: A segunda entidade (PessoaFisica ou PessoaJuridica)
        :param tipo_relacionamento: O tipo de relacionamento (Ex: "Sócio", "Pai", "Filho", "Parente")
        """
        self.entidade_1 = entidade_1
        self.entidade_2 = entidade_2
        self.tipo_relacionamento = tipo_relacionamento

    def __repr__(self):
        return f"Relacionamento({self.entidade_1}, {self.entidade_2}, {self.tipo_relacionamento})"
