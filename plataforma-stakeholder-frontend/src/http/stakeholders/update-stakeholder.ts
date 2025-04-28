import { api } from '../api-client'

interface UpdateStakeholderRequest {
  documento: string
  prospeccao?: boolean
  stakeholder?: boolean
  camada_advogados?: boolean
  camada_stakeholder?: boolean
  associado?: boolean
  stakeholder_advogado?: boolean
}

export async function updateStakeholder({
  documento,
  prospeccao,
  stakeholder,
  camada_advogados,
  camada_stakeholder,
  associado,
  stakeholder_advogado,
}: UpdateStakeholderRequest) {
  const response = await api.put(`/stakeholders`, {
    documento,
    prospeccao,
    camada_stakeholder,
    camada_advogados,
    associado,
    stakeholder_advogado,
  })

  return response.data
}
