from app import db
from app.models.base_model import BaseModel

class CnaeSecundario(BaseModel):
    __tablename__ = 'cnae_secundario'
    __table_args__ = {'schema': 'plataforma_stakeholders'}

    id_empresa = db.Column(db.Integer, db.ForeignKey('plataforma_stakeholders.empresa.empresa_id'), primary_key=True,
                           nullable=False)
    id_segmento_empresa = db.Column(db.SmallInteger,
                                    db.ForeignKey('plataforma_stakeholders.segmento_empresa.segmento_id'),
                                    primary_key=True, nullable=False)

    segmento_empresa = db.relationship("SegmentoEmpresa", back_populates="cnae_secundarios")
    empresa = db.relationship("Empresa", back_populates="cnae_secundarios")
