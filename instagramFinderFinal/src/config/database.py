from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

# Configuração do banco de dados
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_DB = os.getenv("POSTGRES_DB")

# URL para driver assíncrono asyncpg
SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Criar engine assíncrona
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False) # echo=True para debug

# Criar fábrica de sessões assíncronas
# expire_on_commit=False é frequentemente recomendado para asyncio para evitar problemas
# se você acessar atributos de um objeto fora da sessão após o commit.
AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False, autocommit=False, autoflush=False)

Base = declarative_base()

# Dependency assíncrona (para FastAPI, por exemplo)
async def get_async_db() -> AsyncSession: # Alterado para retornar AsyncSession
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit() # Commit no final se tudo deu certo
        except Exception:
            await session.rollback() # Rollback em caso de erro
            raise
        finally:
            await session.close() # Fechar a sessão 