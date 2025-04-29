from flask import request
from flask_restful import Resource, reqparse

import pytz
from datetime import datetime
from app import db
from app.models.log_consulta import LogConsulta
from app.models.consulta import Consulta
from app.models.tipo_log import TipoLog
from sqlalchemy import asc
from app.modules.utils import converter_timezone

class LogsConsultaResource(Resource):
    """
    Recurso da API responsável por manipular a entidade 'LogsConsulta'.
    Este recurso fornece apenas o método GET.
    na entidade 'Consulta'.
    """

    @staticmethod
    def get():
        """
        Recupera todos registros de 'Log', podendo ser geral ou de apenas uma consulta da entidade 'Consulta'.
        Implementa paginação através dos parâmetros `page` e `size`.

        Parâmetros:
            consulta_id (int, opcional): ID da consulta.
            page (int, opcional): Número da página para paginação (default = 1).
            size (int, opcional): Quantidade de registros por página (default = 10, máximo = 20).

        Returns:
            dict: Uma lista paginada de dicionários com os dados dos logs de uma consulta,
            ou uma resposta 204 se não forem encontrados.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('consulta_id', type=int, required=True, location='args', help="Consulta obrigatória")
        args = parser.parse_args()

        # Parâmetros de paginação
        page_number = int(request.args.get('page', 1))
        page_size = min(int(request.args.get('size', 10)), 20)
        start_index = (page_number - 1) * page_size
            
        query_log = LogConsulta.query
        query_consulta = Consulta.query
        
        query_log = query_log.filter_by(consulta_id=args['consulta_id'])
        consulta = query_consulta.filter_by(consulta_id=args['consulta_id']).first()
        
        # Total de registros e aplicação de paginação
        total_logs = query_log.count()
        logs = query_log.order_by(asc(LogConsulta.data_log))
        logs = logs.offset(start_index).limit(page_size).all()
        
        for log in logs:
            log.tipo_log_nome = log.tipo_log.nome
        
        response_data = {
            'consulta_id': consulta.consulta_id,
            'documento': consulta.documento,
            'is_cnpj': consulta.is_cnpj,
            'data_consulta': converter_timezone(consulta.data_consulta),
            'status_consulta': consulta.status,
            'logs': [{
                        'log_consulta_id': log.log_consulta_id,
                        'consulta_id': log.consulta_id,
                        'tipo_log_id': log.tipo_log_id,
                        'tipo_log_nome': getattr(log, "tipo_log_nome", None),
                        'mensagem': log.mensagem,
                        'data_log': converter_timezone(log.data_log)
                    } for log in logs],
            'meta': {
                'total': total_logs,
                'page': page_number,
                'size': page_size,
                'pages': (total_logs + page_size - 1) // page_size
            }
        }

        return response_data, 200
