from flask import request
from flask_restful import Resource, reqparse

from app import db
from app.models.tipo_entidade import TipoEntidade

class TipoEntidadeResource(Resource):
    @staticmethod
    def get():
        parser = reqparse.RequestParser()
        parser.add_argument('tipo_entidade_id', type=int, required=True, location='args', help='Tipo é obrigatório')
        args = parser.parse_args()

        # Parâmetros de paginação
        page_number = int(request.args.get('page', 1))
        page_size = min(int(request.args.get('size', 10)), 20)
        start_index = (page_number - 1) * page_size

        # Consulta
        query = TipoEntidade.query
        if args['tipo_entidade_id']:
            query = query.filter_by(tipo_entidade_id=args['tipo_entidade_id'])

        # Total de registros e aplicação de paginação
        total_tipo_entidade = query.count()
        tipo_entidade= query.offset(start_index).limit(page_size).all()

        if not tipo_entidade:
            return "", 204
        
        response_data = {
            'tipo_entidade': [tipo_entidade.to_dict() for tipo_entidade in tipo_entidade],
            'meta': {
            'total': total_tipo_entidade,
            'page': page_number,
            'size': page_size,
            'pages': (total_tipo_entidade + page_size - 1) // page_size
            }
        }

        return response_data, 200
    
    @staticmethod
    def post():
        parser = reqparse.RequestParser()
        parser.add_argument('descricao', type=str, required=True, help='Descrição é obrigatória')
        args = parser.parse_args()

        novo_tipo = TipoEntidade(**args)

        db.session.add(novo_tipo)
        db.session.commit()

        return novo_tipo.to_dict(), 201
    
    @staticmethod
    def put():
        parser = reqparse.RequestParser()
        parser.add_argument('tipo_entidade_id', type=str, required=True, help='Tipo é obrigatorio')
        parser.add_argument('descricao', type=str, required=True, help='Descrição é obrigatória')
        args = parser.parse_args()

        tipo = TipoEntidade.query.get(args['tipo_entidade_id'])
        if not tipo:
            return {'message': 'Tipo não encontrado'}, 404

        tipo.update_from_dict(args)
        db.session.commit()

        return tipo.to_dict(), 200
    
    @staticmethod
    def delete():
        parser = reqparse.RequestParser()
        parser.add_argument('tipo_entidade_id', type=str, location='args', required=True, help='Tipo é obrigatorio')
        args = parser.parse_args()

        tipo = TipoEntidade.query.get(args['tipo_entidade_id'])
        if not tipo:
            return {'message': 'Tipo não encontrado'}, 404

        db.session.delete(tipo)
        db.session.commit()

        return {"message": f"Tipo com ID {args['tipo_entidade_id']} foi deletado com sucesso"}, 200
    



