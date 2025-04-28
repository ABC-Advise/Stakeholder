from app import db
from app.models.base_model import BaseModel


class SegmentoEmpresa(BaseModel):
    __tablename__ = 'segmento_empresa'
    __table_args__ = {'schema': 'plataforma_stakeholders'}

    segmento_id = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    cnae = db.Column(db.String(7), nullable=False)
    descricao = db.Column(db.String, nullable=False)

    empresa = db.relationship("Empresa", back_populates='segmento_empresa')
    cnae_secundarios = db.relationship("CnaeSecundario", back_populates="segmento_empresa")
