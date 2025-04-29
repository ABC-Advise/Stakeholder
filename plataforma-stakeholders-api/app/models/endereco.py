from app import db
from app.models.base_model import BaseModel
from app.models.tipo_entidade import TipoEntidade


class Endereco(BaseModel):
    __tablename__ = 'enderecos'
    __table_args__ = {'schema': 'plataforma_stakeholders'}

    entidade_id = db.Column(db.Integer, primary_key=True)
    tipo_entidade_id = db.Column(db.SmallInteger, db.ForeignKey('plataforma_stakeholders.tipo_entidade.tipo_entidade_id'), primary_key=True)
    endereco_id = db.Column(db.SmallInteger, primary_key=True)
    logradouro = db.Column(db.String(100), nullable=True)
    numero = db.Column(db.String(8), nullable=True)
    complemento = db.Column(db.String(100), nullable=True)
    bairro = db.Column(db.String(60), nullable=True)
    cidade = db.Column(db.String(60), nullable=False)
    uf = db.Column(db.CHAR(2), nullable=False)
    cep = db.Column(db.String(8), nullable=False)
    
    tipo_entidade = db.relationship("TipoEntidade", back_populates='endereco')
    
