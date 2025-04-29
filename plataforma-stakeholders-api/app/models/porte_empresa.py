from app import db
from app.models.base_model import BaseModel


class PorteEmpresa(BaseModel):
    __tablename__ = 'porte_empresa'
    __table_args__ = {'schema': 'plataforma_stakeholders'}

    porte_id = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    descricao = db.Column(db.String(40), nullable=False)

    empresa = db.relationship("Empresa", back_populates='porte_empresa')
