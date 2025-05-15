import pytest
from src.services.profile_validator import validar_perfil_advogado

def test_advogado_nome_completo_match():
    advogado = {"firstname": "Luiz Fernando", "lastname": "Carvalho"}
    perfis = [
        {"username": "luizfcarvalho", "full_name": "Luiz Fernando Carvalho", "bio": "Advogado ⚖️ OAB 12345"}
    ]
    resultado = validar_perfil_advogado(advogado, perfis)
    assert resultado is not None
    assert resultado["perfil"]["username"] == "luizfcarvalho"
    assert resultado["score"] >= 70

def test_advogado_nome_abreviado():
    advogado = {"firstname": "Luiz Fernando", "lastname": "Carvalho"}
    perfis = [
        {"username": "lfcarvalho", "full_name": "L. F. Carvalho", "bio": "Direito Trabalhista 👨‍⚖️"}
    ]
    resultado = validar_perfil_advogado(advogado, perfis)
    assert resultado is not None
    assert resultado["perfil"]["username"] == "lfcarvalho"
    assert resultado["score"] >= 70

def test_advogado_bio_emojis():
    advogado = {"firstname": "Ana Paula", "lastname": "Mendes"}
    perfis = [
        {"username": "anapmendes", "full_name": "Ana Paula Mendes", "bio": "Advogada 🧑‍⚖️ 📚"}
    ]
    resultado = validar_perfil_advogado(advogado, perfis)
    assert resultado is not None
    assert resultado["perfil"]["username"] == "anapmendes"
    assert resultado["score"] >= 70

def test_advogado_username_termo_juridico():
    advogado = {"firstname": "Carlos", "lastname": "Silva"}
    perfis = [
        {"username": "carlossilva.advogado", "full_name": "Carlos Silva", "bio": "Especialista em Direito"}
    ]
    resultado = validar_perfil_advogado(advogado, perfis)
    assert resultado is not None
    assert resultado["perfil"]["username"] == "carlossilva.advogado"
    assert resultado["score"] >= 70

def test_advogado_bloqueio_sobrenome_comum():
    advogado = {"firstname": "João Victor", "lastname": "Silva Galiote"}
    perfis = [
        {"username": "silvagaliote.adv", "full_name": "Silva Galiote Advocacia", "bio": "Direito Empresarial | OAB 12345"}
    ]
    resultado = validar_perfil_advogado(advogado, perfis)
    assert resultado is not None, "Perfil Silva Galiote Advocacia deveria ser validado"
    assert resultado["score"] >= 70

def test_advogado_nome_invertido():
    advogado = {"firstname": "Marina", "lastname": "Barbosa"}
    perfis = [
        {"username": "barbosamarina", "full_name": "Barbosa Marina", "bio": "OAB 54321 ⚖️"}
    ]
    resultado = validar_perfil_advogado(advogado, perfis)
    assert resultado is not None
    assert resultado["perfil"]["username"] == "barbosamarina"
    assert resultado["score"] >= 70

def test_advogado_score_baixo():
    advogado = {"firstname": "Pedro", "lastname": "Lima"}
    perfis = [
        {"username": "pedrolima", "full_name": "Pedro Lima", "bio": "Dentista"}
    ]
    resultado = validar_perfil_advogado(advogado, perfis)
    assert resultado is None

def test_advogado_nome_composto_longo_bio_detalhada():
    advogado = {"firstname": "Maria Alice", "lastname": "de Souza Campos Guimarães"}
    perfis = [
        {"username": "mariaalicescg_adv", "full_name": "Maria Alice de S. Campos Guimarães", "bio": "Advogada especialista em Direito de Família e Sucessões | OAB/SP 123.456 | Contato: (11) 99999-8888 ⚖️📚"}
    ]
    resultado = validar_perfil_advogado(advogado, perfis)
    assert resultado is not None, "Perfil de Maria Alice deveria ser validado"
    assert resultado["perfil"]["username"] == "mariaalicescg_adv"
    assert resultado["score"] >= 70

def test_advogado_abreviaturas_comuns_bio_multiplos_termos():
    advogado = {"firstname": "José Carlos", "lastname": "Ferreira Junior"}
    perfis = [
        {"username": "jcfjunior.advocacia", "full_name": "Jose Carlos Ferreira Junior", "bio": "Advocacia Criminal e Cível 👨‍⚖️ | Consultoria Jurídica Especializada 📜 | OAB 98765"}
    ]
    resultado = validar_perfil_advogado(advogado, perfis)
    assert resultado is not None, "Perfil de José Carlos deveria ser validado"
    assert resultado["perfil"]["username"] == "jcfjunior.advocacia"
    assert resultado["score"] >= 70

def test_advogado_nome_similar_outra_profissao():
    advogado = {"firstname": "Roberto", "lastname": "Almeida"}
    perfis = [
        {"username": "roberto.almeida.eng", "full_name": "Roberto Almeida", "bio": "Engenheiro Civil | Projetos Estruturais e Consultoria Técnica 🏗️"}
    ]
    resultado = validar_perfil_advogado(advogado, perfis)
    assert resultado is None, "Perfil de Roberto (Engenheiro) não deveria ser validado"

def test_advogado_nome_valido_sem_termos_juridicos():
    advogado = {"firstname": "Beatriz", "lastname": "Costa"}
    perfis = [
        {"username": "bia_costa_oficial", "full_name": "Beatriz Costa", "bio": "Apaixonada por viagens e fotografia ✈️📸"}
    ]
    resultado = validar_perfil_advogado(advogado, perfis)
    assert resultado is not None, "Perfil de Beatriz (sem termos jurídicos) DEVERIA ser validado" 