import { CheckedState } from '@radix-ui/react-checkbox'
import { api } from '../api-client'

interface GetStakeholdersQuery {
  page?: number | null
  size?: number | null
  documento?: string | null
  em_prospecao?: CheckedState | undefined
  associado?: CheckedState | undefined
  tipo_stakeholder?: string | null
  uf?: string | null
  cidade?: string | null
}

export interface GetStakeholdersResponse {
  stakeholders: {
    entidade_id: number
    document: string
    is_CNPJ: boolean
    nome1: string
    nome2: string
    porte_id: number
    segmento_id: number
    linkedin: string
    instagram: string
    stakeholder: boolean
    em_prospecao: boolean
    associado: boolean | null
  }[]
  meta: {
    total: number
    page: number
    size: number
    pages: number
  }
}

export async function getStakeholders({
  page,
  size,
  documento,
  em_prospecao,
  tipo_stakeholder,
  associado,
  uf,
  cidade,
}: GetStakeholdersQuery): Promise<GetStakeholdersResponse> {
  const response = await api.get(`/stakeholders`, {
    params: {
      page,
      size,
      documento,
      em_prospecao,
      tipo_stakeholder,
      associado,
      uf,
      cidade,
    },
  })

  console.log(response.data)

  return response.data
}
