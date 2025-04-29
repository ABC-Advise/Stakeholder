import { api } from '../api-client'

interface DeleteEmpresaRequest {
  empresa_id: number
}

export async function deleteEmpresa({ empresa_id }: DeleteEmpresaRequest) {
  await api.delete(`/empresa?empresa_id=${empresa_id}`)
}
