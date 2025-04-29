from flask import request
from flask_restful import Resource, reqparse

import pytz
from datetime import datetime
from app import db, app
from app.models.consulta import Consulta
from sqlalchemy import desc, asc
from app.modules.utils import converter_timezone

from redis import Redis
from rq.job import Job
from rq.registry import CanceledJobRegistry
from rq import Queue, SimpleWorker
from rq.command import send_kill_horse_command

class ConsultaResource(Resource):
    """
    Recurso da API responsável por manipular a entidade 'Consulta'.
    Este recurso fornece apenas o método GET.
    na entidade 'Consulta'.
    """

    @staticmethod
    def get():
        """
        Recupera um ou mais registros de 'Consulta'.
        O método retorna apenas uma consulta com seus respectivos logs.

        Implementa paginação através dos parâmetros `page` e `size`.

        Parâmetros:
            consulta_id (int, obrigatório): ID da consulta.
            page (int, opcional): Número da página para paginação (default = 1).
            size (int, opcional): Quantidade de registros por página (default = 10, máximo = 20).

        Returns:
            dict: Uma lista paginada de dicionários com os dados da consulta e seus logs,
            ou uma resposta 204 se não forem encontrados.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('consulta_id', type=int, required=False, location='args')
        parser.add_argument('is_cnpj', type=bool, required=False, location='args')
        parser.add_argument('antigo_primeiro', type=bool, required=False, location='args')
        parser.add_argument('data_inicio', type=str, required=False, location='args')
        parser.add_argument('data_fim', type=str, required=False, location='args')
        args = parser.parse_args()

        # Parâmetros de paginação
        page_number = int(request.args.get('page', 1))
        page_size = min(int(request.args.get('size', 10)), 20)
        start_index = (page_number - 1) * page_size

        # Consulta
        filters = []
        if args['consulta_id']:
            filters.append(Consulta.consulta_id == args['consulta_id'])
            
        if args['is_cnpj']:
            filters.append(Consulta.is_cnpj == args['is_cnpj'])
        
        if args['data_inicio'] and args['data_fim']:
            filters.append(Consulta.data_consulta.between(args['data_inicio'], args['data_fim']))
        
        elif args['data_inicio'] and not args['data_fim']:
            filters.append(Consulta.data_consulta >= args['data_inicio'])
        
        elif not args['data_inicio'] and args['data_fim']:
            return "Erro: Data de início não fornecida!", 400
        
        # Consulta com paginação
        consulta_query = db.session.query(Consulta).filter(*filters)
        total_consultas = consulta_query.count()
        
        if args['antigo_primeiro']:
            consultas = consulta_query.order_by(asc(Consulta.data_consulta))
        else:
            consultas = consulta_query.order_by(desc(Consulta.data_consulta))
            
        consultas = consultas.offset(start_index).limit(page_size).all()

        if not consultas:
            return "", 204
    
        response_data = {
            'consultas': [{
                'consulta_id': consulta.consulta_id,
                'documento': consulta.documento,
                'data_consulta': converter_timezone(consulta.data_consulta),
                'is_cnpj': consulta.is_cnpj,
                'status': consulta.status
                } for consulta in consultas],
            'meta': {
                'total': total_consultas,
                'page': page_number,
                'size': page_size,
                'pages': (total_consultas + page_size - 1) // page_size
            }
        }

        return response_data, 200
    
    @staticmethod
    def delete():
        parser = reqparse.RequestParser()
        parser.add_argument('consulta_id', type=int, required=True, location='args', help='ID da consulta obrigatório')
        args = parser.parse_args()
        
        redis_url = app.config["IPBAN_REDIS_URL"]
        redis_conn = Redis.from_url(redis_url)
        
        # O ID do job precisa ser string.
        consulta_id = str(args['consulta_id'])
        
        q = Queue(connection=redis_conn)
        
        job = q.fetch_job(consulta_id)
        if not job:
            return {'msg': f'Consulta {consulta_id} não encontrada.'}, 204
        
        status = job.get_status()
        
        consulta_query = db.session.query(Consulta).filter_by(consulta_id=consulta_id)
        
        if status == 'started':
            return f"O processo {consulta_id} já está sendo processado.", 400
        
        job.cancel()
        
        consulta_query.update({"status": "Cancelado"})
        db.session.commit()
        
        return {'msg': f'Consulta {consulta_id} cancelada com sucesso.'}, 200
