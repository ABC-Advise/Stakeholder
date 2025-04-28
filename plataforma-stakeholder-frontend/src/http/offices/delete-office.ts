import { api } from '../api-client'

interface UpdateOfficeRequest {
  escritorio_id: number
}

export async function deleteOffice({ escritorio_id }: UpdateOfficeRequest) {
  await api.delete(`/escritorio?escritorio_id=${escritorio_id}`)
}
