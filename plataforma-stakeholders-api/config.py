import os
import configparser

from urllib.parse import quote_plus


def get_env_or_default(key, default):
    """Retorna o valor da variável de ambiente ou um valor padrão."""
    return os.environ.get(key, default)


def load_general_config(app, config):
    if "General" in config:
        general = config["General"]
        app.config['SECRET_KEY'] = general.get("secret_key", get_env_or_default('STAKEHOLDERS_API_SECRET_KEY', ''))
        app.config['ENCRYPTION_KEY'] = general.get("encryption_key", get_env_or_default('STAKEHOLDERS_API_ENCRYPTION_KEY', ''))
        app.config["JWT_ACCESS_TOKEN_EXPIRES"] = general.get("token_expires", get_env_or_default(
            'STAKEHOLDERS_API_JWT_ACCESS_TOKEN_EXPIRES', '3600'))
        app.config['DEBUG'] = general.get("debug", get_env_or_default('STAKEHOLDERS_API_DEBUG_MODE', 'false')).lower() in [
                                  'true', '1', 't']
        app.config['LOG_MODE'] = general.get("log_mode", get_env_or_default('STAKEHOLDERS_API_LOG_MODE', ''))
        app.config['LOG_COUNT'] = int(general.get("log_count", get_env_or_default('STAKEHOLDERS_API_LOG_COUNT', '10')))
    else:
        app.config['SECRET_KEY'] = get_env_or_default('STAKEHOLDERS_API_SECRET_KEY', '')
        app.config['ENCRYPTION_KEY'] = get_env_or_default('STAKEHOLDERS_API_ENCRYPTION_KEY', '')
        app.config["JWT_ACCESS_TOKEN_EXPIRES"] = get_env_or_default('STAKEHOLDERS_JWT_ACCESS_TOKEN_EXPIRES',
                                                                    '3600')
        app.config['DEBUG'] = get_env_or_default('STAKEHOLDERS_API_DEBUG_MODE', 'false').lower() in ['true', '1', 't']
        app.config['LOG_MODE'] = get_env_or_default('STAKEHOLDERS_API_LOG_MODE', '')
        app.config['LOG_COUNT'] = int(get_env_or_default('STAKEHOLDERS_API_LOG_COUNT', '10'))

def load_postgresql_config(app, config):
    if "PostgreSQL" in config:
        postgresql = config["PostgreSQL"]
        user = postgresql.get("user", get_env_or_default('STAKEHOLDERS_API_POSTGRES_USER', ''))
        password = quote_plus(postgresql.get("password", get_env_or_default('STAKEHOLDERS_API_POSTGRES_PASSWORD', '')))
        host = postgresql.get("host", get_env_or_default('STAKEHOLDERS_API_POSTGRES_HOST', ''))
        port = postgresql.get("port", get_env_or_default('STAKEHOLDERS_API_POSTGRES_PORT', ''))
        database = postgresql.get("database", get_env_or_default('STAKEHOLDERS_API_POSTGRES_DB', ''))
    else:
        # Use environment variables if section is missing
        user = get_env_or_default('STAKEHOLDERS_API_POSTGRES_USER', '')
        password = quote_plus(get_env_or_default('STAKEHOLDERS_API_POSTGRES_PASSWORD', ''))
        host = get_env_or_default('STAKEHOLDERS_API_POSTGRES_HOST', '')
        port = get_env_or_default('STAKEHOLDERS_API_POSTGRES_PORT', '')
        database = get_env_or_default('STAKEHOLDERS_API_POSTGRES_DB', '')

    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{user}:{password}@{host}:{port}/{database}'

def load_redis_config(app, config):
    if "Redis" in config:
        redis = config["Redis"]
        app.config['REDIS_HOST'] = redis.get("host", get_env_or_default('STAKEHOLDERS_API_REDIS_HOST', 'localhost'))
        app.config['REDIS_PORT'] = redis.get("port", get_env_or_default('STAKEHOLDERS_API_REDIS_PORT', '6379'))
        app.config['REDIS_DB'] = redis.get("database", get_env_or_default('STAKEHOLDERS_API_REDIS_DB', '0'))
        app.config['REDIS_USER'] = redis.get("user", get_env_or_default('STAKEHOLDERS_API_REDIS_USER', 'default'))
        app.config['REDIS_PASSWORD'] = redis.get("password", get_env_or_default('STAKEHOLDERS_API_REDIS_PASSWORD', 'redis123'))
        app.config['REDIS_CACHE_TIMEOUT'] = int(redis.get("cache_timeout", get_env_or_default('STAKEHOLDERS_API_REDIS_CACHE_TIMEOUT', '300')))
    else:
        # Use environment variables if section is missing
        app.config['REDIS_HOST'] = get_env_or_default('STAKEHOLDERS_API_REDIS_HOST', 'localhost')
        app.config['REDIS_PORT'] = get_env_or_default('STAKEHOLDERS_API_REDIS_PORT', '6379')
        app.config['REDIS_DB'] = get_env_or_default('STAKEHOLDERS_API_REDIS_DB', '0')
        app.config['REDIS_USER'] = get_env_or_default('STAKEHOLDERS_API_REDIS_USER', 'default')
        app.config['REDIS_PASSWORD'] = get_env_or_default('STAKEHOLDERS_API_REDIS_PASSWORD', 'redis123')
        app.config['REDIS_CACHE_TIMEOUT'] = int(get_env_or_default('STAKEHOLDERS_API_REDIS_CACHE_TIMEOUT', '300'))

    # Mantém a compatibilidade com o código existente que usa IPBAN_REDIS_URL
    redis_url = f"redis://{app.config['REDIS_USER']}:{quote_plus(app.config['REDIS_PASSWORD'])}@{app.config['REDIS_HOST']}:{app.config['REDIS_PORT']}/{app.config['REDIS_DB']}"
    app.config['IPBAN_REDIS_URL'] = redis_url
    return redis_url

def load_google_config(app, config):
    if "Google" in config:
        general = config["Google"]
        app.config['GOOGLE_CLIENT_ID'] = general.get("client_id", get_env_or_default('STAKEHOLDERS_API_GOOGLE_CLIENT_ID', ''))
        app.config['GOOGLE_CLIENT_SECRET'] = general.get("client_secret", get_env_or_default('STAKEHOLDERS_API_GOOGLE_CLIENT_SECRET', ''))
    else:
        app.config['GOOGLE_CLIENT_ID'] = get_env_or_default('STAKEHOLDERS_API_GOOGLE_CLIENT_ID', '')
        app.config['GOOGLE_CLIENT_SECRET'] = get_env_or_default('STAKEHOLDERS_API_GOOGLE_CLIENT_SECRET', '')

def read_config(app):
    config = configparser.ConfigParser()
    config_file = 'config.ini'

    if os.path.isfile(config_file):
        config.read(config_file)

    load_general_config(app, config)
    load_postgresql_config(app, config)
    load_redis_config(app, config)
    load_google_config(app, config)
