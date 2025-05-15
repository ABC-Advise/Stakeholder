import pytest
from sqlalchemy import text
from src.config.database import engine, SessionLocal

def test_database_connection():
    """Testa a conexão com o banco de dados."""
    try:
        # Tenta executar uma query simples
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            assert result.scalar() == 1
    except Exception as e:
        pytest.fail(f"Falha na conexão com o banco de dados: {str(e)}")

def test_schema_access():
    """Testa o acesso ao schema plataforma_stakeholders."""
    try:
        with engine.connect() as connection:
            # Verifica se o schema existe
            result = connection.execute(
                text("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'plataforma_stakeholders'")
            )
            assert result.scalar() == "plataforma_stakeholders"
    except Exception as e:
        pytest.fail(f"Falha ao acessar o schema: {str(e)}")

def test_tables_access():
    """Testa o acesso às tabelas principais."""
    tables = ["empresa", "pessoa", "advogado", "relacionamentos"]
    schema = "plataforma_stakeholders"
    
    try:
        with engine.connect() as connection:
            for table in tables:
                # Verifica se a tabela existe
                result = connection.execute(
                    text(f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{schema}' AND table_name = '{table}'")
                )
                assert result.scalar() == table
    except Exception as e:
        pytest.fail(f"Falha ao acessar as tabelas: {str(e)}")

def test_session_creation():
    """Testa a criação de uma sessão do banco de dados."""
    try:
        db = SessionLocal()
        assert db is not None
        db.close()
    except Exception as e:
        pytest.fail(f"Falha ao criar sessão do banco de dados: {str(e)}") 