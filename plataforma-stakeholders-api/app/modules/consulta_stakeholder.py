import requests
import json
import os

from app import db
from datetime import datetime, timezone
from app.models.tipo_relacao import TipoRelacao
from app.models.porte_empresa import PorteEmpresa
from app.models.empresa import Empresa
from app.models.pessoa import Pessoa
from app.models.advogado import Advogado
from app.models.segmento_empresa import SegmentoEmpresa
from app.modules.objects.pessoa_juridica import PessoaJuridica
from app.modules.objects.pessoa_fisica import PessoaFisica
from app.modules.objects.relacionamento import Relacionamento
from app.modules.utils import remover_acentos, format_cpf, format_cnpj, validar_documento
from app.modules.entidade_service import EntidadeService


class ConsultaStakeholder:
    def __init__(self, documento, consulta_id, is_stakeholder=True, em_prospecao=False,
                 local_tests=False, save_requests=False, camadas_sociedade=2,
                 camadas_parentescos=1, lazy_start=False, associado=False, logger=None):
        self.__url = "example" if local_tests else "https://apiv3.directd.com.br"
        self.__token = "202FBC0D-D109-4D86-BBAA-569991514FD9"
        self.__consultados = dict()  # Usado para rastrear CPFs/CNPJs já processados
        self.__tipo_relacionamento = dict()
        self.__porte_empresa = dict()
        self.__segmento_empresa = dict()
        self.__relacionamentos = list()
        self.__documento = validar_documento(documento)
        self.__tipo_stakeholder = "CPF" if len(self.__documento) == 11 else "CNPJ"
        self.__stakeholder = None
        self.__is_stakeholder = is_stakeholder
        self.__em_prospecao = em_prospecao
        self.__is_stakeholder = is_stakeholder
        self.__inseridos = set()
        self.__ids = dict()
        self.__max_camadas_sociedade = camadas_sociedade
        self.__max_camadas_parentescos = camadas_parentescos
        self.__save_requests = save_requests
        self.__lazy_start = lazy_start
        self.__associado = associado
        self.__pessoas_cadastradas = dict()
        self.__empresas_cadastradas = dict()
        self.__logger = logger
        self.__consulta_id = consulta_id

        self.__load_data()

    @property
    def consultados(self):
        return self.__consultados

    @property
    def tipo_relacionamento(self):
        return self.__tipo_relacionamento

    @property
    def porte_empresa(self):
        return self.__porte_empresa

    @property
    def segmento_empresa(self):
        return self.__segmento_empresa

    @property
    def relacionamentos(self):
        return self.__relacionamentos

    @property
    def stakeholder(self):
        return self.__stakeholder

    @property
    def documento(self):
        return self.__documento

    @property
    def inseridos(self):
        return self.__inseridos

    @inseridos.setter
    def inseridos(self, value):
        self.__inseridos = value

    @property
    def ids(self):
        return self.__ids
    
    @property
    def pessoas_cadastradas(self):
        return self.__pessoas_cadastradas

    @property
    def empresas_cadastradas(self):
        return self.__empresas_cadastradas

    @property
    def consulta_id(self):
        return self.__consulta_id

    @ids.setter
    def ids(self, value):
        self.__ids = value

    def clear(self):
        self.__consultados.clear()
        self.__relacionamentos.clear()
        self.__inseridos.clear()
        self.__ids.clear()

    def start(self):
        print("Iniciando consulta de análise de Stakeholders...") 
        self.__logger.add_log(
            mensagem="Iniciando consulta de análise de Stakeholders...",
            tipo_log="INFO",
            consulta_id=self.__consulta_id,
            data_log=datetime.now(timezone.utc)
        )
         
        self.__stakeholder = self.__get_pessoa_fisica(self.__documento, camadas_sociedade=0,
                                                      camadas_parentescos=0,
                                                      lazy_start=self.__lazy_start) \
            if self.__tipo_stakeholder == "CPF" \
            else self.__get_pessoa_juridica(self.__documento, camadas_sociedade=0,
                                            camadas_parentescos=0)

    def save(self):
        if not self.__stakeholder:
            print("Stakeholder não encontrado...")
            self.__logger.add_log(
                mensagem= "Stakeholder não encontrado...",
                tipo_log="INFO",
                consulta_id=self.__consulta_id,
                data_log=datetime.now(timezone.utc)
            )
            return
        
        print("Salvando dados da análise de Stakeholders...")
        self.__logger.add_log(
            mensagem= "Salvando dados da análise de Stakeholders...",
            tipo_log="INFO",
            consulta_id=self.__consulta_id,
            data_log=datetime.now(timezone.utc)
        )
        
        self.__commit(self.__stakeholder)

    @staticmethod
    def __salvar_json(self, path, data, consulta_id):
        """Salva o JSON no arquivo, usando o `oab_numero` como nome."""
        nome_arquivo = os.path.join("DirectData", f"{path}")
        try:
            with open(nome_arquivo, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print(f"Arquivo salvo: {nome_arquivo}")
        except Exception as e:
            print(f"Erro ao salvar o arquivo {nome_arquivo}: {str(e)}")

    @staticmethod
    def __check_relacionamento_existe(relacionamento_id_1, relacionamento_id_2, inseridos):
        # Verificar se um link com a mesma source e target (ou invertido) já existe
        for relacionamento in inseridos:
            mesma_origem = relacionamento['source'] == relacionamento_id_1
            mesmo_destino = relacionamento['target'] == relacionamento_id_2
            invertido_origem = relacionamento['source'] == relacionamento_id_2
            invertido_destino = relacionamento['target'] == relacionamento_id_1

            if (mesma_origem and mesmo_destino) or (invertido_origem and invertido_destino):
                return True
        return False

    def __commit(self, stakeholder):
        if isinstance(stakeholder, PessoaJuridica):
            self.__commit_empresa(stakeholder, self.__is_stakeholder, self.__em_prospecao)
        else:
            self.__commit_pessoa(stakeholder, self.__is_stakeholder, self.__em_prospecao)

        self.__commit_relacionamento()

    def __commit_relacionamento(self):
        from app.models.relacionamentos import Relacionamentos

        inseridos = list()
        for relacionamento in self.__relacionamentos:
            entidade_origem_id = self.__ids.get(relacionamento.entidade_1, None)
            entidade_destino_id = self.__ids.get(relacionamento.entidade_2, None)
            tipo_relacao_id = self.__tipo_relacionamento.get(relacionamento.tipo_relacionamento, None)

            if entidade_origem_id and entidade_destino_id and tipo_relacao_id:
                tipo_origem_id = 1 if len(relacionamento.entidade_1) == 11 else 3
                tipo_destino_id = 1 if len(relacionamento.entidade_2) == 11 else 3

                relacionamento_id_origem = f"{tipo_origem_id}:{entidade_origem_id}"
                relacionamento_id_destino = f"{tipo_destino_id}:{entidade_destino_id}"

                if self.__check_relacionamento_existe(relacionamento_id_origem, relacionamento_id_destino, inseridos):
                    continue

                rel = Relacionamentos.query.filter_by(entidade_origem_id=entidade_origem_id,
                                                      tipo_origem_id=tipo_origem_id,
                                                      entidade_destino_id=entidade_destino_id,
                                                      tipo_destino_id=tipo_destino_id).first()
                try:
                    if rel:
                        rel.tipo_relacao_id = tipo_relacao_id
                        db.session.commit()
                        
                        print(f"Relacionamento {rel} atualizado")
                        self.__logger.add_log(
                            mensagem=f"Relacionamento {rel} atualizado",
                            tipo_log="SUCCESS",
                            consulta_id=self.__consulta_id,
                            data_log=datetime.now(timezone.utc)
                        )
                    else:
                        rel = Relacionamentos(entidade_origem_id=entidade_origem_id,
                                              tipo_origem_id=tipo_origem_id,
                                              entidade_destino_id=entidade_destino_id,
                                              tipo_destino_id=tipo_destino_id,
                                              tipo_relacao_id=tipo_relacao_id)
                        db.session.add(rel)
                        db.session.commit()
                        
                        print(f"Relacionamento {rel.to_dict()} cadastrado")
                        self.__logger.add_log(
                            mensagem=f"Relacionamento {rel.to_dict()} cadastrado",
                            tipo_log="SUCCESS",
                            consulta_id=self.__consulta_id,
                            data_log=datetime.now(timezone.utc)
                        )    

                    inseridos.append({
                        "source": relacionamento_id_origem,
                        "target": relacionamento_id_destino
                    })
                except Exception as e:
                    print(e)
                    self.__logger.add_log(
                        mensagem=e,
                        tipo_log="ERROR",
                        consulta_id=self.__consulta_id,
                        data_log=datetime.now(timezone.utc)
                    )  

    def __commit_empresa(self, pessoa_juridica, is_stakeholder, em_prospeccao=False):
        from app.models.empresa import Empresa

        if not pessoa_juridica or pessoa_juridica in self.__inseridos:
            # print(f"Pulando registro: {pessoa_juridica}")
            return

        empresa = Empresa.query.filter_by(cnpj=str(pessoa_juridica.cnpj)).first()
        
        new_data = {
            **pessoa_juridica.to_dict(),
            "porte_id": self.__get_porte_id(pessoa_juridica.porte),
            "segmento_id": self.__get_segmento_id(pessoa_juridica.cnae_codigo, pessoa_juridica.cnae_descricao),
            "stakeholder": is_stakeholder,
            "em_prospecao": em_prospeccao
        }
        try:
            if empresa:
                if empresa.cnpj != self.__documento:
                    new_data.pop("stakeholder", None)
                    new_data.pop("em_prospecao", None)
                empresa.update_from_dict(new_data)
                db.session.commit()
                
                print(f"Empresa {empresa.cnpj} atualizada")
                self.__logger.add_log(
                    mensagem=f"Empresa {empresa.cnpj} atualizada",
                    tipo_log="SUCCESS",
                    consulta_id=self.__consulta_id,
                    data_log=datetime.now(timezone.utc)
                )
            else:
                empresa = Empresa(**new_data)
                db.session.add(empresa)
                db.session.commit()
                # print(f"Empresa {empresa.cnpj} cadastrada")

            self.__inseridos.add(pessoa_juridica)
            self.__ids[pessoa_juridica.cnpj] = empresa.empresa_id
            tipo_entidade_id = 3
            entidade_id = empresa.empresa_id

            EntidadeService.commit_endereco(entidade_id, self.__consulta_id, self.__logger, tipo_entidade_id, pessoa_juridica.enderecos)
            EntidadeService.commit_telefone(entidade_id, self.__consulta_id, self.__logger, tipo_entidade_id, pessoa_juridica.telefones)
            EntidadeService.commit_email(entidade_id, self.__consulta_id, self.__logger, tipo_entidade_id, pessoa_juridica.emails)

        except Exception as e:
            print(e)
            self.__logger.add_log(
                mensagem=e,
                tipo_log="ERROR",
                consulta_id=self.__consulta_id,
                data_log=datetime.now(timezone.utc)
            )

        for socio in pessoa_juridica.socios:
            self.__commit_pessoa(socio, False, False)

    def __commit_pessoa(self, pessoa_fisica, is_stakeholder, em_prospeccao=False):
        from app.models.pessoa import Pessoa

        if not pessoa_fisica or pessoa_fisica in self.__inseridos:
            # print(f"Pulando registro: {pessoa_fisica}")
            return

        pessoa = Pessoa.query.filter_by(cpf=str(pessoa_fisica.cpf)).first()

        new_data = pessoa_fisica.to_dict()
        if str(pessoa_fisica.cpf) == self.__documento:
            new_data.update({
                "stakeholder": is_stakeholder,
                "em_prospecao": em_prospeccao,
                "associado": self.__associado
            })

        try:
            if pessoa:
                pessoa.update_from_dict(new_data)
                db.session.commit()
                print(f"Pessoa {pessoa.cpf} atualizada")
                self.__logger.add_log(
                    mensagem=f"Pessoa {pessoa.cpf} atualizada",
                    tipo_log="INFO",
                    consulta_id=self.__consulta_id,
                    data_log=datetime.now(timezone.utc)
                )
            else:
                pessoa = Pessoa(**pessoa_fisica.to_dict())
                db.session.add(pessoa)
                db.session.commit()
                print(f"Pessoa {pessoa.cpf} cadastrada")
                self.__logger.add_log(
                    mensagem=f"Pessoa {pessoa.cpf} cadastrada",
                    tipo_log="INFO",
                    consulta_id=self.__consulta_id,
                    data_log=datetime.now(timezone.utc)
                )

            self.__inseridos.add(pessoa_fisica)
            self.__ids[pessoa_fisica.cpf] = pessoa.pessoa_id
            tipo_entidade_id = 1
            entidade_id = pessoa.pessoa_id

            EntidadeService.commit_endereco(entidade_id, self.__consulta_id, self.__logger, tipo_entidade_id, pessoa_fisica.enderecos)
            EntidadeService.commit_telefone(entidade_id, self.__consulta_id, self.__logger, tipo_entidade_id, pessoa_fisica.telefones)
            EntidadeService.commit_email(entidade_id, self.__consulta_id, self.__logger, tipo_entidade_id, pessoa_fisica.emails)
        except Exception as e:
            self.__logger.add_log(
                mensagem=e,
                tipo_log="ERROR",
                consulta_id=self.__consulta_id,
                data_log=datetime.now(timezone.utc)
            )
            print(e)

        if pessoa_fisica.parentescos:
            for parentesco in pessoa_fisica.parentescos:
                self.__commit_pessoa(parentesco, False, False)

        if pessoa_fisica.sociedades:
            for sociedade in pessoa_fisica.sociedades:
                self.__commit_empresa(sociedade, False, False)

    def __get_porte_id(self, porte):
        try:
            return self.__porte_empresa[str(porte)]
        except KeyError:
            if not porte:
                return self.__porte_empresa['NÃO INFORMADO']

            new_porte_empresa = PorteEmpresa(descricao=porte)
            db.session.add(new_porte_empresa)
            db.session.commit()
            self.__porte_empresa[str(porte)] = new_porte_empresa.porte_id

            print(f"Porte {porte} não existente no banco de dados. "
                  f"Cadastro realizado sob ID {new_porte_empresa.porte_id}")
            self.__logger.add_log(
                mensagem=f"Porte {porte} não existente no banco de dados. "
                  f"Cadastro realizado sob ID {new_porte_empresa.porte_id}",
                tipo_log="WARNING",
                consulta_id=self.__consulta_id,
                data_log=datetime.now(timezone.utc)
            )
            return new_porte_empresa.porte_id

    def __get_segmento_id(self, cnae_codigo, cnae_descricao):
        try:
            return self.__segmento_empresa[str(cnae_codigo)]
        except KeyError:
            if cnae_descricao is None:
                cnae_descricao = str(cnae_codigo)
            new_segmento_empresa = SegmentoEmpresa(cnae=cnae_codigo,
                                                   descricao=cnae_descricao)
            db.session.add(new_segmento_empresa)
            db.session.commit()
            self.__segmento_empresa[str(cnae_codigo)] = new_segmento_empresa.segmento_id

            print(f"Segmento {cnae_codigo} não existente no banco de dados. "
                  f"Cadastro realizado sob ID {new_segmento_empresa.segmento_id}")
            self.__logger.add_log(
                mensagem=f"Segmento {cnae_codigo} não existente no banco de dados. "
                  f"Cadastro realizado sob ID {new_segmento_empresa.segmento_id}",
                tipo_log="WARNING",
                consulta_id=self.__consulta_id,
                data_log=datetime.now(timezone.utc)
            )
            return new_segmento_empresa.segmento_id

    def __load_data(self):
        tipos = TipoRelacao.query.all()
        for tipo in tipos:
            self.__tipo_relacionamento[tipo.descricao] = tipo.tipo_relacao_id

        portes_empresa = PorteEmpresa.query.all()
        for porte in portes_empresa:
            self.__porte_empresa[porte.descricao] = porte.porte_id

        segmentos_empresa = SegmentoEmpresa.query.all()
        for segmento in segmentos_empresa:
            self.__segmento_empresa[segmento.cnae] = segmento.segmento_id
            
        pessoas = Pessoa.query.all()
        for pessoa in pessoas:
            self.__pessoas_cadastradas['pessoa.cpf'] = pessoa.pessoa_id
        
        empresas = Empresa.query.all()
        for empresa in empresas:
            self.__empresas_cadastradas['empresa.cnpj'] = empresa.empresa_id
        

    def __get_pessoa_juridica(self, cnpj, camadas_sociedade, camadas_parentescos):
        # Formatar o CNPJ para remover caracteres especiais
        cnpj_formatado = format_cnpj(cnpj)

        # Verificar se já consultamos esse CNPJ
        if cnpj_formatado in self.__consultados.keys():
            # Retornar um objeto PessoaJuridica com apenas o CNPJ, se já consultado
            return self.__consultados[cnpj_formatado]

        if camadas_sociedade > self.__max_camadas_sociedade:
            print(f"Camada de Parentesco máxima atingida: {self.__max_camadas_parentescos}")
            self.__logger.add_log(
                mensagem=f"Camada de Parentesco máxima atingida: {self.__max_camadas_parentescos}",
                tipo_log="INFO",
                consulta_id=self.__consulta_id,
                data_log=datetime.now(timezone.utc)
            )
            return None
        
        print(f"Camada de Sociedade {camadas_sociedade} de {self.__max_camadas_sociedade}")
        self.__logger.add_log(
            mensagem=f"Camada de Sociedade {camadas_sociedade} de {self.__max_camadas_sociedade}",
            tipo_log="INFO",
            consulta_id=self.__consulta_id,
            data_log=datetime.now(timezone.utc)
        )

        # Adicionar o CNPJ ao conjunto de consultados
        self.__consultados[cnpj_formatado] = None
        
        url = f"{self.__url}/api/CadastroPessoaJuridica"
        params = {
                'token': self.__token,
                'CNPJ': cnpj_formatado
            }
        
        try:
            response = requests.get(url, params=params)
            empresa = response.json().get('retorno', None) if response.status_code == 200 else None
            if not empresa:
                return None

            if self.__save_requests:
                self.__salvar_json(f"pessoa_juridica/{cnpj_formatado}.json", response.json())

            # Consultar os sócios da empresa
            socios = list()
            for socio in empresa.get('socios', list()):
                cpf_formatado = format_cpf(socio['documento'])
                result = self.__get_pessoa_fisica(socio['documento'], camadas_sociedade,
                                                camadas_parentescos, cnpj_formatado)
                if result:
                    self.__relacionamentos.append(Relacionamento(cpf_formatado,
                                                                cnpj_formatado,
                                                                'SOCIO'))
                    socios.append(result)

            empresa = {k.lower(): v for k, v in empresa.items()}
            pessoa_juridica = PessoaJuridica(cnpj=empresa.get('cnpj', None),
                                            razaoSocial=empresa.get('razaosocial', None),
                                            nomeFantasia=empresa.get('nomefantasia', None),
                                            cnaeCodigo=empresa.get('cnaecodigo', None),
                                            cnaeDescricao=empresa.get('cnaedescricao', None),
                                            dataFundacao=empresa.get('datafundacao', None),
                                            situacaoCadastral=empresa.get('situacaocadastral', None),
                                            naturezaJuridicaCodigo=empresa.get('naturezajuridicacodigo', None),
                                            naturezaJuridicaDescricao=empresa.get('naturezajuridicadescricao', None),
                                            naturezaJuridicaTipo=empresa.get('naturezajuridicatipo', None),
                                            faixaFuncionarios=empresa.get('faixafuncionarios', None),
                                            quantidadeFuncionarios=empresa.get('quantidadefuncionarios', None),
                                            faixaFaturamento=empresa.get('faixafaturamento', None),
                                            matriz=empresa.get('matriz', None),
                                            orgaoPublico=empresa.get('orgaopublico', None),
                                            ramo=empresa.get('ramo', None),
                                            tipoempresa=empresa.get('tipoempresa', None),
                                            ultimaAtualizacaoPJ=empresa.get('ultimaatualizacaopj', None),
                                            porte=empresa.get('porte', None),
                                            telefones=empresa.get('telefones', None),
                                            enderecos=empresa.get('enderecos', None),
                                            emails=empresa.get('emails', None),
                                            socios=socios)
                    
        except Exception as e:
            print(f"(/api/CadastroPessoaJuridica) Erro inesperado ao processar CNPJ {cnpj_formatado}: {str(e)}")
            self.__logger.add_log(
                mensagem=f"(/api/CadastroPessoaJuridica) Erro inesperado ao processar CNPJ {cnpj_formatado}: {str(e)}",
                tipo_log="ERROR",
                consulta_id=self.__consulta_id,
                data_log=datetime.now(timezone.utc)
            )
            
        # Atualizar o CNPJ ao conjunto de consultados
        self.__consultados[cnpj_formatado] = pessoa_juridica

        return pessoa_juridica

    def __get_pessoa_fisica(self, cpf, camadas_sociedade, camadas_parentescos, cnpj_sociedade=None, lazy_start=False):
        # Formatar o CPF para remover caracteres especiais
        cpf_formatado = format_cpf(cpf)

        # Verificar se já consultamos esse CPF
        if cpf_formatado in self.__consultados.keys():
            # Retornar um objeto PessoaFisica com apenas o CPF, se já consultado
            return self.__consultados[cpf_formatado]

        if camadas_parentescos > self.__max_camadas_parentescos:
            print(f"Camada de Parentesco máxima atingida: {self.__max_camadas_parentescos}")
            self.__logger.add_log(
                mensagem=f"Camada de Parentesco máxima atingida: {self.__max_camadas_parentescos}",
                tipo_log="INFO",
                consulta_id=self.__consulta_id,
                data_log=datetime.now(timezone.utc)
            )

            return None
        
        print(f"Camada de Parentesco {camadas_parentescos} de {self.__max_camadas_parentescos}")
        self.__logger.add_log(
            mensagem=f"Camada de Parentesco {camadas_parentescos} de {self.__max_camadas_parentescos}",
            tipo_log="INFO",
            consulta_id=self.__consulta_id,
            data_log=datetime.now(timezone.utc)
        )

        try:
            url = f"{self.__url}/api/CadastroPessoaFisica"
            params = {
                'token': self.__token,
                'CPF': cpf_formatado
            }

            response = requests.get(url, params=params)
            pessoa = response.json().get("retorno", None) if response.status_code == 200 else None
            if not pessoa:
                return None

            if self.__save_requests:
                self.__salvar_json(f"pessoa_fisica/{cpf_formatado}.json", response.json())

            # Consultar AML (parentescos e sociedades)
            url_aml = f"{self.__url}/api/AML"
            response_aml = requests.get(url_aml, params=params)
            info_complementar = response_aml.json().get("retorno", None) if response_aml.status_code == 200 else None

            parentescos = list()
            sociedades = list()
            if info_complementar:
                if self.__save_requests:
                    self.__salvar_json(f"pessoa_fisica/info_complementar/{cpf_formatado}.json", response_aml.json())

                if cpf_formatado == self.__documento or cnpj_sociedade == self.__documento:
                    if info_complementar.get('parentescos'):
                        for parentesco in info_complementar.get('parentescos', list()):
                            cpf_formatado_parentesco = format_cpf(parentesco['cpf'])
                            result = self.__get_pessoa_fisica(cpf_formatado_parentesco,
                                                            camadas_sociedade + 1,
                                                            camadas_parentescos + 1)
                            if result:
                                tipo_relacao = remover_acentos(parentesco['grauParentesco'])
                                self.__relacionamentos.append(Relacionamento(cpf_formatado,
                                                                            cpf_formatado_parentesco,
                                                                            tipo_relacao))
                                parentescos.append(result)

                if info_complementar.get('sociedades'):
                    for sociedade in info_complementar.get('sociedades', list()):
                        cnpj_formatado = format_cnpj(sociedade['cnpj'])
                        result = self.__get_pessoa_juridica(cnpj_formatado,
                                                            0 if lazy_start else camadas_sociedade + 1,
                                                            camadas_parentescos)
                        if result:
                            self.__relacionamentos.append(Relacionamento(cnpj_formatado,
                                                                        cpf_formatado,
                                                                        'SOCIEDADE'))
                            sociedades.append(result)

                pessoa_fisica = PessoaFisica(cpf=pessoa.get('cpf', None),
                                            nome=pessoa.get('nome', None),
                                            sexo=pessoa.get('sexo', None),
                                            dataNascimento=pessoa.get('dataNascimento', None),
                                            nomeMae=pessoa.get('nomeMae', None),
                                            idade=pessoa.get('idade', None),
                                            signo=pessoa.get('signo', None),
                                            isObito=info_complementar.get('isObito', None),
                                            dataObito=info_complementar.get('dataObito', None),
                                            rendaEstimada=pessoa.get('rendaEstimada', None),
                                            isPEP=info_complementar.get('isPEP', None),
                                            parentescos=parentescos,
                                            sociedades=sociedades,
                                            endereco=pessoa.get('enderecos', None),
                                            emails=pessoa.get('emails', None),
                                            telefone=pessoa.get('telefones', None))

            else:
                print("Sem informações complementares...")
                self.__logger.add_log(
                    mensagem="Sem informações complementares...",
                    tipo_log="INFO",
                    consulta_id=self.__consulta_id,
                    data_log=datetime.now(timezone.utc)
                )
                pessoa_fisica = PessoaFisica(cpf=pessoa.get('cpf', None),
                                            nome=pessoa.get('nome', None),
                                            sexo=pessoa.get('sexo', None),
                                            dataNascimento=pessoa.get('dataNascimento', None),
                                            nomeMae=pessoa.get('nomeMae', None),
                                            idade=pessoa.get('idade', None),
                                            signo=pessoa.get('signo', None),
                                            rendaEstimada=pessoa.get('rendaEstimada', None),
                                            endereco=pessoa.get('enderecos', None),
                                            emails=pessoa.get('emails', None),
                                            telefone=pessoa.get('telefones', None))
                    
        except Exception as e:
            print(f"(/api/AML) Erro inesperado ao processar CPF {cpf_formatado}: {str(e)}")
            self.__logger.add_log(
                mensagem=f"(/api/AML) Erro inesperado ao processar CPF {cpf_formatado}: {str(e)}",
                tipo_log="ERROR",
                consulta_id=self.__consulta_id,
                data_log=datetime.now(timezone.utc)
            )
        
        # Atualizar o CPF ao conjunto de consultados
        self.__consultados[cpf_formatado] = pessoa_fisica

        return pessoa_fisica
