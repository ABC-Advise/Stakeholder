import { api } from '../api-client'

interface CreatePessoaRequest {
  firstname: string
  lastname: string
  cpf: string
  linkedin?: string
  instagram?: string
  stakeholder: boolean
  em_prospecao: boolean
  projeto_id?: number
}

interface CreatePessoaResponse {
  pessoa_id: number
  firstname: string
  lastname: string
  cpf: string
  stakeholder: boolean
  em_prospecao: boolean
  linkedin: string
  instagram: string
  projeto_id: number
}

export async function createPessoa({
  firstname,
  lastname,
  cpf,
  linkedin,
  instagram,
  stakeholder,
  em_prospecao,
  projeto_id,
}: CreatePessoaRequest): Promise<CreatePessoaResponse> {
  const response = await api.post(`/pessoa`, {
    firstname,
    lastname,
    cpf,
    linkedin,
    instagram,
    stakeholder,
    em_prospecao,
    projeto_id,
  })

  return response.data
}
