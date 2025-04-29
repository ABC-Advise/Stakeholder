import datetime
import logging
from flask import request, jsonify, redirect, url_for, session
from flask_limiter.util import get_remote_address
from flask_restful import Resource

from app import app, api, limiter
from app.resources.empresa import EmpresaResource
from app.resources.advogado import AdvogadoResource
from app.resources.pessoa import PessoaResource
from app.resources.escritorio import EscritorioResource
from app.resources.porte_empresa import PorteEmpresaResource
from app.resources.segmento_empresa import SegmentoEmpresaResource
from app.resources.stakeholders import StakeholdersResources
from app.resources.endereco import EnderecosResource
from app.resources.telefone import TelefonesResource
from app.resources.email import EmailsResource
from app.resources.relacionamentos import RelacionamentosResource
from app.resources.projeto import ProjetoResource
from app.resources.tipo_log import TipoLogResource
from app.resources.consulta import ConsultaResource
from app.resources.logs_consulta import LogsConsultaResource


# Rotas
api.add_resource(EmpresaResource, "/empresa")
api.add_resource(AdvogadoResource, "/advogado")
api.add_resource(PessoaResource, "/pessoa")
api.add_resource(EscritorioResource, "/escritorio")
api.add_resource(PorteEmpresaResource, "/porte_empresa")
api.add_resource(SegmentoEmpresaResource, "/segmento_empresa")
api.add_resource(StakeholdersResources, "/stakeholders")
api.add_resource(EnderecosResource, "/endereco")
api.add_resource(TelefonesResource, "/telefone")
api.add_resource(EmailsResource, "/email")
api.add_resource(RelacionamentosResource, "/relacionamentos")
api.add_resource(ProjetoResource, "/projetos")
api.add_resource(TipoLogResource, "/tipo_log")
api.add_resource(ConsultaResource, "/consulta")
api.add_resource(LogsConsultaResource, "/log")



@app.before_request
def block_banned_ip():
    """
    Função executada antes de cada requisição para verificar se o IP do cliente está bloqueado.

    Verifica se o endereço IP do cliente está banido pela implementação do Limiter.
    Se o IP estiver bloqueado, a função retorna uma resposta com código 401 (Unauthorized).

    Retorna:
        - Resposta JSON com mensagem de 'Unauthorized' e status 401 se o IP estiver bloqueado.
    """
    if limiter._storage.get(get_remote_address()):
        return {"message": "Unauthorized"}, 401

@app.after_request
def after_request(response):
    """
    Função executada após cada requisição para configurar os cabeçalhos de CORS.

    Define o cabeçalho 'Access-Control-Allow-Origin' com a origem da requisição,
    permitindo que requisições entre diferentes domínios (CORS) sejam realizadas.

    Parâmetros:
        - response: A resposta HTTP gerada pela aplicação.

    Retorna:
        - A resposta HTTP com os cabeçalhos de CORS definidos.
    """
    # Obtenha a origem da solicitação (ou '*')
    origin = request.headers.get('Origin', '*')

    # Defina o cabeçalho Access-Control-Allow-Origin para a origem da solicitação
    response.headers['Access-Control-Allow-Origin'] = origin

    # Defina outros cabeçalhos e métodos permitidos
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'OPTIONS, HEAD, GET, POST, DELETE, PUT'

    return response

# @app.route('/login/google', methods=['GET'])
# @limiter.limit("5 per minute")
# def login_google():
#     """
#     Rota que redireciona o usuário para a página de login do Google.

#     Returns:
#         A resposta HTTP redirecionando o usuário para a página de login do Google com o nonce gerado.
#     """
#     return google_auth.login()


# @app.route('/authorize/google')
# @limiter.limit("5 per minute")
# def authorize_google():
#     """
#     Rota de callback que é acessada após o login bem-sucedido do usuário pelo Google.
#     Ele processa o token de ID do Google, registra ou atualiza o usuário no banco de dados,
#     e redireciona o usuário para a página inicial com um token JWT.

#     Returns:
#         Redireciona o usuário para a página inicial em caso de sucesso ou para uma página de erro.
#     """
#     return google_auth.authorize()

# @app.route('/protected')
# @google_auth.google_jwt_required
# def protected_route():
#     """
#     Rota protegida que requer autenticação JWT via Google.

#     Retorna as informações do usuário autenticado.
#     """
#     user_info = session.get('user')
#     if user_info:
#         return jsonify(user_info)
#     return jsonify({"message": "User information not found in session"}), 404


@app.route('/', methods=['GET'])
def index():
    """
    Rota principal da API que retorna a data atual do servidor.

    Método:
        - GET

    Retorna:
        - Uma string com a data atual do servidor no formato "Server time: YYYY-MM-DD".
        - Código de status HTTP 200.
    """
    return f"Server time: {datetime.date.today()}", 200

class ProjectResource(Resource):
    pass  # Adicionado pass para corrigir indentação
