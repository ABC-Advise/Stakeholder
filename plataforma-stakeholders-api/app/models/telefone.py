from app import db
from app.models.base_model import BaseModel
from app.models.tipo_entidade import TipoEntidade


class Telefone(BaseModel):
    __tablename__ = 'telefone'
    __table_args__ = {'schema': 'plataforma_stakeholders'}

    entidade_id = db.Column(db.Integer, primary_key=True)
    tipo_entidade_id = db.Column(db.SmallInteger, db.ForeignKey('plataforma_stakeholders.tipo_entidade.tipo_entidade_id'), primary_key=True)
    telefone_id = db.Column(db.SmallInteger, primary_key=True)
    telefone = db.Column(db.String(16), nullable=False)
    operadora = db.Column(db.String(20), nullable=True)
    tipo_telefone = db.Column(db.String(150), nullable=False)
    whatsapp = db.Column(db.Boolean, nullable=True, default=False)

    tipo_entidade = db.relationship("TipoEntidade", back_populates='telefone')
