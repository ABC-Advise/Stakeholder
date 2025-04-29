import { api } from '../api-client'

interface UpdateOfficeRequest {
  escritorio_id: number
  nome_fantasia?: string
  razao_social?: string
}

interface UpdateOfficeResponse {
  escritorio_id: number
  razao_social: string
  nome_fantasia: string
  linkedin: string
  instagram: string
}

export async function updateOffice({
  escritorio_id,
  nome_fantasia,
  razao_social,
}: UpdateOfficeRequest): Promise<UpdateOfficeResponse> {
  const response = await api.put(`/escritorio`, {
    escritorio_id,
    nome_fantasia,
    razao_social,
  })

  return response.data
}
