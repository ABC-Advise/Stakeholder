import { api } from '../api-client';

interface GetEmpresasQuery {
  empresa_id?: number | null;
  page?: number | null;
  size?: number | null;
  cnpj?: string | null;
  razao_social?: string | null;
  segmento_id?: string | null;
  porte_id?: string | null;
  uf?: string | null;
  cidade?: string | null;
}

export interface GetEmpresasResponse {
  empresas: {
    empresa_id: number;
    cnpj: string;
    razao_social: string;
    nome_fantasia: string;
    data_fundacao: string;
    quantidade_funcionarios: string;
    situacao_cadastral: string;
    codigo_natureza_juridica: string;
    natureza_juridica_descricao: string;
    natureza_juridica_tipo: string;
    faixa_funcionarios: string;
    faixa_faturamento: string;
    matriz: string;
    orgao_publico: string;
    ramo: string;
    tipo_empresa: string;
    ultima_atualizacao_pj: string;
    porte_id: number;
    segmento_id: number;
    linkedin: string;
    instagram: string;
    stakeholder: boolean;
    em_prospecao: boolean;
    projeto_id: string;
    projeto: any;
    cnae: string;
    descricao_cnae: string;
    porte: string;
    segmento: string;
  }[];
  meta: {
    total: number;
    page: number;
    size: number;
    pages: number;
  };
}

export async function getEmpresas({
  empresa_id,
  page,
  size,
  cnpj,
  razao_social,
  segmento_id,
  porte_id,
  uf,
  cidade,
}: GetEmpresasQuery): Promise<GetEmpresasResponse> {
  const response = await api.get(`/empresa`, {
    params: {
      empresa_id,
      page,
      size,
      cnpj,
      razao_social,
      segmento_id,
      porte_id,
      uf,
      cidade,
    },
  });

  return response.data;
}
