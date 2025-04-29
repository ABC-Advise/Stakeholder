from graphviz import Digraph
from app.modules.objects.pessoa_juridica import PessoaJuridica
from app.modules.objects.pessoa_fisica import PessoaFisica
from app.modules.objects.advogado import Advogado
from app.modules.utils import capitalize_first_letter, format_cpf, format_cnpj


class RedeStakeholder:
    def __init__(self, relacionamentos=None):
        self.__graph = Digraph(comment="Rede de Relacionamentos", format='png')  # Criar grafo com Graphviz
        self.__added_nodes = set()  # Conjunto para rastrear nós já adicionados
        self.__added_edges = set()  # Conjunto para rastrear arestas já adicionadas
        self.__relacionamentos = relacionamentos if relacionamentos else dict()

    @staticmethod
    def print_rede(no, n=1):
        if not no:
            return

        print("*" * n, no)
        n += 1
        if isinstance(no, PessoaJuridica) and no.socios:
            for socio in no.socios:
                RedeStakeholder.print_rede(socio, n)
        elif isinstance(no, PessoaFisica):
            if no.parentescos:
                for parentesco in no.parentescos:
                    RedeStakeholder.print_rede(parentesco, n - 1)
            if no.sociedades:
                for sociedade in no.sociedades:
                    RedeStakeholder.print_rede(sociedade, n)

    def add_to_graph(self, no, parent=None, relationship_label=""):
        """Recursivamente adiciona nós e arestas ao grafo, evitando duplicação."""
        # Verificar se o nó já foi adicionado
        if isinstance(no, PessoaJuridica):
            node_id = format_cnpj(no.cnpj)  # Identificador único
            label = f"Empresa: {no.razao_social}\nCNPJ: {no.cnpj}"
        elif isinstance(no, PessoaFisica):
            node_id = format_cpf(no.cpf)  # Identificador único
            label = f"Pessoa: {no.nome}\nCPF: {no.cpf}"
        elif isinstance(no, Advogado):
            node_id = str(no.oabs[0].numero)
            label = f"Advogado: {no.nome}\nOAB: {node_id}"
        else:
            return  # Caso seja algum tipo desconhecido

        # Se o nó ainda não foi adicionado, adicioná-lo ao grafo e ao conjunto de nós já adicionados
        if node_id not in self.__added_nodes:
            self.__graph.node(node_id, label)
            self.__added_nodes.add(node_id)

        # Se existir um nó pai, verificar se a aresta já foi adicionada
        if parent:
            edge_id = (parent, node_id)  # Identificar aresta como um par (parent, node_id)
            if edge_id not in self.__added_edges:
                self.__graph.edge(parent, node_id, label=relationship_label)  # Adicionar aresta ao grafo
                self.__added_edges.add(edge_id)  # Marcar a aresta como adicionada

        # Adicionar sócios para PessoaJuridica
        if isinstance(no, PessoaJuridica):
            if no.socios:
                for socio in no.socios:
                    self.add_to_graph(socio, node_id, relationship_label="Sociedade")

            if no.advogados:
                for advogado in no.advogados:
                    self.add_to_graph(advogado, node_id, relationship_label="Advogado")

        # Adicionar parentescos e sociedades para PessoaFisica
        elif isinstance(no, PessoaFisica):
            if no.parentescos:
                for parentesco in no.parentescos:
                    parentesco_label = "Parentesco"
                    if parentesco:
                        cpf_formatado = format_cpf(parentesco.cpf)
                        for relacao in self.__relacionamentos:
                            if relacao.entidade_1 == node_id and relacao.entidade_2 == cpf_formatado:
                                # print(relacao, cpf_formatado, node_id)
                                parentesco_label = capitalize_first_letter(relacao.tipo_relacionamento)
                                break
                        self.add_to_graph(parentesco, node_id,
                                          relationship_label=parentesco_label)
            if no.sociedades:
                for sociedade in no.sociedades:
                    self.add_to_graph(sociedade, node_id,
                                      relationship_label="Sócio")

            if no.advogados:
                for advogado in no.advogados:
                    self.add_to_graph(advogado, node_id,
                                      relationship_label="Advogado")

        # Adicionar clientes para Advogado
        elif isinstance(no, Advogado) and no.envolvidos:
            for envolvido in no.envolvidos:
                self.add_to_graph(envolvido, node_id,
                                  relationship_label="Cliente")

    def render_graph(self, output_filename="rede_relacionamentos"):
        """Renderiza e salva o grafo como um arquivo de imagem."""
        self.__graph.render(output_filename, view=True)  # Gera o arquivo PNG e o exibe automaticamente
