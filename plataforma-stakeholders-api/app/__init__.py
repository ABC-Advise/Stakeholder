from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_ipban import IpBan
from flask_cors import CORS
from flask_limiter.util import get_remote_address

from config import read_config
from app.modules.error_handling import ErrorHandler
from app.modules.redis_client import RedisClient

# Inicialização da aplicação Flask
app = Flask(__name__)

# Configura a aplicação a partir do arquivo de configuração
read_config(app)

# Habilita o log de queries SQL (remover em produção)
app.config['SQLALCHEMY_ECHO'] = True

# Inicialização da extensão SQLAlchemy para interação com o banco de dados
db = SQLAlchemy(app)

redis_client = RedisClient(app)

# Inicialização da API RESTful
api = Api(app)

# Configuração do JWT (JSON Web Token) para autenticação
jwt = JWTManager(app)

# Inicialização do Limiter para limitar o número de requisições por IP
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["5 per second"],  # Limita 5 requisições por segundo por IP
    storage_uri=app.config.get('IPBAN_REDIS_URL')  # Utiliza Redis para armazenar limites
)

# Inicialização do IpBan para bloquear IPs com comportamento malicioso
ipban = IpBan(app)

# Habilita o Cross-Origin Resource Sharing (CORS) para permitir comunicação entre domínios diferentes
cors = CORS(app, supports_credentials=True)

# Configuração do gerenciador de erros personalizados da aplicação
error_handler = ErrorHandler(app, db)

# Configuração do Google OAuth
# google_auth = GoogleAuth(app)

# Importa as rotas e modelos após a inicialização da aplicação e extensões
from app import routes
from app.models import *
