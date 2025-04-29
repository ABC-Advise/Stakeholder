from app import db
from app.models.base_model import BaseModel


class Advogado(BaseModel):
    __tablename__ = 'advogado'
    __table_args__ = (
        db.UniqueConstraint('oab', name='idx_unique_advogado_oab'),
        db.Index('idx_oab_trgm', 'oab', postgresql_using='gin', postgresql_ops={'oab': 'gin_trgm_ops'}),
        {'schema': 'plataforma_stakeholders'}
    )

    advogado_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    firstname = db.Column(db.String(40), nullable=False)
    lastname = db.Column(db.String(80), nullable=False)
    oab = db.Column(db.String(8), nullable=False)
    cpf = db.Column(db.String(11), nullable=True)
    linkedin = db.Column(db.String(20), nullable=True)
    instagram = db.Column(db.String(20), nullable=True)
    stakeholder = db.Column(db.Boolean, nullable=False, default=False)
