from flask import request
from flask_restful import Resource, reqparse
from sqlalchemy.sql import func

from app import db
from app.models.pessoa import Pessoa
from app.models.endereco import Endereco
from app.models.email import Email
from app.models.telefone import Telefone
from app.models.relacionamentos import Relacionamentos
from app.modules.utils import validar_documento
from app.resources.endereco import EnderecosResource


class PessoaResource(Resource):
    """
    Recurso para gerenciar operações CRUD relacionadas à entidade 'Pessoa'.

    Métodos disponíveis:
        - GET: Retorna uma ou mais pessoas com base nos parâmetros fornecidos.
        - POST: Cria uma nova pessoa e suas informações adicionais.
        - PUT: Atualiza os dados de uma pessoa existente, incluindo suas informações adicionais.
        - DELETE: Remove uma pessoa do banco de dados.
    """

    @staticmethod
    def get():
        """
        Recupera as informações de uma ou mais pessoas com base nos parâmetros fornecidos
        (`pessoa_id` ou `cpf`).

        Implementa paginação através dos parâmetros `page` e `size`.

        Parâmetros:
            pessoa_id (int, opcional): ID da pessoa.
            cpf (str, opcional): CPF da pessoa.
            page (int, opcional): Número da página para paginação (default = 1).
            size (int, opcional): Quantidade de registros por página (default = 10, máximo = 20).

        Returns:
            dict: Uma lista paginada de dicionários com os dados das pessoas e informações de meta,
            ou uma resposta 204 se não forem encontrados.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('pessoa_id', type=int, required=False, location='args')
        parser.add_argument('cpf', type=str, required=False, location='args')  # CPF deve ser uma string
        parser.add_argument('uf', type=str, required=False, location='args')
        parser.add_argument('cidade', type=str, required=False, location='args')
        parser.add_argument('projeto_id', type=int, required=False, location='args')
        args = parser.parse_args()

        # Parâmetros de paginação
        page_number = int(request.args.get('page', 1))
        page_size = min(int(request.args.get('size', 10)), 20)
        start_index = (page_number - 1) * page_size

        # Filtros
        filters = []
        if args['pessoa_id']:
            filters.append(Pessoa.pessoa_id == args['pessoa_id'])
        if args['cpf']:
            filters.append(
                func.chatsync.similarity(Pessoa.cpf, args['cpf']) > 0.7)  # Ajuste no operador de similaridade
        if args['uf']:
            pessoa_ids = PessoaResource.get_pessoas_por_estado(args['uf'], args.get('cidade', None))
            if not pessoa_ids:
                return "", 204
            
            if pessoa_ids:
                filters.append(Pessoa.pessoa_id.in_(pessoa_ids))
            
        if args['projeto_id']:
            filters.append(Pessoa.projeto_id == args['projeto_id'])

        # Consulta com paginação
        pessoas_query = db.session.query(Pessoa).filter(*filters)
        total_pessoas = pessoas_query.count()
        pessoas = pessoas_query.offset(start_index).limit(page_size).all()

        if not pessoas:
            return "", 204

        response_data = {
            'pessoas': [pessoa.to_dict() for pessoa in pessoas],
            'meta': {
                'total': total_pessoas,
                'page': page_number,
                'size': page_size,
                'pages': (total_pessoas + page_size - 1) // page_size
            }
        }

        return response_data, 200

    @staticmethod
    def post():
        """
        Cria uma nova pessoa no banco de dados, juntamente com suas informações adicionais.

        Requer o envio dos dados da pessoa, como PEP, sexo, data de nascimento, nome da mãe, idade, signo, 
        e informações adicionais opcionais como óbito, data do óbito e renda estimada.

        Returns:
            tuple: Um dicionário com os dados da pessoa criada e o código de status 201 (criado).
        """
        parser = reqparse.RequestParser()
        parser.add_argument('firstname', type=str, required=True)
        parser.add_argument('lastname', type=str, required=False)
        parser.add_argument('cpf', type=str, required=True)
        parser.add_argument('pep', type=bool, required=False)
        parser.add_argument('sexo', type=str, required=False)
        parser.add_argument('data_nascimento', type=str, required=False)
        parser.add_argument('nome_mae', type=str, required=False)
        parser.add_argument('idade', type=int, required=False)
        parser.add_argument('signo', type=str, required=False)
        parser.add_argument('obito', type=bool, required=False)
        parser.add_argument('data_obito', type=str, required=False)
        parser.add_argument('renda_estimada', type=float, required=False)

        args = request.json

        args['cpf'] = validar_documento(args['cpf'])

        new_pessoa = Pessoa(**args)

        db.session.add(new_pessoa)
        db.session.commit()

        return new_pessoa.to_dict(), 201

    @staticmethod
    def put():
        """
        Atualiza os dados de uma pessoa existente, incluindo suas informações adicionais.

        Requer o `pessoa_id` para identificar a pessoa a ser atualizada.
        Pode atualizar o nome, sobrenome e as informações adicionais (cep, linkedin, instagram, número de contato).

        Returns:
            tuple: Um dicionário com os dados atualizados da pessoa e o código de status 200 (OK).
        """
        parser = reqparse.RequestParser()
        parser.add_argument('pessoa_id', type=int, required=True)
        args = request.json

        if args['cpf']:
            args['cpf'] = validar_documento(args['cpf'])

        pessoa = Pessoa.query.get(args['pessoa_id'])
        if not pessoa:
            return {'message': 'Pessoa não encontrada'}, 404

        pessoa.update_from_dict(args)

        db.session.commit()
        return pessoa.to_dict(), 200

    @staticmethod
    def delete():
        """
        Remove uma pessoa do banco de dados com base no `pessoa_id`.

        Requer que o `pessoa_id` seja passado para identificar a pessoa correta.
        Após encontrar a pessoa, a entrada será removida do banco de dados.

        Returns:
            dict: Uma mensagem de sucesso ou uma mensagem de erro, com os respectivos códigos de status.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('pessoa_id', type=int, location='args', required=True)
        args = parser.parse_args()

        pessoa = Pessoa.query.get(args['pessoa_id'])
        if not pessoa:
            return {'message': 'Pessoa não encontrada'}, 404

        Endereco.query.filter_by(tipo_entidade_id=1, entidade_id=args['pessoa_id']).delete()
        Telefone.query.filter_by(tipo_entidade_id=1, entidade_id=args['pessoa_id']).delete()
        Email.query.filter_by(tipo_entidade_id=1, entidade_id=args['pessoa_id']).delete()
        Relacionamentos.query.filter_by(tipo_destino_id=1, entidade_destino_id=args['pessoa_id']).delete()
        Relacionamentos.query.filter_by(tipo_origem_id=1, entidade_origem_id=args['pessoa_id']).delete()
        db.session.delete(pessoa)
        db.session.commit()

        return {'message': 'Pessoa removida com sucesso'}, 200

    @staticmethod
    def get_pessoas_por_estado(uf, cidade=None):
        enderecos_pessoas = EnderecosResource.get_enderecos_em_estado(uf, cidade, 3)
        pessoa_ids = {endereco.entidade_id for endereco in enderecos_pessoas}
        
        return pessoa_ids