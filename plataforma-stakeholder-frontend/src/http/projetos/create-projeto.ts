import { api } from '../api-client';

interface CreateProjetoRequest {
  nome: string;
  descricao: string;
  data_inicio: string;
  data_fim: string;
}

interface CreateProjetoResponse {
  projeto_id: number;
  nome: string;
  descricao: string;
  data_inicio: string;
  data_fim: string;
}

export async function createProjeto({
  nome,
  descricao,
  data_inicio,
  data_fim,
}: CreateProjetoRequest): Promise<CreateProjetoResponse> {
  const response = await api.post(`/projetos`, {
    nome,
    descricao,
    data_inicio,
    data_fim,
  });

  return response.data;
}
