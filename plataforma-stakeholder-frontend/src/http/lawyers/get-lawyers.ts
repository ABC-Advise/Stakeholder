import { api } from '../api-client'

interface GetLawyersQuery {
  page?: number | null
  size?: number | null
  advogado_id?: number | null
  oab?: string | null
  cpf?: string | null
  nome?: string | null
  sobrenome?: string | null
  stakeholder?: string | null
}

export interface GetLawyersResponse {
  advogados: {
    advogado_id: number
    firstname: string
    lastname: string
    oab: string
    cpf: string
    linkedin: string
    instagram: string
  }[]
  meta: {
    total: number
    page: number
    size: number
    pages: number
  }
}

export async function getLawyers({
  page,
  size,
  advogado_id,
  oab,
  cpf,
  nome,
  sobrenome,
  stakeholder,
}: GetLawyersQuery): Promise<GetLawyersResponse> {
  const response = await api.get(`/advogado`, {
    params: {
      page,
      size,
      advogado_id,
      oab,
      cpf,
      nome,
      sobrenome,
      stakeholder,
    },
  })

  return response.data
}
