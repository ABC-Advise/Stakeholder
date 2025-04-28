from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from config import read_config
from app.modules.error_handling import ErrorHandler
from app.modules.redis_client import RedisClient

# Inicialização da aplicação Flask
app = Flask(__name__)

# Configura a aplicação a partir do arquivo de configuração
read_config(app)

# Inicialização da extensão SQLAlchemy para interação com o banco de dados
db = SQLAlchemy(app)

redis_client = RedisClient(app)

# Inicialização da API RESTful
api = Api(app)

# Habilita o Cross-Origin Resource Sharing (CORS) para permitir comunicação entre domínios diferentes
cors = CORS(app, supports_credentials=True)

# Configuração do gerenciador de erros personalizados da aplicação
error_handler = ErrorHandler(app, db)

# Importa as rotas e modelos após a inicialização da aplicação e extensões
from app import routes
from app.models import *
