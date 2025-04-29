from flask import request
from flask_restful import Resource, reqparse

from app import db
from app.models.porte_empresa import PorteEmpresa


class PorteEmpresaResource(Resource):
    """
    Recurso da API responsável por manipular a entidade 'PorteEmpresa'.
    Este recurso fornece métodos para realizar operações CRUD (GET, POST, PUT e DELETE)
    na entidade 'PorteEmpresa'.
    """

    @staticmethod
    def get():
        """
        Recupera um ou mais registros de 'PorteEmpresa'.
        Se o 'porte_id' for fornecido como argumento, o método retorna o porte específico.
        Caso contrário, retorna todos os portes cadastrados.

        Implementa paginação através dos parâmetros `page` e `size`.

        Parâmetros:
            porte_id (int, opcional): ID do porte da empresa.
            page (int, opcional): Número da página para paginação (default = 1).
            size (int, opcional): Quantidade de registros por página (default = 10, máximo = 20).

        Returns:
            dict: Uma lista paginada de dicionários com os dados dos portes e informações de meta,
            ou uma resposta 204 se não forem encontrados.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('porte_id', type=int, required=False, location='args', help='Porte é obrigatório')
        args = parser.parse_args()

        # Parâmetros de paginação
        page_number = int(request.args.get('page', 1))
        page_size = min(int(request.args.get('size', 10)), 20)
        start_index = (page_number - 1) * page_size

        # Consulta
        query = PorteEmpresa.query
        if args['porte_id']:
            query = query.filter_by(porte_id=args['porte_id'])

        # Total de registros e aplicação de paginação
        total_porte_empresas = query.count()
        porte_empresas = query.offset(start_index).limit(page_size).all()

        if not porte_empresas:
            return "", 204

        response_data = {
            'porte_empresas': [porte_empresa.to_dict() for porte_empresa in porte_empresas],
            'meta': {
                'total': total_porte_empresas,
                'page': page_number,
                'size': page_size,
                'pages': (total_porte_empresas + page_size - 1) // page_size
            }
        }

        return response_data, 200

    @staticmethod
    def post():
        """
        Cria um novo registro de 'PorteEmpresa'.
        O método espera a descrição do porte como argumento.
        Returns:
        - Dicionário com os dados do novo registro e status 201 (Created) se bem-sucedido.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('descricao', type=str, required=True, help='Descrição é obrigatória')
        args = parser.parse_args()

        novo_porte = PorteEmpresa(**args)

        db.session.add(novo_porte)
        db.session.commit()

        return novo_porte.to_dict(), 201

    @staticmethod
    def put():
        """
        Atualiza um registro existente de 'PorteEmpresa' com base no 'porte_id' fornecido.
        O método espera o 'porte_id' e a nova 'descricao' como argumentos.
        Returns:
        - Dicionário com os dados atualizados e status 200 se a atualização for bem-sucedida.
        - Mensagem de erro e status 404 se o porte não for encontrado.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('porte_id', type=str, required=True, help='Porte é obrigatorio')
        parser.add_argument('descricao', type=str, required=True, help='Descrição é obrigatória')
        args = parser.parse_args()

        porte = PorteEmpresa.query.get(args['porte_id'])
        if not porte:
            return {'message': 'Porte não encontrado'}, 404

        porte.update_from_dict(args)
        db.session.commit()

        return porte.to_dict(), 200

    @staticmethod
    def delete():
        """
        Remove um registro de 'PorteEmpresa' com base no 'porte_id' fornecido.
        O método espera o 'porte_id' como argumento.
          Returns:
        - Mensagem de confirmação e status 200 se o porte for deletado com sucesso.
        - Mensagem de erro e status 404 se o porte não for encontrado.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('porte_id', type=str, location='args', required=True, help='Porte é obrigatorio')
        args = parser.parse_args()

        porte = PorteEmpresa.query.get(args['porte_id'])
        if not porte:
            return {'message': 'Porte não encontrado'}, 404

        db.session.delete(porte)
        db.session.commit()

        return {"message": f"Porte com ID {args['porte_id']} foi deletado com sucesso"}, 200
