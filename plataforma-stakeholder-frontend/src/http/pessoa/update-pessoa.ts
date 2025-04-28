import { api } from '../api-client'

interface UpdatePessoaRequest {
  pessoa_id: number
  firstname?: string
  lastname?: string
  cpf: string
  linkedin?: string
  instagram?: string
  stakeholder: boolean
  em_prospecao: boolean
  associado?: boolean
  projeto_id?: number
}

export async function updatePessoa({
  pessoa_id,
  firstname,
  lastname,
  cpf,
  linkedin,
  instagram,
  stakeholder,
  em_prospecao,
  associado,
  projeto_id,
}: UpdatePessoaRequest) {
  const response = await api.put(`/pessoa`, {
    pessoa_id,
    firstname,
    lastname,
    cpf,
    linkedin,
    instagram,
    stakeholder,
    em_prospecao,
    associado,
    projeto_id,
  })

  return response.data
}
