from flask import request, jsonify
from flask_restful import Resource, reqparse
import json

from app import db, app, redis_client
from app.modules.utils import validar_documento
from app.models.empresa import Empresa
from app.models.pessoa import Pessoa
from app.resources.endereco import EnderecosResource
from app.models.consulta import Consulta
from datetime import datetime, timezone
from rq import Queue
from redis import Redis
from app.modules.tasks import tarefa_consulta


class StakeholdersResources(Resource):
    """
    Recurso para obter stakeholders cadastrados no sistema.

    Métodos disponíveis:
        - GET: Retorna um ou mais stakeholders com base nos parâmetros fornecidos.
    """

    @staticmethod
    def get():
        """
        Recupera as informações de um ou mais stakeholders com base nos parâmetros fornecidos
        (`em_prospecao`).

        Implementa paginação através dos parâmetros `page` e `size`.

        Parâmetros:
            em_prospecao (boolean, opcional): Prospecao do stakeholder
            page (int, opcional): Número da página para paginação (default = 1).
            size (int, opcional): Quantidade de registros por página (default = 10, máximo = 20).

        Returns:
            dict: Uma lista paginada de dicionários com os dados dos stakeholders e informações de meta,
            ou uma resposta 204 se não forem encontrados.
        """

        parser = reqparse.RequestParser()
        parser.add_argument('documento', type=str, required=False, location='args', help='Documento (CPF ou CNPJ)')
        parser.add_argument('em_prospecao', type=bool, required=False, location='args')
        parser.add_argument('tipo_stakeholder', type=str, required=False, location='args')
        parser.add_argument('associado', type=bool, required=False, location='args')
        parser.add_argument('uf', type=str, required=False, location='args')
        parser.add_argument('cidade', type=str, required=False, location='args')
        parser.add_argument('projeto_id', type=int, required=False, location='args')
        args = parser.parse_args()

        # Gera uma chave única para o cache baseada nos parâmetros da requisição
        cache_key = f"stakeholders:{json.dumps(args, sort_keys=True)}"
        
        # Tenta obter os dados do cache
        cached_data = redis_client.get(cache_key)
        if cached_data:
            return json.loads(cached_data), 200

        # Se não estiver no cache, continua com a lógica normal
        documento = validar_documento(args.get('documento')) if args.get('documento') else None

        # Parâmetros de paginação
        page_number = int(request.args.get('page', 1))
        page_size = min(int(request.args.get('size', 10)), 20)
        start_index = (page_number - 1) * page_size

        # Filtros
        filters_pessoa = [Pessoa.stakeholder == True]
        filters_empresa = [Empresa.stakeholder == True]

        # Caso tenha um parâmetro de documento válido, ele adicionao documento como filtro na entidade correspondente
        if documento:
            if len(documento) == 11:
                filters_pessoa.append(Pessoa.cpf == documento)
            elif len(documento) == 14:
                filters_empresa.append(Empresa.cnpj == documento)

        if args['em_prospecao']:
            em_prospecao_bool = args['em_prospecao']
            if em_prospecao_bool:
                filters_pessoa.append(Pessoa.em_prospecao)
                filters_empresa.append(Empresa.em_prospecao)

        if args['associado']:
            associado_bool = args['associado']
            filters_pessoa.append(Pessoa.associado == associado_bool)
            
        if args['projeto_id']:
            filters_pessoa.append(Pessoa.projeto_id == args['projeto_id'])
            filters_empresa.append(Empresa.projeto_id == args['projeto_id'])

        if args['uf']:
            pessoa_ids = StakeholdersResources.get_entidades_por_estado(args['uf'], 1, args.get('cidade', None))
            empresa_ids = StakeholdersResources.get_entidades_por_estado(args['uf'], 3, args.get('cidade', None))

            if not pessoa_ids and not empresa_ids:
                return "", 204

            if pessoa_ids:
                filters_pessoa.append(Pessoa.pessoa_id.in_(pessoa_ids))

            if empresa_ids:
                filters_empresa.append(Empresa.empresa_id.in_(empresa_ids))

        # Consulta com paginação
        stakeholders_query = []

        # Caso o filtro documento esteja sendo usado           
        if documento:
            if len(documento) == 11:
                filters_pessoa.append(Pessoa.cpf == documento)
                pessoas = db.session.query(Pessoa).filter(*filters_pessoa).all()
                stakeholders_query.extend(pessoas)
            elif len(documento) == 14:
                empresas = db.session.query(Empresa).filter(*filters_empresa).all()
                stakeholders_query.extend(empresas)

        elif args['tipo_stakeholder']:
            if args['tipo_stakeholder'] == 'pessoa':
                pessoas = db.session.query(Pessoa).filter(*filters_pessoa).all()
                stakeholders_query.extend(pessoas)
            elif args['tipo_stakeholder'] == 'empresa':
                empresas = db.session.query(Empresa).filter(*filters_empresa).all()
                stakeholders_query.extend(empresas)

        # Caso nenhum dos dois filtros esteja sendo usado
        else:
            empresas = db.session.query(Empresa).filter(*filters_empresa).all()
            stakeholders_query.extend(empresas)

            pessoas = db.session.query(Pessoa).filter(*filters_pessoa).all()
            stakeholders_query.extend(pessoas)

        start_index = (page_number - 1) * page_size
        end_index = start_index + page_size
        stakeholders = stakeholders_query[start_index:end_index]

        total_stakeholders = len(stakeholders_query)

        if not stakeholders:
            return "", 204

        # Formata o retorno das duas entidades
        stakeholders_list = []
        for stakeholder in stakeholders:
            if hasattr(stakeholder, 'cnpj') and stakeholder.cnpj:
                stakeholders_list.append({
                    "entidade_id": stakeholder.empresa_id,
                    "document": stakeholder.cnpj,
                    "is_CNPJ": True,
                    "nome1": stakeholder.razao_social,
                    "nome2": stakeholder.nome_fantasia,
                    "porte_id": stakeholder.porte_id,
                    "segmento_id": stakeholder.segmento_id,
                    "linkedin": stakeholder.linkedin,
                    "instagram": stakeholder.instagram,
                    "stakeholder": stakeholder.stakeholder,
                    "em_prospecao": stakeholder.em_prospecao,
                    "projeto_id": stakeholder.projeto_id
                })

            else:
                stakeholders_list.append({
                    "entidade_id": stakeholder.pessoa_id,
                    "document": stakeholder.cpf,
                    "is_CNPJ": False,
                    "nome1": stakeholder.firstname,
                    "nome2": stakeholder.lastname,
                    "porte_id": None,
                    "segmento_id": None,
                    "linkedin": stakeholder.linkedin,
                    "instagram": stakeholder.instagram,
                    "stakeholder": stakeholder.stakeholder,
                    "em_prospecao": stakeholder.em_prospecao,
                    "associado": stakeholder.associado,
                    "projeto_id": stakeholder.projeto_id
                })

        response_data = {
            'stakeholders': stakeholders_list,
            'meta': {
                'total': total_stakeholders,
                'page': page_number,
                'size': page_size,
                'pages': (total_stakeholders + page_size - 1) // page_size
            }
        }

        # Antes de retornar, salva no cache
        redis_client.set(cache_key, json.dumps(response_data), ex=300)  # Cache por 5 minutos

        return response_data, 200

    @staticmethod
    def post():
        parser = reqparse.RequestParser()
        parser.add_argument('documento', type=str, required=True, help='CPF/CNPJ obrigatório', location='json')
        parser.add_argument('prospeccao', type=bool, required=False, default=False, location='json')
        parser.add_argument('camada_stakeholder', type=bool, required=False, default=True, location='json')
        parser.add_argument('camada_advogados', type=bool, required=False, default=True, location='json')
        parser.add_argument('associado', type=bool, required=False, default=False, location='json')
        parser.add_argument('stakeholder_advogado', type=bool, required=False, default=False, location='json')
        args = parser.parse_args()

        documento = args.get('documento')
        em_prospeccao = args.get('prospeccao', False)
        camada_stakeholder = args.get('camada_stakeholder', True)
        camada_advogados = args.get('camada_advogados', True)
        associado = args.get('associado', False)
        stakeholder_advogado = args.get('stakeholder_advogado', False)
        
        if len(documento) == 11:
            stakeholder = Pessoa.query.filter_by(cpf=documento).first()
        else:
            stakeholder = Empresa.query.filter_by(cnpj=documento).first()
            stakeholder_advogado = False
            associado = False

        if stakeholder:
            return {"message": "Stakeholder já cadastrado"}, 400
        
        # Cadastra uma nova consulta
        new_consulta = Consulta(
            documento=documento,
            is_cnpj = False if len(documento) == 11 else True,
            data_consulta=datetime.now(timezone.utc),
            status="Pendente"
        )
        db.session.add(new_consulta)
        db.session.commit()
        
        # Recebe o id da consulta criada
        consulta_id = new_consulta.consulta_id
        
        # Adiciona os dados à fila
        redis_url = app.config["IPBAN_REDIS_URL"]
        redis_conn = Redis.from_url(redis_url)
        q = Queue(connection=redis_conn)
        
        job = q.enqueue(
            tarefa_consulta,  # Função que vai processar os dados
            redis_url,  # Passando a URL do Redis para a função de processamento
            documento,  # Passando o documento
            consulta_id,
            em_prospeccao,
            camada_stakeholder,
            camada_advogados,
            associado,
            stakeholder_advogado,
            job_timeout=None,  # Pode adicionar o job_timeout se necessário, retirei por conta de um erro
            job_id=str(consulta_id)
        )

        # Após criar/atualizar um stakeholder, invalida o cache
        redis_client.delete("stakeholders:*")

        return jsonify({"Consulta criada": job.id, "status": job.get_status()})

    @staticmethod
    def put():
        parser = reqparse.RequestParser()
        parser.add_argument('documento', type=str, required=True, help='CPF/CNPJ obrigatório', location='json')
        parser.add_argument('prospeccao', type=bool, required=False, default=False, location='json')
        parser.add_argument('camada_stakeholder', type=bool, required=False, default=True, location='json')
        parser.add_argument('camada_advogados', type=bool, required=False, default=True, location='json')
        parser.add_argument('associado', type=bool, required=False, default=False, location='json')
        parser.add_argument('stakeholder_advogado', type=bool, required=False, default=False, location='json')
        args = parser.parse_args()

        documento = args.get('documento')
        em_prospeccao = args.get('prospeccao', False)
        camada_stakeholder = args.get('camada_stakeholder', True)
        camada_advogados = args.get('camada_advogados', True)
        associado = args.get('associado', False)
        stakeholder_advogado = args.get('stakeholder_advogado', False)
        
        if len(documento) == 11:
            stakeholder = Pessoa.query.filter_by(cpf=documento).first()
        else:
            stakeholder = Empresa.query.filter_by(cnpj=documento).first()
            associado = False
            stakeholder_advogado = False

        if not stakeholder:
            return "", 204
        
        # Cadastra uma nova consulta
        new_consulta = Consulta(
            documento=documento,
            is_cnpj = False if len(documento) == 11 else True,
            data_consulta=datetime.now(timezone.utc),
            status="Pendente"
        )
        db.session.add(new_consulta)
        db.session.commit()
        
        # Recebe o id da consulta criada
        consulta_id = new_consulta.consulta_id
        
        # Adiciona os dados à fila
        redis_url = app.config["IPBAN_REDIS_URL"]
        redis_conn = Redis.from_url(redis_url)
        q = Queue(connection=redis_conn)
        
        job = q.enqueue(
            tarefa_consulta,  # Função que vai processar os dados
            redis_url,  # Passando a URL do Redis para a função de processamento
            documento,  # Passando o documento
            consulta_id,
            em_prospeccao,
            camada_stakeholder,
            camada_advogados,
            associado,
            stakeholder_advogado,
            job_timeout=None,  # Pode adicionar o job_timeout se necessário, retirei por conta de um erro
            job_id=str(consulta_id)
        )
        
        stakeholder.stakeholder = True
        db.session.commit()

        # Após criar/atualizar um stakeholder, invalida o cache
        redis_client.delete("stakeholders:*")

        return jsonify({"Consulta criada": job.id, "status": job.get_status()})

    @staticmethod
    def get_entidades_por_estado(uf, tipo_entidade, cidade=None): 
        enderecos_entidade = EnderecosResource.get_enderecos_em_estado(uf, cidade, tipo_entidade)
        entidade_ids = {endereco.entidade_id for endereco in enderecos_entidade}
        return entidade_ids