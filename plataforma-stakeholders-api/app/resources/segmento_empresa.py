from flask import request
from flask_restful import Resource, reqparse
from sqlalchemy import func

from app import db
from app.models.segmento_empresa import SegmentoEmpresa


class SegmentoEmpresaResource(Resource):
    """
    Recurso da API responsável por manipular a entidade 'SegmentoEmpresa'.
    Este recurso fornece métodos para realizar operações CRUD (GET, POST, PUT e DELETE)
    na entidade 'SegmentoEmpresa'.
    """

    @staticmethod
    def get():
        """
        Recupera um ou mais registros de 'SegmentoEmpresa'.
        Se o 'segmento_id' for fornecido como argumento, o método retorna o segmento específico.
        Caso contrário, retorna todos os segmentos cadastrados.

        Implementa paginação através dos parâmetros `page` e `size`.

        Parâmetros:
            segmento_id (int, opcional): ID do segmento da empresa.
            page (int, opcional): Número da página para paginação (default = 1).
            size (int, opcional): Quantidade de registros por página (default = 10, máximo = 20).

        Returns:
            dict: Uma lista paginada de dicionários com os dados dos segmentos e informações de meta,
            ou uma resposta 204 se não forem encontrados.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('segmento_id', type=int, required=False, location='args', help='O segmento é obrigatório')
        parser.add_argument('descricao', type=str, required=False, location='args')
        args = parser.parse_args()

        # Parâmetros de paginação
        page_number = int(request.args.get('page', 1))
        page_size = min(int(request.args.get('size', 10)), 20)
        start_index = (page_number - 1) * page_size

        # Consulta
        query = SegmentoEmpresa.query
        if args['segmento_id']:
            query = query.filter_by(segmento_id=args['segmento_id'])
        elif args['descricao']:
            query = query.filter(func.chatsync.similarity(SegmentoEmpresa.descricao, args['descricao']) > 0.2)

        query = query.order_by(SegmentoEmpresa.descricao)
    
        # Total de registros e aplicação de paginação
        total_segmento_empresas = query.count()
        segmento_empresas = query.offset(start_index).limit(page_size).all()

        if not segmento_empresas:
            return "", 204

        response_data = {
            'segmento_empresas': [segmento_empresa.to_dict() for segmento_empresa in segmento_empresas],
            'meta': {
                'total': total_segmento_empresas,
                'page': page_number,
                'size': page_size,
                'pages': (total_segmento_empresas + page_size - 1) // page_size
            }
        }

        return response_data, 200

    @staticmethod
    def post():
        """
        Cria um novo registro de 'SegmentoEmpresa'.
        O método espera a descrição do segmento como argumento.
        Returns:
        - Dicionário com os dados do novo registro e status 201 (Created) se bem-sucedido.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('descricao', type=str, required=True, help='Descrição é obrigatória')
        args = request.json

        novo_segmento = SegmentoEmpresa(**args)

        db.session.add(novo_segmento)
        db.session.commit()

        return novo_segmento.to_dict(), 201

    @staticmethod
    def put():
        """
        Atualiza um registro existente de 'SegmentoEmpresa' com base no 'segmento_id' fornecido.
        O método espera o 'segmento_id' e a nova 'descricao' como argumentos.
          Returns:
        - Dicionário com os dados atualizados e status 200 se a atualização for bem-sucedida.
        - Mensagem de erro e status 404 se o segmento não for encontrado.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('segmento_id', type=str, required=True, help='O segmento é obrigatorio')
        parser.add_argument('descricao', type=str, required=True, help='Descrição é obrigatória')
        args = request.json

        segmento = SegmentoEmpresa.query.get(args['segmento_id'])
        if not segmento:
            return {'message': 'Segmento não encontrado'}, 404

        segmento.update_from_dict(args)
        db.session.commit()

        return segmento.to_dict(), 200

    @staticmethod
    def delete():
        """
        Remove um registro de 'SegmentoEmpresa' com base no 'segmento_id' fornecido.
        O método espera o 'segmento_id' como argumento.
          Returns:
        - Mensagem de confirmação e status 200 se o segmento for deletado com sucesso.
        - Mensagem de erro e status 404 se o segmento não for encontrado.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('segmento_id', type=str, location='args', required=True, help='O Segmento é obrigatorio')
        args = parser.parse_args()

        segmento = SegmentoEmpresa.query.get(args['segmento_id'])
        if not segmento:
            return {'message': 'Segmento não encontrado'}, 404

        db.session.delete(segmento)
        db.session.commit()

        return {"message": f"Segmento com ID {args['segmento_id']} foi deletado com sucesso"}, 200
