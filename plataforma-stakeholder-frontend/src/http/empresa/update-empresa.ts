import { api } from '../api-client';

interface UpdateEmpresaRequest {
  empresa_id: number;
  cnpj?: string;
  razao_social?: string;
  nome_fantasia?: string;
  porte_id?: number;
  segmento_id?: number;
  linkedin?: string;
  instagram?: string;
  stakeholder?: boolean;
  em_prospecao?: boolean;
  projeto_id?: number;
}

export async function updateEmpresa({
  empresa_id,
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
}: UpdateEmpresaRequest) {
  const response = await api.put(`/empresa`, {
    empresa_id,
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
