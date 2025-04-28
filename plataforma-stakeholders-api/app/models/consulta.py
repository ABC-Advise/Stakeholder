from app import db
from app.models.base_model import BaseModel
from datetime import datetime
import pytz

class Consulta(BaseModel):
    __tablename__ = 'consulta'
    
    consulta_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    documento = db.Column(db.String(14), nullable=False)
    is_cnpj = db.Column(db.Boolean, nullable=False, default=False)
    data_consulta = db.Column(db.DateTime(timezone=True), default=lambda:datetime.now(pytz.utc))
    status = db.Column(db.String(20), default="Pendente", nullable=False)
    
    log_consulta = db.relationship("LogConsulta", back_populates='consulta')