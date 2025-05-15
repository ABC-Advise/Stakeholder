import pytest
from src.services.profile_validator import ProfileValidator

validator = ProfileValidator()

@pytest.mark.asyncio
async def test_validar_perfil_advogado():
    validator = ProfileValidator()
    
    # Dados de teste
    advogado = {
        "nome": "João Silva",
        "oab": "123456/SP"
    }
    
    perfis_instagram = [
        {
            "username": "joaosilva",
            "full_name": "João Silva",
            "bio": "Advogado OAB/SP 123456",
            "is_private": False
        },
        {
            "username": "outro_usuario",
            "full_name": "Outro Nome",
            "bio": "Outra bio",
            "is_private": False
        }
    ]
    
    # Testa a validação
    perfil_valido, todos_perfis = await validator.validar_perfil_advogado(advogado, perfis_instagram)
    
    # Verifica se o perfil correto foi selecionado
    assert perfil_valido is not None
    assert perfil_valido["perfil"]["username"] == "joaosilva"
    assert perfil_valido["score"] > 0
    
    # Verifica se todos os perfis foram processados
    assert len(todos_perfis) == 2

@pytest.mark.asyncio
async def test_advogado_nome_completo_match():
    advogado = {"firstname": "Luiz Fernando", "lastname": "Carvalho"}
    perfis = [
        {"username": "luizfcarvalho", "full_name": "Luiz Fernando Carvalho", "bio": "Advogado ⚖️ OAB 12345"}
    ]
    resultado, _ = await validator.validar_perfil_advogado(advogado, perfis)
    assert resultado is not None
    assert resultado["perfil"]["username"] == "luizfcarvalho"
    assert resultado["score"] >= 70

@pytest.mark.asyncio
async def test_advogado_nome_abreviado():
    advogado = {"firstname": "Luiz Fernando", "lastname": "Carvalho"}
    perfis = [
        {"username": "lfcarvalho", "full_name": "L. F. Carvalho", "bio": "Direito Trabalhista 👨‍⚖️"}
    ]
    resultado, _ = await validator.validar_perfil_advogado(advogado, perfis)
    assert resultado is not None
    assert resultado["perfil"]["username"] == "lfcarvalho"
    assert resultado["score"] >= 70

@pytest.mark.asyncio
async def test_advogado_bio_emojis():
    advogado = {"firstname": "Ana Paula", "lastname": "Mendes"}
    perfis = [
        {"username": "anapmendes", "full_name": "Ana Paula Mendes", "bio": "Advogada 🧑‍⚖️ 📚"}
    ]
    resultado, _ = await validator.validar_perfil_advogado(advogado, perfis)
    assert resultado is not None
    assert resultado["perfil"]["username"] == "anapmendes"
    assert resultado["score"] >= 70

@pytest.mark.asyncio
async def test_advogado_username_termo_juridico():
    advogado = {"firstname": "Carlos", "lastname": "Silva"}
    perfis = [
        {"username": "carlossilva.advogado", "full_name": "Carlos Silva", "bio": "Especialista em Direito"}
    ]
    resultado, _ = await validator.validar_perfil_advogado(advogado, perfis)
    assert resultado is not None
    assert resultado["perfil"]["username"] == "carlossilva.advogado"
    assert resultado["score"] >= 70

@pytest.mark.asyncio
async def test_advogado_bloqueio_sobrenome_comum():
    advogado = {"firstname": "João Victor", "lastname": "Silva Galiote"}
    perfis = [
        {"username": "silvagaliote.adv", "full_name": "Silva Galiote Advocacia", "bio": "Direito Empresarial | OAB 12345"}
    ]
    resultado, _ = await validator.validar_perfil_advogado(advogado, perfis)
    assert resultado is not None, "Perfil Silva Galiote Advocacia deveria ser validado"
    assert resultado["score"] >= 70

@pytest.mark.asyncio
async def test_advogado_nome_invertido():
    advogado = {"firstname": "Marina", "lastname": "Barbosa"}
    perfis = [
        {"username": "barbosamarina", "full_name": "Barbosa Marina", "bio": "OAB 54321 ⚖️"}
    ]
    resultado, _ = await validator.validar_perfil_advogado(advogado, perfis)
    assert resultado is not None
    assert resultado["perfil"]["username"] == "barbosamarina"
    assert resultado["score"] >= 70

@pytest.mark.asyncio
async def test_advogado_score_baixo():
    advogado = {"firstname": "Pedro", "lastname": "Lima"}
    perfis = [
        {"username": "pedrolima", "full_name": "Pedro Lima", "bio": "Dentista"}
    ]
    resultado, _ = await validator.validar_perfil_advogado(advogado, perfis)
    assert resultado is None

@pytest.mark.asyncio
async def test_advogado_nome_composto_longo_bio_detalhada():
    advogado = {"firstname": "Maria Alice", "lastname": "de Souza Campos Guimarães"}
    perfis = [
        {"username": "mariaalicescg_adv", "full_name": "Maria Alice de S. Campos Guimarães", "bio": "Advogada especialista em Direito de Família e Sucessões | OAB/SP 123.456 | Contato: (11) 99999-8888 ⚖️📚"}
    ]
    resultado, _ = await validator.validar_perfil_advogado(advogado, perfis)
    assert resultado is not None, "Perfil de Maria Alice deveria ser validado"
    assert resultado["perfil"]["username"] == "mariaalicescg_adv"
    assert resultado["score"] >= 70

@pytest.mark.asyncio
async def test_advogado_abreviaturas_comuns_bio_multiplos_termos():
    advogado = {"firstname": "José Carlos", "lastname": "Ferreira Junior"}
    perfis = [
        {"username": "jcfjunior.advocacia", "full_name": "Jose Carlos Ferreira Junior", "bio": "Advocacia Criminal e Cível 👨‍⚖️ | Consultoria Jurídica Especializada 📜 | OAB 98765"}
    ]
    resultado, _ = await validator.validar_perfil_advogado(advogado, perfis)
    assert resultado is not None, "Perfil de José Carlos deveria ser validado"
    assert resultado["perfil"]["username"] == "jcfjunior.advocacia"
    assert resultado["score"] >= 70

@pytest.mark.asyncio
async def test_advogado_nome_similar_outra_profissao():
    advogado = {"firstname": "Roberto", "lastname": "Almeida"}
    perfis = [
        {"username": "roberto.almeida.eng", "full_name": "Roberto Almeida", "bio": "Engenheiro Civil | Projetos Estruturais e Consultoria Técnica 🏗️"}
    ]
    resultado, _ = await validator.validar_perfil_advogado(advogado, perfis)
    assert resultado is None, "Perfil de Roberto (Engenheiro) não deveria ser validado"

@pytest.mark.asyncio
async def test_advogado_nome_valido_sem_termos_juridicos():
    advogado = {"firstname": "Beatriz", "lastname": "Costa"}
    perfis = [
        {"username": "bia_costa_oficial", "full_name": "Beatriz Costa", "bio": "Apaixonada por viagens e fotografia ✈️📸"}
    ]
    resultado, _ = await validator.validar_perfil_advogado(advogado, perfis)
    assert resultado is not None, "Perfil de Beatriz (sem termos jurídicos) DEVERIA ser validado" 