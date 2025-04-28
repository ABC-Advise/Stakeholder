import { api } from './api-client'

interface GetNetworkQuery {
  nome?: string | null
  razao_social?: string | null
  associado?: string | null
  em_prospecao?: string | null
  documento?: string | null
  camadas?: number | null
  uf?: string | null
  cidade?: string | null
  projeto_id?: string | null
  segmento_id?: string | null
}

export interface Node {
  id: string
  label: string
  type: string
  title: string
  documento: string
  stakeholder: boolean
  em_prospeccao: boolean
  matched: boolean
  root: boolean
}

// export interface Link {
//   source: string
//   target: string
//   label: string
// }

type Links = {
  source: string
  target: string
  label: string
}

type Nodes = {
  id: string
  subgroup: string
  title: string
  label: string
  type: string
  documento: string
  em_prospeccao: boolean
  matched: boolean
  root: boolean
  stakeholder: boolean
}

type NetworkGraphProps = {
  links: Links[]
  nodes: Nodes[]
}

export async function getNetwork(
  query: GetNetworkQuery,
): Promise<NetworkGraphProps[]> {
  const response = await api.get(`/relacionamentos`, { params: query })

  return response.data.clusters
}
