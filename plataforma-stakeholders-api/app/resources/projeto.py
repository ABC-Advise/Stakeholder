from flask import request
from flask_restful import Resource, reqparse
from sqlalchemy.sql import func

from app import db
from app.models.projeto import Projeto
from app.models.empresa import Empresa

class ProjetoResource(Resource):
    """
    Recurso para gerenciar operações CRUD relacionadas à entidade 'Projeto'.

    Métodos disponíveis:
        - GET: Retorna um ou mais projetos com base nos parâmetros fornecidos.
        - POST: Cria um novo projeto.
        - PUT: Atualiza os dados de um projeto existente.
        - DELETE: Remove um projeto do banco de dados.
    """
    
    @staticmethod
    def get():
        """
        Recupera as informações de um ou mais projetos com base nos parâmetros fornecidos
        (`projeto_id`)

        Implementa paginação através dos parâmetros `page` e `size`.

        Parâmetros:
            projeto_id (int, opcional): ID do projeto.
        Returns:
            dict: Uma lista paginada de dicionários com os dados dos projetos e informações de meta,
            ou uma resposta 204 se não forem encontrados.
        """
    
        parser = reqparse.RequestParser()
        parser.add_argument('projeto_id', type=int, required=False, location='args')
        args = parser.parse_args()
        
        page_number = int(request.args.get('page', 1))
        page_size = min(int(request.args.get('size', 10)), 20)
        start_index = (page_number - 1) * page_size
        
        filters = []
        if args['projeto_id']:
            filters.append(Projeto.projeto_id == args['projeto_id'])
            
        projetos_query = db.session.query(Projeto).filter(*filters)
        total_projetos = projetos_query.count()
        projetos = projetos_query.offset(start_index).limit(page_size).all()
        
        if not projetos:
            return "", 204
        
        response_data = {
            'projetos': [projeto.to_dict() for projeto in projetos],
                'meta': {
                    'total': total_projetos,
                    'page': page_number,
                    'size': page_size,
                    'pages': (total_projetos + page_size - 1) // page_size
                }
        }
        
        return response_data, 200
    
    @staticmethod
    def post():
        """
        Cria um novo projeto no banco de dados.

        Requer o envio dos dados da pessoa, como Nome, Descrição, Data de início e Data de fim.

        Returns:
            tuple: Um dicionário com os dados do projeto criado e o código de status 201 (criado).
        """
        parser = reqparse.RequestParser()
        parser.add_argument('nome', type=str, required=True, help='Nome é obrigatório.')
        parser.add_argument('descricao', type=str, required=False)
        parser.add_argument('data_inicio', type=str, required=False)
        parser.add_argument('data_fim', type=str, required=False)
        args = request.json
        
        new_projeto = Projeto(**args)
        
        db.session.add(new_projeto)
        db.session.commit()
        
        return new_projeto.to_dict(), 201
    
    @staticmethod
    def put():
        """
        Atualiza os dados de um projeto existente.

        Requer o `projeto_id` para identificar o projeto a ser atualizado.
        Pode atualizar nome, descrição, data de inicio e fim..

        Returns:
            tuple: Um dicionário com os dados atualizados do projeto e o código de status 200 (OK).
        """
        parser = reqparse.RequestParser()
        parser.add_argument('projeto_id', type=int, required=True, help='ID do projeto é obrigatório.')
        args = request.json
        
        projeto = Projeto.query.get(args['projeto_id'])
        if not projeto:
            return {'message': 'Projeto não encontrado.'}
        
        projeto.update_from_dict(args)
        db.session.commit()
        
        return projeto.to_dict(), 200
    
    @staticmethod
    def delete():
        """
        Remove um projeto do banco de dados com base no `projeto_id`.

        Requer que o `projeto_id` seja passado para identificar o projeto correto.
        Após encontrar o projeto, a entrada será removida do banco de dados.

        Returns:
            dict: Uma mensagem de sucesso ou uma mensagem de erro, com os respectivos códigos de status.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('projeto_id', type=int, required=True, help='ID do projeto é obrigatório.')
        args = parser.parse_args()
        
        projeto = Projeto.query.get(args['projeto_id'])
        if not projeto:
            return {'message': 'Projeto não encontrado'}
        
        db.session.delete(projeto)
        db.session.commit()
        
        return {'message': 'Projeto removido com sucesso'}, 200