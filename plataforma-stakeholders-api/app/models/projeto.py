from app import db
from app.models.base_model import BaseModel

class Projeto(BaseModel):
    __tablename__ = 'projeto'
    __table_args__ = {'schema': 'plataforma_stakeholders'}
    
    projeto_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(160), nullable=True)
    descricao = db.Column(db.String, nullable=False)
    data_inicio = db.Column(db.Date, nullable=False)
    data_fim = db.Column(db.Date, nullable=False)
    
    empresa = db.relationship("Empresa", back_populates='projeto')
    pessoa = db.relationship("Pessoa", back_populates='projeto')