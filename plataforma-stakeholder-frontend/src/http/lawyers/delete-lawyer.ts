import { api } from '../api-client'

interface UpdateLawyerRequest {
  advogado_id: number
}

export async function deleteLawyer({ advogado_id }: UpdateLawyerRequest) {
  await api.delete(`/advogado?advogado_id=${advogado_id}`)
}
