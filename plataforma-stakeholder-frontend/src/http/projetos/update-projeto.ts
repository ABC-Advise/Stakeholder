import { api } from '../api-client';

interface UpdateProjetoRequest {
  projeto_id: number;
  nome: string;
  descricao: string;
  data_inicio: string;
  data_fim: string;
}

export async function updateProjeto({
  projeto_id,
  nome,
  descricao,
  data_inicio,
  data_fim,
}: UpdateProjetoRequest) {
  const response = await api.put(`/projetos`, {
    projeto_id,
    nome,
    descricao,
    data_inicio,
    data_fim,
  });

  return response.data;
}
