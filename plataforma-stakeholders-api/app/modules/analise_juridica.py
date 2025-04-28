import requests
import json
import os

from itertools import chain

from app import db
from app.modules.objects.advogado import Advogado
from app.modules.utils import validar_documento, data_anos_atras
from datetime import datetime, timezone


class AnaliseJuridica:
    def __init__(self, documento, consulta_id, local_tests=False, save_requests=False, is_stakeholder_advogado=False, logger=None):
        self.__url = "example" if local_tests else "https://api.escavador.com"
        self.__token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiZTU0N2UxZDc0M2E0YjcxYzZkNmVjZTEzNzhkNzNlYTY1OTYyOGJhYjYyNmQ1ODA2ZmQyMzQyMDRjOTgyNTU4MjkxODgyMDYyYmVjNzFjZjQiLCJpYXQiOjE3MzAzMTI4MjYuNzUyNDEzLCJuYmYiOjE3MzAzMTI4MjYuNzUyNDE1LCJleHAiOjIwNDU4NDU2MjYuNzQ4NjYyLCJzdWIiOiIxODg2NTk2Iiwic2NvcGVzIjpbImFjZXNzYXJfYXBpX3BhZ2EiXX0.rYtSjo03QTBmCN25gKD1tkvvLMBnwE8o8QlUK26-oNGRKaXU8YWSgFga8dzEh-b3arfl9iwX8wAnck5kb8h1iD7AGj_0WEtiapA0Q14tcs3NbVHl_qHT6o7D8mpus7RzlQUdM1iGlqSasOBNQOdTnnV4TXP9-LlsGn2uTGiegaQQGSWv9YR919FArLOaiqvZxu6VDYhUFCzzf7GboxfLnz5md1xsTY1LwQJGqetvFJXbnVPjDGVlJdLNHc2WBvK7NduirmD_f_8KJlXLWTxP7OGBpE9R57nEo2AyHcjOpdJZo5A0bcpsB99FH46cbHiZCZ5H01NL39AOuAGillSP32MUdMLu9nhPKXUg9oGOGrbfBrW8QoFhqWAg9GmwffVj_NbKP8vyeN1iTgScHMBN3OGotSrPQkA-vCT6ZxtJWyJrBcMs27TrJr5tYu-0XP95f-33Pvb5eG58CYouk8du7iHvJ-PwJUbGC-hNXzL5sHQDfeh9kIg1kOg7uBQzBSsspbIB6r0vsbNpxcTcz6LrGt1uW4WWMn6UxmYE941jBbq8JZZC2vunErl-oUjDiTdGqX5_zk9s1kCRKKF1yr6QFWbDzcF27neDEDKXSo1iy-wKOG-P9h8M2D_Hyk2iNUD4igAbcT4blpsiVOP01IR7NsLG60dwc1zVo2pZ1eJU8tI"
        self.__advogados = []
        self.__stakeholder_advogado = None
        self.__documento = validar_documento(documento)
        self.__is_stakeholder_advogado = is_stakeholder_advogado
        self.__inseridos = set()
        self.__inseridos = set()
        self.__ids = dict()
        self.__save_requests = save_requests
        self.__logger = logger
        self.__consulta_id = consulta_id

    @property
    def documento(self):
        return self.__documento
    
    @property
    def is_stakeholder_advogado(self):
        return self.__is_stakeholder_advogado
    
    @property
    def stakeholder_advogado(self):
        return self.__stakeholder_advogado

    @property
    def advogados(self):
        temp = self.__advogados
        if self.__stakeholder_advogado:
            temp.append(self.__stakeholder_advogado)
            
        return temp
    
    @property
    def consulta_id(self):
        return self.__consulta_id

    def start(self):
        self.__advogados = self.__get_processos_cpf_cnpj(self.documento)

    def save(self):
        if not self.__advogados and not self.__stakeholder_advogado:
            return

        self.__commit(self.__advogados, self.__stakeholder_advogado)

    @staticmethod
    def __salvar_json(self, cpf_cnpj, data, consulta_id):
        """Salva o JSON no arquivo, usando o `oab_numero` como nome."""
        nome_arquivo = os.path.join("Escavador/processos_cpf_cnpj", f"{cpf_cnpj}.json")
        try:
            with open(nome_arquivo, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print(f"Arquivo salvo: {nome_arquivo}")
        except Exception as e:
            print(f"Erro ao salvar o arquivo {nome_arquivo}: {str(e)}")

    def __get_processos_cpf_cnpj(self, cpf_cnpj):
        url = f"{self.__url}/api/v2/envolvido/processos"
        params = {'cpf_cnpj': cpf_cnpj,
                  "data_minima": data_anos_atras(3)}
        headers = {'Authorization': f'Bearer {self.__token}'}

        try:
            print(f"Iniciando busca de advogados do stakeholder {self.__documento}...")
            self.__logger.add_log(
                mensagem=f"Iniciando busca de advogados do stakeholder {self.__documento}...",
                tipo_log="INFO",
                consulta_id=self.__consulta_id,
                data_log=datetime.now(timezone.utc)
            )
            
            response = requests.get(url, params=params, headers=headers)
            if response.status_code != 200:
                print(f"Nenhum processo encontrado para o stakeholder {self.__documento}.")
                self.__logger.add_log(
                    mensagem=f"Nenhum processo encontrado para o stakeholder {self.__documento}.",
                    tipo_log="INFO",
                    consulta_id=self.__consulta_id,
                    data_log=datetime.now(timezone.utc)
                )
                return []

            if self.__save_requests:
                self.__salvar_json(cpf_cnpj, response.json(), self.__consulta_id)

            # Achatar todas as fontes e envolvidos diretamente
            envolvidos = chain.from_iterable(
                fonte.get('envolvidos', [])
                for item in response.json().get('items', [])
                for fonte in item.get('fontes', [])
            )

            # Filtrar os envolvidos cujo CNPJ corresponde ao CPF/CNPJ fornecido
            envolvidos_filtrados = (envolvido for envolvido in envolvidos if envolvido.get('cnpj') == str(cpf_cnpj) or envolvido.get('cpf') == str(cpf_cnpj))

            # Adicionar advogados únicos
            for envolvido in envolvidos_filtrados:
                if self.__is_stakeholder_advogado:
                    for oab in envolvido.get('oabs', []):
                        if oab.get("tipo") == 'ADVOGADO':
                            self.__stakeholder_advogado = envolvido
                            self.__stakeholder_advogado['stakeholder'] = True
                            self.__stakeholder_advogado['oabs'] = [oab]
                            break
                
                for advogado in envolvido.get('advogados', []):
                    if not advogado.get("oabs", None):
                        continue
                    # Evitar duplicatas com base no nome
                    if not any(d['nome'] == advogado['nome'] for d in self.__advogados):
                        self.__advogados.append(advogado)

            print(f"Finalizando busca de advogados do stakeholder {self.__documento}"
                f" - {len(self.__advogados)} Advogados encontrados.")
            self.__logger.add_log(
                mensagem=f"Finalizando busca de advogados do stakeholder {self.__documento}"
                f" - {len(self.__advogados)} Advogados encontrados.",
                tipo_log="INFO",
                consulta_id=self.__consulta_id,
                data_log=datetime.now(timezone.utc)
            )

            self.__advogados = [Advogado(**dados) for dados in self.__advogados]
            
            if self.__stakeholder_advogado:
                self.__stakeholder_advogado = Advogado(**self.__stakeholder_advogado)
            
        except Exception as e:
            print(f"(/api/v2/envolvido/processos) Erro inesperado: {str(e)}")
            self.__logger.add_log(
                mensagem=f"(/api/v2/envolvido/processos) Erro inesperado: {str(e)}",
                tipo_log="ERROR",
                consulta_id=self.__consulta_id,
                data_log=datetime.now(timezone.utc)
            )
        
        return self.__advogados

    def __commit(self, envolvidos, stakeholder_advogado):
        if envolvidos:
            for envolvido in envolvidos:
                if isinstance(envolvido, Advogado):
                    self.__commit_advogado(envolvido, False)
        
        if stakeholder_advogado:
            if isinstance(stakeholder_advogado, Advogado):
                self.__commit_advogado(stakeholder_advogado, True)
            

    def __commit_advogado(self, advogado, stakeholder_advogado=False):
        from app.models.advogado import Advogado
        from app.models.empresa import Empresa
        from app.models.pessoa import Pessoa
        from app.models.relacionamentos import Relacionamentos
        
        stakeholder = Empresa.query.filter_by(cnpj=self.__documento).first() if len(
            self.__documento) == 14 else Pessoa.query.filter_by(cpf=self.__documento).first()

        if not stakeholder or not len(advogado.oabs):
            print(f"Advogado sem OABS: {advogado}")
            self.__logger.add_log(
                mensagem=f"Advogado sem OABS: {advogado}",
                tipo_log="INFO",
                consulta_id=self.__consulta_id,
                data_log=datetime.now(timezone.utc)
            )
            return

        if not advogado or advogado in self.__inseridos:
            print(f"Pulando registro: {advogado}")
            self.__logger.add_log(
                mensagem=f"Pulando registro: {advogado}",
                tipo_log="INFO",
                consulta_id=self.__consulta_id,
                data_log=datetime.now(timezone.utc)
            )
            return

        query_advogado = Advogado.query.filter_by(oab=str(advogado.oabs[0].numero)).first()

        new_data = {**advogado.to_dict()}
        try:
            if query_advogado:
                query_advogado.update_from_dict(new_data)
                db.session.commit()
                
                print(f"Advogado {query_advogado.oab} atualizada")
                self.__logger.add_log(
                    mensagem=f"Advogado {query_advogado.oab} atualizada",
                    tipo_log="INFO",
                    consulta_id=self.__consulta_id,
                    data_log=datetime.now(timezone.utc)
                )
            else:
                query_advogado = Advogado(**advogado.to_dict())

                db.session.add(query_advogado)
                db.session.commit()
                
                print(f"Advogado {query_advogado.oab} cadastrada")
                self.__logger.add_log(
                    mensagem=f"Advogado {query_advogado.oab} cadastrada",
                    tipo_log="INFO",
                    consulta_id=self.__consulta_id,
                    data_log=datetime.now(timezone.utc)
                )
                
            self.__inseridos.add(query_advogado)
            self.__ids[advogado.oabs[0].numero] = query_advogado.advogado_id

            rel = Relacionamentos.query.filter_by(
                entidade_origem_id=stakeholder.empresa_id if len(self.__documento) == 14 else stakeholder.pessoa_id,
                tipo_origem_id=3 if len(self.__documento) == 14 else 1,
                entidade_destino_id=query_advogado.advogado_id,
                tipo_destino_id=4).first()

            if not rel:
                rel = Relacionamentos(
                    entidade_origem_id=stakeholder.empresa_id if len(self.__documento) == 14 else stakeholder.pessoa_id,
                    tipo_origem_id=3 if len(self.__documento) == 14 else 1,
                    entidade_destino_id=query_advogado.advogado_id,
                    tipo_destino_id=4,
                    tipo_relacao_id=26 if not stakeholder_advogado else 27)
                db.session.add(rel)
                db.session.commit()
            elif stakeholder_advogado:
                rel.tipo_relacao_id = 27
                db.session.commit()
                            
        except Exception as e:
            print(e)
            self.__logger.add_log(
                mensagem=e,
                tipo_log="ERROR",
                consulta_id=self.__consulta_id,
                data_log=datetime.now(timezone.utc)
            )
            
