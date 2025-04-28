"""
Este módulo inicializa todos os modelos ORM utilizados pela aplicação.

Os modelos são importados e registrados no SQLAlchemy nesta ordem específica para evitar
potenciais conflitos e problemas de dependência entre os modelos.

Cada modelo é carregado de acordo com sua prioridade de uso, ou seja, os modelos que
dependem de outros são carregados após os modelos dos quais dependem.

- Sample: Modelo inicial carregado, sem dependências de outros modelos.

Se forem adicionados novos modelos ao sistema, é importante garantir que sejam importados
aqui na ordem correta para evitar conflitos.
"""

from .base_model import BaseModel
from .advogado import Advogado
from .empresa import Empresa
from .escritorio import Escritorio
from .pessoa import Pessoa
from .porte_empresa import PorteEmpresa
from .segmento_empresa import SegmentoEmpresa
from .tipo_entidade import TipoEntidade
from .projeto import Projeto
from .endereco import Endereco
from .email import Email
from .telefone import Telefone
from .cnae_secundario import CnaeSecundario
from .log_consulta import LogConsulta
from .consulta import Consulta
from .tipo_log import TipoLog


