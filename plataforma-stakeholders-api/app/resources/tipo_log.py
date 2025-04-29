from flask import request
from flask_restful import Resource, reqparse

from app import db
from app.models.tipo_log import TipoLog

class TipoLogResource(Resource):
    """
    Recurso da API responsável por manipular a entidade 'TipoLog'.
    Este recurso fornece métodos para realizar operações CRUD (GET, POST, PUT e DELETE)
    na entidade 'TipoLog'.
    """

    @staticmethod
    def get():
        """
        Recupera um ou mais registros de 'TipoLog'.
        Se o 'tipo_log_id' for fornecido como argumento, o método retorna o tipo log específico.
        Caso contrário, retorna todos os tipos log cadastrados.

        Implementa paginação através dos parâmetros `page` e `size`.

        Parâmetros:
            tipo_log_id (int, opcional): ID do tipo log.
            page (int, opcional): Número da página para paginação (default = 1).
            size (int, opcional): Quantidade de registros por página (default = 10, máximo = 20).

        Returns:
            dict: Uma lista paginada de dicionários com os dados dos tipos log e informações de meta,
            ou uma resposta 204 se não forem encontrados.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('tipo_log_id', type=int, required=False, location='args', help='Tipo é obrigatório')
        args = parser.parse_args()

        # Parâmetros de paginação
        page_number = int(request.args.get('page', 1))
        page_size = min(int(request.args.get('size', 10)), 20)
        start_index = (page_number - 1) * page_size

        # Consulta
        query = TipoLog.query
        if args['tipo_log_id']:
            query = query.filter_by(tipo_log_id=args['tipo_log_id'])

        # Total de registros e aplicação de paginação
        total_tipos_log = query.count()
        tipos_log = query.offset(start_index).limit(page_size).all()

        if not tipos_log:
            return "", 204

        response_data = {
            'tipos_log': [tipo_log.to_dict() for tipo_log in tipos_log],
            'meta': {
                'total': total_tipos_log,
                'page': page_number,
                'size': page_size,
                'pages': (total_tipos_log + page_size - 1) // page_size
            }
        }

        return response_data, 200

    @staticmethod
    def post():
        """
        Cria um novo registro de 'TipoLog'.
        O método espera o nome do tipo como argumento.
        Returns:
        - Dicionário com os dados do novo registro e status 201 (Created) se bem-sucedido.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('nome', type=str, required=True, help='Nome é obrigatório')
        args = parser.parse_args()

        novo_tipo = TipoLog(**args)

        db.session.add(novo_tipo)
        db.session.commit()

        return novo_tipo.to_dict(), 201

    @staticmethod
    def put():
        """
        Atualiza um registro existente de 'TipoLog' com base no 'tipo_log_id' fornecido.
        O método espera o 'tipo_log_id' e o novo 'nome' como argumentos.
        Returns:
        - Dicionário com os dados atualizados e status 200 se a atualização for bem-sucedida.
        - Mensagem de erro e status 404 se o tipo não for encontrado.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('tipo_log_id', type=str, required=True, help='Tipo é obrigatorio')
        parser.add_argument('nome', type=str, required=True, help='Nome é obrigatório')
        args = parser.parse_args()

        tipo = TipoLog.query.get(args['tipo_log_id'])
        if not tipo:
            return {'message': 'Tipo não encontrado'}, 404

        tipo.update_from_dict(args)
        db.session.commit()

        return tipo.to_dict(), 200

    @staticmethod
    def delete():
        """
        Remove um registro de 'TipoLog' com base no 'tipo_log_id' fornecido.
        O método espera o 'tipo_log_id' como argumento.
          Returns:
        - Mensagem de confirmação e status 200 se o porte for deletado com sucesso.
        - Mensagem de erro e status 404 se o tipo não for encontrado.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('tipo_log_id', type=str, location='args', required=True, help='Tipo é obrigatorio')
        args = parser.parse_args()

        tipo = TipoLog.query.get(args['tipo_log_id'])
        if not tipo:
            return {'message': 'Tipo não encontrado'}, 404

        db.session.delete(tipo)
        db.session.commit()

        return {"message": f"Tipo log com ID {args['tipo_log_id']} foi deletado com sucesso"}, 200