from app import db
from app.models.base_model import BaseModel
from app.models.consulta import Consulta
from app.models.tipo_log import TipoLog
from datetime import datetime
import pytz

class LogConsulta(BaseModel):
    __tablename__ = 'log_consulta'
    __table_args__ = {'schema': 'plataforma_stakeholders'}
    
    log_consulta_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    mensagem = db.Column(db.String, nullable=False)
    consulta_id = db.Column(db.Integer, db.ForeignKey('plataforma_stakeholders.consulta.consulta_id'), nullable=False)
    tipo_log_id = db.Column(db.Integer, db.ForeignKey('plataforma_stakeholders.tipo_log.tipo_log_id'), nullable=False)
    data_log = db.Column(db.DateTime(timezone=True), default=lambda:datetime.now(pytz.utc))

    consulta = db.relationship("Consulta", back_populates='log_consulta')
    tipo_log = db.relationship("TipoLog", back_populates='log_consulta')