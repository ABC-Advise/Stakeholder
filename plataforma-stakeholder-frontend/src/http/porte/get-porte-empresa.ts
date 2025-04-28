import { api } from '../api-client'

interface GetPorteEmpresaResponseQuery {
  porte_id?: number | null
  page?: number | null
  size?: number | null
}

export interface GetPorteEmpresaResponse {
  porte_empresas: {
    porte_id: number
    descricao: string
  }[]
  meta: {
    total: number
    page: number
    size: number
    pages: number
  }
}

export async function getPorteEmpresa({
  porte_id,
  page,
  size,
}: GetPorteEmpresaResponseQuery): Promise<GetPorteEmpresaResponse> {
  const response = await api.get(`/porte_empresa`, {
    params: {
      porte_id,
      page,
      size,
    },
  })

  return response.data
}
