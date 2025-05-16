import { api } from '../api-client';

interface CreateEmpresaRequest {
  cnpj: string;
  razao_social: string;
  nome_fantasia: string;
  porte_id: number;
  segmento_id: number;
  linkedin?: string;
  instagram?: string;
  stakeholder: boolean;
  em_prospecao: boolean;
  projeto_id?: number;
}

interface CreateEmpresaResponse {
  cnpj: string;
  razao_social: string;
  nome_fantasia: string;
  porte_id: number;
  segmento_id: number;
  linkedin: string;
  instagram: string;
  stakeholder: boolean;
  em_prospecao: boolean;
  projeto_id: number;
}

export async function createEmpresa({
  cnpj,
  razao_social,
  nome_fantasia,
  porte_id,
  segmento_id,
  linkedin,
  instagram,
  stakeholder,
  em_prospecao,
  projeto_id,
}: CreateEmpresaRequest): Promise<CreateEmpresaResponse> {
  const response = await api.post(`/empresa`, {
    cnpj,
    razao_social,
    nome_fantasia,
    porte_id,
    segmento_id,
    linkedin,
    instagram,
    stakeholder,
    em_prospecao,
    projeto_id,
  });

  return response.data;
}
