import { api } from '../api-client';

interface GetLogsByIdQuery {
  consulta_id: number;
  page?: number;
  size?: number;
}

export interface Log {
  consulta_id: number;
  log_consulta_id: number;
  mensagem: string;
  tipo_log_id: number;
  tipo_log_nome: string;
  data_log: string;
}

export interface GetLogsByIdResponse {
  consulta_id: number;
  documento: string;
  is_cnpj: boolean;
  data_consulta: string;
  logs: Log[];
  meta: {
    total: number;
    page: number;
    size: number;
    pages: number;
  };
}

export async function getLogsById(
  query: GetLogsByIdQuery
): Promise<GetLogsByIdResponse> {
  const response = await api.get(`/log`, { params: query });

  return response.data;
}
