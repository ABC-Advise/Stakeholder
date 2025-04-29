import time

import pandas as pd
from flask_restful import Resource, reqparse
from collections import namedtuple
from rapidfuzz.fuzz import partial_ratio

from app.modules.utils import validar_documento, safe_strip, serialize_objects
from app.models.empresa import Empresa
from app.models.pessoa import Pessoa
from app.models.advogado import Advogado
from app.models.escritorio import Escritorio
from app.models.relacionamentos import Relacionamentos
from app.models.tipo_relacao import TipoRelacao
from app.resources.endereco import EnderecosResource
from app.modules.objects.node import Node
from app.modules.objects.link import Link

import json

class RelacionamentosResource(Resource):
    """
    Recurso para gerenciar e visualizar relacionamentos entre entidades.

    Este recurso permite buscar relacionamentos de entidades e organizá-los em formato de grafo.
    Ele utiliza camadas para definir a profundidade dos relacionamentos explorados e retorna
    nós e links representando as conexões entre as entidades.
    """

    @staticmethod
    def get():
        """
        Recupera os relacionamentos das entidades no formato de clusters.

        Parâmetros:
        - documento (str, opcional): CPF ou CNPJ de uma entidade específica.
        - camadas (int, opcional, padrão=5): Número máximo de camadas a explorar.
        - em_prospecao (bool, opcional): Filtrar entidades marcadas como "em prospecção".
        - associado (bool, opcional): Filtrar entidades marcadas como associadas.
        - uf (str, opcional): Filtrar entidades por estado.
        - cidade (str, opcional): Filtrar entidades por cidade.
        - projeto_id (int, opcional): Filtrar entidades vinculadas a um projeto específico.

        Retorna:
        dict: Um dicionário contendo os clusters de entidades, onde cada cluster possui nós e links.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('documento', type=str, required=False, location='args', help='Documento (CPF ou CNPJ)')
        parser.add_argument('camadas', type=int, required=False, default=5, location='args')
        parser.add_argument('em_prospecao', type=bool, required=False, location='args')
        parser.add_argument('associado', type=bool, required=False, location='args')
        parser.add_argument('uf', type=str, required=False, location='args')
        parser.add_argument('cidade', type=str, required=False, location='args')
        parser.add_argument('projeto_id', type=int, required=False, location='args')
        parser.add_argument('segmento_id', type=int, required=False, location='args')
        parser.add_argument('nome', type=str, required=False, location='args')
        parser.add_argument('razao_social', type=str, required=False, location='args')
        args = parser.parse_args()

        max_camadas = args.get('camadas')
        clusters = {"clusters": list()}

        enderecos_empresa = []
        enderecos_pessoa = []
        if args['uf']:
            enderecos_empresa = RelacionamentosResource.get_entidades_por_estado(
                args['uf'], args['cidade'], 3
            )
            enderecos_pessoa = RelacionamentosResource.get_entidades_por_estado(
                args['uf'], args['cidade'], 1
            )

        df_relacionamentos = RelacionamentosResource.buscar_relacionamentos()
        df_tipo_relacao = TipoRelacao.to_dataframe(TipoRelacao.query.all(), TipoRelacao.__table__.columns)
        df_tipo_relacao["tipo_relacao_id"] = df_tipo_relacao["tipo_relacao_id"].astype(int)
        ids_empresa = RelacionamentosResource.coletar_ids_entidades(df_relacionamentos, 3)
        ids_pessoa = RelacionamentosResource.coletar_ids_entidades(df_relacionamentos, 1)
        ids_advogado = RelacionamentosResource.coletar_ids_entidades(df_relacionamentos, 4)
        ids_escritorio = RelacionamentosResource.coletar_ids_entidades(df_relacionamentos, 5)

        df_empresas, df_pessoas, df_advogados, df_escritorios = RelacionamentosResource.buscar_entidades(
            ids_empresa,
            ids_pessoa,
            ids_advogado,
            ids_escritorio
        )

        stakeholders = RelacionamentosResource.filtrar_stakeholders(pd.concat([df_empresas, df_pessoas],
                                                                              ignore_index=True), args,
                                                                               enderecos_pessoa, enderecos_empresa)
        clusters_start_time = time.time()
        for i, stakeholder in enumerate(stakeholders):
            clusters["clusters"].append(RelacionamentosResource.montar_cluster(i,
                                                                               stakeholder,
                                                                               df_relacionamentos,
                                                                               df_tipo_relacao,
                                                                               df_empresas,
                                                                               df_pessoas,
                                                                               df_advogados,
                                                                               df_escritorios,
                                                                               max_camadas,
                                                                               enderecos_empresa,
                                                                               enderecos_pessoa,
                                                                               args))
        print(f"Tempo para criar todos os clusters: "
              f"{time.time() - clusters_start_time:.4f} segundos")

        return clusters, 200

    @staticmethod
    def montar_cluster(cluster_id, stakeholder, df_relacionamentos, df_tipo_relacao, df_empresas,
                       df_pessoas, df_advogados, df_escritorios, camadas, enderecos_empresa, enderecos_pessoa, args):
        """
        Constrói um cluster contendo os nós e links para um stakeholder específico.

        Parâmetros:
        - stakeholder (objeto): Entidade inicial para a construção do cluster.
        - df_relacionamentos (DataFrame): Relacionamentos disponíveis.
        - df_tipo_relacao (DataFrame): Tipos de relações existentes.
        - df_empresas (DataFrame): Dados das empresas.
        - df_pessoas (DataFrame): Dados das pessoas.
        - df_advogados (DataFrame): Dados dos advogados.
        - df_escritorios (DataFrame): Dados dos escritórios.
        - camadas (int): Número máximo de camadas a explorar.

        Retorna:
        dict: Um dicionário contendo os nós e links do cluster.
        """
        tipo_id, entidade_id = stakeholder.id.split(":")
        df_relacionamentos_filtrados = RelacionamentosResource.filtrar_relacionamentos(df_relacionamentos,
                                                                                       tipo_id,
                                                                                       entidade_id,
                                                                                       camadas,
                                                                                       cluster_id)

        nodes, links = {stakeholder}, set()
        nodes = RelacionamentosResource.processar_rede(nodes, df_relacionamentos_filtrados,
                                                       df_empresas, df_pessoas, df_advogados,
                                                       df_escritorios,
                                                       enderecos_pessoa,
                                                       enderecos_empresa,
                                                       args)
        links = RelacionamentosResource.adicionar_links(links, df_relacionamentos_filtrados, df_tipo_relacao)

        cluster = {
            "nodes": serialize_objects(nodes),
            "links": serialize_objects(links)
        }

        return cluster

    @staticmethod
    def processar_rede(nodes, df_relacionamentos, df_empresas, df_pessoas,
                      df_advogados, df_escritorios, enderecos_pessoa, enderecos_empresa, args):
        """
        Processa a rede de relacionamentos adicionando novos nós ao grafo.

        Parâmetros:
        - nodes (set): Conjunto atual de nós.
        - df_relacionamentos (DataFrame): Relacionamentos disponíveis.
        - df_empresas (DataFrame): Dados das empresas.
        - df_pessoas (DataFrame): Dados das pessoas.
        - df_advogados (DataFrame): Dados dos advogados.
        - df_escritorios (DataFrame): Dados dos escritórios.

        Retorna:
        set: Conjunto atualizado de nós.
        """
        entidades = RelacionamentosResource.zipar_entidades(df_relacionamentos)

        for entidade in entidades:
            tipo_entidade, entidade_id, subgroup = entidade

            dados_entidade = None
            if tipo_entidade == 1:
                dados_entidade = df_pessoas[df_pessoas.pessoa_id == entidade_id]
            elif tipo_entidade == 3:
                dados_entidade = df_empresas[df_empresas.empresa_id == entidade_id]
            elif tipo_entidade == 4:
                dados_entidade = df_advogados[df_advogados.advogado_id == entidade_id]
            elif tipo_entidade == 5:
                dados_entidade = df_escritorios[df_escritorios.escritorio_id == entidade_id]

            new_node = None

            if not dados_entidade.empty:
                dados_entidade = dados_entidade.iloc[0]

                Entidade = namedtuple("Entidade", dados_entidade.index)
                entidade_obj = Entidade(*dados_entidade.values)

                if tipo_entidade == 3:
                    if not entidade_obj.stakeholder:
                        enderecos_id = enderecos_empresa
                        new_node = RelacionamentosResource.montar_node(
                            dados_entidade,
                            RelacionamentosResource.aplicar_filtros(entidade_obj, args, enderecos_id),
                            False,
                            subgroup
                        )
                else:
                    new_node = RelacionamentosResource.montar_node(dados_entidade, False, False, subgroup)

                RelacionamentosResource.add_node(nodes, new_node)

        return nodes

    @staticmethod
    def adicionar_links(links, df_relacionamentos, df_tipo_relacao):
        """
        Adiciona links ao grafo com base nos relacionamentos fornecidos.

        Parâmetros:
        - links (set): Conjunto atual de links.
        - df_relacionamentos (DataFrame): Relacionamentos disponíveis.
        - df_tipo_relacao (DataFrame): Tipos de relações existentes.

        Retorna:
        set: Conjunto atualizado de links.
        """
        for relacionamento in df_relacionamentos.itertuples(index=False, name="Relacionamento"):
            entidade_origem_id = f"{relacionamento.tipo_origem_id}:{relacionamento.entidade_origem_id}"
            entidade_destino_id = f"{relacionamento.tipo_destino_id}:{relacionamento.entidade_destino_id}"
            tipo_relacao = df_tipo_relacao[df_tipo_relacao.tipo_relacao_id == relacionamento.tipo_relacao_id].iloc[0]

            new_link = Link(source=entidade_origem_id,
                            target=entidade_destino_id,
                            label=tipo_relacao.descricao)

            if new_link not in links:
                links.add(new_link)

        return links

    @staticmethod
    def buscar_relacionamentos():
        """
        Recupera todos os relacionamentos existentes no banco de dados.

        Retorna:
        DataFrame: Um DataFrame contendo os relacionamentos estruturados.
        """
        relacionamentos_start_time = time.time()

        df_result = Relacionamentos.to_dataframe(
            Relacionamentos.query
            .order_by(
                Relacionamentos.entidade_origem_id,
                Relacionamentos.tipo_origem_id,
                Relacionamentos.entidade_destino_id,
                Relacionamentos.tipo_destino_id
            )
            .all(),
            Relacionamentos.__table__.columns
        )
        df_result['entidade_origem_id'] = df_result['entidade_origem_id'].astype(int)
        df_result['tipo_origem_id'] = df_result['tipo_origem_id'].astype(int)
        df_result['entidade_destino_id'] = df_result['entidade_destino_id'].astype(int)
        df_result['tipo_destino_id'] = df_result['tipo_destino_id'].astype(int)

        relacionamentos_end_time = time.time()
        print(f"Tempo para coletar os relacionamentos: "
              f"{relacionamentos_end_time - relacionamentos_start_time:.4f} segundos")

        return df_result

    @staticmethod
    def coletar_ids_entidades(relacionamentos_df, tipo_entidade):
        """
         Coleta IDs de entidades específicas com base no tipo de entidade.

         Parâmetros:
         - df_relacionamentos (DataFrame): Relacionamentos disponíveis.
         - tipo_entidade (int): Tipo de entidade a ser filtrada.

         Retorna:
         list: Lista de IDs das entidades filtradas.
         """
        ids_start_time = time.time()

        # Filtrar IDs de origem e destino para cada tipo de entidade
        ids_entidade = list(map(int, set(
            relacionamentos_df.loc[relacionamentos_df['tipo_origem_id'] == tipo_entidade, 'entidade_origem_id']
            .dropna().unique()).union(
            relacionamentos_df.loc[relacionamentos_df['tipo_destino_id'] == tipo_entidade, 'entidade_destino_id']
            .dropna().unique()
        )))

        ids_end_time = time.time()
        print(f"Tempo para coletar os IDs das entidades: "
              f"{ids_end_time - ids_start_time:.4f} segundos")

        # Retorna os conjuntos organizados como listas
        return ids_entidade

    @staticmethod
    def buscar_entidades(ids_empresa, ids_pessoa, ids_advogado, ids_escritorio):
        entidades_start_time = time.time()

        df_empresas = Empresa.to_dataframe(Empresa.query.filter(
            Empresa.empresa_id.in_(ids_empresa)).all(), Empresa.__table__.columns)
        df_pessoas = Pessoa.to_dataframe(Pessoa.query.filter(
            Pessoa.pessoa_id.in_(ids_pessoa)).all(), Pessoa.__table__.columns)
        df_advogados = Advogado.to_dataframe(Advogado.query.filter(
            Advogado.advogado_id.in_(ids_advogado)).all(), Advogado.__table__.columns)
        df_escritorios = Escritorio.to_dataframe(Escritorio.query.filter(
            Escritorio.escritorio_id.in_(ids_escritorio)).all(), Escritorio.__table__.columns)

        df_empresas['empresa_id'] = df_empresas['empresa_id'].astype(int)
        df_pessoas['pessoa_id'] = df_pessoas['pessoa_id'].astype(int)
        df_advogados['advogado_id'] = df_advogados['advogado_id'].astype(int)
        df_escritorios['escritorio_id'] = df_escritorios['escritorio_id'].astype(int)

        entidades_end_time = time.time()
        print(f"Tempo para buscar todas as entidades: "
              f"{entidades_end_time - entidades_start_time:.4f} segundos")

        return df_empresas, df_pessoas, df_advogados, df_escritorios

    @staticmethod
    def montar_node(entidade, matched=False, root=False, subgroup=None):
        """
        Monta um objeto Node com base nos atributos da entidade fornecida.

        :param entidade: Tupla contendo atributos da entidade (gerada por itertuples).
        :param matched: Booleano indicando se o nó foi combinado (matched).
        :param root: Booleano indicando se o nó é a raiz (root).
        :param subgroup: Subgrupo a que o node pertence.
        :return: Objeto Node ou None se não houver ID.
        """
        is_stakeholder = entidade.stakeholder if (hasattr(entidade, "stakeholder")
                                                  and pd.notna(entidade.stakeholder)) else False
        em_prospecao = entidade.em_prospecao if (hasattr(entidade, "em_prospecao")
                                                 and pd.notna(entidade.em_prospecao)) else False
        new_node = Node(
            stakeholder=is_stakeholder,
            em_prospeccao=em_prospecao,
            matched=matched,
            root=root,
            subgroup=subgroup if pd.notna(subgroup) else None
        )

        if hasattr(entidade, "pessoa_id") and pd.notna(entidade.pessoa_id):
            new_node.id = f"1:{entidade.pessoa_id}".split(".")[0]
            new_node.label = f"{safe_strip(entidade.firstname)} {safe_strip(entidade.lastname)}"
            new_node.type = "Pessoa"
            new_node.title = new_node.label
            new_node.documento = entidade.cpf

        elif hasattr(entidade, "empresa_id") and pd.notna(entidade.empresa_id):
            new_node.id = f"3:{entidade.empresa_id}".split(".")[0]
            new_node.label = safe_strip(entidade.razao_social)
            new_node.type = "Empresa"
            new_node.title = new_node.label
            new_node.documento = entidade.cnpj

        elif hasattr(entidade, "advogado_id") and pd.notna(entidade.advogado_id):
            new_node.id = f"4:{entidade.advogado_id}".split(".")[0]
            new_node.label = f"{safe_strip(entidade.firstname)} {safe_strip(entidade.lastname)}"
            new_node.type = "Advogado"
            new_node.title = new_node.label
            new_node.documento = entidade.oab

        elif hasattr(entidade, "escritorio_id") and pd.notna(entidade.escritorio_id):
            new_node.id = f"5:{entidade.escritorio_id}".split(".")[0]
            new_node.label = safe_strip(entidade.razao_social)
            new_node.type = "Escritorio"
            new_node.title = new_node.label
            new_node.documento = entidade.cnpj

        return new_node if new_node.id else None

    @staticmethod
    def add_node(nodes, new_node):
        if new_node and new_node not in nodes:
            nodes.add(new_node)

        return nodes

    @staticmethod
    def filtrar_stakeholders(df_entidades, filtros, enderecos_pessoa, enderecos_empresa):
        """
        Filtra os stakeholders com base nos filtros fornecidos.

        :param df_entidades: DataFrame contendo as colunas de atributos das entidades.
        :param filtros: Dicionário com filtros como 'uf' e 'cidade'.
        :return: Um conjunto de stakeholders filtrados.
        """
        stakeholders = set()

        if df_entidades.empty:
            return stakeholders
        df_entidades = df_entidades[df_entidades['stakeholder']]

        documento = validar_documento(filtros['documento']) if filtros.get('documento') else None

        stakeholders_start_time = time.time()
        for entidade in df_entidades.itertuples(index=False, name="Entidade"):
            stakeholder_documento = entidade.cpf if pd.notna(entidade.pessoa_id) else entidade.cnpj
            if documento and stakeholder_documento != documento:
                continue

            enderecos_id = (enderecos_pessoa if pd.notna(entidade.pessoa_id) else enderecos_empresa)
            new_node = RelacionamentosResource.montar_node(
                entidade,
                RelacionamentosResource.aplicar_filtros(entidade, filtros, enderecos_id),
                True
            )
            stakeholders = RelacionamentosResource.add_node(stakeholders, new_node)

        stakeholders_end_time = time.time()
        print(f"Tempo para filtrar os stakeholders: "
              f"{stakeholders_end_time - stakeholders_start_time:.4f} segundos")

        return stakeholders


    @staticmethod
    def aplicar_filtros(entidade, filtros, enderecos_id=None):
        matched = False
    
        if pd.notna(entidade.em_prospecao) and filtros.get("em_prospecao"):
            matched = filtros.get("em_prospecao")

        if not hasattr(entidade, 'empresa_id') and pd.notna(entidade.associado) and filtros.get("associado"):
            matched = filtros.get("associado")

        if filtros.get("uf"):
            entidade_id = entidade.empresa_id if pd.notna(entidade.empresa_id) \
                else entidade.pessoa_id
            matched = True if entidade_id in enderecos_id else False

        if not hasattr(entidade, 'empresa_id') and pd.notna(entidade.pessoa_id) and filtros.get("nome"):
            filtro_nome = filtros.get("nome")
            matched = RelacionamentosResource.calcular_similaridade(entidade.firstname, filtro_nome) >= 82

        if pd.notna(entidade.empresa_id) and filtros.get("razao_social"):
            filtro_razao_social = filtros.get("razao_social")
            print("### Precisao: ", RelacionamentosResource.calcular_similaridade(entidade.razao_social, filtro_razao_social))
            matched = RelacionamentosResource.calcular_similaridade(entidade.razao_social, filtro_razao_social) >= 85
        
        if hasattr(entidade, "projeto_id") and filtros.get("projeto_id"):
            matched = entidade.projeto_id == filtros["projeto_id"]
            
        if hasattr(entidade, "empresa_id") and filtros.get("segmento_id"):
            matched = entidade.segmento_id == filtros["segmento_id"]

        return matched

    @staticmethod
    def get_entidades_por_estado(uf, cidade=None, tipo=None):
        if tipo == 3:
            enderecos_empresa = EnderecosResource.get_enderecos_em_estado(uf, cidade, 3)
            empresa_ids = {endereco.entidade_id for endereco in enderecos_empresa}
            return empresa_ids
        if tipo == 1:
            enderecos_pessoa = EnderecosResource.get_enderecos_em_estado(uf, cidade, 1)
            pessoa_ids = {endereco.entidade_id for endereco in enderecos_pessoa}
            return pessoa_ids

    @staticmethod
    def filtrar_relacionamentos(df_relacionamentos, tipo_entidade_raiz_id, entidade_raiz_id, max_camadas, cluster_id):
        tipo_entidade_raiz_id = int(tipo_entidade_raiz_id)
        entidade_raiz_id = int(entidade_raiz_id.split(".")[0])

        df_todos_relacionamentos = pd.DataFrame()

        # Adiciona a coluna 'subgroup' no DataFrame, inicializando com NaN
        df_relacionamentos = df_relacionamentos.copy()
        df_relacionamentos['subgroup'] = pd.NA

        # Define o conjunto inicial de entidades a serem exploradas, começando pela entidade raiz
        entidades_para_visitar = {(entidade_raiz_id, tipo_entidade_raiz_id)}

        # Cria um conjunto para manter controle das entidades que já foram visitadas e evitar ciclos
        entidades_visitadas = set()

        # Define a camada inicial
        camada_atual = 0

        # Enquanto ainda houver entidades para visitar e a camada atual for menor que o limite de camadas
        while entidades_para_visitar and camada_atual < max_camadas:
            # Define um novo conjunto para armazenar entidades que serão visitadas na próxima camada
            nova_entidades_para_visitar = set()

            # Percorre todas as entidades na camada atual
            for entidade_atual_id, tipo_entidade_atual_id in entidades_para_visitar:
                # Marca a entidade atual como visitada
                entidades_visitadas.add((entidade_atual_id, tipo_entidade_atual_id))

                # Cria um identificador único para o subgrupo da entidade atual
                subgrupo_id = f"{cluster_id}:{camada_atual}:{entidade_atual_id}"

                # Filtra os relacionamentos no DataFrame (df_relacionamentos)
                df_relacionamentos_encontrados = df_relacionamentos[
                    ((df_relacionamentos['entidade_origem_id'] == entidade_atual_id) &
                     (df_relacionamentos['tipo_origem_id'] == tipo_entidade_atual_id)) |
                    ((df_relacionamentos['entidade_destino_id'] == entidade_atual_id) &
                     (df_relacionamentos['tipo_destino_id'] == tipo_entidade_atual_id))
                    ]

                # Adiciona o identificador do subgrupo às linhas correspondentes
                df_relacionamentos.loc[df_relacionamentos_encontrados.index, 'subgroup'] = subgrupo_id

                # Adiciona todos os relacionamentos encontrados à lista final de relacionamentos
                df_todos_relacionamentos = pd.concat([df_todos_relacionamentos, df_relacionamentos_encontrados],
                                                     ignore_index=True)

                # Para cada relacionamento, identifica a próxima entidade conectada
                for _, relacionamento in df_relacionamentos_encontrados.iterrows():
                    # Verifica se a entidade atual é origem; se for, a próxima é o destino; caso contrário, a próxima é a origem
                    if (relacionamento['entidade_origem_id'], relacionamento['tipo_origem_id']) == (
                            entidade_atual_id, tipo_entidade_atual_id):
                        proxima_entidade = (relacionamento['entidade_destino_id'], relacionamento['tipo_destino_id'])
                    else:
                        proxima_entidade = (relacionamento['entidade_origem_id'], relacionamento['tipo_origem_id'])

                    # Adiciona a próxima entidade ao conjunto da próxima camada se ainda não foi visitada
                    if proxima_entidade not in entidades_visitadas:
                        nova_entidades_para_visitar.add(proxima_entidade)

            # Incrementa a camada atual, avançando para a próxima camada
            camada_atual += 1

            # Atualiza as entidades para visitar na próxima camada
            entidades_para_visitar = nova_entidades_para_visitar

        df_relacionamentos_desconexos = df_todos_relacionamentos.loc[df_todos_relacionamentos['subgroup'].isna()]
        df_todos_relacionamentos = df_todos_relacionamentos.dropna(subset=['subgroup'])

        if not df_relacionamentos_desconexos.empty:
            df_todos_relacionamentos = pd.concat([df_todos_relacionamentos,
                                                  RelacionamentosResource.agrupar_relacionamentos(df_relacionamentos_desconexos)],
                                                 ignore_index=True)

        return df_todos_relacionamentos

    @staticmethod
    def zipar_entidades(df_relacionamentos):
        entidades_set = set()

        entidades_set.update(
            zip(df_relacionamentos['tipo_origem_id'], df_relacionamentos['entidade_origem_id'], df_relacionamentos['subgroup']))
        entidades_set.update(
            zip(df_relacionamentos['tipo_destino_id'], df_relacionamentos['entidade_destino_id'], df_relacionamentos['subgroup']))

        return entidades_set

    @staticmethod
    def agrupar_relacionamentos(df_relacionamentos):
        return df_relacionamentos.groupby("subgroup").agg({
            "tipo_origem_id": list,
            "entidade_origem_id": list,
            "tipo_destino_id": list,
            "entidade_destino_id": list,
            "tipo_relacao_id": list
        }).reset_index()
        
    @staticmethod
    def calcular_similaridade(a, b):
        if not isinstance(a, str):
            a = str(a) if a is not None else ""
        if not isinstance(b, str):
            b = str(b) if b is not None else ""
            
        return partial_ratio(a.lower(), b.lower())
