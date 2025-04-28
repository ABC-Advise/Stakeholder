import { api } from '../api-client'

interface GetProjetosQuery {
  projeto_id?: number | null
  page?: number | null
  size?: number | null
}

export interface GetProjetosResponse {
  projetos: {
    projeto_id: number
    nome: string
    descricao: string
    data_inicio: string
    data_fim: string
  }[]
  meta: {
    total: number
    page: number
    size: number
    pages: number
  }
}

export async function getProjetos({
  projeto_id,
  page,
  size,
}: GetProjetosQuery): Promise<GetProjetosResponse> {
  const response = await api.get(`/projetos`, {
    params: {
      projeto_id,
      page,
      size,
    },
  })

  return response.data
}
