import { api } from '../api-client';

interface GetAllConsultQuery {
  consulta_id?: number;
  data_inicio?: string;
  data_fim?: string;
  antigo_primeiro?: boolean | null;
  page?: number;
  size?: number;
}

export interface Consulta {
  consulta_id: number;
  documento: string;
  is_cnpj: boolean;
  data_consulta: string;
  status: string;
}

interface GetAllConsultResponse {
  consultas: Consulta[];
  meta: {
    total: number;
    page: number;
    size: number;
    pages: number;
  };
}

export async function getAllConsult(
  query: GetAllConsultQuery
): Promise<GetAllConsultResponse> {
  const response = await api.get(`/consulta`, { params: query });

  return response.data;
}
