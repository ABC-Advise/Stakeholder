from app import db
from app.models.base_model import BaseModel
from app.models.projeto import Projeto

class Pessoa(BaseModel):
    __tablename__ = 'pessoa'
    __table_args__ = {'schema': 'plataforma_stakeholders'}

    pessoa_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    firstname = db.Column(db.String(40), nullable=False)
    lastname = db.Column(db.String(80), nullable=False)
    cpf = db.Column(db.String(11), nullable=False)
    linkedin = db.Column(db.String(20), nullable=True)
    instagram = db.Column(db.String(20), nullable=True)
    stakeholder = db.Column(db.Boolean, nullable=False, default=False)
    em_prospecao = db.Column(db.Boolean, nullable=False, default=False)
    pep = db.Column(db.Boolean, nullable=True, default=False)
    sexo = db.Column(db.String(20), nullable=True)
    data_nascimento = db.Column(db.String(20), nullable=True)
    nome_mae = db.Column(db.String(255), nullable=True)
    idade = db.Column(db.Integer, nullable=True)
    signo = db.Column(db.String(35), nullable=True)
    obito = db.Column(db.Boolean, nullable=True, default=False)
    data_obito = db.Column(db.String(20), nullable=True)
    renda_estimada = db.Column(db.Numeric(10,2), nullable=True)
    projeto_id = db.Column(db.Integer, db.ForeignKey('plataforma_stakeholders.projeto.projeto_id'), nullable=False)
    associado = db.Column(db.Boolean, nullable=False, default=False)
    
    projeto = db.relationship("Projeto", back_populates='pessoa')
    
    