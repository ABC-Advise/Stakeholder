from flask import request
from flask_restful import Resource, reqparse
from sqlalchemy.sql import func

from app import db
from app.models.escritorio import Escritorio


class EscritorioResource(Resource):
    """
    Recurso da API responsável por manipular a entidade 'Escritorio'.

    Métodos disponíveis:
        - GET: Retorna um ou mais escritórios com base no ID fornecido.
        - POST: Cria um novo escritório e suas informações adicionais.
        - PUT: Atualiza os dados de um escritório existente, incluindo suas informações adicionais.
        - DELETE: Remove um escritório do banco de dados.
    """

    @staticmethod
    def get():
        """
        Recupera as informações de escritórios com base nos parâmetros `escritorio_id`, `razao_social` ou `nome_fantasia`.

        Implementa paginação através dos parâmetros `page` e `size`.

        Parâmetros:
            escritorio_id (int, opcional): ID do escritório.
            razao_social (str, opcional): Razão social do escritório.
            nome_fantasia (str, opcional): Nome fantasia do escritório.
            page (int, opcional): Número da página para paginação (default = 1).
            size (int, opcional): Quantidade de registros por página (default = 10, máximo = 20).

        Returns:
            dict: Uma lista paginada de dicionários com os dados dos escritórios e informações de meta,
            ou uma resposta 204 se não forem encontrados.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('escritorio_id', type=int, required=False, location='args')
        parser.add_argument('razao_social', type=str, required=False, location='args')
        parser.add_argument('nome_fantasia', type=str, required=False, location='args')
        args = parser.parse_args()

        # Parâmetros de paginação
        page_number = int(request.args.get('page', 1))
        page_size = min(int(request.args.get('size', 10)), 20)
        start_index = (page_number - 1) * page_size

        # Filtros
        filters = []
        if args['escritorio_id']:
            filters.append(Escritorio.escritorio_id == args['escritorio_id'])
        if args['razao_social']:
            filters.append(func.chatsync.similarity(Escritorio.razao_social, args['razao_social']) >= 0.7)
        if args['nome_fantasia']:
            filters.append(func.chatsync.similarity(Escritorio.nome_fantasia, args['nome_fantasia']) >= 0.7)

        # Consulta com paginação
        escritorios_query = db.session.query(Escritorio).filter(*filters)
        total_escritorios = escritorios_query.count()
        escritorios = escritorios_query.offset(start_index).limit(page_size).all()

        if not escritorios:
            return "", 204

        response_data = {
            'escritorios': [escritorio.to_dict() for escritorio in escritorios],
            'meta': {
                'total': total_escritorios,
                'page': page_number,
                'size': page_size,
                'pages': (total_escritorios + page_size - 1) // page_size
            }
        }

        return response_data, 200

    @staticmethod
    def post():
        """
        Cria um novo escritório no banco de dados, juntamente com suas informações adicionais.

        Requer o envio dos dados do escritório, como razão social, nome fantasia e um dicionário com os detalhes
        das informações adicionais (cep, linkedin, instagram, número de contato e email).
        Caso alguma dessas informações esteja vazia, será retornado uma exceção.

        Returns:
            tuple: Um dicionário com os dados do escritório criado e o código de status 201 (criado).
        """
        parser = reqparse.RequestParser()
        parser.add_argument('razao_social', type=str, required=True, help='Razão social é obrigatório')
        parser.add_argument('nome_fantasia', type=str, required=True, help='Nome fantasia é obrigatório')
        args = request.json

        new_escritorio = Escritorio(**args)

        db.session.add(new_escritorio)
        db.session.commit()

        return new_escritorio.to_dict(), 201

    @staticmethod
    def put():
        """
        Atualiza os dados de um escritório existente, incluindo suas informações adicionais.

        Requer o `escritorio_id` para identificar o escritório a ser atualizado.
        Pode atualizar a razao social, nome fantasia e as informações adicionais (cep, linkedin, instagram, número de contato).

        Returns:
            tuple: Um dicionário com os dados atualizados do escritório e o código de status 200 (OK).
        """
        parser = reqparse.RequestParser()
        parser.add_argument('escritorio_id', type=int, required=True, help='Escritorio id é obrigatório')
        args = request.json

        escritorio = Escritorio.query.get(args['escritorio_id'])
        if not escritorio:
            return {'Message': 'Escritório não encontrado.'}, 404

        escritorio.update_from_dict(args)

        db.session.commit()
        return escritorio.to_dict(), 200

    @staticmethod
    def delete():
        """
        Remove um escritório do banco de dados com base no `escritorio_id` e `info_adicional_id`.

        Requer que o `escritorio_id`seja passado para identificar o escritório correto.
        Após encontrar o escritório, a entrada será removida do banco de dados.

        Returns:
            dict: Uma mensagem de sucesso ou uma mensagem de erro, com os respectivos códigos de status.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('escritorio_id', type=int, location='args', required=True, help='Escritorio id é obrigatório')
        args = parser.parse_args()

        escritorio = Escritorio.query.get(args['escritorio_id'])
        if not escritorio:
            return {'Message': 'Escritório não encontrado.'}, 404

        db.session.delete(escritorio)
        db.session.commit()

        return {'Message': 'Escritório removido com sucesso'}, 200
