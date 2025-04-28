from app import db
from app.models.base_model import BaseModel
from app.models.tipo_entidade import TipoEntidade


class Email(BaseModel):
    __tablename__ = 'email'
    __table_args__ = {'schema': 'plataforma_stakeholders'}

    entidade_id = db.Column(db.Integer, primary_key=True)
    tipo_entidade_id = db.Column(db.SmallInteger, db.ForeignKey(TipoEntidade.tipo_entidade_id), primary_key=True)
    email_id = db.Column(db.SmallInteger, primary_key=True)
    email = db.Column(db.String(180), nullable=True)

    tipo_entidade = db.relationship("TipoEntidade", back_populates='email')
