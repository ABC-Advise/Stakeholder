import { api } from '../api-client'

interface UpdateLawyerRequest {
  advogado_id: number
  firstname?: string
  lastname?: string
  oab?: string
}

interface UpdateLawyerResponse {
  advogado_id: number
  firstname: string
  lastname: string
  oab: string
  linkedin: string
  instagram: string
}

export async function updateLawyer({
  advogado_id,
  firstname,
  lastname,
  oab,
}: UpdateLawyerRequest): Promise<UpdateLawyerResponse> {
  const response = await api.put(`/advogado`, {
    advogado_id,
    firstname,
    lastname,
    oab,
  })

  return response.data
}
