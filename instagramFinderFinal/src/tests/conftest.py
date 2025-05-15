import pytest
import asyncio
from typing import AsyncGenerator
from src.config.database import AsyncSessionLocal, Base, engine

@pytest.fixture(scope="session")
def event_loop():
    """Cria um event loop para os testes assíncronos."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def db_engine():
    """Cria o engine do banco de dados para os testes."""
    yield engine

@pytest.fixture(scope="function")
async def db_session(db_engine) -> AsyncGenerator:
    """Cria uma sessão do banco de dados para cada teste."""
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
        await session.close()

@pytest.fixture(autouse=True)
async def setup_database():
    """Configura o banco de dados antes de cada teste."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all) 