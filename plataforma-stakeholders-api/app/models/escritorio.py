from app import db
from app.models.base_model import BaseModel


class Escritorio(BaseModel):
    __tablename__ = 'escritorio'
    __table_args__ = {'schema': 'plataforma_stakeholders'}

    escritorio_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    razao_social = db.Column(db.String(255), nullable=False)
    nome_fantasia = db.Column(db.String(255), nullable=False)
    linkedin = db.Column(db.String(20), nullable=True)
    instagram = db.Column(db.String(20), nullable=True)
    cnpj = db.Column(db.String(14), nullable=False)
