import logging

from flask import jsonify, request
from sqlalchemy.exc import IntegrityError, DataError, StatementError
from werkzeug.exceptions import HTTPException

from app.modules.exceptions import ValidationError, AuthorizationError, HTTPError


class ErrorHandler:
    """
    A classe ErrorHandler é responsável por gerenciar e tratar erros em toda a aplicação Flask.

    Ela captura exceções globais e fornece respostas padronizadas em formato JSON, além de
    logar os erros encontrados. Adicionalmente, faz rollback da sessão do banco de dados
    em caso de exceções relacionadas ao SQLAlchemy.

    Parâmetros:
    - app (Flask): Instância da aplicação Flask.
    - db (SQLAlchemy): Instância do banco de dados SQLAlchemy.
    - socketio (SocketIO, opcional): Instância do SocketIO, se usada na aplicação.

    A classe trata vários tipos de erros, incluindo:
    - Exceções HTTP (HTTPException)
    - Erros de integridade de banco de dados (IntegrityError)
    - Erros de dados (DataError)
    - Erros de declaração SQL (StatementError)
    - Erros personalizados, como ValidationError, AuthorizationError e HTTPError
    """

    def __init__(self, app=None, db=None, socketio=None):
        """
        Inicializa o ErrorHandler com a aplicação Flask, o banco de dados e o WebSocket opcional.

        Parâmetros:
        - app (Flask): Instância da aplicação Flask.
        - db (SQLAlchemy): Instância do banco de dados.
        - socketio (SocketIO, opcional): Instância do SocketIO (opcional).

        Se a aplicação e o banco de dados forem fornecidos, o método __init_app será chamado
        para registrar os handlers de erro.
        """
        if app and db:
            self.__app = app
            self.__socketio = socketio
            self.__db = db
            self.__init_app(app, socketio)

    def __init_app(self, app, socketio):
        """
        Registra os handlers de erro para a aplicação Flask e, opcionalmente, para o SocketIO.

        Este método define handlers para diversos erros comuns, como erros de banco de dados,
        erros de autorização, erros HTTP e exceções não tratadas. Além disso, também registra
        o logger de erros para a aplicação.

        Parâmetros:
        - app (Flask): Instância da aplicação Flask.
        - socketio (SocketIO): Instância do SocketIO para tratamento de erros WebSocket.
        """
        handler = logging.StreamHandler()
        handler.setLevel(logging.ERROR)
        app.logger.addHandler(handler)

        @app.errorhandler(Exception)
        def handle_exception(e):
            """
            Trata exceções gerais e retorna uma resposta com o código de erro e a mensagem correspondente.

            Este handler captura todas as exceções não tratadas, incluindo erros HTTP, de banco de dados e outros.
            Realiza o rollback da sessão do banco de dados sempre que ocorre um erro relacionado ao SQLAlchemy.

            Parâmetros:
            - e (Exception): Exceção capturada.

            Retorna:
            - Response: Resposta JSON com a mensagem de erro e o código HTTP apropriado.
            """
            code = 500
            error = "Internal server error"
            if isinstance(e, HTTPException):
                code = e.code
                error = str(e)
            elif isinstance(e, IntegrityError):
                code = 400
                error = "Database integrity error"
                app.logger.error(f"Integrity Error: {e.orig}", exc_info=True)
                self.__db.session.rollback()
            elif isinstance(e, DataError):
                code = 400
                error = "Invalid data"
                app.logger.error(f"Data Error: {e.orig}", exc_info=True)
                self.__db.session.rollback()
            elif isinstance(e, StatementError):
                code = 400
                error = "Statement error"
                app.logger.error(f"Statement Error: {e.orig}", exc_info=True)
                self.__db.session.rollback()
            elif isinstance(e, ValidationError):
                code = 400
                error = e.message
            elif isinstance(e, HTTPError):
                code = 400
                error = e.message
                self.__db.session.rollback()
            elif isinstance(e, AuthorizationError):
                code = 401
                error = e.message
            else:
                app.logger.error(f"Unhandled Exception: {e}", exc_info=True)
                self.__db.session.rollback()

            return self.__create_error_response(error, code)

        @app.errorhandler(404)
        def resource_not_found(e):
            """
            Handler para requisições que tentam acessar recursos inexistentes (404 Not Found).

            Retorna:
            - Response: Resposta JSON com a mensagem 'Resource not found' e código 404.
            """
            app.logger.warning(f"Resource Not Found: {request.url}")
            return self.__create_error_response('Resource not found', 404)

        @app.errorhandler(400)
        def bad_request(e):
            """
            Handler para requisições malformadas (400 Bad Request).

            Retorna:
            - Response: Resposta JSON com a mensagem 'Bad request' e código 400.
            """
            app.logger.warning(f"Bad Request: {request.data}")
            return self.__create_error_response('Bad request', 400)

        @app.errorhandler(401)
        def unauthorized(e):
            """
            Handler para acessos não autorizados (401 Unauthorized).

            Retorna:
            - Response: Resposta JSON com a mensagem de erro e código 401.
            """
            app.logger.warning("Unauthorized access attempt.")
            return self.__create_error_response(str(e), 401)

        @app.errorhandler(403)
        def forbidden(e):
            """
            Handler para acessos proibidos (403 Forbidden).

            Retorna:
            - Response: Resposta JSON com a mensagem 'Forbidden' e código 403.
            """
            app.logger.warning("Forbidden access attempt.")
            return self.__create_error_response('Forbidden', 403)

        @app.errorhandler(405)
        def method_not_allowed(e):
            """
            Handler para métodos HTTP não permitidos (405 Method Not Allowed).

            Retorna:
            - Response: Resposta JSON com a mensagem 'Method not allowed' e código 405.
            """
            app.logger.warning(f"Method Not Allowed: {request.method}")
            return self.__create_error_response('Method not allowed', 405)

        @app.errorhandler(500)
        def internal_server_error(e):
            """
            Handler para erros internos do servidor (500 Internal Server Error).

            Retorna:
            - Response: Resposta JSON com a mensagem 'Internal server error' e código 500.
            """
            app.logger.error(f"Internal Server Error: {e}", exc_info=True)
            self.__db.session.rollback()
            return self.__create_error_response('Internal server error', 500)

        if socketio:
            @socketio.on_error_default
            def websocket_error_handler(e):
                """
                Handler para erros WebSocket.

                Este handler captura exceções que ocorrem durante a comunicação via WebSocket.

                Retorna:
                - Response: Resposta JSON com a mensagem de erro e código 500.
                """
                app.logger.error(f"WebSocket Error: {e}")
                self.__db.session.rollback()
                return self.__create_error_response(str(e), 500)

    @staticmethod
    def __create_error_response(error, code):
        """
        Cria uma resposta JSON padronizada para erros.

        Parâmetros:
        - error (str): Mensagem de erro.
        - code (int): Código HTTP do erro.

        Retorna:
        - Response: Resposta JSON com a mensagem de erro, código HTTP, método HTTP e URL.
        """
        response = {
            "error": error,
            "code": code,
            "method": request.method,
            "url": request.url
        }
        return jsonify(response), code