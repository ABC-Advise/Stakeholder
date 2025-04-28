from operator import and_, or_
import time

from flask_restful import Resource, reqparse

from app import db
from app.modules.utils import validar_documento
from app.modules.exceptions import InvalidStakeholder
from app.models.empresa import Empresa
from app.models.pessoa import Pessoa
from app.models.advogado import Advogado
from app.models.escritorio import Escritorio
from app.models.relacionamentos import Relacionamentos
from app.models.tipo_entidade import TipoEntidade
from app.resources.endereco import EnderecosResource


class RelacionamentosResource(Resource):
    """
    Recurso para buscar relacionamentos de entidades e retornar no formato de grafo.
    """

    @staticmethod
    def get():
        start_time = time.time()  # Início da medição de tempo total

        # 1. Medir o tempo do parsing dos argumentos
        parse_start_time = time.time()
        parser = reqparse.RequestParser()
        parser.add_argument('documento', type=str, required=False, location='args', help='Documento (CPF ou CNPJ)')
        parser.add_argument('camadas', type=int, required=False, location='args')
        parser.add_argument('em_prospecao', type=bool, required=False, location='args')
        parser.add_argument('associado', type=bool, required=False, location='args')
        parser.add_argument('uf', type=str, required=False, location='args')
        parser.add_argument('cidade', type=str, required=False, location='args')
        parser.add_argument('projeto_id', type=int, required=False, location='args')
        args = parser.parse_args()
        parse_end_time = time.time()

        print(f"Tempo para parsing dos argumentos: {parse_end_time - parse_start_time:.4f} segundos")

        # Validando o documento apenas se fornecido
        documento = validar_documento(args['documento']) if args.get('documento') else None
        max_camadas = args.get('camadas')

        nodes = {}
        links = []

        if documento:
            tipo_entidade = {tipo.tipo_entidade_id: tipo.descricao for tipo in TipoEntidade.query.all()}

            # 2. Medir o tempo para adicionar o nó raiz
            add_no_raiz_start_time = time.time()
            tipo_entidade_raiz_id, entidade_raiz_id = RelacionamentosResource.adicionar_no_raiz(documento, nodes)
            add_no_raiz_end_time = time.time()

            print(f"Tempo para adicionar o nó raiz: {add_no_raiz_end_time - add_no_raiz_start_time:.4f} segundos")

            # 3. Medir o tempo para coletar os relacionamentos
            relacionamentos_start_time = time.time()
            if max_camadas:
                relacionamentos = RelacionamentosResource.coletar_relacionamentos_por_camadas(
                    entidade_raiz_id, tipo_entidade_raiz_id, max_camadas
                )
            else:
                relacionamentos = RelacionamentosResource.coletar_relacionamentos_conectados(
                    entidade_raiz_id, tipo_entidade_raiz_id
                )
            relacionamentos_end_time = time.time()

            print(
                f"Tempo para coletar os relacionamentos: {relacionamentos_end_time - relacionamentos_start_time:.4f} segundos")

            # 4. Medir o tempo para coletar os IDs das entidades
            ids_start_time = time.time()
            ids_empresas, ids_pessoas, ids_advogados, ids_escritorios = RelacionamentosResource.coletar_ids_entidades(
                relacionamentos)
            ids_end_time = time.time()

            print(f"Tempo para coletar os IDs das entidades: {ids_end_time - ids_start_time:.4f} segundos")

            # 5. Medir o tempo para consultar as entidades em massa
            cache_start_time = time.time()
            cache_empresas = {empresa.empresa_id: empresa for empresa in
                              Empresa.query.filter(Empresa.empresa_id.in_(ids_empresas)).all()}
            cache_pessoas = {pessoa.pessoa_id: pessoa for pessoa in
                             Pessoa.query.filter(Pessoa.pessoa_id.in_(ids_pessoas)).all()}
            cache_advogados = {advogado.advogado_id: advogado for advogado in
                               Advogado.query.filter(Advogado.advogado_id.in_(ids_advogados)).all()}
            cache_escritorios = {escritorio.escritorio_id: escritorio for escritorio in
                                 Escritorio.query.filter(Escritorio.escritorio_id.in_(ids_escritorios)).all()}
            cache_end_time = time.time()

            print(f"Tempo para consultar as entidades em massa: {cache_end_time - cache_start_time:.4f} segundos")

            # 6. Processa relacionamentos para montar nós e links
            process_relacionamentos_start_time = time.time()
            for relacionamento in relacionamentos:
                entidade_origem_id = f"{relacionamento.tipo_origem_id}:{relacionamento.entidade_origem_id}"
                entidade_destino_id = f"{relacionamento.tipo_destino_id}:{relacionamento.entidade_destino_id}"

                # Adicionar nó de origem
                RelacionamentosResource.adicionar_no(entidade_origem_id, relacionamento.tipo_origem_id, cache_empresas,
                                                     cache_pessoas, cache_advogados, cache_escritorios, nodes,
                                                     tipo_entidade)

                # Adicionar nó de destino
                RelacionamentosResource.adicionar_no(entidade_destino_id, relacionamento.tipo_destino_id,
                                                     cache_empresas,
                                                     cache_pessoas, cache_advogados, cache_escritorios, nodes,
                                                     tipo_entidade)

                # Adicionar link entre os nós
                RelacionamentosResource.add_link(entidade_origem_id, entidade_destino_id,
                                                 relacionamento.tipo_relacao.descricao, links)

            process_relacionamentos_end_time = time.time()
            print(
                f"Tempo para processar os relacionamentos e montar nós/links: {process_relacionamentos_end_time - process_relacionamentos_start_time:.4f} segundos")

        else:
            print("Documento não fornecido, retornando todos os relacionamentos e entidades.")

            entidades_start_time = time.time()
            empresas = Empresa.query.all()
            pessoas = Pessoa.query.all()
            advogados = Advogado.query.all()
            escritorios = Escritorio.query.all()

            if empresas:
                for empresa in empresas:
                    matched = False

                    if empresa.stakeholder == True:
                        if args['em_prospecao'] and empresa.em_prospecao == args['em_prospecao']:
                            matched = True

                        elif args['projeto_id'] and empresa.projeto_id == args['projeto_id']:
                            matched = True

                        elif args['uf']:
                            empresa_ids = RelacionamentosResource.get_entidades_por_estado(args['uf'],
                                                                                           args.get('cidade', None), 3)

                            if empresa_ids:
                                for empresa_id in empresa_ids:
                                    if empresa_id == empresa.empresa_id:
                                        matched = True

                    RelacionamentosResource.add_node(f"3:{empresa.empresa_id}", empresa.cnpj, 'Empresa',
                                                     empresa.razao_social,
                                                     nodes, empresa.stakeholder, empresa.nome_fantasia,
                                                     empresa.em_prospecao, matched)

            if pessoas:
                for pessoa in pessoas:
                    matched = False

                    if pessoa.stakeholder:
                        if args['em_prospecao'] and pessoa.em_prospecao == args['em_prospecao']:
                            matched = True

                        elif args['associado'] and pessoa.associado == args['associado']:
                            matched = True

                        elif args['projeto_id'] and pessoa.projeto_id == args['projeto_id']:
                            matched = True

                        elif args['uf']:
                            pessoa_ids = RelacionamentosResource.get_entidades_por_estado(args['uf'],
                                                                                          args.get('cidade', None), 1)

                            if pessoa_ids:
                                for pessoa_id in pessoa_ids:
                                    if pessoa_id == pessoa.pessoa_id:
                                        matched = True

                    RelacionamentosResource.add_node(f"1:{pessoa.pessoa_id}", pessoa.cpf, 'Pessoa', pessoa.firstname,
                                                     nodes, pessoa.stakeholder, pessoa.lastname, pessoa.em_prospecao,
                                                     matched)

            if advogados:
                for advogado in advogados:
                    RelacionamentosResource.add_node(f"4:{advogado.advogado_id}", advogado.oab, 'Advogado',
                                                     advogado.firstname, nodes, False, advogado.lastname, None)

            if escritorios:
                for escritorio in escritorios:
                    RelacionamentosResource.add_node(f"5:{escritorio.escritorio_id}", escritorio.escritorio_id,
                                                     'Escritório', escritorio.razao_social, nodes, False,
                                                     escritorio.nome_fantasia)

            entidades_end_time = time.time()
            print(
                f"Tempo para adicionar todas as entidades como nós: {entidades_end_time - entidades_start_time:.4f} segundos")

            if not empresas and not pessoas and not advogados and not escritorios:
                return "", 204

            relacionamentos_start_time = time.time()
            relacionamentos = Relacionamentos.query.all()

            for relacionamento in relacionamentos:
                entidade_origem_id = f"{relacionamento.tipo_origem_id}:{relacionamento.entidade_origem_id}"
                entidade_destino_id = f"{relacionamento.tipo_destino_id}:{relacionamento.entidade_destino_id}"

                RelacionamentosResource.add_link(entidade_origem_id, entidade_destino_id,
                                                 relacionamento.tipo_relacao.descricao, links)

            relacionamentos_end_time = time.time()
            print(
                f"Tempo para adicionar todos os relacionamentos como links: {relacionamentos_end_time - relacionamentos_start_time:.4f} segundos")

        # Monta e retorna a resposta, com `nodes` e `links` sempre inclusos
        response_data = {
            "nodes": list(nodes.values()),
            "links": links
        }

        total_end_time = time.time()
        print(f"Tempo total de execução do método: {total_end_time - start_time:.4f} segundos")

        return response_data, 200

    @staticmethod
    def coletar_ids_entidades(relacionamentos):
        """
        Coleta os IDs de todas as entidades nos relacionamentos para consulta em massa.
        """
        ids_empresas = set()
        ids_pessoas = set()
        ids_advogados = set()
        ids_escritorios = set()

        for relacionamento in relacionamentos:
            if relacionamento.tipo_origem_id == 3:
                ids_empresas.add(relacionamento.entidade_origem_id)
            elif relacionamento.tipo_origem_id == 1:
                ids_pessoas.add(relacionamento.entidade_origem_id)
            elif relacionamento.tipo_origem_id == 4:
                ids_advogados.add(relacionamento.entidade_origem_id)
            elif relacionamento.tipo_origem_id == 5:
                ids_escritorios.add(relacionamento.entidade_origem_id)

            if relacionamento.tipo_destino_id == 3:
                ids_empresas.add(relacionamento.entidade_destino_id)
            elif relacionamento.tipo_destino_id == 1:
                ids_pessoas.add(relacionamento.entidade_destino_id)
            elif relacionamento.tipo_destino_id == 4:
                ids_advogados.add(relacionamento.entidade_destino_id)
            elif relacionamento.tipo_destino_id == 5:
                ids_escritorios.add(relacionamento.entidade_destino_id)

        return ids_empresas, ids_pessoas, ids_advogados, ids_escritorios

    @staticmethod
    def adicionar_no(node_id, tipo_entidade_id, cache_empresas, cache_pessoas, cache_advogados, cache_escritorios,
                     nodes, tipo_entidade):
        """
        Adiciona um nó ao grafo usando os dados das entidades já carregadas em cache.
        """
        if node_id in nodes:
            return  # Se o nó já foi adicionado, não o adiciona novamente

        tipo_raiz = tipo_entidade.get(tipo_entidade_id)
        entidade_id = node_id.split(":")[1]

        if tipo_raiz == 'Empresa' and int(entidade_id) in cache_empresas:
            empresa = cache_empresas[int(entidade_id)]
            RelacionamentosResource.add_node(node_id, empresa.cnpj, 'Empresa', empresa.razao_social,
                                             nodes, empresa.stakeholder, empresa.nome_fantasia,
                                             em_prospeccao=empresa.em_prospecao)
        elif tipo_raiz == 'Pessoa' and int(entidade_id) in cache_pessoas:
            pessoa = cache_pessoas[int(entidade_id)]
            RelacionamentosResource.add_node(node_id, pessoa.cpf, 'Pessoa', pessoa.firstname,
                                             nodes, pessoa.stakeholder, pessoa.lastname,
                                             em_prospeccao=pessoa.em_prospecao)
        elif tipo_raiz == 'Advogado' and int(entidade_id) in cache_advogados:
            advogado = cache_advogados[int(entidade_id)]
            RelacionamentosResource.add_node(node_id, advogado.oab, 'Advogado', advogado.firstname,
                                             nodes, False, advogado.lastname)
        elif tipo_raiz == 'Escritorio' and int(entidade_id) in cache_escritorios:
            escritorio = cache_escritorios[int(entidade_id)]
            RelacionamentosResource.add_node(node_id, escritorio.escritorio_id, 'Escritório',
                                             escritorio.razao_social, nodes, False, escritorio.nome_fantasia)

    @staticmethod
    def add_node(node_id, documento, tipo, nome1, nodes, stakeholder,
                 nome2=None, em_prospeccao=False, matched=False, root=False):
        """
        Função para adicionar um nó ao grafo.
        """
        if node_id not in nodes:
            label = nome1 if not nome2 else f"{nome1} {nome2}"
            nodes[node_id] = {
                "id": node_id,
                "label": label,
                "type": tipo,
                "title": label,
                "documento": documento,
                "stakeholder": stakeholder,
                "em_prospeccao": em_prospeccao,
                "matched": matched,
                "root": root
            }

    @staticmethod
    def add_link(source_id, target_id, relationship_label, links):
        """
        Função para adicionar um link entre dois nós.
        """
        link = {
            "source": source_id,
            "target": target_id,
            "label": relationship_label
        }
        if link not in links:
            links.append(link)

    @staticmethod
    def adicionar_no_raiz(documento, nodes):
        """
        Adiciona o nó raiz ao grafo antes de iniciar a busca.
        """
        # Buscando os detalhes da entidade raiz (pessoa, empresa, advogado, etc.)
        if len(documento) == 14:
            raiz = Empresa.query.filter_by(cnpj=documento).first()

            if not raiz:
                raise InvalidStakeholder(f"CNPJ {documento} não existe ou não está cadastrado como Stakeholder")

            RelacionamentosResource.add_node(f"3:{raiz.empresa_id}", raiz.cnpj, 'Empresa', raiz.razao_social,
                                             nodes, raiz.stakeholder, raiz.nome_fantasia, raiz.em_prospecao)
            return 3, raiz.empresa_id
        elif len(documento) == 11:
            raiz = Pessoa.query.filter_by(cpf=documento).first()

            if not raiz:
                raise InvalidStakeholder(f"CPF {documento} não existe ou não está cadastrado como Stakeholder")

            RelacionamentosResource.add_node(f"1:{raiz.pessoa_id}", raiz.cpf, 'Pessoa', raiz.firstname,
                                             nodes, raiz.stakeholder, raiz.lastname, raiz.em_prospecao)
            return 1, raiz.pessoa_id

    @staticmethod
    def coletar_relacionamentos_conectados(entidade_raiz_id, tipo_entidade_raiz_id):
        """
        Função para coletar todos os relacionamentos diretos e indiretos conectados à entidade raiz.
        """
        todos_relacionamentos = []
        # Conjunto de entidades a serem visitadas, começando com a raiz
        entidades_para_visitar = {(entidade_raiz_id, tipo_entidade_raiz_id)}
        # Conjunto de entidades já visitadas para evitar ciclos
        entidades_visitadas = set()

        while entidades_para_visitar:
            # Remover uma entidade da lista de pendentes para processar
            entidade_atual_id, tipo_entidade_atual_id = entidades_para_visitar.pop()
            # Marcar a entidade atual como visitada
            entidades_visitadas.add((entidade_atual_id, tipo_entidade_atual_id))

            # Buscar todos os relacionamentos onde a entidade atual é origem ou destino
            relacionamentos = Relacionamentos.query.filter(
                (Relacionamentos.entidade_origem_id == entidade_atual_id) & (
                            Relacionamentos.tipo_origem_id == tipo_entidade_atual_id) |
                (Relacionamentos.entidade_destino_id == entidade_atual_id) & (
                            Relacionamentos.tipo_destino_id == tipo_entidade_atual_id)
            ).all()

            # Adicionar os relacionamentos encontrados à lista final
            todos_relacionamentos.extend(relacionamentos)

            # Expandir a busca para as entidades conectadas (origem ou destino)
            for relacionamento in relacionamentos:
                # Se a entidade atual for origem, a outra entidade é o destino, e vice-versa
                if (relacionamento.entidade_origem_id, relacionamento.tipo_origem_id) == (
                entidade_atual_id, tipo_entidade_atual_id):
                    proxima_entidade = (relacionamento.entidade_destino_id, relacionamento.tipo_destino_id)
                else:
                    proxima_entidade = (relacionamento.entidade_origem_id, relacionamento.tipo_origem_id)

                # Adicionar a próxima entidade para visitar, caso ainda não tenha sido visitada
                if proxima_entidade not in entidades_visitadas:
                    entidades_para_visitar.add(proxima_entidade)

        return todos_relacionamentos

    @staticmethod
    def coletar_relacionamentos_por_camadas(entidade_raiz_id, tipo_entidade_raiz_id, max_camadas):
        """
        Função para coletar relacionamentos até um número especificado de camadas a partir da entidade raiz.
        """
        # Inicializa a lista para armazenar todos os relacionamentos encontrados
        todos_relacionamentos = []

        # Define o conjunto inicial de entidades a serem exploradas, começando pela entidade raiz
        entidades_para_visitar = {(entidade_raiz_id, tipo_entidade_raiz_id)}
        print(entidades_para_visitar)
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

                # Consulta todos os relacionamentos em que a entidade atual é origem ou destino
                relacionamentos = Relacionamentos.query.filter(
                    (Relacionamentos.entidade_origem_id == entidade_atual_id) &
                    (Relacionamentos.tipo_origem_id == tipo_entidade_atual_id) |
                    (Relacionamentos.entidade_destino_id == entidade_atual_id) &
                    (Relacionamentos.tipo_destino_id == tipo_entidade_atual_id)
                ).all()

                # Adiciona todos os relacionamentos encontrados à lista final de relacionamentos
                todos_relacionamentos.extend(relacionamentos)

                # Para cada relacionamento, identifica a próxima entidade conectada
                for relacionamento in relacionamentos:
                    # Verifica se a entidade atual é origem; se for, a próxima é o destino; caso contrário, a próxima é a origem
                    if (relacionamento.entidade_origem_id, relacionamento.tipo_origem_id) == (
                    entidade_atual_id, tipo_entidade_atual_id):
                        proxima_entidade = (relacionamento.entidade_destino_id, relacionamento.tipo_destino_id)
                    else:
                        proxima_entidade = (relacionamento.entidade_origem_id, relacionamento.tipo_origem_id)

                    # Adiciona a próxima entidade ao conjunto da próxima camada se ainda não foi visitada
                    if proxima_entidade not in entidades_visitadas:
                        nova_entidades_para_visitar.add(proxima_entidade)

            # Incrementa a camada atual, avançando para a próxima camada
            camada_atual += 1

            # Atualiza as entidades para visitar na próxima camada
            entidades_para_visitar = nova_entidades_para_visitar

        # Retorna todos os relacionamentos encontrados até o limite de camadas
        return todos_relacionamentos

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