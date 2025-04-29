from app import db
from app.models.log_consulta import LogConsulta
from app.models.tipo_log import TipoLog

class Logger:
    
    def __init__(self):
        self.logs = []
        
    def add_log(self, mensagem, tipo_log, consulta_id, data_log):
        """ 
        Método responsável por armazenar um log na memória.
        """
        tipo_log = tipo_log.upper()
        
        if not mensagem or not tipo_log or not consulta_id:
            raise ValueError("Todos os parâmetros são obrigatórios.")
        
        try:
            tipo_log_id = self.get_tipo_log_id(tipo_log)
        except ValueError as e:
            print(f"Erro ao obter tipo de log: {e}")
            return
        
        self.logs.append({
            "mensagem": mensagem,
            "tipo_log_id": tipo_log_id,
            "consulta_id": consulta_id,
            "data_log": data_log
        })
    
    @staticmethod
    def get_tipo_log_id(tipo_log):
        """
        Obtém o ID do tipo de log com base no nome.
        """
        tipo_log = TipoLog.query.filter_by(nome=tipo_log).first()
        if not tipo_log:
            raise ValueError(f"Tipo de log '{tipo_log}' não encontrado!")
        
        return tipo_log.tipo_log_id
    
    def save(self):
        """ 
        Salva todos os logs no banco de dados.
        """
        if not self.logs:
            return
        
        try:
            db.session.bulk_insert_mappings(LogConsulta, self.logs)
            db.session.commit()
        except Exception as e:
            print(f"Erro ao salvar logs: {e}")
        finally:
            self.logs.clear()
