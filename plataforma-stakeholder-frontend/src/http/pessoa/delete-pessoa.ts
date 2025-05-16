import { api } from '../api-client';

interface DeletePessoaRequest {
  pessoa_id: number;
}

export async function deletePessoa({ pessoa_id }: DeletePessoaRequest) {
  await api.delete(`/pessoa?pessoa_id=${pessoa_id}`);
}
