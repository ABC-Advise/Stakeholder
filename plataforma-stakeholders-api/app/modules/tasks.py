import time
import json
from app import db, app

from app.modules.utils import validar_documento
from app.models.empresa import Empresa
from app.models.pessoa import Pessoa
from app.modules.consulta_stakeholder import ConsultaStakeholder
from app.modules.analise_juridica import AnaliseJuridica
from app.modules.analise_escritorios_advogados import AnaliseEscritoriosAdvogados
from app.modules.objects.advogado import Advogado
from app.resources.endereco import EnderecosResource
from app.modules.logger import Logger
from app.models.consulta import Consulta
from datetime import datetime, timezone

def tarefa_consulta(redis_url, documento, consulta_id, em_prospeccao, camada_stakeholder, camada_advogados, associado, stakeholder_advogado):
    from redis import Redis
    from rq import get_current_job
    
    redis = Redis.from_url(redis_url)

    job = get_current_job() 
    
    print(f"Processo {documento} iniciado. (Job_id: {job.id}).")

    with app.app_context():
        
        logger = Logger()
    
        try:
            Consulta.query.filter_by(consulta_id=consulta_id).update({
                "status": "Em processamento"
            })
            db.session.commit()
            
            # Processa a camada de stakeholder, se necessário
            if camada_stakeholder:
                consulta_stakeholder = ConsultaStakeholder(documento, consulta_id, local_tests=True, em_prospecao=em_prospeccao, save_requests=False, logger=logger)
                consulta_stakeholder.start()
                consulta_stakeholder.save()

            # Processa a camada de advogados, se necessário
            if camada_advogados:
                analise = AnaliseJuridica(documento, consulta_id, local_tests=True, save_requests=False, is_stakeholder_advogado=stakeholder_advogado, logger=logger)
                analise.start()
                analise.save()

                for advogado in analise.advogados:
                    if isinstance(advogado, Advogado):
                        if len(advogado.oabs) > 0:
                            analise_advogado = AnaliseEscritoriosAdvogados(
                                advogado.oabs[0].numero,
                                advogado.oabs[0].uf,
                                consulta_id,
                                local_tests=True,
                                save_requests=False,
                                directdata_local=True,
                                logger=logger
                            )
                            analise_advogado.start()
                            analise_advogado.save()

            if len(documento) == 11:
                stakeholder = Pessoa.query.filter_by(cpf=documento).first()  
                if stakeholder:
                    stakeholder.associado = associado
                    stakeholder.em_prospecao = em_prospeccao
            else:
                stakeholder = Empresa.query.filter_by(cnpj=documento).first()
                if stakeholder:
                    stakeholder.em_prospecao = em_prospeccao
                    
            if stakeholder:
                stakeholder.stakeholder = True
                db.session.commit()
            
            # Finaliza a consulta no banco
            logger.save()
            consulta_query = db.session.query(Consulta).filter_by(consulta_id=consulta_id)
            consulta_query.update({"status": "Finalizado"})
            db.session.commit()

        except Exception as e:
            # Caso haja erro, loga a exceção e re-enfileira o job
            print(f"Erro no processo {consulta_id}: {e}")
            logger.add_log(
                mensagem=f"Erro no processo {consulta_id}: {e}",
                tipo_log="ERROR",
                consulta_id=consulta_id,
                data_log=datetime.now(timezone.utc)
            )
            
            consulta_query = db.session.query(Consulta).filter_by(consulta_id=consulta_id)
            consulta_query.update({"status": "Erro"})
            db.session.commit()
            
            logger.save()
            raise
            
    print(f"Processo {consulta_id} finalizado.")
