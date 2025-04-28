import { api } from '../api-client'

interface GetOfficesQuery {
  page?: number | null
  size?: number | null
  escritorio_id?: number | null
}

interface GetOfficesResponse {
  escritorios: {
    escritorio_id: number
    razao_social: string
    nome_fantasia: string
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

export async function getOffices({
  page,
  size,
  escritorio_id,
}: GetOfficesQuery): Promise<GetOfficesResponse> {
  const response = await api.get(`/escritorio`, {
    params: {
      page,
      size,
      escritorio_id,
    },
  })

  return response.data
}
