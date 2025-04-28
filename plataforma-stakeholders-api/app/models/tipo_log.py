from app import db
from app.models.base_model import BaseModel

class TipoLog(BaseModel):
    __tablename__ = 'tipo_log'
    
    tipo_log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(40), nullable=False)
    
    log_consulta = db.relationship("LogConsulta", back_populates='tipo_log')