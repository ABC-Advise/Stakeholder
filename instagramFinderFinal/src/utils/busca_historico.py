import os
import json
from datetime import datetime, timedelta

HISTORICO_PATH = './ultimas_buscas.json'

# Carrega buscas do arquivo
def carregar_ultimas_buscas():
    if not os.path.exists(HISTORICO_PATH):
        return []
    with open(HISTORICO_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

# Salva buscas no arquivo
def salvar_ultimas_buscas(buscas):
    with open(HISTORICO_PATH, 'w', encoding='utf-8') as f:
        json.dump(buscas, f, ensure_ascii=False, indent=2)

# Registra uma nova busca
def registrar_busca(nome, tipo, status):
    print(f"[DEBUG] registrar_busca chamado: nome={nome}, tipo={tipo}, status={status}")
    buscas = carregar_ultimas_buscas()
    agora = datetime.now()
    hoje = agora.date()
    # Remove buscas antigas (>2 dias)
    buscas = [b for b in buscas if datetime.fromisoformat(b['data']).date() >= hoje - timedelta(days=1)]
    # Remove duplicatas do mesmo tipo/nome no mesmo dia
    buscas = [b for b in buscas if not (b['nome'] == nome and b['tipo'] == tipo and datetime.fromisoformat(b['data']).date() == hoje)]
    # Adiciona nova busca
    buscas.append({
        'nome': nome,
        'tipo': tipo,
        'status': status,
        'data': agora.isoformat(timespec='seconds')
    })
    salvar_ultimas_buscas(buscas)

# Retorna buscas ordenadas da mais recente para a mais antiga
def obter_ultimas_buscas():
    buscas = carregar_ultimas_buscas()
    buscas.sort(key=lambda b: b['data'], reverse=True)
    return buscas 