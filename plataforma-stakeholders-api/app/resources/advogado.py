from flask import request
from flask_restful import Resource, reqparse
from sqlalchemy import or_, and_
from sqlalchemy.sql import func

from app import db
from app.models.advogado import Advogado
from app.models.endereco import Endereco
from app.models.email import Email
from app.models.telefone import Telefone
from app.models.relacionamentos import Relacionamentos
from app.models.empresa import Empresa
from app.models.pessoa import Pessoa
from app.modules.utils import validar_documento


class AdvogadoResource(Resource):
    """
    Recurso da API responsável por manipular a entidade 'Advogado'.

    Este recurso possui um método GET protegido por autenticação JWT,
    retornando informações sobre um determinado 'Advogado' relacionado ao usuário autenticado.
    """

    @staticmethod
    def get():
        """
        Recupera as informações de advogados com base no parâmetro `advogado_id` ou `oab`.

        Implementa paginação através dos parâmetros `page` e `size`.

        Parâmetros:
            advogado_id (int, opcional): ID do advogado.
            oab (str, opcional): Número da OAB do advogado.
            page (int, opcional): Número da página para paginação (default = 1).
            size (int, opcional): Quantidade de registros por página (default = 10, máximo = 20).

        Returns:
            dict: Uma lista paginada de dicionários com os dados dos advogados e informações de meta,
            ou uma resposta 204 se não forem encontrados.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('advogado_id', type=int, required=False, location='args')
        parser.add_argument('oab', type=str, required=False, location='args')
        parser.add_argument('cpf', type=str, required=False, location='args')
        parser.add_argument('nome', type=str, required=False, location='args')
        parser.add_argument('sobrenome', type=str, required=False, location='args')
        parser.add_argument('stakeholder', type=str, required=False, location='args')
        args = parser.parse_args()

        # Parâmetros de paginação
        page_number = int(request.args.get('page', 1))
        page_size = min(int(request.args.get('size', 10)), 20)
        start_index = (page_number - 1) * page_size

        # Filtros
        filters = []
        if args['advogado_id']:
            filters.append(Advogado.advogado_id == args['advogado_id'])
        if args['oab']:
            filters.append(func.chatsync.similarity(Advogado.oab, args['oab']) >= 0.5)
        if args['cpf']:
            documento = validar_documento(args['cpf'])
            filters.append(func.chatsync.similarity(Advogado.cpf, documento) >= 0.5)
        if args['nome']:
            filters.append(func.chatsync.similarity(Advogado.firstname, args['nome']) >= 0.2)
        if args['sobrenome']:
            filters.append(func.chatsync.similarity(Advogado.lastname, args['sobrenome']) >= 0.2)
        if args['stakeholder']:
            documento_stakeholder = validar_documento(args['stakeholder'])

            if len(documento_stakeholder) == 11:
                stakeholder = Pessoa.query.filter_by(cpf=documento_stakeholder).first()
                if not stakeholder:
                    return "", 204

                tipo_stakeholder = 1
                stakeholder_id = stakeholder.pessoa_id
            else:
                stakeholder = Empresa.query.filter_by(cnpj=documento_stakeholder).first()
                if not stakeholder:
                    return "", 204

                tipo_stakeholder = 3
                stakeholder_id = stakeholder.empresa_id

            advogados_stakeholder = Relacionamentos.query.filter(
                or_(
                    and_(
                        Relacionamentos.tipo_origem_id == tipo_stakeholder,
                        Relacionamentos.entidade_origem_id == stakeholder_id
                    ),
                    and_(
                        Relacionamentos.tipo_destino_id == tipo_stakeholder,
                        Relacionamentos.entidade_destino_id == stakeholder_id
                    )
                ),
                Relacionamentos.tipo_relacao_id == 26
            ).all()

            # Extrair os IDs dos advogados
            advogado_ids = {
                relacionamento.entidade_origem_id if relacionamento.tipo_origem_id == 4
                else relacionamento.entidade_destino_id
                for relacionamento in advogados_stakeholder
            }

            if not advogado_ids:
                return "", 204

            # Adicionar o filtro para incluir apenas os advogados relacionados
            filters.append(Advogado.advogado_id.in_(advogado_ids))

        # Consulta com paginação
        advogados_query = db.session.query(Advogado).filter(*filters)
        total_advogados = advogados_query.count()
        advogados = advogados_query.offset(start_index).limit(page_size).all()

        if not advogados:
            return "", 204

        response_data = {
            'advogados': [advogado.to_dict() for advogado in advogados],
            'meta': {
                'total': total_advogados,
                'page': page_number,
                'size': page_size,
                'pages': (total_advogados + page_size - 1) // page_size
            }
        }

        return response_data, 200

    @staticmethod
    def post():
        """
        Cria um novo advogado no banco de dados, juntamente com suas informações adicionais.

        Requer o envio dos dados do advogado, como nome, sobrenome, oab e um dicionário com os detalhes
        das informações adicionais (cep, linkedin, instagram, número de contato e email).
        Caso alguma dessas informações esteja vazia, será retornado uma exceção.

        Returns:
            tuple: Um dicionário com os dados do advogado criado e o código de status 201 (criado).
        """
        parser = reqparse.RequestParser()
        parser.add_argument('firstname', type=str, required=True, help='Firstname é obrigatório')
        parser.add_argument('lastname', type=str, required=True, help='Lastname é obrigatório')
        parser.add_argument('oab', type=str, required=True, help='Oab é obrigatório')
        parser.add_argument('cpf', type=str, required=True, help='CPF é obrigatório')
        args = request.json

        new_advogado = Advogado(**args)

        db.session.add(new_advogado)
        db.session.commit()

        return new_advogado.to_dict(), 201

    @staticmethod
    def put():
        """
        Atualiza os dados de um advogado existente, incluindo suas informações adicionais.

        Requer o `advogado_id` para identificar o advogado a ser atualizado.
        Pode atualizar o nome, sobrenome, oab e as informações adicionais (cep, linkedin, instagram, número de contato).

        Returns:
            tuple: Um dicionário com os dados atualizados do advogado e o código de status 200 (OK).
        """
        parser = reqparse.RequestParser()
        parser.add_argument('advogado_id', type=int, required=True, help='Advogado id é obrigatório')
        args = request.json

        advogado = Advogado.query.get(args['advogado_id'])
        if not advogado:
            return {'Message': 'Advogado não encontrado.'}, 404

        advogado.update_from_dict(args)

        db.session.commit()
        return advogado.to_dict(), 200

    @staticmethod
    def delete():
        """
        Remove um advogado do banco de dados com base no `advogado_id`.

        Requer que o `advogado_id` seja passado para identificar o advogado correto.
        Após encontrar o advogado, a entrada será removida do banco de dados.

        Returns:
            dict: Uma mensagem de sucesso ou uma mensagem de erro, com os respectivos códigos de status.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('advogado_id', type=int, location='args', required=True, help='Advogado id é obrigatório')
        args = parser.parse_args()

        advogado = Advogado.query.get(args['advogado_id'])
        if not advogado:
            return {'Message': 'Advogado não encontrado.'}, 404

        Endereco.query.filter_by(tipo_entidade_id=4, entidade_id=args['advogado_id']).delete()
        Telefone.query.filter_by(tipo_entidade_id=4, entidade_id=args['advogado_id']).delete()
        Email.query.filter_by(tipo_entidade_id=4, entidade_id=args['advogado_id']).delete()
        Relacionamentos.query.filter_by(tipo_destino_id=4, entidade_destino_id=args['advogado_id']).delete()
        Relacionamentos.query.filter_by(tipo_origem_id=4, entidade_origem_id=args['advogado_id']).delete()
        db.session.delete(advogado)
        db.session.commit()

        return {'Message': 'Advogado removido com sucesso.'}, 200
