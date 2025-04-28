from app import db
from app.models.base_model import BaseModel


class TipoEntidade(BaseModel):
    __tablename__ = 'tipo_entidade'
    __table_args__ = {'schema': 'plataforma_stakeholders'}

    tipo_entidade_id = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    descricao = db.Column(db.String(40), nullable=False)
    
    endereco = db.relationship("Endereco", back_populates='tipo_entidade')
    telefone = db.relationship("Telefone", back_populates='tipo_entidade')
    email = db.relationship("Email", back_populates='tipo_entidade')