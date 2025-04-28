import pandas as pd

from app import db


class BaseModel(db.Model):
    """
    Classe base para todos os modelos. Inclui métodos utilitários para conversão
    para dicionário e atualização de instâncias a partir de dicionários, além de
    um construtor customizado que aceita um dicionário.
    """
    __abstract__ = True  # Não será criada uma tabela para esta classe

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_dict(self, extend=False):
        """
        Converte o objeto para um dicionário. Apenas atributos com valores do tipo `int` ou `str`
        são diretamente incluídos; os outros são convertidos para string.

        Returns:
            dict: Dicionário contendo os dados da instância.
        """
        return {
            c.name: getattr(self, c.name) if isinstance(getattr(self, c.name), (int, str))
            else str(getattr(self, c.name))
            for c in self.__table__.columns
        }

    def update_from_dict(self, data):
        """
        Atualiza os atributos da instância com base nos pares chave-valor de um dicionário fornecido.

        Args:
            data (dict): Dicionário contendo os novos valores a serem atribuídos aos atributos da instância.
        """
        # Itera sobre os itens do dicionário fornecido
        for key, value in data.items():
            # Verifica se a chave existe no modelo
            if hasattr(self, key):
                # Atualiza a propriedade usando setattr
                setattr(self, key, value)

    @staticmethod
    def to_dataframe(records, columns):
        if not records:
            return pd.DataFrame(columns=[column.name for column in columns])

        return pd.DataFrame([record.to_dict(extend=False) for record in records]).drop_duplicates()
