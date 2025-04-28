import datetime

from flask import request
from app import app, api
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
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Accept, X-Requested-With'
    response.headers['Access-Control-Allow-Methods'] = 'OPTIONS, HEAD, GET, POST, DELETE, PUT'
    response.headers['Access-Control-Allow-Credentials'] = 'true'

    return response

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
