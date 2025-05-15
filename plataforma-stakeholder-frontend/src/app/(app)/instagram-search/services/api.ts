import axios from 'axios';

// Configura a instância do axios para a API de busca de Instagram
const instagramApi = axios.create({
    baseURL: process.env.NEXT_PUBLIC_INSTAGRAM_API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1', // Fallback mais explícito
});

const API_URL = process.env.NEXT_PUBLIC_INSTAGRAM_API_URL;

// --- Interfaces --- //

export interface Entidade {
    id: string;
    nome: string;
    tipo: 'empresa' | 'pessoa' | 'advogado';
    status: 'com_instagram' | 'sem_instagram' | 'pendente'; // Adicionado 'pendente' para clareza
    ultimaBusca: string | null;
    cnpj?: string;
    cpf?: string;
    razao_social?: string;
    nome_fantasia?: string;
    instagram?: string | null; // Adicionado campo instagram (pode ser string ou null)
    oab?: string;
}

// Interface base para um perfil do Instagram
export interface InstagramProfile {
    pk: number;
    username: string;
    full_name: string;
    profile_pic_url: string;
    is_private: boolean;
    is_verified: boolean;
    bio: string;
    is_business: boolean;
}

export interface Candidato extends InstagramProfile {
    // Herda os campos de InstagramProfile
    // Adiciona campos específicos do frontend ou do processo de validação
    status: 'pendente' | 'validado' | 'rejeitado'; // Status no processo de validação do frontend
    score?: number; // Score de validação (opcional, pode vir do validated_profile ou calculado)
}

export interface ValidatedProfile {
    perfil: InstagramProfile;
    score: number;
    is_business_profile: boolean; // Pode ser redundante com perfil.is_business? Verificar API.
}

export interface ResultadoBusca {
    entity: Entidade;
    candidates: Candidato[];
    validated_profile: ValidatedProfile | null;
    possible_profiles?: string[];
    error?: string; // Adicionado campo opcional para erros na busca em massa
}

export interface Estatistica {
    tipo: string;
    quantidade_sem_instagram: number;
    quantidade_com_instagram: number;
}

export interface UltimaBusca {
    nome: string;
    tipo: string;
    status: string;
    data: string;
}

export interface DashboardData {
    estatisticas: Estatistica[];
    ultimas_buscas: UltimaBusca[];
}

// Interface para a resposta da listagem de entidades
export interface PaginatedEntities {
    data: Entidade[];
    total: number;
    pagina: number;
    limite: number;
}

export interface CaminhoResultado {
    origem: string;
    alvo: string;
    caminhos: string[][];
    quantidade: number;
}

// --- Serviço da API --- //

export const instagramService = {
    /**
     * Busca dados para o dashboard (STATS + ÚLTIMAS BUSCAS).
     */
    getDashboardData: async (): Promise<DashboardData> => {
        const response = await fetch(`${API_URL}/ultimas_buscas`);
        if (!response.ok) {
            throw new Error('Erro ao buscar dados do dashboard');
        }
        return response.json();
    },

    /**
     * Lista entidades com filtros.
     * Usa: GET /entities/all/{entity_type}?pagina=X&limite=Y&status=Z
     */
    getEntities: async (params: {
        tipo?: 'empresa' | 'pessoa' | 'advogado' | 'todos';
        status?: 'com_instagram' | 'sem_instagram' | 'pendente' | 'todos';
        pagina?: number;
        limite?: number;
    }): Promise<PaginatedEntities> => {
        const { tipo = 'todos', status, pagina = 1, limite = 10 } = params;
        const queryParams = { pagina, limite, ...(status && status !== 'todos' && { status }) }; // Adiciona status se não for 'todos'

        if (tipo === 'todos') {
            // Se 'todos', busca os 3 tipos e combina. Poderia ser melhorado com Promise.allSettled
            console.warn('Buscando todos os tipos de entidade sequencialmente.');
            try {
                const [empresasRes, pessoasRes, advogadosRes] = await Promise.all([
                    instagramApi.get<PaginatedEntities>('/entities/all/empresa', { params: queryParams }),
                    instagramApi.get<PaginatedEntities>('/entities/all/pessoa', { params: queryParams }),
                    instagramApi.get<PaginatedEntities>('/entities/all/advogado', { params: queryParams }),
                ]);
                const combinedData = [...empresasRes.data.data, ...pessoasRes.data.data, ...advogadosRes.data.data];
                const total = empresasRes.data.total + pessoasRes.data.total + advogadosRes.data.total; // Total combinado pode não ser ideal para paginação real
                // Retorna os dados combinados, mas a paginação fica estranha. Ideal é o backend suportar `tipo=todos`.
                return { data: combinedData, total, pagina, limite };
            } catch (error) {
                console.error('Erro ao buscar todos os tipos de entidades:', error);
                throw error; // Re-lança o erro
            }
        } else {
            // Busca por tipo específico
            const response = await instagramApi.get<PaginatedEntities>(`/entities/all/${tipo}`, { params: queryParams });
            return response.data;
        }
    },

    /**
     * Busca os detalhes da entidade E os perfis candidatos/validados para uma entidade específica por ID ou Identificador.
     * Retorna a estrutura completa ResultadoBusca.
     * Usa: GET /api/v1/{entity_type}?entity_id=X ou GET /api/v1/{entity_type}?identifier=Y
     */
    getEntityProfile: async (
        entityType: 'empresa' | 'pessoa' | 'advogado',
        paramsInput: { entityId: string; identifier?: never } | { entityId?: never; identifier: string }
    ): Promise<ResultadoBusca | null> => {
        let queryParams;
        if (paramsInput.entityId) {
            queryParams = { entity_id: paramsInput.entityId }; // Converte para entity_id aqui
        } else {
            queryParams = { identifier: paramsInput.identifier };
        }

        try {
            const response = await instagramApi.get<ResultadoBusca>(`/${entityType}`, { params: queryParams });
            return response.data;
        } catch (error: any) {
            if (error.response && error.response.status === 404) {
                console.warn(`Entidade ${entityType} com params ${JSON.stringify(queryParams)} não encontrada (404). Retornando null.`);
                return null;
            }
            console.error(`Erro ao buscar perfil/candidatos para ${entityType} com params ${JSON.stringify(queryParams)}:`, error);
            throw error;
        }
    },

    /**
     * Inicia a busca de perfil para uma entidade específica (POST para iniciar job individual).
     * Usa: POST /entity/{entity_type}/{entity_id}/find 
     */
    findInstagramForEntity: async (entityType: string, entityId: string): Promise<{ jobId: string }> => {
        const response = await instagramApi.post<{ jobId: string }>(`/entity/${entityType}/${entityId}/find`);
        return response.data;
    },

    /**
     * Inicia a busca de perfis para TODAS as entidades de um tipo sem Instagram (GET para iniciar job em massa).
     * Usa: GET /api/v1/entities/all/{entity_type}
     * Retorno: { results: ResultadoBusca[] }
     */
    findAllInstagramForEntityType: async (entityType: string): Promise<{ results: ResultadoBusca[] }> => {
        const response = await instagramApi.get<{ results: ResultadoBusca[] }>(`/entities/all/${entityType}`);
        return response.data || { results: [] };
    },

    /**
     * Valida ou rejeita um perfil candidato.
     * Usa: POST /candidate/{candidate_id}/validate (Endpoint Provisório)
     */
    validateCandidate: async (candidateId: string, data: {
        status: 'validado' | 'rejeitado';
        observacao?: string;
    }): Promise<void> => {
        // NOTA: Endpoint não presente no Swagger.
        console.warn(`PROVISÓRIO: Usando endpoint POST /candidate/${candidateId}/validate não presente no Swagger.`);
        await instagramApi.post(`/candidate/${candidateId}/validate`, data);
    },

    /**
     * Confirma um username do Instagram para uma entidade específica.
     * Usa: POST /entity/{entity_type}/{entity_id}/confirm_instagram
     */
    confirmInstagramProfile: async (entityType: string, entityId: string, username: string): Promise<void> => {
        await instagramApi.post(`/entity/${entityType}/${entityId}/confirm_instagram`, { instagram: username });
    },

    /**
     * Busca perfis para uma empresa e seus relacionados (pessoas/advogados sem Instagram).
     * Usa: GET /company/{company_id}/related
     * Parâmetro: cnpj da empresa
     */
    getCompanyRelated: async (cnpj: string): Promise<any> => {
        const response = await instagramApi.get(`/company/${cnpj}/related`);
        return response.data;
    },

    /**
     * Lista todas as entidades (fictício, até implementação real do endpoint).
     */
    listAllEntities: async (): Promise<PaginatedEntities> => {
        // Simulação de resposta fictícia
        return {
            data: [
                { id: '1', nome: 'Empresa Fictícia', tipo: 'empresa', status: 'com_instagram', ultimaBusca: null },
                { id: '2', nome: 'Pessoa Fictícia', tipo: 'pessoa', status: 'sem_instagram', ultimaBusca: null },
                { id: '3', nome: 'Advogado Fictício', tipo: 'advogado', status: 'pendente', ultimaBusca: null },
            ],
            total: 3,
            pagina: 1,
            limite: 10,
        };
    },

    /**
     * Lista paginada de todas as entidades (empresa, pessoa, advogado) com status de Instagram.
     * Usa: GET /entities/list/all?pagina=X&limite=Y
     */
    getAllEntitiesPaginated: async (pagina = 1, limite = 10): Promise<PaginatedEntities> => {
        const response = await instagramApi.get('/entities/list/all', { params: { pagina, limite } });
        return response.data;
    },

    /**
     * Lista paginada de entidades por tipo (fictício, ajuste para endpoint real depois).
     * GET /entities/list/{tipo}?pagina=X&limite=Y
     */
    getEntitiesByTypePaginated: async (tipo: 'empresa' | 'pessoa' | 'advogado', pagina = 1, limite = 10): Promise<PaginatedEntities> => {
        const response = await instagramApi.get(`/entities/list/${tipo}`, { params: { pagina, limite } });
        return response.data;
    },

    /**
     * Busca completa de entidades por tipo e termo (nome, CNPJ, CPF).
     * GET /entities/search?tipo=empresa|pessoa|advogado&query=valor&pagina=X&limite=Y
     */
    searchEntities: async (tipo: 'empresa' | 'pessoa' | 'advogado', query: string, pagina = 1, limite = 10): Promise<PaginatedEntities> => {
        const response = await instagramApi.get('/entities/search', {
            params: { tipo, query, pagina, limite }
        });
        return response.data;
    },

    /**
     * Busca relacionados para qualquer entidade (empresa, pessoa, advogado).
     * Usa: GET /entities/{entity_type}/related?identifier={CNPJ_ou_CPF}
     */
    getEntityRelated: async (entityType: 'empresa' | 'pessoa' | 'advogado', identifier: string): Promise<any> => {
        const response = await instagramApi.get(`/entities/${entityType}/related`, { params: { identifier } });
        return response.data;
    },

    /**
     * Busca nomes específicos entre os seguidores de um perfil do Instagram.
     * Usa: POST /search-names-in-followers
     * @param target_username Username do perfil alvo
     * @param names_to_find Lista de nomes a serem buscados
     * @param similarity_threshold Limiar de similaridade (0.0 a 1.0, padrão 0.8)
     * @returns Resultado da busca
     */
    searchNamesInFollowers: async (
        target_username: string,
        names_to_find: string[],
        similarity_threshold: number = 0.8
    ): Promise<any> => {
        const response = await instagramApi.post('/search-names-in-followers', names_to_find, {
            params: { target_username, similarity_threshold },
        });
        return response.data;
    },

    /**
     * Busca todos os menores caminhos (BFS) entre dois usuários do Instagram.
     * Usa: GET /caminhos/bfs?username_origem=X&username_alvo=Y&max_search_depth=Z
     */
    buscarCaminhosBFS: async (
        usernameOrigem: string,
        usernameAlvo: string,
        maxSearchDepth: number = 5
    ): Promise<CaminhoResultado> => {
        const response = await instagramApi.get<CaminhoResultado>('/caminhos/bfs', {
            params: {
                username_origem: usernameOrigem,
                username_alvo: usernameAlvo,
                max_search_depth: maxSearchDepth
            }
        });
        return response.data;
    },

    /**
     * Busca todos os caminhos (DFS) entre dois usuários do Instagram.
     * Usa: GET /caminhos/dfs?username_origem=X&username_alvo=Y&max_search_depth=Z
     */
    buscarCaminhosDFS: async (
        usernameOrigem: string,
        usernameAlvo: string,
        maxSearchDepth: number = 5
    ): Promise<CaminhoResultado> => {
        const response = await instagramApi.get<CaminhoResultado>('/caminhos/dfs', {
            params: {
                username_origem: usernameOrigem,
                username_alvo: usernameAlvo,
                max_search_depth: maxSearchDepth
            }
        });
        return response.data;
    },
}; 