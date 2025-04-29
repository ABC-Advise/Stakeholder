from flask import request
from flask_restful import Resource, reqparse
from sqlalchemy.sql import func

from app import db
from app.models.endereco import Endereco
from app.models.tipo_entidade import TipoEntidade
from app.modules.exceptions import ValidationError


class EnderecosResource(Resource):

    @staticmethod
    def get():
        parser = reqparse.RequestParser()
        parser.add_argument('entidade_id', type=int, required=True, location='args', help=('Entidade_id é obrigatório'))
        parser.add_argument('tipo_entidade_id', type=int, required=True, location='args',
                            help=('tipo_entidade_id é obrigatório'))
        # Não sei se usaremos esses campos como parâmetros.
        # parser.add_argument('logradouro', type=str, required=True, location='args')
        # parser.add_argument('numero', type=str, required=True, location='args')
        # parser.add_argument('complemento', type=str, required=True, location='args') 
        # parser.add_argument('bairro', type=str, required=True, location='args')
        # parser.add_argument('cidade', type=str, required=True, location='args')
        # parser.add_argument('uf', type=str, required=True, location='args')
        # parser.add_argument('cep', type=str, required=True, location='args')

        args = parser.parse_args()

        page_number = int(request.args.get('page', 1))
        page_size = min(int(request.args.get('size', 10)), 20)
        start_index = (page_number - 1) * page_size

        # Filtros
        filters = []
        if args['entidade_id']:
            filters.append(Endereco.entidade_id == args['entidade_id'])
        if args['tipo_entidade_id']:
            filters.append(Endereco.tipo_entidade_id == args['tipo_entidade_id'])
        # Não sei se usaremos esses campos como parâmetros.
        # if args['logradouro']:
        #     filters.append(Endereco.logradouro == args['logradouro'])
        # if args['numero']:
        #     filters.append(Endereco.numero == args['numero'])
        # if args['complemento']:
        #     filters.append(Endereco.complemento == args['complemento'])
        # if args['bairro']:
        #     filters.append(Endereco.bairro == args['bairro'])
        # if args['cidade']:
        #     filters.append(Endereco.cidade == args['cidade'])
        # if args['uf']:
        #     filters.append(Endereco.uf == args['uf'])
        # if args['cep']:
        #     filters.append(Endereco.numero == args['cep'])

        endereco_query = db.session.query(Endereco).filter(*filters)
        total_endereco = endereco_query.count()
        endereco = endereco_query.offset(start_index).limit(page_size).all()

        if not endereco:
            return "", 204

        response_data = {
            'endereco': [endereco.to_dict() for endereco in endereco],
            'meta': {
                'total': total_endereco,
                'page': page_number,
                'size': page_size,
                'pages': (total_endereco + page_size - 1) // page_size
            }
        }

        return response_data, 200

    @staticmethod
    def post():
        parser = reqparse.RequestParser()
        parser.add_argument('entidade_id', type=int, required=True, location='args', help='entidade_id é obrigatório')
        parser.add_argument('tipo_entidade_id', type=int, required=True, location='args',
                            help='tipo_entidade_id é obrigatório')
        parser.add_argument('logradouro', type=str, required=False, location='args')
        parser.add_argument('numero', type=str, required=False, location='args')
        parser.add_argument('complemento', type=str, required=False, location='args')
        parser.add_argument('bairro', type=str, required=False, location='args')
        parser.add_argument('cidade', type=str, required=True, location='args', help='cidade é obrigatório')
        parser.add_argument('uf', type=str, required=True, location='args', help='uf é obrigatório')
        parser.add_argument('cep', type=str, required=True, location='args', help='cep é obrigatório')
        args = request.json

        tipo_entidade = TipoEntidade.query.get(args['tipo_entidade_id'])
        if not tipo_entidade:
            return {'message': 'Tipo da entidade não encontrada'}, 404

        existing_enderecos = Endereco.query.filter_by(entidade_id=args['entidade_id']).count()
        endereco_id = existing_enderecos + 1

        new_endereco = Endereco(**args, endereco_id=endereco_id)

        db.session.add(new_endereco)
        db.session.commit()

        return new_endereco.to_dict(), 201

    @staticmethod
    def put():
        parser = reqparse.RequestParser()
        parser.add_argument('entidade_id', type=int, required=True, location='args', help='entidade_id é obrigatório')
        parser.add_argument('tipo_entidade_id', type=int, required=True, location='args',
                            help='tipo_entidade_id é obrigatório')
        parser.add_argument('endereco_id', type=int, required=True, location='args', help='Endereco é obrigatório.')
        args = request.json

        endereco = Endereco.query.get((args['endereco_id'], args['entidade_id'],
                                       args['tipo_entidade_id']))

        if not endereco:
            return {'message': 'Endereço não encontrado'}, 404

        endereco.update_from_dict(args)

        db.session.commit()
        return endereco.to_dict(), 200

    @staticmethod
    def delete():
        parser = reqparse.RequestParser()
        parser.add_argument('entidade_id', type=int, required=True, location='args', help='entidade_id é obrigatório')
        parser.add_argument('tipo_entidade_id', type=int, required=True, location='args',
                            help='tipo_entidade_id é obrigatório')
        parser.add_argument('endereco_id', type=int, required=True, location='args', help='Endereco é obrigatório.')
        args = parser.parse_args()

        endereco = Endereco.query.get((args['endereco_id'], args['entidade_id'], args['tipo_entidade_id']))

        if not endereco:
            return {'message': 'Endereço não encontrado'}, 404

        db.session.delete(endereco)
        db.session.commit()

        return {'message': 'Endereço removido com sucesso'}, 200

    @staticmethod
    def get_enderecos_em_estado(uf, cidade=None, tipo_entidade_id=None):
        if type(uf) != str or len(uf) != 2:
            raise ValidationError(f"O valor '{uf}' não é uma UF válida")

        if tipo_entidade_id and type(tipo_entidade_id) != int:
            raise TypeError(f"O valor {tipo_entidade_id} não é um valor válido para tipo de entidade")

        filters = [Endereco.uf == uf.upper()]
        if cidade:
            # filters.append(Endereco.cidade == cidade[:60].upper())
            filters.append(func.chatsync.similarity(Endereco.cidade, cidade) >= 0.1)

        if tipo_entidade_id:
            filters.append(Endereco.tipo_entidade_id == tipo_entidade_id)

        enderecos = Endereco.query.filter(*filters).all()

        return enderecos if enderecos else list()
