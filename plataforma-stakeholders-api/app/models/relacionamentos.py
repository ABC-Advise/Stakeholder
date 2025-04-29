from app import db
from app.models.base_model import BaseModel
from app.models.tipo_relacao import TipoRelacao
from app.models.tipo_entidade import TipoEntidade  # Certifique-se de importar a classe correta para TipoEntidade


class Relacionamentos(BaseModel):
    """
    Modelo ORM para a tabela `relacionamentos` na schema `plataforma_stakeholders`.

    Atributos:
        entidade_origem_id (int): ID da entidade de origem.
        tipo_origem_id (int): ID do tipo de origem da entidade.
        entidade_destino_id (int): ID da entidade de destino.
        tipo_destino_id (int): ID do tipo de destino da entidade.
        tipo_relacao_id (int): ID do tipo de relação.
        tipo_relacao_inversa_id (int): ID do tipo de relação inversa.
    """
    __tablename__ = 'relacionamentos'
    __table_args__ = {'schema': 'plataforma_stakeholders'}

    entidade_origem_id = db.Column(db.Integer, primary_key=True)
    tipo_origem_id = db.Column(db.SmallInteger, db.ForeignKey('plataforma_stakeholders.tipo_entidade.tipo_entidade_id'), primary_key=True)
    entidade_destino_id = db.Column(db.Integer, primary_key=True)
    tipo_destino_id = db.Column(db.SmallInteger, db.ForeignKey('plataforma_stakeholders.tipo_entidade.tipo_entidade_id'), primary_key=True)
    tipo_relacao_id = db.Column(db.SmallInteger, db.ForeignKey('plataforma_stakeholders.tipo_relacao.tipo_relacao_id'), nullable=False)

    tipo_relacao = db.relationship("TipoRelacao", foreign_keys=[tipo_relacao_id], backref="relacionamentos_relacao")
    tipo_origem = db.relationship("TipoEntidade", foreign_keys=[tipo_origem_id], backref="relacionamentos_origem")
    tipo_destino = db.relationship("TipoEntidade", foreign_keys=[tipo_destino_id], backref="relacionamentos_destino")
