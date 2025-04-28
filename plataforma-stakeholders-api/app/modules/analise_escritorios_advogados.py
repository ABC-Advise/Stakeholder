import requests
import json
import os

from itertools import chain

from app import db
from app.modules.objects.processo import Processo
from app.modules.objects.pessoa_fisica import PessoaFisica
from app.modules.objects.pessoa_juridica import PessoaJuridica
from app.modules.utils import data_anos_atras
from app.modules.consulta_stakeholder import ConsultaStakeholder
from datetime import datetime, timezone


class AnaliseEscritoriosAdvogados:
    def __init__(self, documento, estado, consulta_id, em_prospecao=False, local_tests=False,
                 directdata_local=False, save_requests=False, logger=None):
        self.__stakeholder_processos = None
        self.__url = "example" if local_tests else "https://api.escavador.com"
        self.__token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiZTU0N2UxZDc0M2E0YjcxYzZkNmVjZTEzNzhkNzNlYTY1OTYyOGJhYjYyNmQ1ODA2ZmQyMzQyMDRjOTgyNTU4MjkxODgyMDYyYmVjNzFjZjQiLCJpYXQiOjE3MzAzMTI4MjYuNzUyNDEzLCJuYmYiOjE3MzAzMTI4MjYuNzUyNDE1LCJleHAiOjIwNDU4NDU2MjYuNzQ4NjYyLCJzdWIiOiIxODg2NTk2Iiwic2NvcGVzIjpbImFjZXNzYXJfYXBpX3BhZ2EiXX0.rYtSjo03QTBmCN25gKD1tkvvLMBnwE8o8QlUK26-oNGRKaXU8YWSgFga8dzEh-b3arfl9iwX8wAnck5kb8h1iD7AGj_0WEtiapA0Q14tcs3NbVHl_qHT6o7D8mpus7RzlQUdM1iGlqSasOBNQOdTnnV4TXP9-LlsGn2uTGiegaQQGSWv9YR919FArLOaiqvZxu6VDYhUFCzzf7GboxfLnz5md1xsTY1LwQJGqetvFJXbnVPjDGVlJdLNHc2WBvK7NduirmD_f_8KJlXLWTxP7OGBpE9R57nEo2AyHcjOpdJZo5A0bcpsB99FH46cbHiZCZ5H01NL39AOuAGillSP32MUdMLu9nhPKXUg9oGOGrbfBrW8QoFhqWAg9GmwffVj_NbKP8vyeN1iTgScHMBN3OGotSrPQkA-vCT6ZxtJWyJrBcMs27TrJr5tYu-0XP95f-33Pvb5eG58CYouk8du7iHvJ-PwJUbGC-hNXzL5sHQDfeh9kIg1kOg7uBQzBSsspbIB6r0vsbNpxcTcz6LrGt1uW4WWMn6UxmYE941jBbq8JZZC2vunErl-oUjDiTdGqX5_zk9s1kCRKKF1yr6QFWbDzcF27neDEDKXSo1iy-wKOG-P9h8M2D_Hyk2iNUD4igAbcT4blpsiVOP01IR7NsLG60dwc1zVo2pZ1eJU8tI"
        self.__processos = []
        self.__envolvidos = []
        self.__tipo_relacionamento = dict()
        self.__stakeholder = None
        self.__documento = documento
        self.__estado = estado
        self.__local_tests = local_tests
        self.__directdata_local = directdata_local
        self.__em_prospecao = em_prospecao
        self.__inseridos = set()
        self.__ids = dict()
        self.__save_requests = save_requests
        self.__logger = logger
        self.__consulta_id = consulta_id
        
    @property
    def consultados(self):
        return self.__consultados

    @property
    def tipo_relacionamento(self):
        return self.__tipo_relacionamento

    @property
    def documento(self):
        return self.__documento

    @property
    def envolvidos(self):
        return self.__envolvidos
    
    @property
    def consulta_id(self):
        return self.__consulta_id

    def start(self):
        self.__stakeholder = self.__get_envolvidos_oab(self.__documento, self.__estado)
        # self.__stakeholder_processos = self.__get_processos_oab(self.__documento, self.__estado)
        self.__get_envolvidos_info()

    def save(self):
        if not self.__stakeholder:
            return

        self.__commit(self.__stakeholder)

    def __get_envolvidos_info(self):
        inseridos = set()
        ids = dict()

        print(f"Iniciando busca de clientes para o nº OAB {self.__documento}...")
        self.__logger.add_log(
            mensagem=f"Iniciando busca de clientes para o nº OAB {self.__documento}...",
            tipo_log="INFO",
            consulta_id=self.__consulta_id,
            data_log=datetime.now(timezone.utc)
        )
        
        for i in range(len(self.__envolvidos)):
            documento = self.__envolvidos[i].cpf if isinstance(self.__envolvidos[i], PessoaFisica) \
                                                else self.__envolvidos[i].cnpj
            consulta_stakeholder = ConsultaStakeholder(documento, is_stakeholder=False, consulta_id=self.__consulta_id, local_tests=self.__directdata_local,
                                                       save_requests=self.__save_requests, camadas_sociedade=0,
                                                       camadas_parentescos=0, lazy_start=True, logger=self.__logger)
            consulta_stakeholder.inseridos = inseridos
            consulta_stakeholder.ids = ids
            consulta_stakeholder.start()
            consulta_stakeholder.save()
            
            if consulta_stakeholder.stakeholder:
                inseridos.update(consulta_stakeholder.inseridos)
                ids.update(consulta_stakeholder.ids)
                self.__envolvidos[i] = consulta_stakeholder.stakeholder

        print(f"Finalizando busca de clientes para o nº OAB {self.__documento}"
              f" - {len(self.__envolvidos)} clientes encontrados.")
        self.__logger.add_log(
            mensagem=f"Finalizando busca de clientes para o nº OAB {self.__documento}"
              f" - {len(self.__envolvidos)} clientes encontrados.",
            tipo_log="INFO",
            consulta_id=self.__consulta_id,
            data_log=datetime.now(timezone.utc)
        )

    def __get_response_url(self, oab_numero, oab_estado):
        url = f"{self.__url}/api/v2/advogado/processos"
        params = {
            "oab_numero": oab_numero,
            "oab_estado": oab_estado,
            "data_minima": data_anos_atras(3)
        }
        headers = {'Authorization': f'Bearer {self.__token}'}

        try:
            response = requests.get(url, params=params, headers=headers)
            if response.status_code != 200:
                return []
            else:
                if self.__save_requests:
                    self.__salvar_json(oab_numero, response.json())

                return response.json()
        except Exception as e:
            self.__logger.add_log(
                mensagem=f"Erro no consumo de dados: {str(e)}",
                tipo_log="ERROR",
                consulta_id=self.__consulta_id,
                data_log=datetime.now(timezone.utc)
            )
            print(f"Erro no consumo de dados: {str(e)}")
            return []

    @staticmethod
    def __salvar_json(oab_numero, data):
        """Salva o JSON no arquivo, usando o `oab_numero` como nome."""
        nome_arquivo = os.path.join("Escavador/processos_oab", f"{oab_numero}.json")
        try:
            with open(nome_arquivo, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print(f"Arquivo salvo: {nome_arquivo}")
        except Exception as e:
            print(f"Erro ao salvar o arquivo {nome_arquivo}: {str(e)}")

    def __get_processos_oab(self, oab_numero, oab_estado=''):
        response = self.__get_response_url(oab_numero, oab_estado)

        if not len(response):
            return

        for item in response.get('items', []):
            processo = {
                "ano_inicio": item.get('ano_inicio'),
                "data_inicio": item.get('data_inicio')
            }

            for fonte in item.get('fontes', []):
                processo.update({
                    "arquivado": fonte.get('arquivado'),
                    "descricao": fonte.get('descricao')
                })

                capa = fonte.get('capa')
                if capa:
                    processo.update({
                        "assunto": capa.get('assunto'),
                        "classe": capa.get('classe'),
                        "data_arquivamento": capa.get('data_arquivamento'),
                        "data_distribuicao": capa.get('data_distribuicao'),
                        "informacoes_complementares": capa.get('informacoes_complementares')
                    })

            self.__processos.append(processo) if processo not in self.__processos else self.__processos

        self.__processos = [Processo(**dados) for dados in self.__processos]
        return self.__processos

    def identificar_escritorio(self):
        pass

    def __get_envolvidos_oab(self, oab_numero, oab_estado=''):
        response = self.__get_response_url(oab_numero, oab_estado)

        if not len(response):
            self.__logger.add_log(
                mensagem=f"Sem dados para o OAB {oab_numero} SP {oab_estado}",
                tipo_log="INFO",
                consulta_id=self.__consulta_id,
                data_log=datetime.now(timezone.utc)
            )
            print(f"Sem dados para o OAB {oab_numero} SP {oab_estado}")
            return

        envolvidos = chain.from_iterable(
            fonte['envolvidos']
            for item in response.get('items', [])
            for fonte in item.get('fontes', [])
        )

        for envolvido in envolvidos:
            advogados = envolvido.get('advogados', [])
            for advogado in advogados:
                oabs = advogado.get('oabs', [])
                if any(str(oab_advogado['numero']) == str(oab_numero) for oab_advogado in oabs):
                    if envolvido.get('cpf'):
                        _append = {
                            "nome": envolvido['nome'],
                            # "firstname": nome.first,
                            # "lastname": nome.last,
                            "cpf": envolvido['cpf']
                        }
                    elif envolvido.get('cnpj'):
                        _append = {
                            "razaoSocial": envolvido['nome'],
                            "cnpj": envolvido['cnpj']
                        }
                    else:
                        continue

                    if _append not in self.__envolvidos:
                        self.__envolvidos.append(_append)

        envolvidos_convertidos = []
        for dados in self.__envolvidos:
            envolvidos_convertidos.append(PessoaFisica(**dados) if dados.get("cpf") else PessoaJuridica(**dados))
        self.__envolvidos = envolvidos_convertidos

        return self.__envolvidos

    def __commit(self, envolvidos):
        for envolvido in envolvidos:
            self.__commit_pessoa(envolvido, True, self.__em_prospecao) if isinstance(envolvido, PessoaFisica) else self.__commit_empresa(envolvido)

        self.__commit_relacionamento()

    def __commit_relacionamento(self):
            from app.models.relacionamentos import Relacionamentos
            from app.models.advogado import Advogado
            from app.modules.analise_juridica import AnaliseJuridica

            query_advogado = Advogado.query.filter_by(oab=str(self.documento)).first()
            if not query_advogado:
                print(f"ID do advogado não encontrado!")
                self.__logger.add_log(
                    mensagem=f"ID do advogado não encontrado!",
                    tipo_log="INFO",
                    consulta_id=self.__consulta_id,
                    data_log=datetime.now(timezone.utc)
                )
                return

            entidade_origem_id = query_advogado.advogado_id
            print(f"Advogado Encontrado: {query_advogado.advogado_id}")
            self.__logger.add_log(
                mensagem=f"Advogado Encontrado: {query_advogado.advogado_id}",
                tipo_log="INFO",
                consulta_id=self.__consulta_id,
                data_log=datetime.now(timezone.utc)
            )
            
            print(f"Relacionamentos a serem criados: {len(self.__envolvidos)}")
            self.__logger.add_log(
                mensagem=f"Relacionamentos a serem criados: {len(self.__envolvidos)}",
                tipo_log="INFO",
                consulta_id=self.__consulta_id,
                data_log=datetime.now(timezone.utc)
            )
            for relacionamento in self.__envolvidos:  
                documento = relacionamento.cpf if isinstance(relacionamento, PessoaFisica) else relacionamento.cnpj
                entidade_destino_id = self.__ids.get(documento, None)
                tipo_relacao_id = 26

                if not entidade_destino_id:
                    print(f"Entidade com documento {documento} não encontrada")
                    self.__logger.add_log(
                        mensagem=f"Entidade com documento {documento} não encontrada",
                        tipo_log="INFO",
                        consulta_id=self.__consulta_id,
                        data_log=datetime.now(timezone.utc)
                    )
                    continue

                tipo_origem_id = 4
                tipo_destino_id = 1 if isinstance(relacionamento, PessoaFisica) else 3

                try:
                    rel = Relacionamentos.query.filter_by(entidade_origem_id=entidade_origem_id,
                                                          tipo_origem_id=tipo_origem_id,
                                                          entidade_destino_id=entidade_destino_id,
                                                          tipo_destino_id=tipo_destino_id).first()
                    
                    if not rel:
                        rel = Relacionamentos(
                            entidade_origem_id=entidade_origem_id,
                            tipo_origem_id=tipo_origem_id,
                            entidade_destino_id=entidade_destino_id,
                            tipo_destino_id=tipo_destino_id,
                            tipo_relacao_id=tipo_relacao_id)
                        db.session.add(rel)
                        db.session.commit()
                        
                        print(f"Relacionamento criado com sucesso!\n")
                        self.__logger.add_log(
                            mensagem=f"Relacionamento criado com sucesso!\n",
                            tipo_log="SUCCESS",
                            consulta_id=self.__consulta_id,
                            data_log=datetime.now(timezone.utc)
                        )
                except Exception as e:
                    print(e)
                    self.__logger.add_log(
                        mensagem=e,
                        tipo_log="ERROR",
                        consulta_id=self.__consulta_id,
                        data_log=datetime.now(timezone.utc)
                    )

    def __commit_pessoa(self, pessoa_fisica, stakeholder=True, em_prospeccao=False):
        from app.models.pessoa import Pessoa

        if not pessoa_fisica or pessoa_fisica in self.__inseridos:
            # print(f"Pulando registro: {pessoa_fisica}")
            return

        pessoa = Pessoa.query.filter_by(cpf=str(pessoa_fisica.cpf)).first()

        new_data = {
            **pessoa_fisica.to_dict(),
            "stakeholder": stakeholder,
            "em_prospecao": em_prospeccao
        }
        try:
            if pessoa:
                if pessoa.cpf != self.documento:
                    new_data.pop("stakeholder", None)
                    new_data.pop("em_prospecao", None)
                pessoa.update_from_dict(new_data)
                db.session.commit()
                
                print(f"Pessoa {pessoa.cpf} atualizada")
                self.__logger.add_log(
                    mensagem=f"Pessoa {pessoa.cpf} atualizada",
                    tipo_log="SUCCESS",
                    consulta_id=self.__consulta_id,
                    data_log=datetime.now(timezone.utc)
                )
            else:
                pessoa = Pessoa(**pessoa_fisica.to_dict())

                db.session.add(pessoa)
                db.session.commit()
                
                self.__logger.add_log(
                    mensagem=f"Pessoa {pessoa.cpf} cadastrada",
                    tipo_log="INFO",
                    consulta_id=self.__consulta_id,
                    data_log=datetime.now(timezone.utc)
                )
                print(f"Pessoa {pessoa.cpf} cadastrada")
                
            self.__inseridos.add(pessoa_fisica)
            self.__ids[pessoa_fisica.cpf] = pessoa.pessoa_id
        except Exception as e:
            self.__logger.add_log(
                mensagem=e,
                tipo_log="ERROR",
                consulta_id=self.__consulta_id,
                data_log=datetime.now(timezone.utc)
            )
            print(e)

    def __commit_empresa(self, pessoa_juridica):
        from app.models.empresa import Empresa

        if not pessoa_juridica or pessoa_juridica in self.__inseridos:
            return

        empresa = Empresa.query.filter_by(cnpj=str(pessoa_juridica.cnpj)).first()

        new_data = {
            **pessoa_juridica.to_dict()
        }
        try:
            if empresa:
                print(f"Empresa {empresa.cnpj} já existente!")
                self.__logger.add_log(
                    mensagem=f"Empresa {empresa.cnpj} já existente!",
                    tipo_log="WARNING",
                    consulta_id=self.__consulta_id,
                    data_log=datetime.now(timezone.utc)
                )
            else:
                empresa = Empresa(**new_data)

                db.session.add(empresa)
                db.session.commit()
                print(f"Empresa {empresa.cnpj} cadastrada")
                self.__logger.add_log(
                    mensagem=f"Empresa {empresa.cnpj} cadastrada",
                    tipo_log="SUCCESS",
                    consulta_id=self.__consulta_id,
                    data_log=datetime.now(timezone.utc)
                )
            self.__inseridos.add(pessoa_juridica)
            self.__ids[pessoa_juridica.cnpj] = empresa.empresa_id
        except Exception as e:
            print(e)
            self.__logger.add_log(
                mensagem=e,
                tipo_log="ERROR",
                consulta_id=self.__consulta_id,
                data_log=datetime.now(timezone.utc)
            )