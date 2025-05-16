import { api } from '../api-client';

interface GetPessoasQuery {
  pessoa_id?: number | null;
  page?: number | null;
  size?: number | null;
  cpf?: string | null;
  nome?: string | null;
  sobrenome?: string | null;
  uf?: string | null;
  cidade?: string | null;
}

export interface GetPessoasResponse {
  pessoas: {
    pessoa_id: number;
    firstname: string;
    lastname: string;
    cpf: string;
    linkedin: string;
    instagram: string;
    stakeholder: boolean;
    em_prospecao: boolean;
    pep: boolean;
    sexo: string;
    data_nascimento: string;
    nome_mae: string;
    idade: number;
    signo: string;
    obito: boolean;
    data_obito: string;
    renda_estimada: string;
    projeto_id: number;
  }[];
  meta: {
    total: number;
    page: number;
    size: number;
    pages: number;
  };
}

export async function getPessoas({
  pessoa_id,
  page,
  size,
  cpf,
  nome,
  sobrenome,
  uf,
  cidade,
}: GetPessoasQuery): Promise<GetPessoasResponse> {
  const response = await api.get(`/pessoa`, {
    params: {
      pessoa_id,
      page,
      size,
      cpf,
      nome,
      sobrenome,
      uf,
      cidade,
    },
  });

  return response.data;
}
