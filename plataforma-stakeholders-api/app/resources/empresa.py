from flask import request
from flask_restful import Resource, reqparse
from sqlalchemy.sql import func

from app import db
from app.models.empresa import Empresa
from app.models.porte_empresa import PorteEmpresa
from app.models.segmento_empresa import SegmentoEmpresa
from app.models.endereco import Endereco
from app.models.email import Email
from app.models.telefone import Telefone
from app.models.relacionamentos import Relacionamentos
from app.models.projeto import Projeto
from app.modules.utils import validar_documento
from app.resources.endereco import EnderecosResource


class EmpresaResource(Resource):
    """
    Recurso da API responsável por manipular a entidade 'Empresa'.

    Este recurso possui métodos GET, POST, PUT e DELETE para gerenciar informações relacionadas à entidade 'Empresa',
    incluindo porte, segmento e informações adicionais associadas.
    """

    @staticmethod
    def get():
        """
        Recupera as informações de uma ou mais empresas com base nos parâmetros fornecidos
        (`empresa_id`, `cnpj`, `porte_id`, `segmento_id`).

        Implementa paginação através dos parâmetros `page` e `size`.

        Parâmetros:
            empresa_id (int, opcional): ID da empresa.
            cnpj (str, opcional): CNPJ da empresa.
            porte_id (int, opcional): ID do porte da empresa.
            segmento_id (int, opcional): ID do segmento da empresa.
            page (int, opcional): Número da página para paginação (default = 1).
            size (int, opcional): Quantidade de registros por página (default = 10, máximo = 20).

        Returns:
            dict: Uma lista paginada de dicionários com os dados das empresas e informações de meta,
            ou uma resposta 204 se não forem encontrados.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('empresa_id', type=int, required=False, location='args')
        parser.add_argument('cnpj', type=str, required=False, location='args')  # CNPJ deve ser uma string
        parser.add_argument('porte_id', type=int, required=False, location='args')
        parser.add_argument('segmento_id', type=int, required=False, location='args')
        parser.add_argument('razao_social', type=str, required=False, location='args')
        parser.add_argument('nome_fantasia', type=str, required=False, location='args')
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
        if args['empresa_id']:
            filters.append(Empresa.empresa_id == args['empresa_id'])
        if args['cnpj']:
            documento = validar_documento(args['cnpj'])
            filters.append(func.chatsync.similarity(Empresa.cnpj, documento) >= 0.5)
        if args['porte_id']:
            filters.append(Empresa.porte_id == args['porte_id'])
        if args['segmento_id']:
            filters.append(Empresa.segmento_id == args['segmento_id'])
        if args['razao_social']:
            filters.append(func.chatsync.similarity(Empresa.razao_social, args['razao_social']) >= 0.1)
        if args['nome_fantasia']:
            filters.append(func.chatsync.similarity(Empresa.nome_fantasia, args['nome_fantasia']) >= 0.1)
        if args['uf']:
            empresa_ids = EmpresaResource.get_empresas_por_estado(args['uf'], args.get('cidade', None))
            if not empresa_ids:
                return "", 204

            if empresa_ids:
                filters.append(Empresa.empresa_id.in_(empresa_ids))

        if args['projeto_id']:
            filters.append(Empresa.projeto_id == args['projeto_id'])

        # Consulta com paginação
        empresas_query = db.session.query(Empresa).filter(*filters)
        total_empresas = empresas_query.count()
        empresas = empresas_query.offset(start_index).limit(page_size).all()

        if not empresas:
            return "", 204

        response_data = {
            'empresas': [
                {
                    **empresa.to_dict(),
                    'segmento': SegmentoEmpresa.query.get(empresa.segmento_id).descricao
                    if SegmentoEmpresa.query.get(empresa.segmento_id) else None
                }
                for empresa in empresas
            ],
            'meta': {
                'total': total_empresas,
                'page': page_number,
                'size': page_size,
                'pages': (total_empresas + page_size - 1) // page_size
            }
        }

        return response_data, 200

    @staticmethod
    def post():
        """
        Cria uma nova empresa no banco de dados, juntamente com seus detalhes de porte, segmento e informações adicionais.

        Requer o envio dos dados da empresa, incluindo CNPJ, razão social, nome fantasia, porte_id, segmento_id, 
        e informações adicionais opcionais, como data de fundação, quantidade de funcionários, situação cadastral, 
        código e descrição da natureza jurídica, faixa de funcionários, faixa de faturamento, matriz, órgão público, ramo, 
        tipo de empresa e última atualização PJ.


        Returns:
            tuple: Um dicionário com os dados da empresa criada e o código de status 201 (criado).
        """
        parser = reqparse.RequestParser()
        parser.add_argument('cnpj', type=str, required=True)
        parser.add_argument('razao_social', type=str, required=True)
        parser.add_argument('nome_fantasia', type=str, required=True)
        parser.add_argument('porte_id', type=int, required=True)
        parser.add_argument('segmento_id', type=int, required=True)
        parser.add_argument('data_fundacao', type=str, required=False)
        parser.add_argument('quantidade_funcionarios', type=int, required=False)
        parser.add_argument('situacao_cadastral', type=str, required=False)
        parser.add_argument('codigo_natureza_juridica', type=int, required=False)
        parser.add_argument('natureza_juridica_descricao', type=str, required=False)
        parser.add_argument('faixa_funcionarios', type=str, required=False)
        parser.add_argument('faixa_faturamento', type=str, required=False)
        parser.add_argument('matriz', type=bool, required=False)
        parser.add_argument('orgao_publico', type=str, required=False)
        parser.add_argument('ramo', type=str, required=False)
        parser.add_argument('tipo_empresa', type=str, required=False)
        parser.add_argument('ultima_atualizacao_pj', type=str, required=False)
        parser.add_argument('projeto_id', type=int, required=False)
        args = request.json

        args['cnpj'] = validar_documento(args['cnpj'])

        porte_empresa = PorteEmpresa.query.get(args['porte_id'])
        if not porte_empresa:
            return {'message': 'PorteEmpresa não encontrada'}, 404

        segmento_empresa = SegmentoEmpresa.query.get(args['segmento_id'])
        if not segmento_empresa:
            return {'message': 'SegmentoEmpresa não encontrada'}, 404

        if args.get('projeto_id'):
            projeto = Projeto.query.get(args['projeto_id'])
            if not projeto:
                return {'message': 'Projeto não encontrado'}, 404

        new_empresa = Empresa(**args)

        db.session.add(new_empresa)
        db.session.commit()

        return new_empresa.to_dict(), 201

    @staticmethod
    def put():
        """
        Atualiza os dados de uma empresa existente, incluindo porte, segmento e suas informações adicionais.

        Requer o `empresa_id` para identificar a empresa a ser atualizada.
        Pode atualizar CNPJ, razão social, nome fantasia, porte, segmento e as informações adicionais (CEP, LinkedIn, Instagram, número de contato e email).

        Returns:
            tuple: Um dicionário com os dados atualizados da empresa e o código de status 200 (OK).
        """
        parser = reqparse.RequestParser()
        parser.add_argument('empresa_id', type=int, required=True)
        args = request.json

        if args.get('cnpj'):
            args['cnpj'] = validar_documento(args['cnpj'])

        if args.get('porte_id'):
            porte_empresa = PorteEmpresa.query.get(args['porte_id'])
            if not porte_empresa:
                return {'message': 'PorteEmpresa não encontrada'}, 404

        if args.get('segmento_id'):
            segmento_empresa = SegmentoEmpresa.query.get(args['segmento_id'])
            if not segmento_empresa:
                return {'message': 'SegmentoEmpresa não encontrada'}, 404

        if args.get('projeto_id'):
            projeto = Projeto.query.get(args['projeto_id'])
            if not projeto:
                return {'message': 'Projeto não encontrado'}, 404

        empresa = Empresa.query.get(args['empresa_id'])
        if not empresa:
            return {'message': 'Empresa não encontrada'}, 404

        empresa.update_from_dict(args)

        db.session.commit()
        return empresa.to_dict(), 200

    @staticmethod
    def delete():
        """
        Remove uma empresa do banco de dados com base no `empresa_id` e em suas associações.

        Requer que o `empresa_id` seja passado para identificar a empresa correta.
        Após encontrar a empresa, a entrada será removida do banco de dados.

        Returns:
            dict: Uma mensagem de sucesso ou uma mensagem de erro, com os respectivos códigos de status.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('empresa_id', type=int, location='args', required=True)
        args = parser.parse_args()

        empresa = Empresa.query.get(args['empresa_id'])
        if not empresa:
            return {'message': 'Empresa não encontrada'}, 404

        # Remover as associações
        Endereco.query.filter_by(tipo_entidade_id=3, entidade_id=args['empresa_id']).delete()
        Telefone.query.filter_by(tipo_entidade_id=3, entidade_id=args['empresa_id']).delete()
        Email.query.filter_by(tipo_entidade_id=3, entidade_id=args['empresa_id']).delete()
        Relacionamentos.query.filter_by(tipo_destino_id=3, entidade_destino_id=args['empresa_id']).delete()
        Relacionamentos.query.filter_by(tipo_origem_id=3, entidade_origem_id=args['empresa_id']).delete()
        db.session.delete(empresa)
        db.session.commit()

        return {'message': 'Empresa removida com sucesso'}, 200

    @staticmethod
    def get_empresas_por_estado(uf, cidade=None):
        enderecos_empresa = EnderecosResource.get_enderecos_em_estado(uf, cidade, 3)
        empresa_ids = {endereco.entidade_id for endereco in enderecos_empresa}

        return empresa_ids
