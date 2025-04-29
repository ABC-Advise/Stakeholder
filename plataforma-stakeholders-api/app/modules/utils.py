import re
import pandas as pd
import unicodedata

import pytz
from datetime import datetime
from app.modules.exceptions import ValidationError


def remover_acentos(texto):
    # Normaliza a string para remover acentos
    nfkd = unicodedata.normalize('NFKD', texto)
    texto_sem_acento = ''.join([c for c in nfkd if not unicodedata.combining(c)])

    # Converte para caixa alta
    return texto_sem_acento.upper()

def format_cpf(cpf):
    return str(cpf).replace('.', '').replace('-', '')

def format_cnpj(cnpj):
    return str(cnpj).replace('.', '').replace('/', '').replace('-', '')

def capitalize_first_letter(text):
    if not text:
        return ""
    return text[0].upper() + text[1:].lower()

def validar_documento(documento):
    documento = re.sub(r'\D', '', documento)  # Remove todos os caracteres não numéricos

    if len(documento) == 11:
        if not validar_cpf(documento):
            raise DocumentoInvalidoError(f"CPF {documento} inválido")
    elif len(documento) == 14:
        if not validar_cnpj(documento):
            raise ValidationError(f"CNPJ {documento} inválido")
    else:
        raise ValidationError("Documento deve ser um CPF ou CNPJ válido")

    return documento


def validar_cpf(cpf):
    # Verifica se todos os dígitos são iguais (ex: 111.111.111-11 não é válido)
    if cpf == cpf[0] * 11:
        return False

    # Cálculo do primeiro dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    digito1 = (soma * 10) % 11
    digito1 = 0 if digito1 == 10 else digito1

    # Cálculo do segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    digito2 = (soma * 10) % 11
    digito2 = 0 if digito2 == 10 else digito2

    return cpf[-2:] == f"{digito1}{digito2}"


def validar_cnpj(cnpj):
    # Verifica se todos os dígitos são iguais (ex: 11.111.111/1111-11 não é válido)
    if cnpj == cnpj[0] * 14:
        return False

    # Cálculo do primeiro dígito verificador
    pesos_1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(cnpj[i]) * pesos_1[i] for i in range(12))
    digito1 = (soma % 11)
    digito1 = 0 if digito1 < 2 else 11 - digito1

    # Cálculo do segundo dígito verificador
    pesos_2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(cnpj[i]) * pesos_2[i] for i in range(13))
    digito2 = (soma % 11)
    digito2 = 0 if digito2 < 2 else 11 - digito2

    return cnpj[-2:] == f"{digito1}{digito2}"


def data_anos_atras(anos):
    # Data atual
    data_atual = datetime.now()

    # Calcular o ano resultante
    ano_resultante = data_atual.year - anos

    # Verificar se a data resultante é válida (ajuste para 29 de fevereiro, se necessário)
    try:
        data_resultante = data_atual.replace(year=ano_resultante)
    except ValueError:
        # Se for um ano não bissexto e a data for 29 de fevereiro, ajusta para 28 de fevereiro
        data_resultante = data_atual.replace(year=ano_resultante, day=28)

    # Formatar para o padrão AAAA-MM-DD
    return data_resultante.strftime('%Y-%m-%d')


def safe_strip(value):
    # Garante que o valor seja uma string antes de aplicar strip
    return str(value).strip() if pd.notna(value) else ""

def serialize_objects(objects):
    object_list = list()
    for obj in objects:
        if hasattr(obj, "to_dict") and callable(getattr(obj, "to_dict")):
            object_list.append(obj.to_dict())

    return object_list

def converter_timezone(data):
    if data is None:
        return None
    
    # Verifica se a data tem algum timezone, se não assume que é UTC
    if data.tzinfo is None:
        data = data.replace(tzinfo=pytz.UTC)
    
    # Aplica a timezone local
    fuso = pytz.timezone('America/Sao_Paulo')
    data_fuso = data.astimezone(fuso)
        
    return data_fuso.strftime('%d-%m-%Y %H:%M:%S')



