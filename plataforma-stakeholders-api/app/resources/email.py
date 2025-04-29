import email
from flask import request
from flask_restful import Resource, reqparse
from sqlalchemy.sql import func

from app import db
from app.models.email import Email 
from app.models.tipo_entidade import TipoEntidade

class EmailsResource(Resource):
    """
    Recurso da API responsável por manipular a entidade 'Email'.

    Este recurso possui métodos GET, POST, PUT e DELETE para gerenciar informações relacionadas à entidade 'Email'.
    """
    @staticmethod
    def get():
        """
        Recupera as informações de um ou mais emails com base nos parâmetros fornecidos
        (`entidade_id`, `tipo_entidade_id`).

        Implementa paginação através dos parâmetros `page` e `size`.

        Parâmetros:
            email_id (int, opcional): ID do email.
            entidade_id (int, opcional): ID da entidade.
            tipo_entidade_id (int, opcional): ID do tipo da entidade.
            page (int, opcional): Número da página para paginação (default = 1).
            size (int, opcional): Quantidade de registros por página (default = 10, máximo = 20).

        Returns:
            dict: Uma lista paginada de dicionários com os dados dos emails,
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
            filters.append(email.entidade_id == args['entidade_id'])
        if args['tipo_entidade_id']:
            filters.append(email.tipo_entidade_id == args['tipo_entidade_id'])

        email_query = db.session.query(email).filter(*filters)
        total_email = email_query.count()
        email = email_query.offset(start_index).limit(page_size).all()


        if not email:
            return "", 204
        
        response_data = {
            'email': [email.to_dict() for email in email],
            'meta': {
                'total': total_email,
                'page': page_number,
                'size': page_size,
                'pages': (total_email + page_size - 1) // page_size
            }
        }

        return response_data, 200
    
    @staticmethod
    def post():
        """
        Cria um nova email no banco de dados.

        Requer o envio dos dados do email.

        Returns:
            tuple: Um dicionário com os dados do email criado e o código de status 201 (criado).
        """
        parser = reqparse.RequestParser()
        parser.add_argument('entidade_id', type=int, required=True, location='args', help='Entidade id é obrigatório.')
        parser.add_argument('tipo_entidade_id', type=int, required=True, location='args', help='Tipo entidade id é obrigatório.')  
        parser.add_argument('email', type=str, required=True, location='args', help='email é obrigatório.')
        args = request.json

        existing_email = Email.query.filter_by(entidade_id=args['entidade_id']).count()  # Contagem de emails
        email_id = existing_email + 1


        tipo_entidade = TipoEntidade.query.get(args['tipo_entidade_id'])
        if not tipo_entidade:
            return {'message': 'Tipo da entidade não encontrada'}, 404

        new_email = Email(**args, email_id=email_id)
        

        db.session.add(new_email)
        db.session.commit()

        return new_email.to_dict(), 201
    
    @staticmethod
    def put():
        """
        Atualiza os dados de um email existente.

        Requer o `email_id` para identificar o email a ser atualizado.

        Returns:
            tuple: Um dicionário com os dados atualizados do email e o código de status 200 (OK).
        """
        parser = reqparse.RequestParser()
        parser.add_argument('entidade_id', type=int, required=True, location='args', help='Entidade id é obrigatório.')
        parser.add_argument('tipo_entidade_id', type=int, required=True, location='args', help='Tipo entidade id é obrigatório.')
        parser.add_argument('email_id', type=int, required=True, location='args', help='Email é obrigatório.')
        args = request.json

        email = Email.query.get((args['email_id'], args['entidade_id'], args['tipo_entidade_id']))
        email = Email.query.filter_by(
            entidade_id=args['entidade_id'],
            tipo_entidade_id=args['tipo_entidade_id']
        ).first()

        if not email:
            return {'message': 'email não encontrado'}, 404

        email.update_from_dict(args)

        db.session.commit()
        return email.to_dict(), 200
    
    @staticmethod
    def delete():
        """
        Remove um email do banco de dados com base no `email_id` e em suas associações.

        Requer que o `email_id` seja passado para identificar o email correto.
        Após encontrar o email, a entrada será removida do banco de dados.

        Returns:
            dict: Uma mensagem de sucesso ou uma mensagem de erro, com os respectivos códigos de status.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('entidade_id', type=int, required=True, location='args', help='Entidade id é obrigatório.')
        parser.add_argument('tipo_entidade_id', type=int, required=True, location='args', help='Tipo entidade id é obrigatório.')
        parser.add_argument('email_id', type=int, required=True, location='args', help='Email é obrigatório.')
        args = parser.parse_args()
        
        email = Email.query.get((args['email_id'], args['entidade_id'], args['tipo_entidade_id']))
        email = Email.query.filter_by(
            entidade_id=args['entidade_id'],
            tipo_entidade_id=args['tipo_entidade_id']
        ).first()
        if not email:
            return {'message': 'email não encontrado'}, 404

        db.session.delete(email)
        db.session.commit()

        return {'message': 'email removido com sucesso'}, 200
