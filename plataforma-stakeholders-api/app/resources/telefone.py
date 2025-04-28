from flask import request
from flask_restful import Resource, reqparse
from sqlalchemy.sql import func 

from app import db
from app.models.telefone import Telefone 
from app.models.tipo_entidade import TipoEntidade

class TelefonesResource(Resource):
    """
    Recurso da API responsável por manipular a entidade 'Telefone'.

    Este recurso possui métodos GET, POST, PUT e DELETE para gerenciar informações relacionadas à entidade 'Telefone'.
    """
    @staticmethod
    def get():
        """
        Recupera as informações de um ou mais emails com base nos parâmetros fornecidos
        (`telefone_id`, `entidade_id`, `tipo_entidade_id`).

        Implementa paginação através dos parâmetros `page` e `size`.

        Parâmetros:
            telefone_id (int, opcional): ID do telefone.
            entidade_id (int, opcional): ID da entidade.
            tipo_entidade_id (int, opcional): ID do tipo da entidade.
            page (int, opcional): Número da página para paginação (default = 1).
            size (int, opcional): Quantidade de registros por página (default = 10, máximo = 20).

        Returns:
            dict: Uma lista paginada de dicionários com os dados dos telefones,
            ou uma resposta 204 se não forem encontrados.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('entidade_id', type=int, required=True, location='args', help='Entidade id é obrigatório')
        parser.add_argument('tipo_entidade_id', type=int, required=True, location='args', help='Tipo_entidade_id é obrigatório')  
        
        args = parser.parse_args()

        page_number = int(request.args.get('page', 1))
        page_size = min(int(request.args.get('size', 10)), 20)
        start_index = (page_number - 1) * page_size


        # Filtros
        filters = []
        if args['entidade_id']:
            filters.append(Telefone.entidade_id == args['entidade_id'])
        if args['tipo_entidade_id']:
            filters.append(Telefone.tipo_entidade_id == args['tipo_entidade_id'])

        telefone_query = db.session.query(Telefone).filter(*filters)
        total_telefone = telefone_query.count()
        telefone = telefone_query.offset(start_index).limit(page_size).all()


        if not telefone:
            return "", 204
        
        response_data = {
            'telefone': [telefone.to_dict() for telefone in telefone],
            'meta': {
                'total': total_telefone,
                'page': page_number,
                'size': page_size,
                'pages': (total_telefone + page_size - 1) // page_size
            }
        }

        return response_data, 200
    
    @staticmethod
    def post():
        """
        Cria um novo telefone no banco de dados.

        Requer o envio dos dados do telefone.

        Returns:
            tuple: Um dicionário com os dados do telefone criado e o código de status 201 (criado).
        """
        parser = reqparse.RequestParser()
        # parser.add_argument('entidade_id', type=int, required=True, location='args', help='Entidade id é obrigatório.')
        parser.add_argument('tipo_entidade_id', type=int, required=True, location='args', help='Tipo entidade id é obrigatório.')
        parser.add_argument('telefone', type=str, required=True, location='args', help='Telefone é obrigatório.')
        parser.add_argument('operadora', type=str, required=True, location='args', help='Operadora é obrigatório.') 
        parser.add_argument('tipo_telefone', type=str, required=False, location='args')
        parser.add_argument('whatsapp', type=bool, required=True, location='args', help='Whatsapp é obrigatório: True or False.')
        args = request.json
             
        existing_telefone = Telefone.query.filter_by(entidade_id=args['entidade_id']).count()  # Contagem de emails
        telefone_id = existing_telefone + 1

        tipo_entidade = TipoEntidade.query.get(args['tipo_entidade_id'])
        if not tipo_entidade:
            return {'message': 'Tipo da entidade não encontrada'}, 404

        new_telefone = Telefone(**args, telefone_id=telefone_id)

        db.session.add(new_telefone)
        db.session.commit()

        return new_telefone.to_dict(), 201
    
    @staticmethod
    def put():
        """
        Atualiza os dados de um telefone existente.

        Requer o `telefone_id` para identificar o telefone a ser atualizado.

        Returns:
            tuple: Um dicionário com os dados atualizados do telefone e o código de status 200 (OK).
        """
        parser = reqparse.RequestParser()
        parser.add_argument('entidade_id', type=int, required=True, location='args', help='Entidade id é obrigatório.')
        parser.add_argument('tipo_entidade_id', type=int, required=True, location='args', help='Tipo entidade id é obrigatório.')
        parser.add_argument('telefone_id', type=int, required=True, location='args', help='Telefone é obrigatório.')
        args = request.json

        telefone = Telefone.query.get((args['telefone_id'], args['entidade_id'], args['tipo_entidade_id']))
        telefone = Telefone.query.filter_by(
            entidade_id=args['entidade_id'],
            tipo_entidade_id=args['tipo_entidade_id']
        ).first()

        if not telefone:
            return {'message': 'Telefone não encontrado'}, 404

        telefone.update_from_dict(args)

        db.session.commit()
        return telefone.to_dict(), 200
    
    @staticmethod
    def delete():
        """
        Remove um telefone do banco de dados com base no `telefone_id` e em suas associações.

        Requer que o `telefone_id` seja passado para identificar a empresa correta.
        Após encontrar o telefone, a entrada será removida do banco de dados.

        Returns:
            dict: Uma mensagem de sucesso ou uma mensagem de erro, com os respectivos códigos de status.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('entidade_id', type=int, required=True, location='args', help='Entidade id é obrigatório.')
        parser.add_argument('tipo_entidade_id', type=int, required=True, location='args', help='Tipo entidade id é obrigatório.')
        parser.add_argument('telefone_id', type=int, required=True, location='args', help='Telefone é obrigatório.')
        args = parser.parse_args()

        telefone = Telefone.query.get((args['telefone_id'], args['entidade_id'], args['tipo_entidade_id']))
        telefone = Telefone.query.filter_by(
            telefone_id=args['telefone_id']
        ).first()
        if not telefone:
            return {'message': 'Telefone não encontrado'}, 404

        db.session.delete(telefone)
        db.session.commit()

        return {'message': 'Telefone removido com sucesso'}, 200
