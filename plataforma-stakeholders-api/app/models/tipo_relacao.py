from app import db
from app.models.base_model import BaseModel


class TipoRelacao(BaseModel):
    """
    Modelo ORM para a tabela `tipo_relacao` na schema `plataforma_stakeholders`.

    Atributos:
        tipo_relacao_id (int): Identificador único para o tipo de relação.
        descricao (str): Descrição do tipo de relação.
        descricao_inversa (str): Descrição do inverso da relação
    """
    __tablename__ = 'tipo_relacao'
    __table_args__ = {'schema': 'plataforma_stakeholders'}  # Define o schema

    tipo_relacao_id = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    descricao = db.Column(db.String(20), nullable=False)
    descricao_inversa = db.Column(db.String(20), nullable=False)
